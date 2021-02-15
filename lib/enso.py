import pandas as pd

TRIMONTHLY_MAPPING = {
    'DJF': 1,
    'JFM': 2,
    'FMA': 3,
    'MAM': 4,
    'AMJ': 5,
    'MJJ': 6,
    'JJA': 7,
    'JAS': 8,
    'ASO': 9,
    'SON': 10,
    'OND': 11,
    'NDJ': 12,
}


def oni_trimonthly():
    df = pd.read_csv('https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt', sep='\s+')
    df['MONTH'] = df['SEAS'].apply(seas_to_mo)
    return df


def seas_to_mo(seas):
    return TRIMONTHLY_MAPPING[seas]
