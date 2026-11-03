"""
Spatial analysis module for Smart Yeshwanthpur GIS Analytics.
Implements metric spatial grid generation, buffer analysis, overlay analysis,
spatial joins, and Euclidean vs network accessibility comparison.
"""

from typing import Any, Dict, List, Optional, Tuple

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

from src.config import (
    CRS_GEOGRAPHIC,
    CRS_PROJECTED,
    GRID_RESOLUTION_METERS,
    SPATIAL_GRID_GEOJSON,
    SPATIAL_GRID_GPKG,
)
from src.utils import logger, safe_save_geodataframe, timer, validate_geodataframe


@timer
def generate_metric_spatial_grid(
    boundary_gdf: gpd.GeoDataFrame,
    cell_size_m: float = GRID_RESOLUTION_METERS,
) -> gpd.GeoDataFrame:
    """
    Generate a uniform rectangular spatial grid over the study boundary
    in projected coordinate space (EPSG:32643) and clip to the study area boundary.
    Returns:
        GeoDataFrame with grid polygons, cell IDs, and centroid coordinates.
    """
    logger.info(
        f"Generating spatial grid at {cell_size_m}m resolution in {CRS_PROJECTED}..."
    )

    # Project boundary to UTM
    boundary_proj = boundary_gdf.to_crs(CRS_PROJECTED)
    total_bounds = boundary_proj.total_bounds  # (minx, miny, maxx, maxy)
    minx, miny, maxx, maxy = total_bounds

    # Create grid cells
    x_coords = np.arange(minx, maxx + cell_size_m, cell_size_m)
    y_coords = np.arange(miny, maxy + cell_size_m, cell_size_m)

    cells = []
    grid_ids = []
    idx = 0

    study_geom = boundary_proj.geometry.iloc[0]

    for x in x_coords:
        for y in y_coords:
            cell_poly = box(x, y, x + cell_size_m, y + cell_size_m)
            # Only retain cells intersecting the study boundary
            if cell_poly.intersects(study_geom):
                clipped_geom = cell_poly.intersection(study_geom)
                if not clipped_geom.is_empty and clipped_geom.area > 100.0:
                    cells.append(clipped_geom)
                    grid_ids.append(f"GRID_{idx:04d}")
                    idx += 1

    gdf_grid_proj = gpd.GeoDataFrame(
        {"grid_id": grid_ids, "geometry": cells}, crs=CRS_PROJECTED
    )

    # Compute cell area and centroids
    gdf_grid_proj["cell_area_sqkm"] = (gdf_grid_proj.geometry.area / 1e6).round(4)
    centroids = gdf_grid_proj.geometry.centroid
    gdf_grid_proj["centroid_x_m"] = centroids.x
    gdf_grid_proj["centroid_y_m"] = centroids.y

    # Transform centroids to WGS84 for convenient web mapping
    centroids_gdf = gpd.GeoDataFrame(geometry=centroids, crs=CRS_PROJECTED).to_crs(
        CRS_GEOGRAPHIC
    )
    gdf_grid_proj["centroid_lon"] = centroids_gdf.geometry.x.round(6)
    gdf_grid_proj["centroid_lat"] = centroids_gdf.geometry.y.round(6)

    # Reproject grid polygons to EPSG:4326 for GIS visualization
    gdf_grid = gdf_grid_proj.to_crs(CRS_GEOGRAPHIC)

    logger.info(
        f"Spatial grid generated: {len(gdf_grid)} cells covering study area."
    )
    return gdf_grid


@timer
def create_facility_buffers(
    healthcare_gdf: gpd.GeoDataFrame,
    buffer_radii_m: List[float] = [500, 1000, 2000, 3000],
    facility_type_filter: Optional[str] = "Hospital",
) -> gpd.GeoDataFrame:
    """
    Generate Euclidean circular service buffers around healthcare facilities in projected CRS.
    Allows comparison of Euclidean straight-line coverage against network accessibility.
    """
    logger.info(
        f"Generating facility service buffers for radii: {buffer_radii_m}m..."
    )

    facilities = healthcare_gdf.copy()
    if facility_type_filter and "facility_type" in facilities.columns:
        if facility_type_filter != "All":
            facilities = facilities[
                facilities["facility_type"] == facility_type_filter
            ]

    if facilities.empty:
        return gpd.GeoDataFrame(
            columns=["buffer_radius_m", "geometry"], crs=CRS_GEOGRAPHIC
        )

    # Project to metric CRS
    fac_proj = facilities.to_crs(CRS_PROJECTED)

    buffer_records = []
    for radius in buffer_radii_m:
        # Buffer each facility and create union
        buffered_geoms = [geom.buffer(radius) for geom in fac_proj.geometry]
        union_geom = unary_union(buffered_geoms)
        area_sqkm = round(union_geom.area / 1e6, 2)
        buffer_records.append(
            {
                "buffer_radius_m": radius,
                "radius_km": radius / 1000.0,
                "service_area_sqkm": area_sqkm,
                "geometry": union_geom,
            }
        )

    gdf_buffers_proj = gpd.GeoDataFrame(buffer_records, crs=CRS_PROJECTED)
    gdf_buffers = gdf_buffers_proj.to_crs(CRS_GEOGRAPHIC)
    return gdf_buffers


