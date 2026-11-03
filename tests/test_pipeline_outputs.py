"""
Tests to verify generated GIS datasets and outputs integrity.
"""

from pathlib import Path
import geopandas as gpd
import pytest

from src.config import (
    CLUSTER_METRICS_CSV,
    HEALTHCARE_PROCESSED_GEOJSON,
    HEALTHCARE_PROCESSED_GPKG,
    KMEANS_MODEL_FILE,
    METRICS_JSON_FILE,
    NODES_PROCESSED_GPKG,
    ROADS_PROCESSED_GPKG,
    SCALER_FILE,
    SPATIAL_GRID_GEOJSON,
    SPATIAL_GRID_GPKG,
    STUDY_BOUNDARY_GEOJSON,
)
from src.utils import load_json


def test_processed_geopackage_files():
    # Verify roads.gpkg
    assert ROADS_PROCESSED_GPKG.exists()
    roads = gpd.read_file(ROADS_PROCESSED_GPKG)
    assert len(roads) > 1000
    assert "road_category" in roads.columns
    assert "length_meters" in roads.columns
    assert all(roads["length_meters"] >= 0)

    # Verify nodes.gpkg
    assert NODES_PROCESSED_GPKG.exists()
    nodes = gpd.read_file(NODES_PROCESSED_GPKG)
    assert len(nodes) > 500

    # Verify healthcare_facilities.gpkg
    assert HEALTHCARE_PROCESSED_GPKG.exists()
    hc = gpd.read_file(HEALTHCARE_PROCESSED_GPKG)
    assert len(hc) > 10
    assert "facility_name" in hc.columns
    assert "facility_type" in hc.columns

    # Verify spatial_grid.gpkg
    assert SPATIAL_GRID_GPKG.exists()
    grid = gpd.read_file(SPATIAL_GRID_GPKG)
    assert len(grid) > 50
    assert "accessibility_band" in grid.columns
    assert "nearest_hosp_dist_m" in grid.columns


def test_processed_geojson_files():
    assert STUDY_BOUNDARY_GEOJSON.exists()
    b = gpd.read_file(STUDY_BOUNDARY_GEOJSON)
    assert len(b) == 1

    assert HEALTHCARE_PROCESSED_GEOJSON.exists()
    h = gpd.read_file(HEALTHCARE_PROCESSED_GEOJSON)
    assert len(h) > 10

    assert SPATIAL_GRID_GEOJSON.exists()
    g = gpd.read_file(SPATIAL_GRID_GEOJSON)
    assert len(g) > 50


def test_metrics_json_structure():
    assert METRICS_JSON_FILE.exists()
    data = load_json(METRICS_JSON_FILE)

    assert "study_area" in data
    assert "road_statistics" in data
    assert "network_statistics" in data
    assert "centrality_statistics" in data
    assert "healthcare_statistics" in data
    assert "accessibility_statistics" in data
    assert "ml_clustering" in data

    assert data["road_statistics"]["total_segments"] > 1000
    assert data["healthcare_statistics"]["total_facilities"] > 10

