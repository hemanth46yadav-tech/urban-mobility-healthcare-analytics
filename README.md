# SMART YESHWANTHPUR — GIS TRAFFIC & HEALTHCARE ACCESSIBILITY ANALYTICS

An end-to-end spatial data science, network topology, and multi-tier healthcare accessibility analytics platform engineered for **Yeshwanthpur, Bengaluru, Karnataka, India**.

---

## 📌 Project Executive Summary

This platform integrates OpenStreetMap drivable network graphs, verified healthcare facility infrastructure, metric spatial grid models, and unsupervised machine learning clustering into an interactive, multi-page **Streamlit & Folium GIS dashboard**.

### Study Area Parameters
- **Location:** Yeshwanthpur, BBMP North Zone, Bengaluru, Karnataka, India
- **Reference Coordinates:** Latitude `13.0285° N`, Longitude `77.5400° E`
- **Analytical Study Buffer:** 2.5 km metric radius (~19.63 km²)
- **Projected CRS:** `EPSG:32643` (UTM Zone 43N — metric distance and area precision)
- **Geographic CRS:** `EPSG:4326` (WGS84 — web maps, Folium, GeoJSON interchange)

---

## 🏗️ System Architecture & Folder Structure

```
smart-yeshwanthpur-gis/
│
├── app/                                # Streamlit Multi-Page Web Application
│   ├── app.py                          # Primary application entrypoint & overview
│   ├── shared.py                       # Reusable UI styles, metric cards & cached loaders
│   └── pages/
│       ├── 01_Overview.py              # Study area geography & summary metrics
│       ├── 02_Road_Analysis.py         # Street hierarchy, density & centrality bottlenecks
│       ├── 03_Route_Analysis.py        # Dijkstra shortest paths, travel times & circuity
│       ├── 04_Healthcare_Analysis.py   # Facility directory, category mix & hospital buffers
│       ├── 05_Accessibility_Analysis.py# Spatial grid choropleth & nearest hospital finder
│       ├── 06_Machine_Learning.py      # K-Means clustering, Elbow, Silhouette & 2D PCA
│       └── 07_Insights.py              # Dynamically computed urban planning observations
│
├── src/                                # Core Analytical & Spatial Engines
│   ├── __init__.py
│   ├── config.py                       # Global paths, CRS, parameters & road hierarchy
│   ├── utils.py                        # Logging, validators, GeoDataFrame savers & timers
│   ├── data_collection.py              # OSMnx network & amenity fetcher with caching & retry
│   ├── preprocessing.py                # Geometry validation, deduplication & classification
│   ├── road_network.py                 # Topology, intersection density & betweenness centrality
│   ├── route_analysis.py               # NetworkX shortest routes, haversine & circuity
│   ├── healthcare.py                   # Facility profiling & nearest neighbor query
│   ├── spatial_analysis.py             # Metric grid generator (250m) & spatial overlays
│   ├── accessibility.py                # Multi-tier accessibility bands & population weighting
│   ├── clustering.py                   # Scikit-learn K-Means, Elbow, Silhouette & PCA pipeline
│   ├── visualizations.py               # Folium map generators & Plotly chart builders
│   └── run_pipeline.py                 # End-to-end pipeline execution orchestrator
│
├── data/
│   ├── raw/                            # Immutable raw OpenStreetMap downloads
│   │   ├── roads.gpkg
│   │   ├── nodes.gpkg
│   │   ├── road_network.graphml
│   │   └── healthcare_facilities_raw.geojson
│   └── processed/                      # Cleaned, standardized QGIS-compatible GIS layers
│       ├── roads.gpkg                  # Drivable road segments (15,798 features)
│       ├── nodes.gpkg                  # Junction nodes (5,924 features)
│       ├── road_network.graphml        # NetworkX drivable multigraph
│       ├── healthcare_facilities.geojson# Cleaned healthcare facilities (84 features)
│       ├── healthcare_facilities.gpkg  # QGIS GeoPackage layer
│       ├── study_boundary.geojson      # 2.5 km study boundary polygon
│       ├── spatial_grid.geojson        # 250m × 250m metric grid (344 cells)
│       └── spatial_grid.gpkg           # QGIS GeoPackage spatial grid
│
├── outputs/
│   ├── models/                         # Serialized Machine Learning artifacts
│   │   ├── kmeans_model.joblib         # Trained K-Means estimator
│   │   ├── scaler.joblib               # StandardScaler feature normalizer
│   │   └── clustering_results.json     # Silhouette, inertia & interpretations
│   ├── cluster_assignments.csv         # Grid-level cluster assignments & PCA coordinates
│   └── summary_metrics.json            # Consolidated analytical metrics
│
├── notebooks/
│   └── exploratory_analysis.ipynb      # Interactive Jupyter exploratory notebook
│
├── tests/                              # Automated Pytest Suite
│   ├── conftest.py
│   ├── test_coordinates.py             # Coordinate & geometry validation tests
│   ├── test_road_network.py            # Road statistics, haversine & routing tests
│   ├── test_healthcare.py              # Facility classification & nearest query tests
│   ├── test_clustering.py              # Machine learning pipeline tests
│   └── test_pipeline_outputs.py        # Output files integrity & schema verification
│
├── requirements.txt                    # Project dependencies
├── .gitignore
└── README.md
```

