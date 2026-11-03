"""
Shared UI components, styles, and cached loaders for Streamlit dashboard.
"""

from pathlib import Path
import sys
from typing import Any, Dict, Optional, Tuple

import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
import streamlit as st

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import (
    CLUSTER_METRICS_CSV,
    GRAPH_PROCESSED_GRAPHML,
    HEALTHCARE_PROCESSED_GEOJSON,
    HEALTHCARE_PROCESSED_GPKG,
    METRICS_JSON_FILE,
    NODES_PROCESSED_GPKG,
    ROADS_PROCESSED_GPKG,
    SPATIAL_GRID_GEOJSON,
    SPATIAL_GRID_GPKG,
    STUDY_BOUNDARY_GEOJSON,
)
from src.utils import load_json


def apply_custom_styles():
    """Apply modern CSS styling to Streamlit app."""
    st.markdown(
        """
        <style>
        /* Main Container Styling */
        .main {
            background-color: #f8fafc;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        /* Metric Cards */
        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            margin-bottom: 15px;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .metric-title {
            color: #64748b;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }
        .metric-value {
            color: #0f172a;
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0;
            line-height: 1.2;
        }
        .metric-sub {
            color: #10b981;
            font-size: 0.8rem;
            margin-top: 4px;
            font-weight: 500;
        }
        .metric-sub.neutral {
            color: #64748b;
        }

        /* Headers */
        h1, h2, h3 {
            color: #0f172a;
            font-weight: 700;
        }
        .hero-banner {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: white;
            border-radius: 12px;
            padding: 24px 30px;
            margin-bottom: 25px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .hero-title {
            font-size: 1.8rem;
            font-weight: 800;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }
        .hero-subtitle {
            font-size: 1.0rem;
            color: #94a3b8;
            margin: 0;
            font-weight: 400;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
        }
        [data-testid="stSidebar"] * {
            color: #e2e8f0;
        }

        /* Section divider */
        .section-divider {
            height: 1px;
            background: #e2e8f0;
            margin: 25px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_cached_datasets():
    """Load all processed GIS datasets and cached summary metrics."""
    metrics = load_json(METRICS_JSON_FILE)

    boundary = (
        gpd.read_file(STUDY_BOUNDARY_GEOJSON)
        if STUDY_BOUNDARY_GEOJSON.exists()
        else gpd.GeoDataFrame()
    )
    healthcare = (
        gpd.read_file(HEALTHCARE_PROCESSED_GEOJSON)
        if HEALTHCARE_PROCESSED_GEOJSON.exists()
        else gpd.GeoDataFrame()
    )
    grid = (
        gpd.read_file(SPATIAL_GRID_GEOJSON)
        if SPATIAL_GRID_GEOJSON.exists()
        else gpd.GeoDataFrame()
    )
    roads = (
        gpd.read_file(ROADS_PROCESSED_GPKG)
        if ROADS_PROCESSED_GPKG.exists()
        else gpd.GeoDataFrame()
    )
    nodes = (
        gpd.read_file(NODES_PROCESSED_GPKG)
        if NODES_PROCESSED_GPKG.exists()
        else gpd.GeoDataFrame()
    )

    clusters_csv = (
        pd.read_csv(CLUSTER_METRICS_CSV)
        if CLUSTER_METRICS_CSV.exists()
        else pd.DataFrame()
    )

    return {
        "metrics": metrics,
        "boundary": boundary,
        "healthcare": healthcare,
        "grid": grid,
        "roads": roads,
        "nodes": nodes,
        "clusters_csv": clusters_csv,
    }


@st.cache_resource(show_spinner=False)
def load_cached_graph() -> Optional[nx.MultiDiGraph]:
    """Load processed OSM road network graph from GraphML."""
    if GRAPH_PROCESSED_GRAPHML.exists():
        try:
            return ox.load_graphml(GRAPH_PROCESSED_GRAPHML)
        except Exception:
            return None
    return None


def render_metric_card(
    title: str, value: Any, subtext: str = "", neutral: bool = False
):
    """Render a clean custom HTML metric card."""
    sub_class = "metric-sub neutral" if neutral else "metric-sub"
    html = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {f'<div class="{sub_class}">{subtext}</div>' if subtext else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_download_buttons(
    gdf: gpd.GeoDataFrame, base_filename: str, label_prefix: str = "Download Data"
):
    """Provide standard GeoJSON and CSV download buttons."""
    col1, col2 = st.columns(2)
    with col1:
        geojson_str = gdf.to_json()
        st.download_button(
            label=f"{label_prefix} (GeoJSON)",
            data=geojson_str,
            file_name=f"{base_filename}.geojson",
            mime="application/geo+json",
            use_container_width=True,
        )
    with col2:
        df_export = pd.DataFrame(gdf.drop(columns=["geometry"], errors="ignore"))
        csv_str = df_export.to_csv(index=False)
        st.download_button(
            label=f"{label_prefix} (CSV)",
            data=csv_str,
            file_name=f"{base_filename}.csv",
            mime="text/csv",
            use_container_width=True,
        )

