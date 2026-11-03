"""
Healthcare analysis module for Smart Yeshwanthpur GIS Analytics.
Filters, profiles, and analyzes healthcare facilities, nearest hospital lookup,
and deficit spot identification for potential future facility placement.
"""

from typing import Any, Dict, List, Optional, Tuple

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from shapely.geometry import Point

from src.config import ACCESSIBILITY_BANDS, CRS_GEOGRAPHIC, CRS_PROJECTED
from src.route_analysis import calculate_haversine_distance, find_shortest_route
from src.utils import logger, timer, validate_coordinates


def get_facility_summary(gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
    """Calculate summary statistics for healthcare facilities."""
    if gdf.empty:
        return {
            "total_facilities": 0,
            "num_hospitals": 0,
            "num_clinics": 0,
            "num_other": 0,
            "breakdown": {},
        }

    total = len(gdf)
    type_counts = gdf["facility_type"].value_counts().to_dict()

    num_hospitals = type_counts.get("Hospital", 0)
    num_clinics = type_counts.get("Clinic", 0) + type_counts.get(
        "Doctors / Clinic", 0
    )
    num_other = total - (num_hospitals + num_clinics)

    return {
        "total_facilities": total,
        "num_hospitals": int(num_hospitals),
        "num_clinics": int(num_clinics),
        "num_other": int(num_other),
        "breakdown": {str(k): int(v) for k, v in type_counts.items()},
    }


def classify_distance(distance_m: float) -> Tuple[str, str]:
    """
    Classify a distance into project-defined accessibility bands.
    Returns: (band_label, hex_color)
    """
    for low, high, label, color in ACCESSIBILITY_BANDS:
        if low <= distance_m < high:
            return label, color
    return "Very Low Accessibility (> 3 km)", "#e74c3c"


@timer
def find_nearest_healthcare_facility(
    origin_coords: Tuple[float, float],
    healthcare_gdf: gpd.GeoDataFrame,
    graph: Optional[nx.MultiDiGraph] = None,
    facility_type_filter: Optional[str] = "Hospital",
) -> Dict[str, Any]:
    """
    Find the nearest healthcare facility to a given origin point.
    Calculates straight-line distance, and if graph is provided,
    computes full road-network route, driving distance, and travel time.
    """
    orig_lat, orig_lon = origin_coords
    if not validate_coordinates(orig_lat, orig_lon):
        raise ValueError(f"Invalid origin coordinates: {origin_coords}")

    facilities = healthcare_gdf.copy()
    if facility_type_filter and "facility_type" in facilities.columns:
        if facility_type_filter != "All":
            facilities = facilities[
                facilities["facility_type"] == facility_type_filter
            ]

    if facilities.empty:
        return {
            "found": False,
            "message": f"No facilities found matching filter: {facility_type_filter}",
        }

    # Calculate Euclidean / Haversine distances to all candidate facilities
    distances_m = [
        calculate_haversine_distance(orig_lat, orig_lon, lat, lon)
        for lat, lon in zip(facilities["latitude"], facilities["longitude"])
    ]
    facilities["euclidean_dist_m"] = distances_m

    # Sort by straight line distance first to get closest candidate(s)
    facilities_sorted = facilities.sort_values(by="euclidean_dist_m")
    nearest_candidate = facilities_sorted.iloc[0]

    dest_coords = (
        float(nearest_candidate["latitude"]),
        float(nearest_candidate["longitude"]),
    )
    facility_name = nearest_candidate.get("facility_name", "Unknown Facility")
    facility_type = nearest_candidate.get("facility_type", "Healthcare Facility")
    address = nearest_candidate.get("address", "Yeshwanthpur, Bengaluru")
    straight_line_dist_m = float(nearest_candidate["euclidean_dist_m"])

    # If road graph is available, calculate network route
    network_dist_m = straight_line_dist_m
    travel_time_min = round(straight_line_dist_m / (25 * 1000 / 60), 1)
    route_geom = None
    circuity = 1.0
    segments = []

    if graph is not None:
        try:
            route_res = find_shortest_route(graph, origin_coords, dest_coords)
            if route_res.get("success"):
                network_dist_m = route_res["distance_meters"]
                travel_time_min = route_res["travel_time_min"]
                route_geom = route_res.get("route_geometry")
                circuity = route_res.get("circuity_factor", 1.0)
                segments = route_res.get("segments_table", [])
        except Exception as e:
            logger.warning(
                f"Network route computation failed ({e}). Falling back to straight-line distance."
            )

    band_label, band_color = classify_distance(network_dist_m)

    result = {
        "found": True,
        "facility_name": facility_name,
        "facility_type": facility_type,
        "address": address,
        "dest_coords": dest_coords,
        "straight_line_distance_m": round(straight_line_dist_m, 1),
        "straight_line_distance_km": round(straight_line_dist_m / 1000.0, 2),
        "network_distance_m": round(network_dist_m, 1),
        "network_distance_km": round(network_dist_m / 1000.0, 2),
        "estimated_travel_time_min": travel_time_min,
        "circuity_factor": circuity,
        "accessibility_band": band_label,
        "band_color": band_color,
        "route_geometry": route_geom,
        "segments": segments,
    }

    logger.info(
        f"Nearest {facility_type} for ({orig_lat:.4f}, {orig_lon:.4f}) is '{facility_name}' ({result['network_distance_km']} km, {travel_time_min} mins)."
    )
    return result


def identify_deficit_areas(
    grid_gdf: gpd.GeoDataFrame, top_k: int = 5
) -> gpd.GeoDataFrame:
    """
    Identify spatial grid cells with relatively poor healthcare accessibility
    (highest distance to nearest hospital with adequate road connectivity),
    representing candidate zones for additional healthcare facilities.
    """
    if grid_gdf.empty or "nearest_hosp_dist_m" not in grid_gdf.columns:
        return gpd.GeoDataFrame()

    df = grid_gdf.copy()
    # Prioritize cells with high distance and at least moderate road density
    # (avoiding uninhabited lakes or restricted railway yards where possible)
    if "road_density_km_sqkm" in df.columns:
        viable = df[df["road_density_km_sqkm"] > 1.0].copy()
    else:
        viable = df.copy()

    deficit_cells = viable.sort_values(
        by="nearest_hosp_dist_m", ascending=False
    ).head(top_k)
    return deficit_cells
