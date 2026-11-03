"""
Shortest-path route analysis module for Smart Yeshwanthpur GIS Analytics.
Uses NetworkX and OSMnx to calculate network paths, distances, travel times,
and circuity compared to straight-line Euclidean distance.
"""

from typing import Any, Dict, List, Optional, Tuple

import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
from shapely.geometry import LineString, Point

from src.config import CRS_GEOGRAPHIC, CRS_PROJECTED
from src.utils import logger, timer, validate_coordinates


def find_nearest_node(
    graph: nx.MultiDiGraph, lat: float, lon: float
) -> Optional[int]:
    """Find the nearest drivable network node to a given coordinate."""
    if not validate_coordinates(lat, lon):
        logger.error(f"Invalid coordinates supplied: ({lat}, {lon})")
        return None

    try:
        # In OSMnx 2.x, ox.distance.nearest_nodes takes (G, X, Y)
        node = ox.distance.nearest_nodes(graph, X=lon, Y=lat)
        return int(node)
    except Exception as e:
        logger.error(f"Error finding nearest node to ({lat}, {lon}): {e}")
        return None


def calculate_haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Calculate the great-circle distance between two points in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = (
        np.sin(delta_phi / 2.0) ** 2
        + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
    )
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return float(R * c)


@timer
def find_shortest_route(
    graph: nx.MultiDiGraph,
    orig_coords: Tuple[float, float],
    dest_coords: Tuple[float, float],
    weight: str = "length",
) -> Dict[str, Any]:
    """
    Compute the shortest driving path between origin and destination coordinates.
    Args:
        graph: Drivable road network MultiDiGraph
        orig_coords: (latitude, longitude)
        dest_coords: (latitude, longitude)
        weight: 'length' (distance in meters) or 'travel_time' (seconds)
    Returns:
        Dictionary with route details, geometry, step-by-step road segments,
        network distance, straight-line distance, and circuity factor.
    """
    orig_lat, orig_lon = orig_coords
    dest_lat, dest_lon = dest_coords

    if not validate_coordinates(orig_lat, orig_lon) or not validate_coordinates(
        dest_lat, dest_lon
    ):
        raise ValueError("Invalid origin or destination coordinates.")

    # 1. Straight-line (great-circle) distance
    straight_line_dist_m = calculate_haversine_distance(
        orig_lat, orig_lon, dest_lat, dest_lon
    )

    # 2. Nearest network nodes
    orig_node = find_nearest_node(graph, orig_lat, orig_lon)
    dest_node = find_nearest_node(graph, dest_lat, dest_lon)

    if orig_node is None or dest_node is None:
        raise RuntimeError("Could not snap coordinates to network nodes.")

    if orig_node == dest_node:
        return {
            "success": True,
            "same_node": True,
            "orig_node": orig_node,
            "dest_node": dest_node,
            "distance_meters": 0.0,
            "distance_km": 0.0,
            "straight_line_dist_meters": round(straight_line_dist_m, 2),
            "circuity_factor": 1.0,
            "travel_time_sec": 0.0,
            "travel_time_min": 0.0,
            "num_segments": 0,
            "route_geometry": LineString([(orig_lon, orig_lat), (dest_lon, dest_lat)]),
            "path_nodes": [orig_node],
            "segments_table": [],
        }

    # 3. Shortest path via Dijkstra
    try:
        route_nodes = nx.shortest_path(
            graph, source=orig_node, target=dest_node, weight=weight
        )
    except nx.NetworkXNoPath:
        # Fallback to undirected graph if one-way constraints isolate nodes in the buffer
        logger.warning(
            "No directed route found. Attempting route on undirected network graph..."
        )
        G_undir = graph.to_undirected()
        try:
            route_nodes = nx.shortest_path(
                G_undir, source=orig_node, target=dest_node, weight=weight
            )
        except nx.NetworkXNoPath:
            return {
                "success": False,
                "error": "No drivable route exists between the selected points within the study area.",
                "orig_coords": orig_coords,
                "dest_coords": dest_coords,
                "straight_line_dist_meters": round(straight_line_dist_m, 2),
            }

    # 4. Extract edge geometries and attributes along the path
    total_dist_m = 0.0
    total_time_sec = 0.0
    line_coords = []
    segments_info = []

    for u, v in zip(route_nodes[:-1], route_nodes[1:]):
        # Retrieve edge data (choose edge with minimum weight if multigraph)
        edge_dict = graph.get_edge_data(u, v)
        if edge_dict is None:
            # Undirected fallback lookup
            edge_dict = graph.get_edge_data(v, u, {0: {}})

        best_key = min(
            edge_dict.keys(),
            key=lambda k: edge_dict[k].get(weight, edge_dict[k].get("length", 1.0)),
        )
        edge_data = edge_dict[best_key]

        edge_len = float(edge_data.get("length", 0.0))
        edge_time = float(
            edge_data.get("travel_time", edge_len / (20.0 * 1000 / 3600))
        )
        edge_name = edge_data.get("name", "Unnamed Road")
        if isinstance(edge_name, list):
            edge_name = edge_name[0]
        edge_highway = edge_data.get("highway", "local")
        if isinstance(edge_highway, list):
            edge_highway = edge_highway[0]

        total_dist_m += edge_len
        total_time_sec += edge_time

        # Extract line coordinates
        if "geometry" in edge_data:
            line_coords.extend(list(edge_data["geometry"].coords))
        else:
            u_pt = (graph.nodes[u]["x"], graph.nodes[u]["y"])
            v_pt = (graph.nodes[v]["x"], graph.nodes[v]["y"])
            line_coords.extend([u_pt, v_pt])

        segments_info.append(
            {
                "from_node": u,
                "to_node": v,
                "road_name": edge_name,
                "road_category": str(edge_highway),
                "length_meters": round(edge_len, 1),
                "estimated_speed_kph": float(edge_data.get("speed_kph", 20.0)),
                "travel_time_sec": round(edge_time, 1),
            }
        )

    # Clean coordinate duplicates in line
    clean_coords = []
    for pt in line_coords:
        if not clean_coords or clean_coords[-1] != pt:
            clean_coords.append(pt)

    route_geom = LineString(clean_coords) if len(clean_coords) >= 2 else None

    # Circuity Factor (Network Distance / Straight Line Distance)
    circuity = (
        round(total_dist_m / max(straight_line_dist_m, 1.0), 2)
        if straight_line_dist_m > 0
        else 1.0
    )

    result = {
        "success": True,
        "orig_node": orig_node,
        "dest_node": dest_node,
        "distance_meters": round(total_dist_m, 2),
        "distance_km": round(total_dist_m / 1000.0, 2),
        "straight_line_dist_meters": round(straight_line_dist_m, 2),
        "circuity_factor": circuity,
        "travel_time_sec": round(total_time_sec, 1),
        "travel_time_min": round(total_time_sec / 60.0, 2),
        "num_segments": len(segments_info),
        "path_nodes": route_nodes,
        "route_geometry": route_geom,
        "segments_table": segments_info,
    }

    logger.info(
        f"Route found: {result['distance_km']} km, {result['travel_time_min']} mins, circuity {circuity}."
    )
    return result

