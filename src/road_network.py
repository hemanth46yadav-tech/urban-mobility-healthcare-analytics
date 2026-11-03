"""
Road network analysis module for Smart Yeshwanthpur GIS Analytics.
Computes road statistics, network topology, connectivity, centrality metrics,
and identifies structural bottleneck corridors.
"""

from typing import Any, Dict, Optional, Tuple

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from shapely.geometry import Point

from src.config import CRS_GEOGRAPHIC, CRS_PROJECTED
from src.utils import logger, timer


@timer
def calculate_road_statistics(
    roads_gdf: gpd.GeoDataFrame, study_area_sqkm: float = 19.63
) -> Dict[str, Any]:
    """
    Compute descriptive statistics for the road network.
    Includes segment counts, total lengths, median/mean lengths,
    distribution by classification, and density per square km.
    """
    if roads_gdf.empty:
        logger.warning("Empty roads GeoDataFrame supplied.")
        return {}

    # Ensure metric length is available
    if "length_meters" not in roads_gdf.columns:
        roads_proj = roads_gdf.to_crs(CRS_PROJECTED)
        lengths = roads_proj.geometry.length
    else:
        lengths = roads_gdf["length_meters"]

    total_segments = int(len(roads_gdf))
    total_length_m = float(lengths.sum())
    total_length_km = round(total_length_m / 1000.0, 2)
    avg_length_m = round(float(lengths.mean()), 2)
    median_length_m = round(float(lengths.median()), 2)
    std_length_m = round(float(lengths.std()), 2)
    min_length_m = round(float(lengths.min()), 2)
    max_length_m = round(float(lengths.max()), 2)

    # Road density: km of road per sq km of study area
    road_density_km_per_sqkm = round(total_length_km / max(study_area_sqkm, 0.01), 2)

    # Breakdown by category
    cat_col = "road_category" if "road_category" in roads_gdf.columns else "highway"
    category_counts = (
        roads_gdf[cat_col].value_counts().to_dict()
    )
    category_lengths_km = (
        roads_gdf.groupby(cat_col)["length_meters"]
        .sum()
        .apply(lambda x: round(x / 1000.0, 2))
        .to_dict()
    )

    stats = {
        "total_segments": total_segments,
        "total_length_km": total_length_km,
        "total_length_meters": round(total_length_m, 2),
        "avg_length_meters": avg_length_m,
        "median_length_meters": median_length_m,
        "std_length_meters": std_length_m,
        "min_length_meters": min_length_m,
        "max_length_meters": max_length_m,
        "study_area_sqkm": round(study_area_sqkm, 2),
        "road_density_km_per_sqkm": road_density_km_per_sqkm,
        "category_counts": category_counts,
        "category_lengths_km": category_lengths_km,
    }

    logger.info(
        f"Calculated road statistics: {total_segments} segments, {total_length_km} km total, {road_density_km_per_sqkm} km/km²."
    )
    return stats


@timer
def calculate_network_statistics(
    graph: nx.MultiDiGraph, study_area_sqkm: float = 19.63
) -> Dict[str, Any]:
    """
    Compute graph-theoretic topological statistics for the road network.
    Includes node counts, edge counts, intersection count, average node degree,
    connected components, and intersection density.
    """
    if graph is None or len(graph) == 0:
        logger.warning("Empty or null network graph supplied.")
        return {}

    num_nodes = graph.number_of_nodes()
    num_edges = graph.number_of_edges()

    # Convert to undirected graph for component analysis and degree calculation
    G_undir = graph.to_undirected()
    degrees = [d for _, d in G_undir.degree()]
    avg_degree = round(float(np.mean(degrees)), 2)

    # An intersection in street networks is typically a node with degree >= 3
    # (degree 1 = cul-de-sac/dead end, degree 2 = continuous curve or mid-segment link)
    intersections = [n for n, d in G_undir.degree() if d >= 3]
    num_intersections = len(intersections)
    dead_ends = [n for n, d in G_undir.degree() if d == 1]
    num_dead_ends = len(dead_ends)

    # Intersection density
    intersection_density = round(num_intersections / max(study_area_sqkm, 0.01), 2)

    # Connected components
    connected_components = list(nx.connected_components(G_undir))
    num_components = len(connected_components)
    largest_component_size = (
        len(max(connected_components, key=len)) if connected_components else 0
    )
    connectivity_ratio = round(largest_component_size / max(num_nodes, 1), 4)

    # Circuity / network density index
    stats = {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "num_intersections": num_intersections,
        "num_dead_ends": num_dead_ends,
        "avg_node_degree": avg_degree,
        "num_connected_components": num_components,
        "largest_component_nodes": largest_component_size,
        "connectivity_ratio": connectivity_ratio,
        "intersection_density_per_sqkm": intersection_density,
    }

    logger.info(
        f"Calculated network statistics: {num_nodes} nodes, {num_edges} edges, {num_intersections} intersections ({intersection_density}/km²)."
    )
    return stats


