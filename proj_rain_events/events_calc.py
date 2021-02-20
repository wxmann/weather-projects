from sklearn.metrics import pairwise_distances
from sklearn.cluster import DBSCAN


def precip_events(df, eps, min_samples):
    rain_hrs = df[df.precip_in >= 0.01]
    
    def to_hour(ns):
        return abs(ns / 3.6e12)

    dists = pairwise_distances(
        rain_hrs.valid.values.reshape(-1, 1), 
        metric=lambda x, y: to_hour(y - x),
    )
    db = DBSCAN(eps=eps, metric='precomputed', min_samples=min_samples)
    clusts = db.fit_predict(dists, sample_weight=rain_hrs.precip_in.values / 0.01)
    return clusts