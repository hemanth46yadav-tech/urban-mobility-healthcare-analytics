"""
Interactive mapping and plotting module for Smart Yeshwanthpur GIS Analytics.
Generates Folium interactive geospatial maps and Plotly analytical charts.
"""

from typing import Any, Dict, List, Optional, Tuple

import folium
from folium import plugins
import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from shapely.geometry import LineString, Point

from src.config import CENTER_LAT, CENTER_LON, STUDY_AREA_NAME


# ==========================================
# FOLIUM INTERACTIVE MAP BUILDERS
# ==========================================

def create_base_map(
    center_lat: float = CENTER_LAT,
    center_lon: float = CENTER_LON,
    zoom_start: int = 14,
) -> folium.Map:
    """Create a high-contrast base Folium map with OpenStreetMap default tiles."""
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles="OpenStreetMap",
        control_scale=True,
    )
    return m


def add_study_boundary_to_map(
    m: folium.Map, boundary_gdf: gpd.GeoDataFrame
) -> folium.Map:
    """Add study boundary polygon to Folium map."""
    if boundary_gdf.empty:
        return m

    boundary_geojson = boundary_gdf.to_json()
    folium.GeoJson(
        boundary_geojson,
        name="Study Area Boundary (2.5 km)",
        style_function=lambda x: {
            "fillColor": "#3498db",
            "color": "#2980b9",
            "weight": 2.5,
            "dashArray": "6, 6",
            "fillOpacity": 0.05,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "radius_meters", "area_sqkm"],
            aliases=["Study Area:", "Radius (m):", "Area (km²):"],
            localize=True,
        ),
    ).add_to(m)
    return m


def add_healthcare_markers_to_map(
    m: folium.Map,
    healthcare_gdf: gpd.GeoDataFrame,
    marker_cluster: bool = False,
) -> folium.Map:
    """Add hospital and clinic markers with custom icons and rich HTML popups."""
    if healthcare_gdf.empty:
        return m

    target_group = (
        plugins.MarkerCluster(name="Healthcare Facilities Cluster")
        if marker_cluster
        else folium.FeatureGroup(name="Healthcare Facilities")
    )

    for _, row in healthcare_gdf.iterrows():
        lat = row.get("latitude")
        lon = row.get("longitude")
        if pd.isna(lat) or pd.isna(lon):
            continue

        fac_name = row.get("facility_name", "Healthcare Facility")
        fac_type = row.get("facility_type", "Clinic")
        address = row.get("address", "Yeshwanthpur, Bengaluru")

        # Styling depending on facility classification
        if fac_type == "Hospital":
            icon_color = "red"
            icon_symbol = "plus"
        elif "Clinic" in fac_type:
            icon_color = "blue"
            icon_symbol = "medkit"
        elif "Doctor" in fac_type:
            icon_color = "darkblue"
            icon_symbol = "user-md"
        else:
            icon_color = "cadetblue"
            icon_symbol = "tint"

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 180px;">
            <h4 style="margin: 0 0 5px 0; color: #2c3e50;">{fac_name}</h4>
            <p style="margin: 2px 0;"><strong>Category:</strong> <span style="color: {'#c0392b' if fac_type == 'Hospital' else '#2980b9'};">{fac_type}</span></p>
            <p style="margin: 2px 0; font-size: 11px; color: #7f8c8d;">{address}</p>
            <p style="margin: 4px 0 0 0; font-size: 10px; color: #95a5a6;">Coords: {lat:.4f}, {lon:.4f}</p>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{fac_name} ({fac_type})",
            icon=folium.Icon(
                color=icon_color, icon=icon_symbol, prefix="fa"
            ),
        ).add_to(target_group)

    target_group.add_to(m)
    return m


