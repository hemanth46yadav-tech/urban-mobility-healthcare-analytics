"""
Tests for road network analysis, statistics, and shortest-path routing.
"""

import geopandas as gpd
import networkx as nx
import pytest
from shapely.geometry import LineString, Point

from src.config import GRAPH_PROCESSED_GRAPHML, ROADS_PROCESSED_GPKG
from src.road_network import (
    calculate_network_statistics,
    calculate_road_statistics,
)
from src.route_analysis import (
    calculate_haversine_distance,
    find_nearest_node,
    find_shortest_route,
)


def test_calculate_haversine_distance():
    # Distance between two identical points should be 0
    d_zero = calculate_haversine_distance(13.0285, 77.5400, 13.0285, 77.5400)
    assert d_zero == 0.0

    # Distance between two points in Yeshwanthpur should be non-negative
    d = calculate_haversine_distance(13.0285, 77.5400, 13.0385, 77.5500)
    assert d > 0.0
    assert 1000 < d < 3000  # approximately ~1.5 km


def test_road_statistics_calculation():
    line1 = LineString([(77.54, 13.02), (77.55, 13.02)])
    line2 = LineString([(77.55, 13.02), (77.55, 13.03)])

    gdf = gpd.GeoDataFrame(
        {
            "road_category": ["Primary Arterial", "Secondary Collector"],
            "length_meters": [1000.0, 1200.0],
            "geometry": [line1, line2],
        },
        crs="EPSG:4326",
    )

    stats = calculate_road_statistics(gdf, study_area_sqkm=10.0)
    assert stats["total_segments"] == 2
    assert stats["total_length_km"] == 2.2
    assert stats["road_density_km_per_sqkm"] == 0.22
    assert stats["avg_length_meters"] == 1100.0
    assert stats["min_length_meters"] >= 0.0


def test_shortest_route_on_loaded_graph():
    # Check that the real graph exists
    assert GRAPH_PROCESSED_GRAPHML.exists()
    import osmnx as ox

    G = ox.load_graphml(GRAPH_PROCESSED_GRAPHML)
    assert len(G) > 0

    # Pick origin and destination near center
    orig = (13.0285, 77.5400)
    dest = (13.0350, 77.5450)

    res = find_shortest_route(G, orig, dest)
    assert res["success"] is True
    assert res["distance_meters"] > 0
    assert res["distance_km"] > 0
    assert res["circuity_factor"] >= 1.0  # network distance >= Euclidean
    assert len(res["path_nodes"]) >= 2
    assert res["route_geometry"] is not None
    assert res["travel_time_min"] > 0

