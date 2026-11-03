"""
Utility functions for Smart Yeshwanthpur GIS Analytics.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon
from shapely.validation import make_valid

# Configure logger
logger = logging.getLogger("smart_yeshwanthpur")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def timer(func: Callable) -> Callable:
    """Decorator to log function execution time."""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__}...")
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        logger.info(f"Completed {func.__name__} in {duration:.2f} seconds.")
        return result

    return wrapper


def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate that latitude and longitude fall within reasonable geographic limits."""
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return False
    if np.isnan(lat) or np.isnan(lon):
        return False
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def validate_geodataframe(
    gdf: gpd.GeoDataFrame, fix_invalid: bool = True
) -> gpd.GeoDataFrame:
    """
    Validate geometries in a GeoDataFrame, removing empty or null geometries,
    and optionally repairing invalid ones.
    """
    if gdf.empty:
        logger.warning("GeoDataFrame is empty.")
        return gdf

    initial_len = len(gdf)
    # Filter empty or null
    gdf = gdf[gdf.geometry.notnull() & (~gdf.geometry.is_empty)].copy()

    if fix_invalid:
        invalid_mask = ~gdf.geometry.is_valid
        if invalid_mask.any():
            logger.info(f"Repairing {invalid_mask.sum()} invalid geometries.")
            gdf.loc[invalid_mask, "geometry"] = gdf.loc[
                invalid_mask, "geometry"
            ].apply(make_valid)

    # Re-check validity and drop anything still corrupt
    gdf = gdf[gdf.geometry.is_valid].copy()
    cleaned_len = len(gdf)

    if cleaned_len < initial_len:
        logger.info(
            f"Validation retained {cleaned_len}/{initial_len} features ({initial_len - cleaned_len} dropped)."
        )

    return gdf


def safe_save_geodataframe(
    gdf: gpd.GeoDataFrame,
    filepath: Path,
    layer_name: Optional[str] = None,
    driver: Optional[str] = None,
) -> bool:
    """
    Safely save a GeoDataFrame to disk, creating parent folders if needed.
    Supports GeoPackage (.gpkg) and GeoJSON (.geojson).
    """
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if filepath.suffix.lower() == ".gpkg":
            layer = layer_name or filepath.stem
            gdf.to_file(filepath, layer=layer, driver="GPKG")
        elif filepath.suffix.lower() == ".geojson":
            gdf.to_file(filepath, driver="GeoJSON")
        elif filepath.suffix.lower() == ".csv":
            # If exported to CSV, keep geometry as WKT
            df = gdf.copy()
            df["geometry_wkt"] = df.geometry.apply(lambda g: g.wkt if g else "")
            df.drop(columns=["geometry"], inplace=True)
            df.to_csv(filepath, index=False)
        else:
            gdf.to_file(filepath, driver=driver)

        logger.info(f"Successfully saved {len(gdf)} records to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save GeoDataFrame to {filepath}: {e}")
        return False


def load_geodataframe(
    filepath: Path, layer: Optional[str] = None
) -> gpd.GeoDataFrame:
    """Safely load a GeoDataFrame from disk."""
    filepath = Path(filepath)
    if not filepath.exists():
        logger.warning(f"File not found: {filepath}")
        return gpd.GeoDataFrame()

    try:
        if filepath.suffix.lower() == ".gpkg" and layer:
            gdf = gpd.read_file(filepath, layer=layer)
        else:
            gdf = gpd.read_file(filepath)
        return gdf
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return gpd.GeoDataFrame()


class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for NumPy / Pandas / Shapely objects."""

    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (pd.Timestamp, pd.DatetimeIndex)):
            return str(obj)
        elif hasattr(obj, "wkt"):
            return obj.wkt
        return super().default(obj)


def save_json(data: Dict[str, Any], filepath: Path) -> bool:
    """Safely serialize dictionary data to JSON."""
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, cls=NumpyJSONEncoder)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON to {filepath}: {e}")
        return False


def load_json(filepath: Path) -> Dict[str, Any]:
    """Safely load JSON data from disk."""
    filepath = Path(filepath)
    if not filepath.exists():
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON from {filepath}: {e}")
        return {}

