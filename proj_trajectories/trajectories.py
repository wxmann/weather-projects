from collections import OrderedDict

import pandas as pd
import numpy as np


def back_trajectory(latlon, level, times, u, v, w, T=None):
    lat, lon = latlon
    lev = level
    result = OrderedDict()
    times = [pd.Timestamp(t) for t in times]
    if len(times) < 2:
        raise ValueError('len(times) must >= 2')

    def get_values(t, lon_, lat_, lev_):
        if not T:
            return lat_, lon_, lev_
        Tval = float(sel(T.T, t, lon_, lat_, lev_))
        return lat_, lon_, lev_, Tval

    result[times[0]] = get_values(times[0], lon, lat, lev)

    for t, t1 in zip(times[:-1], times[1:]):
        ut = float(sel(u.U, t, lon, lat, lev))
        vt = float(sel(v.V, t, lon, lat, lev))
        wt = float(sel(w.W, t, lon, lat, lev))
        dt = t - t1
        lon1, lat1, lev1 = calc_step(ut, vt, wt, lon, lat, lev, dt)

        ut2 = float(sel(u.U, t1, lon1, lat1, lev1))
        vt2 = float(sel(v.V, t1, lon1, lat1, lev1))
        wt2 = float(sel(w.W, t1, lon1, lat1, lev1))
        lon2, lat2, lev2 = calc_step(ut2, vt2, wt2, lon, lat, lev, dt)

        lat_avg = (lat1 + lat2) / 2
        lon_avg = (lon1 + lon2) / 2
        lev_avg = (lev1 + lev2) / 2
        result[t1] = get_values(t1, lon_avg, lat_avg, lev_avg)

        lat, lon, lev = lat_avg, lon_avg, lev_avg

    return result


def sel(ds, t, lon, lat, lev):
    sel_kw = {'time': t}
    lonmin, lonmax = lon - 5 + 360, lon + 5 + 360
    latmin, latmax = lat - 5, lat + 5
    levmin, levmax = lev - 100, lev + 100
    sel_kw['longitude'] = slice(max(lonmin, 0), min(lonmax, 360))
    sel_kw['latitude'] = slice(min(latmax, 90), max(latmin, -90))
    sel_kw['level'] = slice(max(levmin, 1), levmax)

    ds_subset = ds.sel(**sel_kw)
    return ds_subset.interp(latitude=lat, longitude=lon + 360, level=lev)


def dest_pt(lon0, lat0, bearing, dist, R=6378.1):
    lon0 = np.radians(lon0)
    lat0 = np.radians(lat0)

    lat1 = np.arcsin(np.sin(lat0) * np.cos(dist / R) + np.cos(lat0) * np.sin(dist / R) * np.cos(bearing))
    lon1 = lon0 + np.arctan2(np.sin(bearing) * np.sin(dist / R) * np.cos(lat0),
                             np.cos(dist / R) - np.sin(lat0) * np.sin(lat1))

    return np.degrees(lon1), np.degrees(lat1)


# u, v in units of m/s
# w in units of Pa/s
# dt = pd.Timedelta instance
def calc_step(u, v, w, lon, lat, lev, dt, back=True):
    def to_heading(angle):
        return np.pi / 2 - angle

    def mps_to_kph(mps):
        return mps * 3.6

    def pa_s_to_hPa_hr(pa_s):
        return pa_s * 36

    dt /= pd.Timedelta(1, 'h')
    dlev = pa_s_to_hPa_hr(w) * dt

    offset = np.pi if back else 0
    theta = to_heading(np.arctan2(v, u) + offset)
    r = mps_to_kph(np.sqrt(v ** 2 + u ** 2)) * dt
    lon1, lat1 = dest_pt(lon, lat, theta, r)

    return lon1, lat1, lev + dlev
