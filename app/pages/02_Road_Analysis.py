"""
PAGE 2: ROAD NETWORK ANALYSIS
Road distribution, network topology, connectivity, centrality, and structural bottleneck corridors.
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
    add_road_network_to_map,
    add_study_boundary_to_map,
    create_base_map,
    plot_road_category_distribution,
)

st.set_page_config(page_title="Road Network | Smart Yeshwanthpur", page_icon="🛣️", layout="wide")
apply_custom_styles()

st.title("🛣️ Road Network & Topological Analysis")
st.markdown(
    "Structural analysis of Yeshwanthpur's drivable street network, road classification hierarchy, and network centrality."
)

data = load_cached_datasets()
metrics = data.get("metrics", {})
boundary = data.get("boundary")
roads = data.get("roads")
nodes = data.get("nodes")

road_stats = metrics.get("road_statistics", {})
net_stats = metrics.get("network_statistics", {})
central_stats = metrics.get("centrality_statistics", {})

# KPI Cards
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_metric_card("Total Length", f"{road_stats.get('total_length_km', 0)} km", "Full street network")
with c2:
    render_metric_card("Road Density", f"{road_stats.get('road_density_km_per_sqkm', 0)}", "km / km²")
with c3:
    render_metric_card("Intersections", f"{net_stats.get('num_intersections', 0):,}", f"{net_stats.get('intersection_density_per_sqkm', 0)} / km²")
with c4:
    render_metric_card("Avg Node Degree", f"{net_stats.get('avg_node_degree', 0)}", "Junction connectivity")
with c5:
    render_metric_card("Bottlenecks", f"{central_stats.get('num_bottleneck_segments', 0)}", "Top 5% betweenness links", neutral=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Filters & Map Controls
st.subheader("🔍 Road Network Hierarchy & Interactive Map")

f_col1, f_col2 = st.columns([7, 3])

all_categories = sorted(list(roads["road_category"].dropna().unique())) if not roads.empty else []

with f_col1:
    selected_cats = st.multiselect(
        "Filter Roads by Category:",
        options=all_categories,
        default=all_categories[:4] if len(all_categories) >= 4 else all_categories,
    )

with f_col2:
    highlight_bottlenecks = st.checkbox(
        "🚨 Highlight Structural Bottlenecks (Top 5% Betweenness)",
        value=True,
    )

# Filter roads
if selected_cats and not roads.empty:
    filtered_roads = roads[roads["road_category"].isin(selected_cats)].copy()
else:
    filtered_roads = roads.copy() if not roads.empty else roads

map_col, stats_col = st.columns([7, 3])

with map_col:
    m = create_base_map(zoom_start=14)
    if not boundary.empty:
        add_study_boundary_to_map(m, boundary)
    if not filtered_roads.empty:
        add_road_network_to_map(
            m, filtered_roads, max_segments=1000, highlight_bottlenecks=highlight_bottlenecks
        )

    st_folium(m, width="100%", height=520, returned_objects=[])

with stats_col:
    st.markdown("#### Category Breakdown")
    if not roads.empty:
        cat_counts = roads["road_category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Segments"]
        st.dataframe(cat_counts, use_container_width=True, height=220)

    st.markdown("#### Centrality Distribution")
    st.info(
        "⚠️ **Note:** Structural betweenness centrality measures topological bridging importance. It indicates critical routing corridors, not actual live vehicle density."
    )

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Analytical Charts Row
ch1, ch2 = st.columns(2)

with ch1:
    st.subheader("📊 Road Hierarchy Distribution")
    if not roads.empty:
        fig_bar = plot_road_category_distribution(roads)
        st.plotly_chart(fig_bar, use_container_width=True)

with ch2:
    st.subheader("📈 Segment Length vs Travel Time Distribution")
    if not roads.empty:
        fig_hist = px.histogram(
            roads,
            x="length_meters",
            color="road_category",
            nbins=40,
            title="Distribution of Road Segment Lengths (meters)",
            template="plotly_white",
        )
        fig_hist.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)

# Bottleneck Corridor Inspection Table
if not roads.empty and "is_bottleneck_corridor" in roads.columns:
    st.subheader("🚨 Identified Critical Structural Corridors")
    st.caption("Road segments whose removal or obstruction would cause the largest detour circuity.")
    bottlenecks = roads[roads["is_bottleneck_corridor"]].copy()
    display_cols = [
        "road_name",
        "road_category",
        "length_meters",
        "speed_kph",
        "edge_betweenness",
    ]
    avail_cols = [c for c in display_cols if c in bottlenecks.columns]
    sorted_bn = bottlenecks[avail_cols].sort_values(by="edge_betweenness", ascending=False).head(20)
    st.dataframe(sorted_bn, use_container_width=True)

st.subheader("📥 Export Road Network Dataset")
if not filtered_roads.empty:
    render_download_buttons(filtered_roads, "yeshwanthpur_roads_filtered", "Road Dataset")

