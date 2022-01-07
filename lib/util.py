from itertools import product

import pandas as pd


def generate_yearmonths(years, months):
    return [pd.Timestamp(year=year, month=month, day=1)
            for year, month in product(years, months)]
