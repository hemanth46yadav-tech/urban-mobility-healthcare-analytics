"""
Tests for healthcare accessibility and facility search.
"""

import geopandas as gpd
import pytest
from shapely.geometry import Point

from src.config import HEALTHCARE_PROCESSED_GEOJSON
from src.healthcare import (
    classify_distance,
    find_nearest_healthcare_facility,
    get_facility_summary,
)


def test_classify_distance():
    label_high, color_high = classify_distance(500)
    assert "High" in label_high
    assert color_high == "#2ecc71"

    label_mod, _ = classify_distance(1500)
    assert "Moderate" in label_mod

    label_low, _ = classify_distance(2500)
    assert "Low" in label_low

    label_vlow, color_vlow = classify_distance(3500)
    assert "Very Low" in label_vlow
    assert color_vlow == "#e74c3c"


def test_find_nearest_facility():
    assert HEALTHCARE_PROCESSED_GEOJSON.exists()
    gdf = gpd.read_file(HEALTHCARE_PROCESSED_GEOJSON)
    assert not gdf.empty

    origin = (13.0285, 77.5400)
    res = find_nearest_healthcare_facility(
        origin, gdf, graph=None, facility_type_filter="All"
    )

    assert res["found"] is True
    assert res["facility_name"] is not None
    assert res["straight_line_distance_m"] >= 0.0
    assert res["accessibility_band"] in [
        "High Accessibility (< 1 km)",
        "Moderate Accessibility (1-2 km)",
        "Low Accessibility (2-3 km)",
        "Very Low Accessibility (> 3 km)",
    ]


def test_facility_summary():
    assert HEALTHCARE_PROCESSED_GEOJSON.exists()
    gdf = gpd.read_file(HEALTHCARE_PROCESSED_GEOJSON)

    summary = get_facility_summary(gdf)
    assert summary["total_facilities"] == len(gdf)
    assert summary["num_hospitals"] >= 0
    assert summary["num_clinics"] >= 0
    assert isinstance(summary["breakdown"], dict)