def add_road_network_to_map(
    m: folium.Map,
    roads_gdf: gpd.GeoDataFrame,
    max_segments: int = 1500,
    highlight_bottlenecks: bool = False,
) -> folium.Map:
    """Add styled road segments to Folium map."""
    if roads_gdf.empty:
        return m

    # Subsample if roads dataset is excessively large for web rendering
    sample_roads = (
        roads_gdf.sample(n=min(len(roads_gdf), max_segments), random_state=42)
        if len(roads_gdf) > max_segments
        else roads_gdf
    )

    fg_roads = folium.FeatureGroup(name="Road Network Hierarchy")

    def _style_road(feature):
        props = feature["properties"]
        cat = props.get("road_category", "")
        is_bottleneck = props.get("is_bottleneck_corridor", False)

        if highlight_bottlenecks and is_bottleneck:
            return {"color": "#e74c3c", "weight": 4.5, "opacity": 0.9}
        elif "Highway" in cat or "Expressway" in cat:
            return {"color": "#8e44ad", "weight": 3.8, "opacity": 0.85}
        elif "Arterial" in cat:
            return {"color": "#e67e22", "weight": 3.2, "opacity": 0.8}
        elif "Collector" in cat:
            return {"color": "#f39c12", "weight": 2.5, "opacity": 0.75}
        elif "Tertiary" in cat:
            return {"color": "#2980b9", "weight": 2.0, "opacity": 0.7}
        else:
            return {"color": "#95a5a6", "weight": 1.4, "opacity": 0.6}

    folium.GeoJson(
        sample_roads.to_json(),
        style_function=_style_road,
        tooltip=folium.GeoJsonTooltip(
            fields=["road_name", "road_category", "length_meters", "speed_kph"],
            aliases=["Road:", "Class:", "Length (m):", "Est Speed (km/h):"],
            localize=True,
        ),
    ).add_to(fg_roads)

    fg_roads.add_to(m)
    return m


def add_route_to_map(
    m: folium.Map,
    route_result: Dict[str, Any],
    orig_coords: Tuple[float, float],
    dest_coords: Tuple[float, float],
    orig_label: str = "Origin",
    dest_label: str = "Destination",
) -> folium.Map:
    """Render shortest road-network route on Folium map."""
    if not route_result.get("success"):
        return m

    # Origin Marker (Green)
    folium.Marker(
        location=[orig_coords[0], orig_coords[1]],
        popup=f"<b>Origin: {orig_label}</b><br>{orig_coords[0]:.4f}° N, {orig_coords[1]:.4f}° E",
        tooltip=f"Origin: {orig_label}",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(m)

    # Destination Marker (Red)
    folium.Marker(
        location=[dest_coords[0], dest_coords[1]],
        popup=f"<b>Destination: {dest_label}</b><br>{dest_coords[0]:.4f}° N, {dest_coords[1]:.4f}° E",
        tooltip=f"Destination: {dest_label}",
        icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
    ).add_to(m)

    # Route Line
    route_geom = route_result.get("route_geometry")
    if route_geom and isinstance(route_geom, LineString):
        route_coords = [(lat, lon) for lon, lat in route_geom.coords]

        # Shadow line
        folium.PolyLine(
            locations=route_coords,
            color="#2c3e50",
            weight=7,
            opacity=0.6,
        ).add_to(m)

        # Foreground route line
        folium.PolyLine(
            locations=route_coords,
            color="#3498db",
            weight=4.5,
            opacity=0.95,
            tooltip=f"Driving Route: {route_result.get('distance_km')} km ({route_result.get('travel_time_min')} mins)",
        ).add_to(m)

    # Straight-line connector for comparison
    folium.PolyLine(
        locations=[
            [orig_coords[0], orig_coords[1]],
            [dest_coords[0], dest_coords[1]],
        ],
        color="#e67e22",
        weight=2,
        dash_array="5, 8",
        opacity=0.7,
        tooltip=f"Straight Line: {route_result.get('straight_line_dist_meters')}m (Circuity: {route_result.get('circuity_factor')}x)",
    ).add_to(m)

    # Fit map bounds to encompass the two locations and the route
    all_lats = [orig_coords[0], dest_coords[0]]
    all_lons = [orig_coords[1], dest_coords[1]]
    if route_geom and isinstance(route_geom, LineString):
        for lon, lat in route_geom.coords:
            all_lats.append(lat)
            all_lons.append(lon)
    m.fit_bounds(
        [[min(all_lats), min(all_lons)], [max(all_lats), max(all_lons)]],
        padding=(30, 30),
    )

    return m


def add_accessibility_grid_to_map(
    m: folium.Map,
    grid_gdf: gpd.GeoDataFrame,
    color_by: str = "accessibility_band",
) -> folium.Map:
    """Render spatial grid choropleth on Folium map."""
    if grid_gdf.empty:
        return m

    fg_grid = folium.FeatureGroup(name="Healthcare Accessibility Grid")

    def _get_cell_color(feature):
        props = feature["properties"]
        if color_by == "accessibility_band":
            return props.get("band_color", "#bdc3c7")
        elif color_by == "cluster":
            return props.get("cluster_color", "#34495e")
        else:
            score = props.get("accessibility_score", 50)
            if score >= 70:
                return "#2ecc71"
            elif score >= 50:
                return "#f39c12"
            elif score >= 30:
                return "#e67e22"
            else:
                return "#e74c3c"

    folium.GeoJson(
        grid_gdf.to_json(),
        style_function=lambda feature: {
            "fillColor": _get_cell_color(feature),
            "color": "#7f8c8d",
            "weight": 0.8,
            "fillOpacity": 0.55,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "grid_id",
                "nearest_hosp_dist_m",
                "total_healthcare_count",
                "road_density_km_sqkm",
                "accessibility_band",
                "accessibility_score",
            ],
            aliases=[
                "Grid Cell:",
                "Hospital Dist (m):",
                "Facilities in Cell:",
                "Road Density (km/km²):",
                "Accessibility Tier:",
                "Access Score (0-100):",
            ],
            localize=True,
        ),
    ).add_to(fg_grid)

    fg_grid.add_to(m)
    return m


