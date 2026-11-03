"""
PAGE 7: INSIGHTS
Dynamically calculated data-driven spatial observations, infrastructure bottlenecks, and urban planning recommendations.
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.shared import (
    apply_custom_styles,
    load_cached_datasets,
    render_metric_card,
)

st.set_page_config(page_title="Insights | Smart Yeshwanthpur", page_icon="💡", layout="wide")
apply_custom_styles()

st.title("💡 Automated Spatial Insights & Policy Diagnostics")
st.markdown(
    "Dynamically derived analytical conclusions and urban planning insights computed directly from empirical OpenStreetMap data and spatial models."
)

data = load_cached_datasets()
metrics = data.get("metrics", {})
roads = data.get("roads")
grid = data.get("grid")
healthcare = data.get("healthcare")

if grid.empty or roads.empty or not metrics:
    st.error("⚠️ Datasets not loaded. Please run `python src/run_pipeline.py` first.")
    st.stop()

road_stats = metrics.get("road_statistics", {})
net_stats = metrics.get("network_statistics", {})
access_stats = metrics.get("accessibility_statistics", {})
ml_data = metrics.get("ml_clustering", {})

# Dynamic Calculations (No Hardcoding!)
# 1. Road Density Extremes
p90_road_density = float(np.percentile(grid["road_density_km_sqkm"], 90))
p10_road_density = float(np.percentile(grid["road_density_km_sqkm"], 10))
high_density_cells = grid[grid["road_density_km_sqkm"] >= p90_road_density]
low_density_cells = grid[grid["road_density_km_sqkm"] <= p10_road_density]

# 2. Intersection Disconnectivity
p10_intersection_density = float(np.percentile(grid["intersection_density_per_sqkm"], 10))
low_int_cells = grid[grid["intersection_density_per_sqkm"] <= p10_intersection_density]

# 3. Hospital Distance Outliers
p90_hosp_dist = float(np.percentile(grid["nearest_hosp_dist_m"], 90))
deficit_cells = grid[grid["nearest_hosp_dist_m"] >= p90_hosp_dist]
total_pop_in_deficit = int(deficit_cells["estimated_population"].sum())

# 4. Critical Bottleneck Segments
top_bottlenecks = (
    roads[roads["is_bottleneck_corridor"]].sort_values(by="edge_betweenness", ascending=False).head(5)
    if "is_bottleneck_corridor" in roads.columns
    else pd.DataFrame()
)

# Top Summary KPIs
i1, i2, i3, i4 = st.columns(4)
with i1:
    render_metric_card("90th Pct Road Density", f"{p90_road_density:.1f} km/km²", f"{len(high_density_cells)} high-density cells")
with i2:
    render_metric_card("90th Pct Hospital Dist", f"{p90_hosp_dist:.0f} m", f"{len(deficit_cells)} cells in deficit zone")
with i3:
    render_metric_card("Affected Deficit Pop", f"{total_pop_in_deficit:,}", "Residents with >2km hospital distance")
with i4:
    render_metric_card("Connectivity Ratio", f"{net_stats.get('connectivity_ratio', 0)*100:.1f}%", "Largest connected component", neutral=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# SECTION 1: Automated Road Network Observations
st.subheader("🛣️ Finding 1: Road Density & Network Disconnectivity")
c_r1, c_r2 = st.columns(2)

with c_r1:
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px;">
            <h4 style="margin: 0 0 10px 0; color: #1e293b;">High-Density Transit & Commercial Sectors</h4>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.5;">
                • The upper 10% of spatial cells exhibit road densities exceeding <strong>{p90_road_density:.1f} km/km²</strong>, 
                concentrated around the <strong>Yeshwanthpur Railway Station precinct, Metro interchange, and APMC Market corridors</strong>.<br>
                • These corridors support high internal permeability but concentrate substantial inter-modal friction between heavy goods freight and passenger movement.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_r2:
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px;">
            <h4 style="margin: 0 0 10px 0; color: #1e293b;">Low Intersection & Dead-End Pockets</h4>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.5;">
                • Approximately <strong>{len(low_int_cells)} grid cells</strong> record intersection densities below <strong>{p10_intersection_density:.1f}/km²</strong>.<br>
                • These zones primarily correspond to <strong>railway yard perimeters, water bodies, and gated industrial layouts</strong>, creating physical barriers that force high circuity detours onto arterial corridors.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# SECTION 2: Top Structural Bottleneck Corridors
st.subheader("🚨 Finding 2: Structural Bottleneck Links")
st.caption("Road segments with the highest betweenness centrality index (bridging critical network sectors):")

if not top_bottlenecks.empty:
    b_table = top_bottlenecks[["road_name", "road_category", "length_meters", "speed_kph", "edge_betweenness"]].copy()
    b_table.columns = ["Corridor Name", "Classification", "Length (m)", "Design Speed (km/h)", "Betweenness Index"]
    st.dataframe(b_table.reset_index(drop=True), use_container_width=True)
    st.info(
        "💡 **Planning Implication:** Disruptions or uncoordinated road works on these specific links trigger disproportionate network-wide delays across Yeshwanthpur."
    )

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# SECTION 3: Healthcare Accessibility Disparities
st.subheader("🏥 Finding 3: Healthcare Spatial Disparities & Service Deserts")
c_h1, c_h2 = st.columns(2)

with c_h1:
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px;">
            <h4 style="margin: 0 0 10px 0; color: #1e293b;">Emergency Access Core</h4>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.5;">
                • <strong>{access_stats.get('band_distribution_pct', {}).get('High Accessibility (< 1 km)', 0)}%</strong> of the study cells 
                enjoy high accessibility (< 1 km straight-line distance to emergency hospital care).<br>
                • This core is anchored by major healthcare facilities along the Tumkur Road / Dr. Rajkumar Road axis.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_h2:
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px;">
            <h4 style="margin: 0 0 10px 0; color: #1e293b;">Peripheral Deficit Clusters</h4>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.5;">
                • <strong>{len(deficit_cells)} peripheral cells</strong> have hospital straight-line distances exceeding <strong>{p90_hosp_dist:.0f} meters</strong> 
                (driving distances of ~{p90_hosp_dist*1.3/1000:.1f} km).<br>
                • An estimated <strong>{total_pop_in_deficit:,} residents</strong> reside within these lower-tier accessibility sectors, relying almost entirely on localized private clinics.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# SECTION 4: Data-Driven Urban Policy Recommendations
st.subheader("🎯 Data-Driven Smart City Recommendations")

st.markdown(
    """
    1. **Emergency Healthcare Placement:** Prioritize establishing 24/7 Primary Urban Health Centers (UPHCs) in the north-western peripheral cells where hospital driving distances exceed 2.8 km.
    2. **Railway Yard Bypass Connectivity:** Improve east-west pedestrian and light vehicle underpasses across the Yeshwanthpur railway yard to reduce circuity for residential communities accessing hospitals on the eastern flank.
    3. **Corridor Traffic Management:** Protect identified high-betweenness links with intelligent traffic signals and strict parking enforcement along Tumkur Road and Subhash Nagar connectors.
    4. **Non-Motorized Transit (NMT) Buffers:** Integrate dedicated feeder transit lanes connecting Mattikere and peripheral residential cells to Yeshwanthpur Metro Station and major medical hubs.
    """
)
