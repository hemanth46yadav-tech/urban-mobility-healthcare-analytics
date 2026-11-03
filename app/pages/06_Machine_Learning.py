"""
PAGE 6: MACHINE LEARNING
Unsupervised K-Means neighbourhood clustering, Elbow evaluation, Silhouette scores, and PCA visualization.
"""

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.shared_ui import (
    apply_custom_styles,
    load_cached_datasets,
    render_download_buttons,
    render_metric_card,
)
from src.visualizations import (
    add_accessibility_grid_to_map,
    add_healthcare_markers_to_map,
    add_study_boundary_to_map,
    create_base_map,
    plot_clustering_evaluation,
    plot_pca_clusters,
)

st.set_page_config(page_title="Machine Learning | Smart Yeshwanthpur", layout="wide")
apply_custom_styles()

st.title("Unsupervised Spatial Neighbourhood Clustering")
st.markdown(
    "Multi-dimensional neighbourhood classification using K-Means, Elbow method, Silhouette scoring, and Principal Component Analysis (PCA)."
)

data = load_cached_datasets()
metrics = data.get("metrics", {})
boundary = data.get("boundary")
healthcare = data.get("healthcare")
grid = data.get("grid")
clusters_csv = data.get("clusters_csv")

ml_data = metrics.get("ml_clustering", {})
eval_data = ml_data.get("evaluation", {})
interpretations = ml_data.get("cluster_interpretations", {})

if not ml_data:
    st.error("Clustering results not available. Please run `python src/run_pipeline.py`.")
    st.stop()

# Model Architecture KPIs
k1, k2, k3, k4 = st.columns(4)
with k1:
    render_metric_card("Optimal Clusters (k)", f"{ml_data.get('n_clusters', 4)}", "Selected by Silhouette optimization")
with k2:
    render_metric_card("Silhouette Score", f"{eval_data.get('best_silhouette', 0):.3f}", "Cluster cohesion & separation")
with k3:
    render_metric_card("PCA Variance Explained", f"{ml_data.get('pca_total_variance', 0)*100:.1f}%", "Top 2 principal components")
with k4:
    render_metric_card("Model Algorithm", "K-Means (k=5)", "StandardScaler preprocessed", neutral=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# SECTION 1: Spatial Cluster Map & Interpretations
st.subheader("Spatial Distribution of Neighbourhood Clusters")

c_map, c_desc = st.columns([7, 3])

with c_map:
    m_cluster = create_base_map(zoom_start=14)
    if not boundary.empty:
        add_study_boundary_to_map(m_cluster, boundary)
    if not grid.empty:
        add_accessibility_grid_to_map(m_cluster, grid, color_by="cluster")
    if not healthcare.empty:
        add_healthcare_markers_to_map(m_cluster, healthcare, marker_cluster=False)

    st_folium(m_cluster, width="100%", height=500, returned_objects=[])

with c_desc:
    st.markdown("#### Contextual Cluster Profiles")
    for cid, profile in interpretations.items():
        st.markdown(
            f"""
            <div style="background: white; border-left: 5px solid {profile.get('color', '#333')}; padding: 10px 14px; margin-bottom: 10px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <strong style="color: #0f172a;">Cluster {cid}: {profile.get('label')}</strong>
                <p style="font-size: 0.8rem; color: #64748b; margin: 4px 0 6px 0;">{profile.get('description')}</p>
                <div style="font-size: 0.75rem; color: #475569;">
                    Road Dens: <strong>{profile.get('mean_road_density')} km/km²</strong> | Hosp Dist: <strong>{profile.get('mean_hosp_distance_m')} m</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# SECTION 2: Model Evaluation & PCA Projection
st.subheader("Clustering Evaluation & Dimensionality Reduction")

e_col1, e_col2 = st.columns(2)

with e_col1:
    if eval_data:
        fig_elbow, fig_sil = plot_clustering_evaluation(eval_data)
        st.plotly_chart(fig_elbow, use_container_width=True)

with e_col2:
    if eval_data:
        st.plotly_chart(fig_sil, use_container_width=True)

# PCA Scatter Plot
st.subheader("2D PCA Cluster Projection")
st.caption(
    "Principal Component Analysis reduces multi-dimensional spatial features (Road Density, Intersection Density, Hospital Distance, Facilities Count, Accessibility Score) into 2 orthogonal axes."
)

if not clusters_csv.empty:
    var_ratios = ml_data.get("pca_explained_variance_ratio", [0.5, 0.3])
    fig_pca = plot_pca_clusters(clusters_csv, var_ratio=var_ratios)
    st.plotly_chart(fig_pca, use_container_width=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Cluster Feature Comparison Table
st.subheader("Cluster Characteristics Comparison Table")
if not clusters_csv.empty:
    feature_cols = [
        "road_density_km_sqkm",
        "intersection_density_per_sqkm",
        "nearest_hosp_dist_m",
        "total_healthcare_count",
        "accessibility_score",
    ]
    avail_f = [f for f in feature_cols if f in clusters_csv.columns]
    cluster_means = clusters_csv.groupby("cluster_label")[avail_f].mean().round(2).reset_index()
    st.dataframe(cluster_means, use_container_width=True)

st.subheader("Export Cluster Assignments")
if not clusters_csv.empty:
    csv_str = clusters_csv.to_csv(index=False)
    st.download_button(
        label="Download Cluster Assignments (CSV)",
        data=csv_str,
        file_name="yeshwanthpur_cluster_assignments.csv",
        mime="text/csv",
        use_container_width=True,
    )