# ==========================================
# PLOTLY ANALYTICAL CHARTS
# ==========================================

def plot_road_category_distribution(roads_gdf: gpd.GeoDataFrame) -> go.Figure:
    """Plot road segment breakdown by hierarchy classification."""
    cat_col = (
        "road_category" if "road_category" in roads_gdf.columns else "highway"
    )
    counts = roads_gdf[cat_col].value_counts().reset_index()
    counts.columns = ["Classification", "Segments"]

    fig = px.bar(
        counts,
        x="Segments",
        y="Classification",
        orientation="h",
        color="Segments",
        color_continuous_scale="Viridis",
        title="Road Network Distribution by Hierarchy",
    )
    fig.update_layout(
        template="plotly_white",
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=360,
    )
    return fig


def plot_accessibility_bands(grid_gdf: gpd.GeoDataFrame) -> go.Figure:
    """Donut chart of accessibility bands distribution."""
    counts = grid_gdf["accessibility_band"].value_counts().reset_index()
    counts.columns = ["Accessibility Tier", "Cell Count"]

    color_map = {
        "High Accessibility (< 1 km)": "#2ecc71",
        "Moderate Accessibility (1-2 km)": "#f39c12",
        "Low Accessibility (2-3 km)": "#e67e22",
        "Very Low Accessibility (> 3 km)": "#e74c3c",
    }

    fig = px.pie(
        counts,
        values="Cell Count",
        names="Accessibility Tier",
        color="Accessibility Tier",
        color_discrete_map=color_map,
        hole=0.45,
        title="Healthcare Accessibility Coverage Tiers",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=360,
    )
    return fig


def plot_clustering_evaluation(
    eval_dict: Dict[str, Any]
) -> Tuple[go.Figure, go.Figure]:
    """Plot Elbow Curve (Inertia) and Silhouette Scores across k."""
    k_vals = eval_dict["k_values"]
    inertias = eval_dict["inertias"]
    sil_scores = eval_dict["silhouette_scores"]

    # Elbow
    fig_elbow = go.Figure()
    fig_elbow.add_trace(
        go.Scatter(
            x=k_vals,
            y=inertias,
            mode="lines+markers",
            marker=dict(size=9, color="#2980b9"),
            line=dict(width=2.5, color="#2980b9"),
            name="Inertia",
        )
    )
    fig_elbow.update_layout(
        title="Elbow Method (Inertia vs Number of Clusters k)",
        xaxis_title="Number of Clusters (k)",
        yaxis_title="Within-Cluster Sum of Squares (Inertia)",
        template="plotly_white",
        height=330,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    # Silhouette
    fig_sil = go.Figure()
    fig_sil.add_trace(
        go.Bar(
            x=k_vals,
            y=sil_scores,
            marker_color="#27ae60",
            name="Silhouette Score",
        )
    )
    fig_sil.update_layout(
        title="Silhouette Score Analysis by Cluster Count k",
        xaxis_title="Number of Clusters (k)",
        yaxis_title="Average Silhouette Coefficient",
        template="plotly_white",
        height=330,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig_elbow, fig_sil


def plot_pca_clusters(
    clustered_df: pd.DataFrame,
    var_ratio: Optional[List[float]] = None,
) -> go.Figure:
    """Plot PCA projection of clusters with interactive tooltips."""
    v1 = f"PCA Component 1 ({var_ratio[0]*100:.1f}%)" if var_ratio else "PCA 1"
    v2 = f"PCA Component 2 ({var_ratio[1]*100:.1f}%)" if var_ratio else "PCA 2"

    fig = px.scatter(
        clustered_df,
        x="pca_1",
        y="pca_2",
        color="cluster_label",
        hover_data=[
            "grid_id",
            "nearest_hosp_dist_m",
            "road_density_km_sqkm",
            "accessibility_score",
        ],
        title=f"PCA 2D Projection of Spatial Neighbourhood Clusters",
        labels={"pca_1": v1, "pca_2": v2, "cluster_label": "Cluster Profile"},
    )
    fig.update_traces(marker=dict(size=8, opacity=0.85))
    fig.update_layout(
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig
