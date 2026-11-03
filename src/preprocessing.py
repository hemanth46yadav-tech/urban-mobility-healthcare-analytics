"""
Data preprocessing module for Smart Yeshwanthpur GIS Analytics.
Cleans and standardizes raw road network and healthcare facility datasets.
"""

from typing import Optional, Tuple

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon

from src.config import (
    CRS_GEOGRAPHIC,
    CRS_PROJECTED,
    GRAPH_PROCESSED_GRAPHML,
    HEALTHCARE_PROCESSED_GEOJSON,
    HEALTHCARE_PROCESSED_GPKG,
    NODES_PROCESSED_GPKG,
    ROAD_HIERARCHY,
    ROADS_PROCESSED_GPKG,
    SPEED_ASSUMPTIONS_KMH,
)
from src.utils import (
    logger,
    safe_save_geodataframe,
    timer,
    validate_coordinates,
    validate_geodataframe,
)


def _normalize_highway_tag(val) -> str:
    """Normalize OSM highway tags which may be strings or lists."""
    if isinstance(val, list):
        # Pick the highest-priority road class if multiple
        for item in val:
            if item in ROAD_HIERARCHY:
                return str(item)
        return str(val[0]) if val else "unclassified"
    elif pd.isna(val):
        return "unclassified"
    return str(val).strip().lower()


def _get_road_category_label(hw_type: str) -> str:
    """Map normalized highway type to human-readable classification."""
    return ROAD_HIERARCHY.get(hw_type, "Local / Other Road")


def _get_estimated_speed(hw_type: str) -> float:
    """Get defensible urban driving speed in km/h."""
    return SPEED_ASSUMPTIONS_KMH.get(hw_type, SPEED_ASSUMPTIONS_KMH["default"])


@timer
def preprocess_road_network(
    roads_gdf: gpd.GeoDataFrame,
    nodes_gdf: gpd.GeoDataFrame,
    graph: Optional[nx.MultiDiGraph] = None,
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, Optional[nx.MultiDiGraph]]:
    """
    Clean, validate, and enrich the road network GeoDataFrames.
    Calculates accurate metric lengths, road hierarchy classifications,
    and estimated travel times.
    """
    logger.info("Preprocessing road network...")

    roads = roads_gdf.copy()
    nodes = nodes_gdf.copy()

    # 1. Validate geometries
    roads = validate_geodataframe(roads)
    nodes = validate_geodataframe(nodes)

    # 2. Normalize highway classifications
    if "highway" in roads.columns:
        roads["highway_clean"] = roads["highway"].apply(_normalize_highway_tag)
    else:
        roads["highway_clean"] = "unclassified"

    roads["road_category"] = roads["highway_clean"].apply(
        _get_road_category_label
    )

    # 3. Handle road names
    if "name" in roads.columns:
        roads["road_name"] = roads["name"].apply(
            lambda x: (
                x
                if isinstance(x, str) and x.strip()
                else (x[0] if isinstance(x, list) and len(x) > 0 else None)
            )
        )
        roads["road_name"] = roads["road_name"].fillna("Unnamed Road")
    else:
        roads["road_name"] = "Unnamed Road"

    # 4. Accurate metric lengths and speed calculations via projected CRS (EPSG:32643)
    roads_proj = roads.to_crs(CRS_PROJECTED)
    roads["length_meters"] = roads_proj.geometry.length.round(2)

    # Assign estimated urban speed and travel time
    roads["speed_kph"] = roads["highway_clean"].apply(_get_estimated_speed)
    # Travel time in seconds: length_meters / (speed_kph * 1000 / 3600)
    roads["travel_time_sec"] = (
        roads["length_meters"] / (roads["speed_kph"] * 1000.0 / 3600.0)
    ).round(2)

    # 5. Clean nodes
    if "x" not in nodes.columns or "y" not in nodes.columns:
        nodes["x"] = nodes.geometry.x
        nodes["y"] = nodes.geometry.y

    # Calculate node degrees if graph is provided
    if graph is not None:
        degrees = dict(graph.degree())
        nodes["degree"] = nodes.index.map(degrees).fillna(0).astype(int)

    # 6. Save processed outputs
    safe_save_geodataframe(roads, ROADS_PROCESSED_GPKG, layer_name="roads")
    safe_save_geodataframe(nodes, NODES_PROCESSED_GPKG, layer_name="nodes")

    # Update graph edge weights if graph is provided
    if graph is not None:
        for u, v, k, data in graph.edges(keys=True, data=True):
            hw = _normalize_highway_tag(data.get("highway", "unclassified"))
            speed = _get_estimated_speed(hw)
            length = float(data.get("length", 1.0))
            time_sec = length / (speed * 1000.0 / 3600.0)
            data["speed_kph"] = speed
            data["travel_time"] = time_sec
            data["weight"] = length

        # Save processed graphml
        try:
            import osmnx as ox
            ox.save_graphml(graph, GRAPH_PROCESSED_GRAPHML)
            logger.info(f"Saved processed graph to {GRAPH_PROCESSED_GRAPHML}")
        except Exception as e:
            logger.warning(f"Could not save processed graphml: {e}")

    logger.info(
        f"Preprocessed {len(roads)} road segments and {len(nodes)} nodes."
    )
    return roads, nodes, graph


