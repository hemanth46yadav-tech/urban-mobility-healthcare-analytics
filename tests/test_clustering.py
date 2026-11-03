"""
Tests for Machine Learning neighbourhood clustering pipeline.
"""

import geopandas as gpd
import joblib
import numpy as np
import pytest

from src.clustering import evaluate_clustering_k, run_neighborhood_clustering
from src.config import (
    CLUSTER_METRICS_CSV,
    KMEANS_MODEL_FILE,
    SCALER_FILE,
    SPATIAL_GRID_GEOJSON,
)


def test_kmeans_artifacts_exist():
    assert KMEANS_MODEL_FILE.exists()
    assert SCALER_FILE.exists()
    assert CLUSTER_METRICS_CSV.exists()

    model = joblib.load(KMEANS_MODEL_FILE)
    scaler = joblib.load(SCALER_FILE)

    assert hasattr(model, "cluster_centers_")
    assert hasattr(scaler, "mean_")


def test_clustering_evaluation_logic():
    # Synthesize small mock 2D feature matrix
    np.random.seed(42)
    X = np.vstack([np.random.randn(20, 3) + 5, np.random.randn(20, 3) - 5])

    eval_res = evaluate_clustering_k(X, k_range=range(2, 5))
    assert len(eval_res["inertias"]) == 3
    assert len(eval_res["silhouette_scores"]) == 3
    assert all(score <= 1.0 for score in eval_res["silhouette_scores"])
    assert eval_res["recommended_k"] in [2, 3, 4]


def test_clustering_on_grid():
    assert SPATIAL_GRID_GEOJSON.exists()
    grid_gdf = gpd.read_file(SPATIAL_GRID_GEOJSON)
    assert not grid_gdf.empty

    df_clustered, summary = run_neighborhood_clustering(grid_gdf, n_clusters=4)

    assert "cluster" in df_clustered.columns
    assert "pca_1" in df_clustered.columns
    assert "pca_2" in df_clustered.columns
    assert df_clustered["cluster"].nunique() == 4
    assert len(summary["cluster_interpretations"]) == 4

