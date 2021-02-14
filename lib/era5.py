import xarray as xr
import pandas as pd

RDA_THREDDS_URL = 'https://rda.ucar.edu/thredds/dodsC/files/g'


class _ERA5Variable:
    def __init__(self, code):
        self.code = code


class PL_VARS:
    HEIGHT = _ERA5Variable(code='128_129_z.ll025sc')
    TEMPERATURE = _ERA5Variable(code='128_130_t.ll025sc')
    U_WIND = _ERA5Variable(code='128_131_u.ll025uv')
    V_WIND = _ERA5Variable(code='128_132_v.ll025uv')
    OMEGA = _ERA5Variable(code='128_135_w.ll025sc')
    VORTICITY = _ERA5Variable(code='128_138_vo.ll025sc')
    RH = _ERA5Variable(code='128_157_r.ll025sc')


def era5_pl_monthly(year, var, session):
    category = 'e5.moda.an.pl'
    catalog = 'ds633.1_nc'
    base_url = f'{RDA_THREDDS_URL}/{catalog}/{category}'
    url = f'{base_url}/{year}/{category}.{var.code}.{year}010100_{year}120100.nc'
    return open_dataset(url, session)


def era5_pl_daily(when, var, session):
    category = 'e5.oper.an.pl'
    catalog = 'ds633.0'

    def _generate_daily_url(t):
        t = pd.Timestamp(t)
        base_url = f'{RDA_THREDDS_URL}/{catalog}/{category}'
        return f'{base_url}/{t:%Y%m}/{category}.{var.code}.{t:%Y%m%d}00_{t:%Y%m%d}23.nc'

    if not isinstance(when, (list, tuple, set)):
        url = _generate_daily_url(when)
        return open_dataset(url, session)

    urls = [_generate_daily_url(t) for t in when]
    stores = [xr.backends.PydapDataStore.open(file, session=session) for file in urls]
    return xr.open_mfdataset(stores)


def open_dataset(url, session, **kwargs):
    print('Opening dataset for ' + url)
    store = xr.backends.PydapDataStore.open(url, session=session)
    return xr.open_dataset(store, **kwargs)
