"""
Data collection module for Smart Yeshwanthpur GIS Analytics.
Uses OSMnx and OpenStreetMap APIs with retry logic, error handling, and local caching.
"""

import time
from pathlib import Path
from typing import Optional, Tuple

import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
from shapely.geometry import Point

from src.config import (
    CENTER_LAT,
    CENTER_LON,
    CRS_GEOGRAPHIC,
    CRS_PROJECTED,
    GRAPH_RAW_GRAPHML,
    HEALTHCARE_OSM_TAGS,
    HEALTHCARE_RAW_GEOJSON,
    NODES_RAW_GPKG,
    ROADS_RAW_GPKG,
    STUDY_AREA_NAME,
    STUDY_BOUNDARY_GEOJSON,
    STUDY_RADIUS_METERS,
)
from src.utils import logger, safe_save_geodataframe, timer, validate_geodataframe


def create_study_boundary(
    lat: float = CENTER_LAT,
    lon: float = CENTER_LON,
    radius_m: float = STUDY_RADIUS_METERS,
    output_path: Optional[Path] = STUDY_BOUNDARY_GEOJSON,
) -> gpd.GeoDataFrame:
    """
    Generate an analytical study boundary buffer around the study center.
    Uses metric projection (EPSG:32643) for precise distance buffering,
    then reprojects to WGS84 (EPSG:4326).
    """
    logger.info(
        f"Creating study boundary for {STUDY_AREA_NAME} with radius {radius_m}m."
    )
    center_point = Point(lon, lat)
    gdf_center = gpd.GeoDataFrame(
        {"name": [STUDY_AREA_NAME], "geometry": [center_point]},
        crs=CRS_GEOGRAPHIC,
    )

    # Project to metric UTM CRS for accurate buffering
    gdf_projected = gdf_center.to_crs(CRS_PROJECTED)
    buffer_geom = gdf_projected.geometry.iloc[0].buffer(radius_m)
    area_sqkm = buffer_geom.area / 1e6

    gdf_boundary_proj = gpd.GeoDataFrame(
        {
            "name": [STUDY_AREA_NAME],
            "center_lat": [lat],
            "center_lon": [lon],
            "radius_meters": [radius_m],
            "area_sqkm": [area_sqkm],
            "geometry": [buffer_geom],
        },
        crs=CRS_PROJECTED,
    )

    # Reproject to EPSG:4326 for GIS visualization and interoperability
    gdf_boundary = gdf_boundary_proj.to_crs(CRS_GEOGRAPHIC)

    if output_path:
        safe_save_geodataframe(gdf_boundary, output_path)

    return gdf_boundary


@timer
def fetch_road_network(
    lat: float = CENTER_LAT,
    lon: float = CENTER_LON,
    radius_m: float = STUDY_RADIUS_METERS,
    force_download: bool = False,
    max_retries: int = 3,
) -> Tuple[nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Download drivable road network using OSMnx with retries and caching.
    Returns:
        (graph, nodes_gdf, edges_gdf)
    """
    if (
        not force_download
        and GRAPH_RAW_GRAPHML.exists()
        and ROADS_RAW_GPKG.exists()
        and NODES_RAW_GPKG.exists()
    ):
        logger.info("Found cached road network data. Loading from disk...")
        try:
            G = ox.load_graphml(GRAPH_RAW_GRAPHML)
            nodes = gpd.read_file(NODES_RAW_GPKG)
            roads = gpd.read_file(ROADS_RAW_GPKG)
            return G, nodes, roads
        except Exception as e:
            logger.warning(
                f"Error loading cached network ({e}). Re-downloading from OSM..."
            )

    logger.info(
        f"Querying OpenStreetMap road network around ({lat}, {lon}) within {radius_m}m..."
    )

    # Configure OSMnx settings
    ox.settings.use_cache = True
    ox.settings.log_console = False

    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            # Download drivable network
            G = ox.graph_from_point(
                (lat, lon),
                dist=radius_m,
                network_type="drive",
                simplify=True,
                retain_all=False,
                truncate_by_edge=True,
            )

            # Convert to GeoDataFrames
            nodes, edges = ox.graph_to_gdfs(G)

            # Ensure CRS
            if nodes.crs is None:
                nodes.set_crs(CRS_GEOGRAPHIC, inplace=True)
            if edges.crs is None:
                edges.set_crs(CRS_GEOGRAPHIC, inplace=True)

            # Validate geometries
            nodes = validate_geodataframe(nodes)
            edges = validate_geodataframe(edges)

            # Save raw outputs
            ox.save_graphml(G, GRAPH_RAW_GRAPHML)
            safe_save_geodataframe(nodes, NODES_RAW_GPKG, layer_name="nodes")
            safe_save_geodataframe(edges, ROADS_RAW_GPKG, layer_name="edges")

            logger.info(
                f"Road network acquired: {len(nodes)} nodes, {len(edges)} edges."
            )
            return G, nodes, edges

        except Exception as e:
            last_exception = e
            logger.warning(
                f"Attempt {attempt}/{max_retries} failed to download road network: {e}"
            )
            if attempt < max_retries:
                time.sleep(2 * attempt)

    raise RuntimeError(
        f"Failed to fetch road network after {max_retries} attempts: {last_exception}"
    )


@timer
def fetch_healthcare_facilities(
    lat: float = CENTER_LAT,
    lon: float = CENTER_LON,
    radius_m: float = STUDY_RADIUS_METERS,
    force_download: bool = False,
    max_retries: int = 3,
) -> gpd.GeoDataFrame:
    """
    Download healthcare amenities (hospitals, clinics, doctors, etc.) using OSMnx.
    """
    if not force_download and HEALTHCARE_RAW_GEOJSON.exists():
        logger.info("Found cached healthcare facilities. Loading from disk...")
        try:
            gdf = gpd.read_file(HEALTHCARE_RAW_GEOJSON)
            if not gdf.empty:
                return gdf
        except Exception as e:
            logger.warning(
                f"Error loading cached healthcare data ({e}). Re-downloading..."
            )

    logger.info(
        f"Querying OpenStreetMap healthcare amenities around ({lat}, {lon}) within {radius_m}m..."
    )

    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            # In OSMnx 2.x, features_from_point retrieves POIs/amenities
            gdf = ox.features_from_point(
                (lat, lon), tags=HEALTHCARE_OSM_TAGS, dist=radius_m
            )

            if gdf.empty:
                logger.warning(
                    "No healthcare features returned for the specified tags and radius."
                )
                return gpd.GeoDataFrame()

            # Ensure CRS
            if gdf.crs is None:
                gdf.set_crs(CRS_GEOGRAPHIC, inplace=True)

            # Validate
            gdf = validate_geodataframe(gdf)

            # Save raw data
            safe_save_geodataframe(gdf, HEALTHCARE_RAW_GEOJSON)
            logger.info(
                f"Healthcare features acquired: {len(gdf)} records saved to {HEALTHCARE_RAW_GEOJSON}."
            )
            return gdf

        except Exception as e:
            last_exception = e
            logger.warning(
                f"Attempt {attempt}/{max_retries} failed to fetch healthcare amenities: {e}"
            )
            if attempt < max_retries:
                time.sleep(2 * attempt)

    raise RuntimeError(
        f"Failed to fetch healthcare facilities after {max_retries} attempts: {last_exception}"
    )

