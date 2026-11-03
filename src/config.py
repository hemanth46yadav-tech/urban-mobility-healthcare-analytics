"""
Configuration and constants for Smart Yeshwanthpur GIS Analytics.
"""

import os
from pathlib import Path

# Ensure Matplotlib config dir doesn't warn
_temp_mpl = Path.home() / "AppData" / "Local" / "Temp" / "matplotlib_cache"
_temp_mpl.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(_temp_mpl)

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

OUTPUTS_DIR = BASE_DIR / "outputs"
MAPS_DIR = OUTPUTS_DIR / "maps"
CHARTS_DIR = OUTPUTS_DIR / "charts"
MODELS_DIR = OUTPUTS_DIR / "models"

ASSETS_DIR = BASE_DIR / "assets"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
TESTS_DIR = BASE_DIR / "tests"

# Ensure all directories exist
for directory in [
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    EXTERNAL_DATA_DIR,
    MAPS_DIR,
    CHARTS_DIR,
    MODELS_DIR,
    ASSETS_DIR,
    NOTEBOOKS_DIR,
    TESTS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Study Area Parameters (Yeshwanthpur, Bengaluru)
STUDY_AREA_NAME = "Yeshwanthpur, Bengaluru"
CENTER_LAT = 13.0285
CENTER_LON = 77.5400
STUDY_RADIUS_METERS = 2500  # 2.5 km circular study area

# Coordinate Reference Systems
CRS_GEOGRAPHIC = "EPSG:4326"  # WGS84 for GeoJSON / Web Maps / Folium
CRS_PROJECTED = "EPSG:32643"  # UTM Zone 43N for accurate metric measurements

# Primary File Paths
ROADS_RAW_GPKG = RAW_DATA_DIR / "roads.gpkg"
NODES_RAW_GPKG = RAW_DATA_DIR / "nodes.gpkg"
GRAPH_RAW_GRAPHML = RAW_DATA_DIR / "road_network.graphml"

ROADS_PROCESSED_GPKG = PROCESSED_DATA_DIR / "roads.gpkg"
NODES_PROCESSED_GPKG = PROCESSED_DATA_DIR / "nodes.gpkg"
GRAPH_PROCESSED_GRAPHML = PROCESSED_DATA_DIR / "road_network.graphml"

HEALTHCARE_RAW_GEOJSON = RAW_DATA_DIR / "healthcare_facilities_raw.geojson"
HEALTHCARE_PROCESSED_GEOJSON = PROCESSED_DATA_DIR / "healthcare_facilities.geojson"
HEALTHCARE_PROCESSED_GPKG = PROCESSED_DATA_DIR / "healthcare_facilities.gpkg"

STUDY_BOUNDARY_GEOJSON = PROCESSED_DATA_DIR / "study_boundary.geojson"
SPATIAL_GRID_GEOJSON = PROCESSED_DATA_DIR / "spatial_grid.geojson"
SPATIAL_GRID_GPKG = PROCESSED_DATA_DIR / "spatial_grid.gpkg"

KMEANS_MODEL_FILE = MODELS_DIR / "kmeans_model.joblib"
SCALER_FILE = MODELS_DIR / "scaler.joblib"
METRICS_JSON_FILE = OUTPUTS_DIR / "summary_metrics.json"
CLUSTER_METRICS_CSV = OUTPUTS_DIR / "cluster_assignments.csv"

# Road Hierarchy Classifications
ROAD_HIERARCHY = {
    "motorway": "Highway / Expressway",
    "motorway_link": "Highway / Expressway",
    "trunk": "Major Arterial",
    "trunk_link": "Major Arterial",
    "primary": "Primary Arterial",
    "primary_link": "Primary Arterial",
    "secondary": "Secondary Collector",
    "secondary_link": "Secondary Collector",
    "tertiary": "Tertiary Road",
    "tertiary_link": "Tertiary Road",
    "residential": "Residential Street",
    "living_street": "Living Street",
    "unclassified": "Local Road",
    "service": "Service Road",
}

# Healthcare Facility Tags
HEALTHCARE_OSM_TAGS = {
    "amenity": [
        "hospital",
        "clinic",
        "doctors",
        "health_post",
        "pharmacy",
    ]
}

# Accessibility Classification Thresholds (in meters)
ACCESSIBILITY_BANDS = [
    (0, 1000, "High Accessibility (< 1 km)", "#2ecc71"),
    (1000, 2000, "Moderate Accessibility (1-2 km)", "#f39c12"),
    (2000, 3000, "Low Accessibility (2-3 km)", "#e67e22"),
    (3000, float("inf"), "Very Low Accessibility (> 3 km)", "#e74c3c"),
]

# Spatial Grid Resolution (meters)
GRID_RESOLUTION_METERS = 250  # 250m x 250m cells

# Average Vehicle Speeds for Travel Time Estimation (km/h)
# Defensible urban driving speed estimates for Bengaluru urban roads
SPEED_ASSUMPTIONS_KMH = {
    "trunk": 35.0,
    "primary": 30.0,
    "secondary": 25.0,
    "tertiary": 20.0,
    "residential": 15.0,
    "service": 10.0,
    "default": 20.0,
}