---

## ⚡ Key Analytical Findings (Yeshwanthpur Baseline)

| Metric Category | Indicator | Computed Value | Description |
|---|---|---|---|
| **Road Network** | Total Segments | **15,798** | Cleaned drivable road edges |
| | Total Length | **983.52 km** | Cumulative road network length |
| | Road Density | **50.17 km/km²** | Drivable road length per unit area |
| **Topology** | Network Nodes | **5,924** | Topological network vertices |
| | Intersections | **4,792** | Junctions with degree ≥ 3 (244.5/km²) |
| | Critical Bottlenecks | **794 segments** | Top 5% betweenness centrality corridors |
| **Healthcare** | Total Facilities | **84** | Verified healthcare amenities |
| | Hospitals | **16** | Secondary & tertiary medical centers |
| | Clinics & Doctors | **50** | Outpatient primary care clinics |
| | Mean Hospital Distance | **972 meters** | Average straight-line distance |
| | Pop-Weighted Distance | **1.14 km** | Urban census density weighted |
| **Spatial Grid** | Grid Resolution | **250m × 250m** | 344 metric cells across study area |
| | High Access (<1km) | **56.7%** | Cells within immediate hospital buffer |
| | Deficit Cells (>2km) | **14.5%** | Priority candidate zones for new clinics |
| **Machine Learning**| Optimal Clusters ($k$) | **5** | Selected via Silhouette maximization (0.392) |
| | PCA Variance Ratio | **83.4%** | Total variance explained by 2 components |

---

## 🛠️ Technology Stack

- **Core & Processing:** Python 3.12, GeoPandas, Pandas, NumPy, Shapely, PyProj, Pyogrio
- **Network Analysis:** OSMnx, NetworkX, OpenStreetMap Overpass API
- **Machine Learning:** Scikit-Learn (KMeans, StandardScaler, PCA, Silhouette Score), Joblib
- **Visualization:** Streamlit, Folium, Streamlit-Folium, Plotly Express & Graph Objects, Altair
- **Testing:** Pytest

---

## 🚀 Installation & Quickstart

### 1. Prerequisites
Ensure Python 3.12 is installed and accessible in your system path.

### 2. Environment Setup & Dependency Installation
Clone or navigate to the project directory:
```bash
cd "c:\Users\dell\Desktop\SEM 3\Projects\GIS"
pip install -r requirements.txt
```

### 3. Run End-to-End Data Pipeline
To execute data acquisition, preprocessing, spatial grid aggregation, and machine learning model training:
```bash
python src/run_pipeline.py
```
*Note: The project already includes pre-downloaded, verified local datasets in `data/processed/` and trained models in `outputs/models/` for immediate offline usage.*

### 4. Launch the Interactive Streamlit Dashboard
Start the full web application:
```bash
streamlit run app/app.py
```
The application will automatically open in your default browser at `http://localhost:8501`.

---

## 🧪 Automated Testing

Execute the comprehensive test suite verifying coordinates, geometries, road metrics, shortest-route algorithms, healthcare classifiers, and ML models:

```bash
python -m pytest tests -v
```

Expected output:
```
======================= 15 passed in 11.52s =======================
```

---

## 📐 Scientific Governance & Methodology Notes

1. **Topological Centrality vs. Live Traffic:**
   Betweenness centrality is a purely structural graph metric reflecting bridging criticality. It identifies corridors where network disruptions cause the largest detours (e.g. Tumkur Road flyover approaches, railway yard perimeter roads). It must **not** be confused with empirical live probe congestion.
2. **Straight-Line vs. Network Distance:**
   Euclidean buffers fail to account for barriers such as railway lines, limited-access highways, and gated industrial zones. The application explicitly measures and visualizes **Circuity Factor** ($\text{Network Distance} / \text{Euclidean Distance}$), which averages $1.28\times$ to $1.45\times$ across Yeshwanthpur.
3. **Accessibility Classification Bands:**
   - **High Accessibility:** $< 1.0\text{ km}$
   - **Moderate Accessibility:** $1.0 - 2.0\text{ km}$
   - **Low Accessibility:** $2.0 - 3.0\text{ km}$
   - **Very Low Accessibility:** $> 3.0\text{ km}$
4. **Machine Learning Scope:**
   Unsupervised K-Means is deployed to discover latent socio-spatial typologies across spatial grid cells using 5 standardized features. It is not an inferential or predictive congestion model.

---

## 📄 License & Attribution
- Road network and POI geometries © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors (ODbL).
- Built for Bengaluru Smart City analytical and planning applications.

