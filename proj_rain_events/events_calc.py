from sklearn.metrics import pairwise_distances
from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np


def precip_events(df, eps, min_samples, chunks=None):
    if not chunks or eps >= chunks:
        return find_hourly_precip_clusts(df, eps, min_samples)

    max_cluster = 0
    result = []
    for chunk in _partition(df, chunks, eps):
        clusts = find_hourly_precip_clusts(chunk, eps, min_samples)
        clusts += np.where(clusts < 0, 0, max_cluster)
        result.append(clusts)
        max_cluster = clusts.max() + 1

    return np.concatenate(result)


def _partition(df, chunks, eps):
    chunk_size = int(np.ceil((len(df) + 1) / chunks))
    diffs = df.valid.diff(1)
    diffs = diffs[diffs > pd.Timedelta(eps, 'h')]

    init = 0
    max_index_df = df.index.max()
    while init <= max_index_df:
        next_index = diffs.index[diffs.index.get_loc(init + chunk_size, method='nearest')]
        # print(f'init: {init}, next index: {next_index}')
        if next_index == init:
            next_index = max_index_df + 1
        yield df.loc[init:next_index - 1]
        init = next_index


def find_hourly_precip_clusts(df, eps, min_samples):
    def to_hour(ns):
        return abs(ns / 3.6e12)

    dists = pairwise_distances(
        df.valid.values.reshape(-1, 1),
        metric=lambda x, y: to_hour(y - x),
    )
    db = DBSCAN(eps=eps, metric='precomputed', min_samples=min_samples)
    clusts = db.fit_predict(dists, sample_weight=df.precip_in.values / 0.01)
    return clusts