@timer
def overlay_and_aggregate_grid(
    grid_gdf: gpd.GeoDataFrame,
    roads_gdf: gpd.GeoDataFrame,
    nodes_gdf: gpd.GeoDataFrame,
    healthcare_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Perform spatial aggregation across the spatial grid cells:
    - Counts healthcare facilities per cell
    - Counts hospitals and clinics per cell
    - Calculates road length and road density (km/km²) per cell
    - Counts intersections (degree >= 3) and intersection density per cell
    """
    logger.info("Executing spatial overlays and grid aggregation...")

    grid = grid_gdf.copy()
    grid_proj = grid.to_crs(CRS_PROJECTED)

    roads_proj = roads_gdf.to_crs(CRS_PROJECTED)
    nodes_proj = nodes_gdf.to_crs(CRS_PROJECTED)
    fac_proj = healthcare_gdf.to_crs(CRS_PROJECTED)

    # 1. Healthcare facility counts per cell
    fac_counts = []
    hosp_counts = []
    clinic_counts = []

    hospitals_proj = (
        fac_proj[fac_proj["facility_type"] == "Hospital"]
        if "facility_type" in fac_proj.columns
        else fac_proj
    )
    clinics_proj = (
        fac_proj[
            fac_proj["facility_type"].isin(["Clinic", "Doctors / Clinic"])
        ]
        if "facility_type" in fac_proj.columns
        else fac_proj
    )

    # Use spatial join for fast point-in-polygon counting
    fac_join = gpd.sjoin(
        fac_proj, grid_proj[["grid_id", "geometry"]], how="inner", predicate="within"
    )
    total_by_cell = fac_join["grid_id"].value_counts().to_dict()

    hosp_join = (
        gpd.sjoin(
            hospitals_proj,
            grid_proj[["grid_id", "geometry"]],
            how="inner",
            predicate="within",
        )
        if not hospitals_proj.empty
        else gpd.GeoDataFrame()
    )
    hosp_by_cell = (
        hosp_join["grid_id"].value_counts().to_dict()
        if not hosp_join.empty
        else {}
    )

    clinic_join = (
        gpd.sjoin(
            clinics_proj,
            grid_proj[["grid_id", "geometry"]],
            how="inner",
            predicate="within",
        )
        if not clinics_proj.empty
        else gpd.GeoDataFrame()
    )
    clinic_by_cell = (
        clinic_join["grid_id"].value_counts().to_dict()
        if not clinic_join.empty
        else {}
    )

    grid_proj["total_healthcare_count"] = (
        grid_proj["grid_id"].map(total_by_cell).fillna(0).astype(int)
    )
    grid_proj["hospital_count"] = (
        grid_proj["grid_id"].map(hosp_by_cell).fillna(0).astype(int)
    )
    grid_proj["clinic_count"] = (
        grid_proj["grid_id"].map(clinic_by_cell).fillna(0).astype(int)
    )

    # 2. Intersections per cell (nodes with degree >= 3)
    if "degree" in nodes_proj.columns:
        intersections_proj = nodes_proj[nodes_proj["degree"] >= 3]
    else:
        intersections_proj = nodes_proj

    node_join = gpd.sjoin(
        intersections_proj,
        grid_proj[["grid_id", "geometry"]],
        how="inner",
        predicate="within",
    )
    nodes_by_cell = node_join["grid_id"].value_counts().to_dict()
    grid_proj["intersection_count"] = (
        grid_proj["grid_id"].map(nodes_by_cell).fillna(0).astype(int)
    )

    # Intersection density per sq km
    grid_proj["intersection_density_per_sqkm"] = (
        grid_proj["intersection_count"] / grid_proj["cell_area_sqkm"]
    ).round(2)

    # 3. Road length and density per cell via spatial overlay
    road_lengths_by_cell = {}
    try:
        # Spatial overlay intersection between road lines and grid cells
        road_overlay = gpd.overlay(
            roads_proj[["road_category", "geometry"]],
            grid_proj[["grid_id", "geometry"]],
            how="intersection",
        )
        road_overlay["sub_length_m"] = road_overlay.geometry.length
        road_length_sums = road_overlay.groupby("grid_id")["sub_length_m"].sum()
        road_lengths_by_cell = road_length_sums.to_dict()
    except Exception as e:
        logger.warning(
            f"Road overlay error ({e}). Using spatial join fallback..."
        )
        rj = gpd.sjoin(
            roads_proj,
            grid_proj[["grid_id", "geometry"]],
            how="inner",
            predicate="intersects",
        )
        road_lengths_by_cell = (
            rj.groupby("grid_id")["length_meters"].sum().to_dict()
        )

    grid_proj["road_length_meters"] = (
        grid_proj["grid_id"].map(road_lengths_by_cell).fillna(0.0).round(1)
    )
    grid_proj["road_density_km_sqkm"] = (
        (grid_proj["road_length_meters"] / 1000.0) / grid_proj["cell_area_sqkm"]
    ).round(2)

    # 4. Nearest hospital distance from cell centroid
    if not hospitals_proj.empty:
        hosp_coords = np.column_stack(
            [hospitals_proj.geometry.x, hospitals_proj.geometry.y]
        )
        centroid_coords = np.column_stack(
            [grid_proj["centroid_x_m"], grid_proj["centroid_y_m"]]
        )

        nearest_dists = []
        for c_pt in centroid_coords:
            dist = np.min(np.linalg.norm(hosp_coords - c_pt, axis=1))
            nearest_dists.append(round(float(dist), 1))
        grid_proj["nearest_hosp_dist_m"] = nearest_dists
    else:
        grid_proj["nearest_hosp_dist_m"] = 9999.0

    grid_proj["nearest_hosp_dist_km"] = (
        grid_proj["nearest_hosp_dist_m"] / 1000.0
    ).round(2)

    # Reproject back to WGS84 for GeoJSON & mapping
    grid_final = grid_proj.to_crs(CRS_GEOGRAPHIC)
    logger.info("Grid spatial aggregation successfully completed.")
    return grid_final