@timer
def preprocess_healthcare_facilities(
    healthcare_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Clean, validate, and standardize healthcare facilities dataset.
    Converts building footprints/polygons to representative coordinate points,
    normalizes facility categories, and removes duplicates.
    """
    logger.info("Preprocessing healthcare facilities...")

    if healthcare_gdf.empty:
        logger.warning(
            "Healthcare GeoDataFrame is empty. Nothing to preprocess."
        )
        return gpd.GeoDataFrame()

    gdf = healthcare_gdf.copy()

    # 1. Validate geometries
    gdf = validate_geodataframe(gdf)

    # 2. Extract representative point geometries for distance analysis
    # If geometry is Polygon, convert to centroid
    gdf["orig_geom_type"] = gdf.geometry.geom_type
    point_geoms = []
    latitudes = []
    longitudes = []

    for geom in gdf.geometry:
        if isinstance(geom, Point):
            pt = geom
        else:
            pt = geom.centroid
        point_geoms.append(pt)
        latitudes.append(pt.y)
        longitudes.append(pt.x)

    gdf["geometry"] = point_geoms
    gdf["latitude"] = latitudes
    gdf["longitude"] = longitudes

    # 3. Validate coordinates
    valid_coord_mask = [
        validate_coordinates(lat, lon)
        for lat, lon in zip(gdf["latitude"], gdf["longitude"])
    ]
    gdf = gdf[valid_coord_mask].copy()

    # 4. Standardize facility names
    if "name" in gdf.columns:
        gdf["name"] = (
            gdf["name"]
            .astype(str)
            .replace(["nan", "None", "<NA>", ""], np.nan)
        )
    else:
        gdf["name"] = np.nan

    # 5. Standardize facility type
    if "amenity" in gdf.columns:
        type_mapping = {
            "hospital": "Hospital",
            "clinic": "Clinic",
            "doctors": "Doctors / Clinic",
            "health_post": "Health Post",
            "pharmacy": "Pharmacy",
        }
        gdf["facility_type"] = (
            gdf["amenity"].map(type_mapping).fillna("Healthcare Facility")
        )
    else:
        gdf["facility_type"] = "Healthcare Facility"

    # Fill missing facility names with generic title
    gdf["facility_name"] = gdf.apply(
        lambda row: (
            row["name"]
            if pd.notna(row["name"]) and row["name"].strip()
            else f"Unnamed {row['facility_type']}"
        ),
        axis=1,
    )

    # 6. Extract Address if available
    addr_cols = [c for c in gdf.columns if "addr:" in c]
    if addr_cols:
        gdf["address"] = (
            gdf[addr_cols]
            .apply(
                lambda row: ", ".join(
                    [str(v) for v in row if pd.notna(v) and str(v).strip()]
                ),
                axis=1,
            )
            .replace("", "Yeshwanthpur, Bengaluru")
        )
    else:
        gdf["address"] = "Yeshwanthpur, Bengaluru"

    # 7. Deduplication
    initial_count = len(gdf)
    # Deduplicate by OSM index/id if available
    gdf = gdf[~gdf.index.duplicated(keep="first")].copy()

    # Spatial deduplication: project to EPSG:32643 and flag facilities within 15 meters
    # having same or similar name
    gdf_proj = gdf.to_crs(CRS_PROJECTED)
    coords = np.column_stack([gdf_proj.geometry.x, gdf_proj.geometry.y])

    keep_mask = np.ones(len(gdf), dtype=bool)
    for i in range(len(gdf)):
        if not keep_mask[i]:
            continue
        dist = np.linalg.norm(coords[i] - coords, axis=1)
        # Check nearby points (within 15m) with duplicate names
        nearby_indices = np.where((dist < 15.0) & (np.arange(len(gdf)) > i))[0]
        for j in nearby_indices:
            if (
                gdf.iloc[i]["facility_name"] == gdf.iloc[j]["facility_name"]
                or gdf.iloc[i]["facility_type"] == gdf.iloc[j]["facility_type"]
            ):
                keep_mask[j] = False

    gdf = gdf[keep_mask].copy()
    dedup_count = len(gdf)
    logger.info(
        f"Deduplication: {initial_count} -> {dedup_count} facilities ({initial_count - dedup_count} duplicates removed)."
    )

    # Select standard clean columns
    keep_cols = [
        "facility_name",
        "facility_type",
        "latitude",
        "longitude",
        "address",
        "orig_geom_type",
        "geometry",
    ]
    available_keep_cols = [c for c in keep_cols if c in gdf.columns]
    clean_gdf = gdf[available_keep_cols].copy()

    # 8. Save processed outputs (GeoJSON and GeoPackage)
    safe_save_geodataframe(clean_gdf, HEALTHCARE_PROCESSED_GEOJSON)
    safe_save_geodataframe(
        clean_gdf, HEALTHCARE_PROCESSED_GPKG, layer_name="healthcare"
    )

    logger.info(
        f"Preprocessed {len(clean_gdf)} healthcare facilities successfully."
    )
    return clean_gdf
