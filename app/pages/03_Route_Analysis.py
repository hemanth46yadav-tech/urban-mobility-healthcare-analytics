"""
PAGE 3: ROUTE ANALYSIS
Dijkstra shortest path routing, network distance, circuity factor, and travel times.
"""

from pathlib import Path
import sys

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.shared import (
    apply_custom_styles,
    load_cached_datasets,
    load_cached_graph,
    render_metric_card,
)
from src.route_analysis import find_shortest_route
from src.visualizations import (
    add_healthcare_markers_to_map,
    add_route_to_map,
    create_base_map,
)

st.set_page_config(page_title="Route Analysis | Smart Yeshwanthpur", page_icon="🧭", layout="wide")
apply_custom_styles()

st.title("🧭 Shortest Route Analysis & Routing Engine")
st.markdown(
    "Calculate Dijkstra optimal road network routes, travel times, and compare driving distance against Euclidean straight-line distance."
)

data = load_cached_datasets()
healthcare = data.get("healthcare")
graph = load_cached_graph()

if graph is None:
    st.error("⚠️ Road network graph not available. Please run `python src/run_pipeline.py` first.")
    st.stop()

# Landmarks Presets
LANDMARKS = {
    "Yeshwanthpur Railway Station": (13.0242, 77.5492),
    "Yeshwanthpur Metro Station": (13.0235, 77.5501),
    "APMC Yard & Market": (13.0298, 77.5385),
    "Goraguntepalya / Outer Ring Road": (13.0292, 77.5348),
    "Mattikere Neighborhood Center": (13.0345, 77.5580),
    "Subhash Nagar Residential Core": (13.0210, 77.5360),
    "Peenya Transition Zone": (13.0335, 77.5255),
}

# If healthcare facilities exist, add hospital landmarks
if not healthcare.empty:
    hosp_df = healthcare[healthcare["facility_type"] == "Hospital"].head(5)
    for _, h in hosp_df.iterrows():
        LANDMARKS[f"🏥 {h['facility_name']}"] = (float(h["latitude"]), float(h["longitude"]))

col_cfg1, col_cfg2, col_cfg3 = st.columns([4, 4, 2])

landmark_names = list(LANDMARKS.keys())

with col_cfg1:
    orig_choice = st.selectbox(
        "Select Starting Location (Origin):",
        options=["Custom Coordinates"] + landmark_names,
        index=1,
    )
    if orig_choice == "Custom Coordinates":
        c_lat = st.number_input("Origin Latitude:", value=13.0285, format="%.5f")
        c_lon = st.number_input("Origin Longitude:", value=77.5400, format="%.5f")
        orig_coords = (c_lat, c_lon)
    else:
        orig_coords = LANDMARKS[orig_choice]
        st.caption(f"Coordinates: {orig_coords[0]:.4f}° N, {orig_coords[1]:.4f}° E")

with col_cfg2:
    dest_choice = st.selectbox(
        "Select Destination Location:",
        options=["Custom Coordinates"] + landmark_names,
        index=min(2, len(landmark_names)),
    )
    if dest_choice == "Custom Coordinates":
        d_lat = st.number_input("Destination Latitude:", value=13.0210, format="%.5f")
        d_lon = st.number_input("Destination Longitude:", value=77.5450, format="%.5f")
        dest_coords = (d_lat, d_lon)
    else:
        dest_coords = LANDMARKS[dest_choice]
        st.caption(f"Coordinates: {dest_coords[0]:.4f}° N, {dest_coords[1]:.4f}° E")

with col_cfg3:
    weight_type = st.radio("Optimization Metric:", ["Shortest Distance", "Quickest Time"])
    weight_param = "length" if weight_type == "Shortest Distance" else "travel_time"
    calc_button = st.button("🚀 Calculate Route", use_container_width=True, type="primary")

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Run Routing
try:
    with st.spinner("Snapping coordinates to road network and computing shortest path..."):
        route_res = find_shortest_route(graph, orig_coords, dest_coords, weight=weight_param)
except Exception as e:
    st.error(f"Routing calculation error: {e}")
    st.stop()

if not route_res.get("success"):
    st.warning(f"⚠️ {route_res.get('error', 'Could not find a route between the selected points.')}")
    st.stop()

# Route KPIs
r1, r2, r3, r4, r5 = st.columns(5)
with r1:
    render_metric_card("Network Distance", f"{route_res.get('distance_km')} km", f"{route_res.get('distance_meters')} meters")
with r2:
    render_metric_card("Est Travel Time", f"{route_res.get('travel_time_min')} min", f"{route_res.get('travel_time_sec')} seconds")
with r3:
    render_metric_card("Straight Line Dist", f"{route_res.get('straight_line_dist_meters')} m", "Euclidean Haversine", neutral=True)
with r4:
    render_metric_card("Circuity Factor", f"{route_res.get('circuity_factor')}x", "Network / Straight Line")
with r5:
    render_metric_card("Road Segments", f"{route_res.get('num_segments')}", "Turn-by-turn edges")

# Interactive Route Map
map_c, seg_c = st.columns([7, 3])

with map_c:
    st.subheader("🗺️ Shortest Path Visualization")
    m = create_base_map(center_lat=(orig_coords[0] + dest_coords[0]) / 2, center_lon=(orig_coords[1] + dest_coords[1]) / 2, zoom_start=14)
    add_route_to_map(
        m,
        route_res,
        orig_coords,
        dest_coords,
        orig_label=orig_choice if orig_choice != "Custom Coordinates" else "Origin",
        dest_label=dest_choice if dest_choice != "Custom Coordinates" else "Destination",
    )
    if not healthcare.empty:
        add_healthcare_markers_to_map(m, healthcare, marker_cluster=False)

    st_folium(m, width="100%", height=500, returned_objects=[])

with seg_c:
    st.subheader("📋 Route Properties")
    st.markdown(
        f"""
        - **From Node:** `{route_res.get('orig_node')}`
        - **To Node:** `{route_res.get('dest_node')}`
        - **Circuity Detour:** **{(route_res.get('circuity_factor', 1.0) - 1.0) * 100:.1f}%** longer than straight-line distance.
        - **Speed Model:** Free-flow speeds based on Bangalore urban road classification standards (15–35 km/h).
        """
    )
    st.info("💡 **Blue Solid Line:** Optimal driving route.\n**Orange Dashed Line:** Straight-line Euclidean connection.")

# Turn-by-Turn Segment Breakdown Table
if route_res.get("segments_table"):
    st.subheader("🛣️ Step-by-Step Road Segments Breakdown")
    seg_df = pd.DataFrame(route_res["segments_table"])
    display_cols = ["road_name", "road_category", "length_meters", "estimated_speed_kph", "travel_time_sec"]
    avail = [c for c in display_cols if c in seg_df.columns]
    st.dataframe(seg_df[avail], use_container_width=True)
