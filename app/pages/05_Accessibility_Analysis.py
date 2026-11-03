"""
PAGE 5: ACCESSIBILITY ANALYSIS
Spatial grid choropleth, multi-tier accessibility classifications, nearest facility lookup, and deficit hotspot identification.
"""

from pathlib import Path
import sys

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.shared_ui import (
    apply_custom_styles,
    load_cached_datasets,
    load_cached_graph,
    render_download_buttons,
    render_metric_card,
)
from src.healthcare import find_nearest_healthcare_facility, identify_deficit_areas
from src.visualizations import (
    add_accessibility_grid_to_map,
    add_healthcare_markers_to_map,
    add_route_to_map,
    add_study_boundary_to_map,
    create_base_map,
    plot_accessibility_bands,
)

st.set_page_config(page_title="Accessibility Analysis | Smart Yeshwanthpur", layout="wide")
apply_custom_styles()

st.title("Healthcare Accessibility & Spatial Grid Analysis")
st.markdown(
    "Multi-tier accessibility classifications, population-weighted coverage, and service deficit hotspot detection."
)

data = load_cached_datasets()
metrics = data.get("metrics", {})
boundary = data.get("boundary")
healthcare = data.get("healthcare")
grid = data.get("grid")
graph = load_cached_graph()

access_stats = metrics.get("accessibility_statistics", {})

# KPI Metric Cards
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    render_metric_card("Grid Resolution", "250m × 250m", f"{len(grid)} total cells")
with k2:
    render_metric_card("Mean Hospital Dist", f"{access_stats.get('mean_nearest_hosp_dist_meters', 0):.0f} m", "Straight-line average")
with k3:
    render_metric_card("Pop-Weighted Dist", f"{access_stats.get('pop_weighted_hosp_dist_km', 0)} km", "BBMP urban density weighted")
with k4:
    render_metric_card("Mean Access Score", f"{access_stats.get('mean_accessibility_score', 0)} / 100", "Composite index")
with k5:
    render_metric_card("Deficit Cells (>2km)", f"{access_stats.get('poor_accessibility_cell_count', 0)}", f"{access_stats.get('poor_accessibility_pct', 0)}% of cells", neutral=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# SECTION 1: Interactive Nearest Healthcare Facility Finder
st.subheader("Nearest Healthcare Facility Finder")
st.caption("Select or input any location in Yeshwanthpur to compute driving distance, Euclidean distance, and travel time to the closest healthcare center.")

c_in1, c_in2, c_in3, c_in4 = st.columns([3, 3, 3, 2])

SAMPLE_ORIGINS = {
    "Yeshwanthpur Railway Station": (13.0242, 77.5492),
    "Yeshwanthpur Circle / Flyover": (13.0285, 77.5400),
    "Goraguntepalya Junction": (13.0292, 77.5348),
    "Subhash Nagar Residential": (13.0210, 77.5360),
    "APMC Yard Industrial Sector": (13.0298, 77.5385),
    "Mattikere Bus Stand": (13.0345, 77.5580),
}

with c_in1:
    origin_preset = st.selectbox("Choose Origin Location:", ["Custom Coordinates"] + list(SAMPLE_ORIGINS.keys()))
    if origin_preset == "Custom Coordinates":
        u_lat = st.number_input("Origin Latitude:", value=13.0285, format="%.5f")
        u_lon = st.number_input("Origin Longitude:", value=77.5400, format="%.5f")
        chosen_coords = (u_lat, u_lon)
    else:
        chosen_coords = SAMPLE_ORIGINS[origin_preset]

with c_in2:
    target_type = st.selectbox("Find Nearest:", ["Hospital", "Clinic", "All"])

with c_in3:
    st.markdown("<br>", unsafe_allow_html=True)
    find_btn = st.button("Locate Nearest Facility", type="primary", use_container_width=True)

# Run Query
if find_btn or origin_preset != "Custom Coordinates":
    try:
        nearest_res = find_nearest_healthcare_facility(
            chosen_coords, healthcare, graph=graph, facility_type_filter=target_type
        )
    except Exception as e:
        nearest_res = {"found": False, "error": str(e)}

    if nearest_res.get("found"):
        st.success(
            f"**Nearest {nearest_res['facility_type']} Found:** **{nearest_res['facility_name']}** at {nearest_res['address']}"
        )
        nr1, nr2, nr3, nr4 = st.columns(4)
        with nr1:
            render_metric_card("Driving Network Dist", f"{nearest_res['network_distance_km']} km", f"{nearest_res['network_distance_m']} m")
        with nr2:
            render_metric_card("Straight-Line Dist", f"{nearest_res['straight_line_distance_km']} km", f"{nearest_res['straight_line_distance_m']} m")
        with nr3:
            render_metric_card("Est Travel Time", f"{nearest_res['estimated_travel_time_min']} mins", "At urban road speeds")
        with nr4:
            render_metric_card("Accessibility Tier", nearest_res['accessibility_band'].split(' ')[0], nearest_res['accessibility_band'])

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# SECTION 2: Spatial Grid Choropleth Map
st.subheader("Spatial Grid Accessibility Choropleth")

map_opt_col, leg_col = st.columns([7, 3])

with map_opt_col:
    grid_color_mode = st.radio(
        "Choropleth Color Theme:",
        ["Accessibility Bands (<1km, 1-2km, 2-3km, >3km)", "Composite Score (0 to 100)"],
        horizontal=True,
    )
    color_mode_param = "accessibility_band" if "Bands" in grid_color_mode else "score"

    m_grid = create_base_map(zoom_start=14)
    if not boundary.empty:
        add_study_boundary_to_map(m_grid, boundary)
    if not grid.empty:
        add_accessibility_grid_to_map(m_grid, grid, color_by=color_mode_param)
    if not healthcare.empty:
        add_healthcare_markers_to_map(m_grid, healthcare, marker_cluster=False)

    st_folium(m_grid, width="100%", height=500, returned_objects=[])

with leg_col:
    st.markdown("#### Analytical Legend")
    st.markdown(
        """
        - **High Accessibility (< 1 km):** Optimal emergency response zone.
        - **Moderate Accessibility (1–2 km):** Standard urban travel buffer.
        - **Low Accessibility (2–3 km):** Noticeable travel detour.
        - **Very Low Accessibility (> 3 km):** Service deficit zone.
        """
    )
    if not grid.empty:
        fig_pie = plot_accessibility_bands(grid)
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# SECTION 3: Service Deficit Hotspot Identification
st.subheader("Priority Service Deficit Areas (Candidate Expansion Zones)")
st.caption(
    "Spatial cells located farthest from emergency hospital care while possessing viable road density and residential population."
)

deficit_cells = identify_deficit_areas(grid, top_k=6)
if not deficit_cells.empty:
    d_cols = [
        "grid_id",
        "nearest_hosp_dist_m",
        "estimated_network_hosp_dist_km",
        "road_density_km_sqkm",
        "estimated_population",
        "accessibility_score",
        "centroid_lat",
        "centroid_lon",
    ]
    avail_d = [c for c in d_cols if c in deficit_cells.columns]
    st.dataframe(deficit_cells[avail_d].reset_index(drop=True), use_container_width=True)

st.subheader("Export Accessibility Grid")
if not grid.empty:
    render_download_buttons(grid, "yeshwanthpur_spatial_accessibility_grid", "Accessibility Grid")

