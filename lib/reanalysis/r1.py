import os
import warnings

import numpy as np
import pandas as pd
import xarray as xr
from xarray import SerializationWarning


def hgt_monthly(level, yearmonths, bbox=None):
    yearmonths = list(map(pd.Timestamp, yearmonths))

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=SerializationWarning)

        workdir = os.getenv('WORKDIR')

        ds_mon = xr.open_dataset(os.path.join(workdir, 'hgt.mon.mean.nc'))
        ds_mon_mean = xr.open_dataset(os.path.join(workdir, 'hgt.mon.ltm.nc'))

        years = set(dt.year for dt in yearmonths)
        ds_mon_mean = _coerce_ltm_ds(ds_mon_mean, years)

        kw = {
            'level': level,
            'time': yearmonths,
        }

        if bbox is not None:
            west, east, north, south = bbox
            kw['lon'] = slice(west, east)
            kw['lat'] = slice(north, south)

        hgt_ret = ds_mon.sel(**kw)
        hgt_mean_ret = ds_mon_mean.sel(**kw)
        hgt_anom_ret = hgt_ret - hgt_mean_ret
        return hgt_ret, hgt_mean_ret, hgt_anom_ret


def _coerce_ltm_ds(ds, years):
    orig_times = ds.time.values
    concat_datasets = []
    for year in years:
        ds_for_year = ds.copy()
        newtimes = np.array([pd.Timestamp(year=year,
                                          month=t.month,
                                          day=t.day,
                                          hour=t.hour,
                                          minute=t.minute) for t in orig_times])
        ds_for_year['time'] = newtimes
        concat_datasets.append(ds_for_year)

    return xr.concat(concat_datasets, dim='time')
