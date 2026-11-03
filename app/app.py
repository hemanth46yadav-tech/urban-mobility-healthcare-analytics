"""
SMART YESHWANTHPUR GIS ANALYTICS
Main Streamlit Application Entrypoint.
"""

from pathlib import Path
import sys

import streamlit as st
from streamlit_folium import st_folium

# Add root directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.shared_ui import (
    apply_custom_styles,
    load_cached_datasets,
    render_download_buttons,
    render_metric_card,
)
from src.visualizations import (
    add_healthcare_markers_to_map,
    add_road_network_to_map,
    add_study_boundary_to_map,
    create_base_map,
)

st.set_page_config(
    page_title="Smart Yeshwanthpur GIS Analytics",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_styles()

# Sidebar Information
with st.sidebar:
    st.image(
        "https://raw.githubusercontent.com/feathericons/feather/master/icons/map-pin.svg",
        width=45,
    )
    st.title("Smart Yeshwanthpur")
    st.markdown(
        """
        **GIS Traffic & Healthcare Accessibility Analytics**
        
        *Bengaluru, Karnataka, India*
        
        ---
        **Modules:**
        - Road Network & Topology
        - Dijkstra Shortest Routes
        - Healthcare Facilities
        - Spatial Accessibility Grid
        - K-Means ML Classification
        - Data-Driven Insights
        ---
        """
    )
    st.caption("Engineered with OSMnx, GeoPandas & Scikit-Learn")

# Hero Banner
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">SMART YESHWANTHPUR — GIS ANALYTICS SYSTEM</div>
        <div class="hero-subtitle">
            Integrated Spatial Analytics Platform for Road Network Topology, Structural Traffic Bottlenecks, 
            and Multi-Tier Healthcare Accessibility in Yeshwanthpur, Bengaluru.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load data
data = load_cached_datasets()
metrics = data.get("metrics", {})
boundary = data.get("boundary")
healthcare = data.get("healthcare")
roads = data.get("roads")
grid = data.get("grid")

if not metrics:
    st.error(
        "Analytical datasets not detected. Please run `python src/run_pipeline.py` to initialize data."
    )
    st.stop()

road_stats = metrics.get("road_statistics", {})
hc_stats = metrics.get("healthcare_statistics", {})
net_stats = metrics.get("network_statistics", {})
access_stats = metrics.get("accessibility_statistics", {})

# KPI Metric Cards Row
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_metric_card(
        "Road Network",
        f"{road_stats.get('total_length_km', 0)} km",
        f"{road_stats.get('total_segments', 0):,} segments",
    )
with c2:
    render_metric_card(
        "Road Density",
        f"{road_stats.get('road_density_km_per_sqkm', 0)}",
        "km per km²",
    )
with c3:
    render_metric_card(
        "Intersections",
        f"{net_stats.get('num_intersections', 0):,}",
        f"{net_stats.get('intersection_density_per_sqkm', 0)} / km²",
    )
with c4:
    render_metric_card(
        "Healthcare Facilities",
        f"{hc_stats.get('total_facilities', 0)}",
        f"{hc_stats.get('num_hospitals', 0)} Hospitals | {hc_stats.get('num_clinics', 0)} Clinics",
    )
with c5:
    render_metric_card(
        "Mean Hospital Dist",
        f"{access_stats.get('mean_nearest_hosp_dist_meters', 0):.0f} m",
        f"Pop-weighted: {access_stats.get('pop_weighted_hosp_dist_km', 0)} km",
        neutral=True,
    )

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Main Two-Column Layout
col_map, col_info = st.columns([7, 3])

with col_map:
    st.subheader("Interactive Study Area Overview")
    st.caption(
        "Showing study area buffer (2.5 km radius around Yeshwanthpur: 13.0285° N, 77.5400° E), road hierarchy, and healthcare locations."
    )

    m = create_base_map(zoom_start=13)
    if not boundary.empty:
        add_study_boundary_to_map(m, boundary)
    if not roads.empty:
        add_road_network_to_map(m, roads, max_segments=800)
    if not healthcare.empty:
        add_healthcare_markers_to_map(m, healthcare, marker_cluster=False)

    st_folium(m, width="100%", height=500, returned_objects=[])

with col_info:
    st.subheader("Analytical Scope")
    st.markdown(
        """
        - **Study Center:** Yeshwanthpur Junction (13.0285° N, 77.5400° E)
        - **Metric Buffer:** 2.5 km Radius (~19.63 km²)
        - **Projected CRS:** EPSG:32643 (UTM Zone 43N)
        - **Geographic CRS:** EPSG:4326 (WGS84)
        - **Road Dataset:** OpenStreetMap drivable network
        - **Spatial Grid:** 250m × 250m metric cells (344 cells)
        """
    )

    st.info(
        "**Navigation Tip:** Use the sidebar menu to explore dedicated analytical modules including Shortest Routes, Topology Centrality, and Machine Learning Clustering."
    )

    st.subheader("Export Datasets")
    if not healthcare.empty:
        render_download_buttons(
            healthcare, "yeshwanthpur_healthcare_facilities", "Healthcare Layer"
        )