@timer
def calculate_centrality(
    graph: nx.MultiDiGraph,
    nodes_gdf: gpd.GeoDataFrame,
    roads_gdf: gpd.GeoDataFrame,
    sample_size: Optional[int] = 300,
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, Dict[str, Any]]:
    """
    Calculate degree centrality and betweenness centrality.
    Annotates both node and edge GeoDataFrames.

    NOTE: Betweenness centrality reflects structural topological routing bottlenecks
    and potential critical corridors. It does not represent actual live traffic volume.
    """
    logger.info("Computing network centrality metrics...")

    # Convert MultiDiGraph to simple Graph for centrality calculation
    G_simple = nx.Graph(graph)

    # 1. Degree Centrality
    deg_centrality = nx.degree_centrality(G_simple)

    # 2. Betweenness Centrality
    # If network is large, use k-sample approximation for interactive responsiveness
    num_nodes = len(G_simple)
    k_val = min(sample_size, num_nodes) if sample_size and num_nodes > sample_size else None

    logger.info(f"Calculating betweenness centrality (nodes={num_nodes}, k={k_val})...")
    bet_centrality = nx.betweenness_centrality(
        G_simple, k=k_val, weight="length", normalized=True, seed=42
    )

    # Assign to nodes GeoDataFrame
    nodes = nodes_gdf.copy()
    nodes["degree_centrality"] = nodes.index.map(deg_centrality).fillna(0.0).round(5)
    nodes["betweenness_centrality"] = (
        nodes.index.map(bet_centrality).fillna(0.0).round(5)
    )

    # Map betweenness to edges by taking the maximum betweenness of its endpoints
    roads = roads_gdf.copy()
    if isinstance(roads.index, pd.MultiIndex):
        # OSMnx edges typically have MultiIndex (u, v, key)
        u_nodes = roads.index.get_level_values(0)
        v_nodes = roads.index.get_level_values(1)
        u_bet = [bet_centrality.get(u, 0.0) for u in u_nodes]
        v_bet = [bet_centrality.get(v, 0.0) for v in v_nodes]
        roads["edge_betweenness"] = np.maximum(u_bet, v_bet).round(5)
    elif "u" in roads.columns and "v" in roads.columns:
        u_bet = roads["u"].map(bet_centrality).fillna(0.0)
        v_bet = roads["v"].map(bet_centrality).fillna(0.0)
        roads["edge_betweenness"] = np.maximum(u_bet, v_bet).round(5)
    else:
        roads["edge_betweenness"] = 0.0

    # Identify top structural bottlenecks (95th percentile betweenness)
    p95_edge_bet = np.percentile(roads["edge_betweenness"], 95)
    roads["is_bottleneck_corridor"] = roads["edge_betweenness"] >= p95_edge_bet

    top_intersections = nodes.sort_values(
        by="betweenness_centrality", ascending=False
    ).head(10)

    summary = {
        "max_degree_centrality": float(nodes["degree_centrality"].max()),
        "mean_degree_centrality": float(nodes["degree_centrality"].mean()),
        "max_betweenness_centrality": float(nodes["betweenness_centrality"].max()),
        "mean_betweenness_centrality": float(nodes["betweenness_centrality"].mean()),
        "bottleneck_threshold_p95": float(p95_edge_bet),
        "num_bottleneck_segments": int(roads["is_bottleneck_corridor"].sum()),
        "top_bottleneck_nodes": top_intersections.index.tolist(),
    }

    logger.info(
        f"Centrality completed: {summary['num_bottleneck_segments']} structural bottleneck segments identified."
    )
    return nodes, roads, summary

