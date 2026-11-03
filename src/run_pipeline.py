"""
End-to-end data pipeline runner for Smart Yeshwanthpur GIS Analytics.
Executes data collection, preprocessing, road analysis, accessibility calculations,
and machine learning neighbourhood clustering.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.accessibility import (
    compute_grid_accessibility,
    get_accessibility_metrics_summary,
)
from src.clustering import run_neighborhood_clustering
from src.config import (
    CENTER_LAT,
    CENTER_LON,
    METRICS_JSON_FILE,
    OUTPUTS_DIR,
    STUDY_RADIUS_METERS,
)
from src.data_collection import (
    create_study_boundary,
    fetch_healthcare_facilities,
    fetch_road_network,
)
from src.healthcare import get_facility_summary, identify_deficit_areas
from src.preprocessing import (
    preprocess_healthcare_facilities,
    preprocess_road_network,
)
from src.road_network import (
    calculate_centrality,
    calculate_network_statistics,
    calculate_road_statistics,
)
from src.spatial_analysis import (
    generate_metric_spatial_grid,
    overlay_and_aggregate_grid,
)
from src.utils import logger, save_json, timer


@timer
def run_full_pipeline(force_download: bool = False):
    """Execute complete GIS analysis and machine learning pipeline."""
    logger.info("=== Starting Smart Yeshwanthpur GIS Analytics Pipeline ===")

    # 1. Create study area boundary
    logger.info("Step 1: Generating study area boundary...")
    boundary_gdf = create_study_boundary(
        lat=CENTER_LAT, lon=CENTER_LON, radius_m=STUDY_RADIUS_METERS
    )
    study_area_sqkm = float(boundary_gdf["area_sqkm"].iloc[0])

    # 2. Acquire road network
    logger.info("Step 2: Acquiring road network from OpenStreetMap...")
    graph, raw_nodes, raw_roads = fetch_road_network(
        lat=CENTER_LAT,
        lon=CENTER_LON,
        radius_m=STUDY_RADIUS_METERS,
        force_download=force_download,
    )

    # 3. Acquire healthcare facilities
    logger.info("Step 3: Acquiring healthcare facilities from OpenStreetMap...")
    raw_healthcare = fetch_healthcare_facilities(
        lat=CENTER_LAT,
        lon=CENTER_LON,
        radius_m=STUDY_RADIUS_METERS,
        force_download=force_download,
    )

    # 4. Preprocess road network and healthcare data
    logger.info("Step 4: Preprocessing road network and healthcare data...")
    clean_roads, clean_nodes, enriched_graph = preprocess_road_network(
        raw_roads, raw_nodes, graph
    )
    clean_healthcare = preprocess_healthcare_facilities(raw_healthcare)

    # 5. Road network statistics & centrality
    logger.info("Step 5: Analyzing road network topology and centrality...")
    road_stats = calculate_road_statistics(clean_roads, study_area_sqkm)
    network_stats = calculate_network_statistics(enriched_graph, study_area_sqkm)
    nodes_central, roads_central, centrality_stats = calculate_centrality(
        enriched_graph, clean_nodes, clean_roads
    )

    # 6. Healthcare facility summary
    logger.info("Step 6: Profiling healthcare facilities...")
    healthcare_stats = get_facility_summary(clean_healthcare)

    # 7. Spatial grid generation and overlay
    logger.info("Step 7: Generating spatial grid and aggregating features...")
    grid_gdf = generate_metric_spatial_grid(boundary_gdf, cell_size_m=250)
    aggregated_grid = overlay_and_aggregate_grid(
        grid_gdf, roads_central, nodes_central, clean_healthcare
    )

    # 8. Healthcare accessibility classification
    logger.info("Step 8: Computing healthcare accessibility tiers and scores...")
    access_grid = compute_grid_accessibility(
        aggregated_grid, graph=enriched_graph
    )
    access_stats = get_accessibility_metrics_summary(access_grid)

    # Deficit areas
    deficit_cells = identify_deficit_areas(access_grid, top_k=5)
    deficit_list = (
        deficit_cells[
            ["grid_id", "nearest_hosp_dist_m", "road_density_km_sqkm", "centroid_lat", "centroid_lon"]
        ].to_dict(orient="records")
        if not deficit_cells.empty
        else []
    )

    # 9. Machine learning neighbourhood clustering
    logger.info("Step 9: Running unsupervised neighbourhood clustering...")
    clustered_grid, ml_results = run_neighborhood_clustering(access_grid)

    # 10. Compile comprehensive metrics summary
    logger.info("Step 10: Saving summary metrics and artifacts...")
    summary_data = {
        "study_area": {
            "name": "Yeshwanthpur, Bengaluru",
            "center_lat": CENTER_LAT,
            "center_lon": CENTER_LON,
            "radius_meters": STUDY_RADIUS_METERS,
            "area_sqkm": study_area_sqkm,
        },
        "road_statistics": road_stats,
        "network_statistics": network_stats,
        "centrality_statistics": centrality_stats,
        "healthcare_statistics": healthcare_stats,
        "accessibility_statistics": access_stats,
        "deficit_priority_zones": deficit_list,
        "ml_clustering": ml_results,
    }

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    save_json(summary_data, METRICS_JSON_FILE)

    logger.info("=== Pipeline Completed Successfully! ===")
    return summary_data


if __name__ == "__main__":
    run_full_pipeline()
