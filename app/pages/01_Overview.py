"""
PAGE 1: OVERVIEW
Executive Summary, Study Area Geography, and Multi-Domain GIS KPIs.
"""

from pathlib import Path
import sys

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
    add_road_network_to_map,
    add_study_boundary_to_map,
    create_base_map,
    plot_accessibility_bands,
    plot_road_category_distribution,
)

st.set_page_config(page_title="Overview | Smart Yeshwanthpur", page_icon="🗺️", layout="wide")
apply_custom_styles()

st.title("🗺️ Overview & Study Area Profile")
st.markdown(
    "High-level geographical synthesis of Yeshwanthpur's transportation network and healthcare infrastructure."
)

data = load_cached_datasets()
metrics = data.get("metrics", {})
boundary = data.get("boundary")
roads = data.get("roads")
healthcare = data.get("healthcare")
grid = data.get("grid")

road_stats = metrics.get("road_statistics", {})
hc_stats = metrics.get("healthcare_statistics", {})
net_stats = metrics.get("network_statistics", {})
access_stats = metrics.get("accessibility_statistics", {})

# KPI Metric Row
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    render_metric_card("Total Road Length", f"{road_stats.get('total_length_km', 0)} km", "Full drivable network")
with k2:
    render_metric_card("Road Segments", f"{road_stats.get('total_segments', 0):,}", "Network edges")
with k3:
    render_metric_card("Total Facilities", f"{hc_stats.get('total_facilities', 0)}", "Verified healthcare amenities")
with k4:
    render_metric_card("Hospitals", f"{hc_stats.get('num_hospitals', 0)}", "Secondary & tertiary care")
with k5:
    render_metric_card("Clinics & Doctors", f"{hc_stats.get('num_clinics', 0)}", "Primary outpatient care")

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Overview Map & Visualizations
m_col, c_col = st.columns([6, 4])

with m_col:
    st.subheader("Geospatial Study Layer")
    map_layer = st.radio(
        "Select Map Layer:",
        ["Roads & Healthcare", "Accessibility Grid & Healthcare"],
        horizontal=True,
    )

    m = create_base_map(zoom_start=13)
    if not boundary.empty:
        add_study_boundary_to_map(m, boundary)

    if map_layer == "Roads & Healthcare":
        if not roads.empty:
            add_road_network_to_map(m, roads, max_segments=800)
    else:
        if not grid.empty:
            add_accessibility_grid_to_map(m, grid, color_by="accessibility_band")

    if not healthcare.empty:
        add_healthcare_markers_to_map(m, healthcare, marker_cluster=False)

    st_folium(m, width="100%", height=480, returned_objects=[])

with c_col:
    st.subheader("Infrastructure Breakdowns")
    if not roads.empty:
        fig_roads = plot_road_category_distribution(roads)
        st.plotly_chart(fig_roads, use_container_width=True)

    if not grid.empty:
        fig_acc = plot_accessibility_bands(grid)
        st.plotly_chart(fig_acc, use_container_width=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Project Scope & Methodology Summary
st.subheader("📌 Project Context & Technical Governance")
c_left, c_right = st.columns(2)

with c_left:
    st.markdown(
        """
        ### Spatial Context
        - **Administrative Jurisdiction:** Yeshwanthpur, BBMP North Zone, Bengaluru, India.
        - **Study Anchor:** Centered at (13.0285° N, 77.5400° E) spanning a 2.5 km circular analytical buffer (~19.63 km²).
        - **Urban Characteristics:** Vital transit corridor containing Yeshwanthpur Junction Railway Station, Tumkur Road (NH 48), Metro Green Line, and major industrial-residential zones (APMC Yard, Subhash Nagar, Mattikere).
        """
    )

with c_right:
    st.markdown(
        """
        ### Methodology Notes
        - **Projection Accuracy:** Distance and spatial overlays calculated in projected metric CRS **EPSG:32643 (UTM Zone 43N)**.
        - **Road Hierarchy:** Classified into Highway, Arterial, Collector, and Residential categories with free-flow travel speed models.
        - **Governance Policy:** Network centrality indicates structural connectivity and bridge bottlenecks, not empirical live congestion volume.
        """
    )

st.subheader("📥 Export Summary Datasets")
if not grid.empty:
    render_download_buttons(grid, "yeshwanthpur_accessibility_grid", "Spatial Grid")

