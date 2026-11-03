"""
PAGE 4: HEALTHCARE ANALYSIS
Healthcare facility mapping, category filtering, hospital service buffers, and facility directories.
"""

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
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
from src.spatial_analysis import create_facility_buffers
from src.visualizations import (
    add_healthcare_markers_to_map,
    add_study_boundary_to_map,
    create_base_map,
)

st.set_page_config(page_title="Healthcare Analysis | Smart Yeshwanthpur", layout="wide")
apply_custom_styles()

st.title("Healthcare Infrastructure & Facility Analysis")
st.markdown(
    "Geospatial distribution, categorization, and Euclidean service radius analysis of healthcare amenities across Yeshwanthpur."
)

data = load_cached_datasets()
metrics = data.get("metrics", {})
boundary = data.get("boundary")
healthcare = data.get("healthcare")

if healthcare.empty:
    st.error("Healthcare dataset is empty. Run `python src/run_pipeline.py` to acquire data.")
    st.stop()

hc_stats = metrics.get("healthcare_statistics", {})

# KPI Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Total Facilities", f"{hc_stats.get('total_facilities', len(healthcare))}", "Verified facilities")
with c2:
    render_metric_card("Hospitals", f"{hc_stats.get('num_hospitals', 0)}", "Secondary & tertiary care centers")
with c3:
    render_metric_card("Clinics & Doctors", f"{hc_stats.get('num_clinics', 0)}", "Primary outpatient clinics")
with c4:
    render_metric_card("Other Amenities", f"{hc_stats.get('num_other', 0)}", "Pharmacies & health posts", neutral=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Filters & Controls
f_col1, f_col2, f_col3 = st.columns([4, 4, 2])

all_types = ["All"] + sorted(list(healthcare["facility_type"].dropna().unique()))

with f_col1:
    selected_type = st.selectbox("Filter by Facility Category:", options=all_types, index=0)

with f_col2:
    search_query = st.text_input("Search Facility Name or Address:", value="")

with f_col3:
    show_buffers = st.checkbox("Show 1 km Hospital Buffers", value=True)

# Apply Filters
filtered_hc = healthcare.copy()
if selected_type != "All":
    filtered_hc = filtered_hc[filtered_hc["facility_type"] == selected_type]

if search_query.strip():
    q = search_query.strip().lower()
    filtered_hc = filtered_hc[
        filtered_hc["facility_name"].str.lower().str.contains(q, na=False)
        | filtered_hc["address"].str.lower().str.contains(q, na=False)
    ]

# Main Map & Distribution Charts
map_c, chart_c = st.columns([7, 3])

with map_c:
    st.subheader("Healthcare Geospatial Map")
    m = create_base_map(zoom_start=14)
    if not boundary.empty:
        add_study_boundary_to_map(m, boundary)

    # Optional Hospital Buffers
    if show_buffers:
        hosp_buffers = create_facility_buffers(
            healthcare, buffer_radii_m=[1000], facility_type_filter="Hospital"
        )
        if not hosp_buffers.empty:
            import folium
            folium.GeoJson(
                hosp_buffers.to_json(),
                name="1 km Hospital Service Buffer",
                style_function=lambda x: {
                    "fillColor": "#e74c3c",
                    "color": "#c0392b",
                    "weight": 1.5,
                    "fillOpacity": 0.12,
                },
            ).add_to(m)

    add_healthcare_markers_to_map(m, filtered_hc, marker_cluster=False)
    st_folium(m, width="100%", height=500, returned_objects=[])

with chart_c:
    st.subheader("Category Distribution")
    type_counts = healthcare["facility_type"].value_counts().reset_index()
    type_counts.columns = ["Facility Type", "Count"]

    fig_pie = px.pie(
        type_counts,
        values="Count",
        names="Facility Type",
        title="Healthcare Amenity Mix",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.4,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(height=350, margin=dict(l=10, r=10, t=35, b=10))
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Facility Directory Table
st.subheader("Healthcare Facilities Directory")
st.caption(f"Displaying {len(filtered_hc)} matching facilities in Yeshwanthpur.")

table_cols = ["facility_name", "facility_type", "latitude", "longitude", "address"]
avail_cols = [c for c in table_cols if c in filtered_hc.columns]
st.dataframe(filtered_hc[avail_cols].reset_index(drop=True), use_container_width=True, height=280)

st.subheader("Export Healthcare Facility Data")
render_download_buttons(filtered_hc, "yeshwanthpur_healthcare_filtered", "Healthcare Facilities")

