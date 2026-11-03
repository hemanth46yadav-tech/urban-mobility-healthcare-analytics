"""
Machine learning clustering module for Smart Yeshwanthpur GIS Analytics.
Implements unsupervised spatial neighbourhood classification via K-Means,
Elbow evaluation, Silhouette score benchmarking, PCA dimensionality reduction,
and cluster profiling.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import geopandas as gpd
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from src.config import (
    CLUSTER_METRICS_CSV,
    KMEANS_MODEL_FILE,
    MODELS_DIR,
    SCALER_FILE,
)
from src.utils import logger, save_json, timer

# Analytical spatial features for neighbourhood classification
FEATURE_COLUMNS = [
    "road_density_km_sqkm",
    "intersection_density_per_sqkm",
    "nearest_hosp_dist_m",
    "total_healthcare_count",
    "accessibility_score",
]


@timer
def evaluate_clustering_k(
    X_scaled: np.ndarray, k_range: range = range(2, 8)
) -> Dict[str, Any]:
    """
    Evaluate K-Means clustering across a range of k values
    using the Elbow Method (inertia) and Silhouette Analysis.
    """
    logger.info(
        f"Evaluating clustering performance for k in [{k_range.start}, {k_range.stop - 1}]..."
    )

    inertias = []
    silhouette_scores = []
    k_values = list(k_range)

    for k in k_values:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(round(float(km.inertia_), 2))
        sil = silhouette_score(X_scaled, labels)
        silhouette_scores.append(round(float(sil), 3))

    # Identify k with highest silhouette score
    best_k_idx = int(np.argmax(silhouette_scores))
    best_k = k_values[best_k_idx]

    logger.info(
        f"Evaluation finished. Best k by Silhouette Score: {best_k} (score: {silhouette_scores[best_k_idx]})."
    )

    return {
        "k_values": k_values,
        "inertias": inertias,
        "silhouette_scores": silhouette_scores,
        "recommended_k": best_k,
        "best_silhouette": silhouette_scores[best_k_idx],
    }


def _generate_cluster_interpretations(
    cluster_profiles: pd.DataFrame,
) -> Dict[int, Dict[str, Any]]:
    """
    Generate contextual domain interpretations for each cluster
    based on relative feature averages across Yeshwanthpur study grid.
    """
    interpretations = {}

    for cluster_id, row in cluster_profiles.iterrows():
        road_dens = row["road_density_km_sqkm"]
        hosp_dist = row["nearest_hosp_dist_m"]
        fac_count = row["total_healthcare_count"]
        access_score = row["accessibility_score"]

        # Classification heuristics
        if hosp_dist < 1200 and fac_count >= 1.0:
            label = "Healthcare & Urban Core"
            desc = "High road density, multiple local facilities, and immediate hospital proximity."
            color = "#27ae60"
        elif hosp_dist < 1800 and road_dens >= 12.0:
            label = "Dense Mixed-Use / Transit Corridor"
            desc = "High road & intersection density with good connectivity and moderate hospital travel time."
            color = "#2980b9"
        elif hosp_dist >= 2000 and road_dens < 8.0:
            label = "Peripheral / Healthcare Deficit Zone"
            desc = "Lower street network density and longer travel distance to emergency healthcare."
            color = "#c0392b"
        else:
            label = "Suburban Residential / Transition Sector"
            desc = "Moderate road density with fair healthcare accessibility and localized clinic access."
            color = "#f39c12"

        interpretations[int(cluster_id)] = {
            "label": label,
            "description": desc,
            "color": color,
            "mean_road_density": round(float(road_dens), 2),
            "mean_hosp_distance_m": round(float(hosp_dist), 1),
            "mean_facilities": round(float(fac_count), 2),
            "mean_accessibility_score": round(float(access_score), 1),
        }

    return interpretations


@timer
def run_neighborhood_clustering(
    grid_gdf: gpd.GeoDataFrame,
    n_clusters: Optional[int] = None,
    feature_cols: List[str] = FEATURE_COLUMNS,
) -> Tuple[gpd.GeoDataFrame, Dict[str, Any]]:
    """
    Execute full unsupervised clustering pipeline:
    1. Feature extraction and outlier/missing check
    2. Feature standardization (StandardScaler)
    3. Multi-k evaluation (Elbow & Silhouette)
    4. K-Means model training
    5. PCA projection (2D components)
    6. Cluster profiling and domain interpretation
    7. Model persistence
    """
    logger.info("Executing K-Means neighbourhood clustering pipeline...")

    df = grid_gdf.copy()

    # Verify features
    missing_features = [f for f in feature_cols if f not in df.columns]
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}")

    # Extract feature matrix and clean missing/inf
    X_raw = df[feature_cols].copy()
    X_clean = X_raw.replace([np.inf, -np.inf], np.nan).fillna(X_raw.median())

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clean)

    # Multi-k evaluation
    evaluation = evaluate_clustering_k(X_scaled)
    chosen_k = n_clusters if n_clusters is not None else evaluation["recommended_k"]

    # Fit final K-Means model
    kmeans = KMeans(n_clusters=chosen_k, random_state=42, n_init=15)
    cluster_labels = kmeans.fit_predict(X_scaled)
    df["cluster"] = cluster_labels

    # Compute PCA for 2D visualization
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    df["pca_1"] = X_pca[:, 0].round(3)
    df["pca_2"] = X_pca[:, 1].round(3)

    pca_explained_variance = [round(float(v), 3) for v in pca.explained_variance_ratio_]
    pca_total_variance = round(float(sum(pca_explained_variance)), 3)

    # Compute cluster profiles
    cluster_profiles = df.groupby("cluster")[feature_cols].mean()
    cluster_counts = df["cluster"].value_counts().to_dict()

    # Generate domain interpretations
    interpretations = _generate_cluster_interpretations(cluster_profiles)
    df["cluster_label"] = df["cluster"].map(
        lambda c: interpretations.get(c, {}).get("label", f"Cluster {c}")
    )
    df["cluster_color"] = df["cluster"].map(
        lambda c: interpretations.get(c, {}).get("color", "#7f8c8d")
    )

    # Save models and assignments
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(kmeans, KMEANS_MODEL_FILE)
    joblib.dump(scaler, SCALER_FILE)

    # Export cluster assignments table
    export_cols = [
        "grid_id",
        "cluster",
        "cluster_label",
        "centroid_lat",
        "centroid_lon",
        "pca_1",
        "pca_2",
    ] + feature_cols
    export_df = df[export_cols]
    export_df.to_csv(CLUSTER_METRICS_CSV, index=False)

    results_summary = {
        "n_clusters": chosen_k,
        "features": feature_cols,
        "evaluation": evaluation,
        "cluster_counts": {str(k): int(v) for k, v in cluster_counts.items()},
        "pca_explained_variance_ratio": pca_explained_variance,
        "pca_total_variance": pca_total_variance,
        "cluster_interpretations": interpretations,
    }

    save_json(results_summary, MODELS_DIR / "clustering_results.json")

    logger.info(
        f"Clustering successfully completed: {chosen_k} clusters identified, PCA variance {pca_total_variance*100:.1f}%."
    )
    return df, results_summary
