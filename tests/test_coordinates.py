"""
Tests for coordinate and geometry validation utilities.
"""

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import LineString, Point, Polygon

from src.utils import validate_coordinates, validate_geodataframe


def test_valid_coordinates():
    assert validate_coordinates(13.0285, 77.5400) is True
    assert validate_coordinates(0.0, 0.0) is True
    assert validate_coordinates(-45.0, 120.0) is True


def test_invalid_coordinates():
    assert validate_coordinates(95.0, 77.5400) is False  # Lat > 90
    assert validate_coordinates(-100.0, 77.5400) is False  # Lat < -90
    assert validate_coordinates(13.0285, 195.0) is False  # Lon > 180
    assert validate_coordinates(np.nan, 77.54) is False
    assert validate_coordinates(13.0285, None) is False


def test_validate_geodataframe_removes_invalid():
    # Construct GeoDataFrame with valid, invalid, and empty geometries
    p1 = Point(77.54, 13.02)
    p2 = Point()  # Empty point
    bowtie = Polygon([(0, 0), (0, 2), (2, 0), (2, 2), (0, 0)])  # Self-intersecting

    gdf = gpd.GeoDataFrame(
        {"id": [1, 2, 3], "geometry": [p1, p2, bowtie]}, crs="EPSG:4326"
    )

    cleaned = validate_geodataframe(gdf, fix_invalid=True)
    assert len(cleaned) == 2  # p1 and repaired bowtie
    assert all(geom.is_valid for geom in cleaned.geometry)
    assert not any(geom.is_empty for geom in cleaned.geometry)
