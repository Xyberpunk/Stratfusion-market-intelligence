from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class ClusteringRegimeInterface:
    """KMeans and HDBSCAN clustering interface for unsupervised regime discovery."""

    def kmeans(self, features: pd.DataFrame, n_clusters: int = 4) -> list[int]:
        numeric = features.select_dtypes(include="number").fillna(0.0)
        if len(numeric.index) < n_clusters:
            raise ValueError("Not enough rows for KMeans regime clustering")
        scaled = StandardScaler().fit_transform(numeric)
        return KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit_predict(scaled).tolist()

    def hdbscan(self, features: pd.DataFrame, min_cluster_size: int = 20) -> list[int]:
        try:
            import hdbscan
        except Exception as exc:
            raise RuntimeError("hdbscan is not installed") from exc
        numeric = features.select_dtypes(include="number").fillna(0.0)
        if len(numeric.index) < min_cluster_size:
            raise ValueError("Not enough rows for HDBSCAN regime clustering")
        scaled = StandardScaler().fit_transform(numeric)
        return hdbscan.HDBSCAN(min_cluster_size=min_cluster_size).fit_predict(scaled).tolist()
