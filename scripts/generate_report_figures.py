"""
Script to generate all 12 publication-grade figures for the Smart Yeshwanthpur GIS Technical Report.
Saves 300 DPI high-resolution figures into outputs/report/figures/.
"""

import os
import sys
from pathlib import Path

# Set MPLCONFIGDIR to avoid warnings
os.environ["MPLCONFIGDIR"] = "outputs/.mpl_cache"

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
import json

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

FIGURES_DIR = BASE_DIR / "outputs" / "report" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Styling defaults
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["figure.dpi"] = 300

# Color palette (Navy Blue, Teal, Slate Grey, Accent Coral)
C_NAVY = "#0f2b48"
C_TEAL = "#028090"
C_BLUE = "#1f77b4"
C_GREY = "#64748b"
C_LIGHT = "#f8fafc"
C_CORAL = "#e74c3c"
C_GOLD = "#f39c12"
C_GREEN = "#27ae60"

# Load Datasets
print("Loading spatial datasets...")
boundary = gpd.read_file(BASE_DIR / "data" / "processed" / "study_boundary.geojson")
roads = gpd.read_file(BASE_DIR / "data" / "processed" / "roads.gpkg")
nodes = gpd.read_file(BASE_DIR / "data" / "processed" / "nodes.gpkg")
healthcare = gpd.read_file(BASE_DIR / "data" / "processed" / "healthcare_facilities.geojson")
grid = gpd.read_file(BASE_DIR / "data" / "processed" / "spatial_grid.geojson")
clusters_df = pd.read_csv(BASE_DIR / "outputs" / "cluster_assignments.csv")

with open(BASE_DIR / "outputs" / "summary_metrics.json", "r", encoding="utf-8") as f:
    metrics = json.load(f)

# Ensure projected UTM CRS for accurate metric buffer and plotting
PROJ_CRS = "EPSG:32643"
boundary_proj = boundary.to_crs(PROJ_CRS)
roads_proj = roads.to_crs(PROJ_CRS)
healthcare_proj = healthcare.to_crs(PROJ_CRS)
grid_proj = grid.to_crs(PROJ_CRS)

print("1. Generating Figure 1: System Architecture Diagram...")
fig, ax = plt.subplots(figsize=(14, 10), facecolor="#ffffff")
ax.axis("off")

# Draw architecture boxes
boxes = [
    # Layer 1: Data Sources
    ("OpenStreetMap (OSM) Ecosystem\n• Overpass API (Healthcare Amenities)\n• OSMnx Python Client (Drivable Multigraph)\n• BBMP Ward Boundaries & Demographic Estimates", 0.05, 0.82, 0.90, 0.12, "#1a365d", "#ffffff", "LAYER 1: GEOSPATIAL DATA ACQUISITION & INGESTION"),
    
    # Layer 2: Preprocessing
    ("Geospatial Preprocessing & Topology Cleaning Pipeline (src/preprocessing.py)\n• Coordinate Validation & WGS84 Parsing • Deduplication & Attribute Normalization\n• Projected CRS Transformation (EPSG:4326 -> EPSG:32643 UTM 43N) • Geometric Snapping", 0.05, 0.65, 0.90, 0.11, "#2b6cb0", "#ffffff", "LAYER 2: DATA PREPROCESSING & STANDARDIZATION"),
    
    # Layer 3: Dual Analytical Engines
    ("Module A: Road Network Analysis\n(src/road_network.py, route_analysis.py)\n• NetworkX MultiDiGraph Construction\n• 15,798 Edges | 5,924 Nodes | 4,792 Junctions\n• Degree & Edge Betweenness Centrality\n• Top 5% Bottleneck Corridor Detection\n• Dijkstra Shortest Path Router (Distance & Time)\n• Circuity Factor Analysis (Network / Haversine)", 0.05, 0.40, 0.43, 0.20, "#2c5282", "#ffffff", "ANALYTICAL ENGINE A: ROAD TOPOLOGY"),
    
    ("Module B: Healthcare Accessibility\n(src/healthcare.py, accessibility.py)\n• 84 Facilities (37 Hospitals, 15 Clinics, 32 Pharm)\n• 250m x 250m Spatial Grid Modeling (344 Cells)\n• KDTree Nearest-Facility Euclidean Matrix\n• Multi-Tier Accessibility Banding (<1k, 1-2k, >2k)\n• Multi-Criteria Spatial Scoring Index (0-100)\n• BBMP Urban Density Population Weighting", 0.52, 0.40, 0.43, 0.20, "#2c5282", "#ffffff", "ANALYTICAL ENGINE B: HEALTHCARE ACCESSIBILITY"),
    
    # Layer 4: Machine Learning
    ("Unsupervised Machine Learning & Spatial Typology Engine (src/clustering.py)\n• 5 Multi-Dimensional Spatial Features • StandardScaler Normalization\n• K-Means Clustering (k=5, Silhouette Score: 0.392) • PCA Dimensionality Reduction (83.4% Variance Explained)", 0.05, 0.22, 0.90, 0.12, "#2b6cb0", "#ffffff", "LAYER 4: UNSUPERVISED MACHINE LEARNING & CLUSTERING"),
    
    # Layer 5: Presentation & Web App
    ("Interactive Multi-Page Streamlit Web Application (app/app.py & app/pages/)\n• Streamlit Dashboard Framework • Dynamic Folium Map Layers & Bounding Box Viewports\n• Plotly Express Analytical Visualizations • QGIS-Compatible Export Engine (GeoPackage, GeoJSON, CSV)", 0.05, 0.04, 0.90, 0.13, "#1a365d", "#ffffff", "LAYER 5: PRESENTATION & INTERACTIVE DECISION SUPPORT SYSTEM"),
]

for text, x, y, w, h, bg, fg, header in boxes:
    rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.02", facecolor=bg, edgecolor="#cbd5e1", linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + 0.02, y + h - 0.028, header, fontsize=10.5, fontweight="bold", color="#90cdf4" if bg == "#1a365d" else "#fbd38d", va="top")
    ax.text(x + 0.02, y + h - 0.055, text, fontsize=9.2, color=fg, va="top", linespacing=1.35)

# Connective Arrows
arrow_style = dict(facecolor="#4a5568", edgecolor="#2d3748", width=2.5, headwidth=8, headlength=8)
plt.annotate("", xy=(0.5, 0.77), xytext=(0.5, 0.81), arrowprops=arrow_style)
plt.annotate("", xy=(0.26, 0.61), xytext=(0.26, 0.64), arrowprops=arrow_style)
plt.annotate("", xy=(0.74, 0.61), xytext=(0.74, 0.64), arrowprops=arrow_style)
plt.annotate("", xy=(0.5, 0.35), xytext=(0.5, 0.39), arrowprops=arrow_style)
plt.annotate("", xy=(0.5, 0.18), xytext=(0.5, 0.21), arrowprops=arrow_style)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig01_system_architecture.png", dpi=300, bbox_inches="tight")
plt.close()

print("2. Generating Figure 2: Road Network Hierarchy Map...")
fig, ax = plt.subplots(figsize=(10, 10), facecolor="#ffffff")
ax.set_facecolor("#f8fafc")

# Category colors
hierarchy_colors = {
    "Highway / Expressway": "#e74c3c",
    "Primary Arterial": "#d35400",
    "Major Arterial": "#e67e22",
    "Secondary Collector": "#f39c12",
    "Tertiary Road": "#3498db",
    "Residential Street": "#94a3b8",
    "Living Street": "#64748b",
    "Local Road": "#cbd5e1",
}

# Plot roads in order of increasing priority
for cat in ["Local Road", "Living Street", "Residential Street", "Tertiary Road", "Secondary Collector", "Major Arterial", "Primary Arterial", "Highway / Expressway"]:
    sub = roads_proj[roads_proj["road_category"] == cat]
    if not sub.empty:
        lw = 2.4 if "Highway" in cat or "Primary" in cat else (1.6 if "Major" in cat or "Secondary" in cat else 0.7)
        sub.plot(ax=ax, color=hierarchy_colors.get(cat, "#64748b"), linewidth=lw, alpha=0.9, label=cat)

boundary_proj.plot(ax=ax, facecolor="none", edgecolor="#0f172a", linewidth=2.2, linestyle="--", label="Study Boundary (2.5 km)")

ax.set_title("Road Network Topology & Street Hierarchy (Yeshwanthpur)", fontsize=13, fontweight="bold", pad=12, color="#0f172a")
ax.set_xlabel("Easting (UTM Zone 43N, meters)", fontsize=9.5)
ax.set_ylabel("Northing (UTM Zone 43N, meters)", fontsize=9.5)
ax.grid(True, linestyle=":", alpha=0.4, color="#94a3b8")
ax.legend(loc="upper right", frameon=True, facecolor="#ffffff", framealpha=0.9, fontsize=8.5)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig02_road_network_hierarchy.png", dpi=300, bbox_inches="tight")
plt.close()

print("3. Generating Figure 3: Road Hierarchy Distribution Charts...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), facecolor="#ffffff")

cat_counts = pd.Series(metrics["road_statistics"]["category_counts"]).sort_values()
cat_lengths = pd.Series(metrics["road_statistics"]["category_lengths_km"]).sort_values()

# Colors matching hierarchy
c_list1 = [hierarchy_colors.get(c, "#64748b") for c in cat_counts.index]
c_list2 = [hierarchy_colors.get(c, "#64748b") for c in cat_lengths.index]

ax1.barh(cat_counts.index, cat_counts.values, color=c_list1, edgecolor="#334155", linewidth=0.6)
ax1.set_title("Road Segment Count by Classification", fontsize=11, fontweight="bold", color="#0f172a")
ax1.set_xlabel("Number of Segments", fontsize=9.5)
ax1.grid(True, axis="x", linestyle=":", alpha=0.5)
for i, v in enumerate(cat_counts.values):
    ax1.text(v + 100, i, f"{v:,}", va="center", fontsize=8.5, color="#1e293b")

ax2.barh(cat_lengths.index, cat_lengths.values, color=c_list2, edgecolor="#334155", linewidth=0.6)
ax2.set_title("Total Road Length by Classification (km)", fontsize=11, fontweight="bold", color="#0f172a")
ax2.set_xlabel("Length (Kilometers)", fontsize=9.5)
ax2.grid(True, axis="x", linestyle=":", alpha=0.5)
for i, v in enumerate(cat_lengths.values):
    ax2.text(v + 5, i, f"{v:.1f} km", va="center", fontsize=8.5, color="#1e293b")

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig03_road_category_distribution.png", dpi=300, bbox_inches="tight")
plt.close()

print("4. Generating Figure 4: Betweenness Centrality & Structural Bottlenecks...")
fig, ax = plt.subplots(figsize=(10, 10), facecolor="#ffffff")
ax.set_facecolor("#f8fafc")

# Plot standard roads in light grey
roads_proj.plot(ax=ax, color="#cbd5e1", linewidth=0.5, alpha=0.6)

# Highlight bottlenecks
if "is_bottleneck_corridor" in roads_proj.columns:
    bottlenecks = roads_proj[roads_proj["is_bottleneck_corridor"]]
    bottlenecks.plot(ax=ax, color="#dc2626", linewidth=2.0, alpha=0.9, label="Critical Bottleneck Corridors (Top 5%)")

boundary_proj.plot(ax=ax, facecolor="none", edgecolor="#0f172a", linewidth=2.0, linestyle="--", label="Study Boundary")

# Annotate key locations
ax.plot(775492, 1302420, "o", color="#1e3a8a", markersize=8) # Approx UTM coords for Yeshwanthpur Stn
ax.set_title("Topological Betweenness Centrality & Network Bottlenecks", fontsize=13, fontweight="bold", pad=12, color="#0f172a")
ax.set_xlabel("Easting (UTM Zone 43N, meters)", fontsize=9.5)
ax.set_ylabel("Northing (UTM Zone 43N, meters)", fontsize=9.5)
ax.grid(True, linestyle=":", alpha=0.4, color="#94a3b8")
ax.legend(loc="upper right", frameon=True, facecolor="#ffffff", framealpha=0.9, fontsize=9)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig04_betweenness_centrality.png", dpi=300, bbox_inches="tight")
plt.close()

print("5. Generating Figure 5: Graph-Based Shortest Path Routing...")
fig, ax = plt.subplots(figsize=(10, 10), facecolor="#ffffff")
ax.set_facecolor("#f8fafc")

roads_proj.plot(ax=ax, color="#e2e8f0", linewidth=0.6, alpha=0.7)

# Pick two representative nodes for an empirical shortest path
from src.route_analysis import find_shortest_route
from src.shared_ui import load_cached_graph
graph = load_cached_graph()

orig_coords = (13.0242, 77.5492) # Yeshwanthpur Railway Station
dest_coords = (13.0298, 77.5385) # APMC Yard

route_res = find_shortest_route(graph, orig_coords, dest_coords, weight="length")
if route_res.get("success"):
    route_geom = route_res.get("route_geometry")
    route_gdf = gpd.GeoDataFrame([{"geometry": route_geom}], crs="EPSG:4326").to_crs(PROJ_CRS)
    route_gdf.plot(ax=ax, color="#1d4ed8", linewidth=3.5, label=f"Dijkstra Shortest Route ({route_res['distance_km']} km, {route_res['travel_time_min']} mins)")

# Draw straight-line comparison
from shapely.geometry import LineString, Point
orig_pt = gpd.GeoDataFrame([{"geometry": Point(orig_coords[1], orig_coords[0])}], crs="EPSG:4326").to_crs(PROJ_CRS).geometry.iloc[0]
dest_pt = gpd.GeoDataFrame([{"geometry": Point(dest_coords[1], dest_coords[0])}], crs="EPSG:4326").to_crs(PROJ_CRS).geometry.iloc[0]
straight_line = LineString([orig_pt, dest_pt])
gpd.GeoDataFrame([{"geometry": straight_line}], crs=PROJ_CRS).plot(ax=ax, color="#f97316", linestyle="--", linewidth=2.0, label=f"Euclidean Haversine ({route_res['straight_line_dist_meters']} m, Circuity: {route_res['circuity_factor']}x)")

ax.plot(orig_pt.x, orig_pt.y, "o", color="#16a34a", markersize=12, label="Origin (Yeshwanthpur Railway Station)")
ax.plot(dest_pt.x, dest_pt.y, "s", color="#dc2626", markersize=12, label="Destination (APMC Yard & Market)")

boundary_proj.plot(ax=ax, facecolor="none", edgecolor="#475569", linewidth=1.8, linestyle=":")

# Zoom into route area with buffer
minx, miny, maxx, maxy = route_gdf.total_bounds
pad = 600
ax.set_xlim(minx - pad, maxx + pad)
ax.set_ylim(miny - pad, maxy + pad)

ax.set_title("Graph-Based Dijkstra Shortest Path vs. Euclidean Distance", fontsize=13, fontweight="bold", pad=12, color="#0f172a")
ax.set_xlabel("Easting (UTM Zone 43N, meters)", fontsize=9.5)
ax.set_ylabel("Northing (UTM Zone 43N, meters)", fontsize=9.5)
ax.grid(True, linestyle=":", alpha=0.5)
ax.legend(loc="lower left", frameon=True, facecolor="#ffffff", framealpha=0.9, fontsize=8.5)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig05_shortest_path_routing.png", dpi=300, bbox_inches="tight")
plt.close()

print("6. Generating Figure 6: Spatial Distribution of Healthcare Facilities...")
fig, ax = plt.subplots(figsize=(10, 10), facecolor="#ffffff")
ax.set_facecolor("#f8fafc")

roads_proj.plot(ax=ax, color="#e2e8f0", linewidth=0.5, alpha=0.7)
boundary_proj.plot(ax=ax, facecolor="none", edgecolor="#0f172a", linewidth=2.0, linestyle="--", label="Study Boundary")

# 1 km hospital service buffers
hosp = healthcare_proj[healthcare_proj["facility_type"] == "Hospital"]
if not hosp.empty:
    hosp_buffers = hosp.geometry.buffer(1000)
    gpd.GeoDataFrame(geometry=hosp_buffers, crs=PROJ_CRS).plot(ax=ax, facecolor="#fee2e2", edgecolor="#ef4444", alpha=0.25, linewidth=1.0, label="1.0 km Hospital Service Buffer")

# Facility points
type_markers = {
    "Hospital": ("#dc2626", "o", 80),
    "Clinic": ("#2563eb", "^", 60),
    "Doctors / Clinic": ("#0284c7", "^", 60),
    "Pharmacy": ("#16a34a", "s", 45),
}

for ftype, (color, marker, size) in type_markers.items():
    sub = healthcare_proj[healthcare_proj["facility_type"] == ftype]
    if not sub.empty:
        ax.scatter(sub.geometry.x, sub.geometry.y, c=color, marker=marker, s=size, edgecolor="#1e293b", linewidth=0.8, alpha=0.9, label=f"{ftype} (n={len(sub)})")

ax.set_title("Spatial Distribution of Healthcare Facilities & Hospital Service Buffers", fontsize=13, fontweight="bold", pad=12, color="#0f172a")
ax.set_xlabel("Easting (UTM Zone 43N, meters)", fontsize=9.5)
ax.set_ylabel("Northing (UTM Zone 43N, meters)", fontsize=9.5)
ax.grid(True, linestyle=":", alpha=0.4)
ax.legend(loc="upper right", frameon=True, facecolor="#ffffff", framealpha=0.9, fontsize=8.5)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig06_healthcare_distribution.png", dpi=300, bbox_inches="tight")
plt.close()

print("7. Generating Figure 7: Healthcare Amenity Mix (Donut Chart)...")
fig, ax = plt.subplots(figsize=(7, 7), facecolor="#ffffff")

hc_counts = pd.Series(metrics["healthcare_statistics"]["breakdown"])
colors = ["#dc2626", "#16a34a", "#2563eb", "#0284c7"]

wedges, texts, autotexts = ax.pie(
    hc_counts.values,
    labels=hc_counts.index,
    autopct="%1.1f%%",
    startangle=140,
    colors=colors,
    wedgeprops=dict(width=0.45, edgecolor="#ffffff", linewidth=2),
    pctdistance=0.75,
)
plt.setp(texts, fontsize=10, color="#0f172a", fontweight="medium")
plt.setp(autotexts, fontsize=9.5, fontweight="bold", color="#ffffff")

ax.set_title("Healthcare Infrastructure Amenity Composition\n(Total Verified Facilities = 84)", fontsize=12, fontweight="bold", color="#0f172a", pad=15)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig07_healthcare_category_mix.png", dpi=300, bbox_inches="tight")
plt.close()

print("8. Generating Figure 8: 250m Spatial Grid Healthcare Accessibility Choropleth...")
fig, ax = plt.subplots(figsize=(10, 10), facecolor="#ffffff")
ax.set_facecolor("#f8fafc")

# Plot grid choropleth by accessibility score
grid_proj.plot(
    column="accessibility_score",
    cmap="YlGnBu",
    linewidth=0.4,
    edgecolor="#64748b",
    legend=True,
    legend_kwds={"label": "Healthcare Accessibility Score (0 - 100)", "shrink": 0.65},
    ax=ax,
    alpha=0.75,
)

roads_proj.plot(ax=ax, color="#334155", linewidth=0.4, alpha=0.4)
boundary_proj.plot(ax=ax, facecolor="none", edgecolor="#0f172a", linewidth=2.0, linestyle="--", label="Study Boundary")

# Plot hospitals
hosp_proj = healthcare_proj[healthcare_proj["facility_type"] == "Hospital"]
ax.scatter(hosp_proj.geometry.x, hosp_proj.geometry.y, c="#dc2626", marker="P", s=70, edgecolor="#ffffff", linewidth=0.8, label="Hospitals (n=37)")

ax.set_title("250m Spatial Grid Healthcare Accessibility Choropleth", fontsize=13, fontweight="bold", pad=12, color="#0f172a")
ax.set_xlabel("Easting (UTM Zone 43N, meters)", fontsize=9.5)
ax.set_ylabel("Northing (UTM Zone 43N, meters)", fontsize=9.5)
ax.grid(True, linestyle=":", alpha=0.4)
ax.legend(loc="upper right", frameon=True, facecolor="#ffffff", framealpha=0.9, fontsize=8.5)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig08_spatial_grid_accessibility.png", dpi=300, bbox_inches="tight")
plt.close()

print("9. Generating Figure 9: K-Means Clustering Evaluation (Elbow & Silhouette)...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), facecolor="#ffffff")

eval_data = metrics["ml_clustering"]["evaluation"]
k_vals = eval_data["k_values"]
inertias = eval_data["inertias"]
sil_scores = eval_data["silhouette_scores"]

# Elbow Curve
ax1.plot(k_vals, inertias, marker="o", color="#1d4ed8", linewidth=2.2, markersize=7)
ax1.axvline(x=5, color="#dc2626", linestyle="--", linewidth=1.5, label="Selected Optimal k=5")
ax1.set_title("Elbow Method: Within-Cluster Inertia vs. k", fontsize=11, fontweight="bold", color="#0f172a")
ax1.set_xlabel("Number of Clusters (k)", fontsize=9.5)
ax1.set_ylabel("Sum of Squared Distances (Inertia)", fontsize=9.5)
ax1.grid(True, linestyle=":", alpha=0.5)
ax1.legend(loc="upper right")

# Silhouette Score
ax2.plot(k_vals, sil_scores, marker="s", color="#16a34a", linewidth=2.2, markersize=7)
ax2.axvline(x=5, color="#dc2626", linestyle="--", linewidth=1.5, label="Peak Score = 0.392 (k=5)")
ax2.set_title("Silhouette Coefficient vs. Number of Clusters (k)", fontsize=11, fontweight="bold", color="#0f172a")
ax2.set_xlabel("Number of Clusters (k)", fontsize=9.5)
ax2.set_ylabel("Mean Silhouette Score", fontsize=9.5)
ax2.grid(True, linestyle=":", alpha=0.5)
ax2.legend(loc="upper right")

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig09_kmeans_evaluation.png", dpi=300, bbox_inches="tight")
plt.close()

print("10. Generating Figure 10: 2D PCA Cluster Projection...")
fig, ax = plt.subplots(figsize=(9, 7), facecolor="#ffffff")

pca_colors = {
    0: "#2563eb",
    1: "#0284c7",
    2: "#f59e0b",
    3: "#16a34a",
    4: "#8b5cf6",
}

for cid in sorted(clusters_df["cluster"].unique()):
    sub_c = clusters_df[clusters_df["cluster"] == cid]
    ax.scatter(
        sub_c["pca_1"],
        sub_c["pca_2"],
        c=pca_colors.get(cid, "#64748b"),
        s=45,
        alpha=0.85,
        edgecolor="#334155",
        linewidth=0.5,
        label=f"Cluster {cid} (n={len(sub_c)})"
    )

var_r = metrics["ml_clustering"]["pca_explained_variance_ratio"]
ax.set_title(f"2D PCA Projection of Spatial Clusters\n(Total Explained Variance: {metrics['ml_clustering']['pca_total_variance']*100:.1f}%)", fontsize=12, fontweight="bold", color="#0f172a", pad=12)
ax.set_xlabel(f"Principal Component 1 ({var_r[0]*100:.1f}% variance)", fontsize=9.5)
ax.set_ylabel(f"Principal Component 2 ({var_r[1]*100:.1f}% variance)", fontsize=9.5)
ax.grid(True, linestyle=":", alpha=0.5)
ax.legend(loc="upper right", frameon=True, facecolor="#ffffff", framealpha=0.9, fontsize=8.5)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig10_pca_cluster_projection.png", dpi=300, bbox_inches="tight")
plt.close()

print("11. Generating Figure 11: Spatial Distribution of K-Means Neighbourhood Clusters...")
fig, ax = plt.subplots(figsize=(10, 10), facecolor="#ffffff")
ax.set_facecolor("#f8fafc")

# Map clusters to grid
grid_with_clusters = grid_proj.merge(clusters_df[["grid_id", "cluster"]], on="grid_id", how="left")

cluster_palette = {
    0: "#2563eb",
    1: "#0284c7",
    2: "#f59e0b",
    3: "#16a34a",
    4: "#8b5cf6",
}

for cid, color in cluster_palette.items():
    sub_g = grid_with_clusters[grid_with_clusters["cluster"] == cid]
    if not sub_g.empty:
        sub_g.plot(ax=ax, facecolor=color, edgecolor="#64748b", linewidth=0.4, alpha=0.7, label=f"Cluster {cid} (n={len(sub_g)})")

roads_proj.plot(ax=ax, color="#1e293b", linewidth=0.4, alpha=0.35)
boundary_proj.plot(ax=ax, facecolor="none", edgecolor="#0f172a", linewidth=2.0, linestyle="--", label="Study Boundary")

ax.set_title("Spatial Distribution of K-Means Neighbourhood Typologies", fontsize=13, fontweight="bold", pad=12, color="#0f172a")
ax.set_xlabel("Easting (UTM Zone 43N, meters)", fontsize=9.5)
ax.set_ylabel("Northing (UTM Zone 43N, meters)", fontsize=9.5)
ax.grid(True, linestyle=":", alpha=0.4)
ax.legend(loc="upper right", frameon=True, facecolor="#ffffff", framealpha=0.9, fontsize=8.5)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig11_spatial_clusters_map.png", dpi=300, bbox_inches="tight")
plt.close()

print("12. Generating Figure 12: Streamlit Dashboard Architecture Mockup...")
fig, ax = plt.subplots(figsize=(13, 7.5), facecolor="#0f172a")
ax.axis("off")

# Sidebar Mockup
ax.add_patch(mpatches.FancyBboxPatch((0.02, 0.05), 0.22, 0.90, boxstyle="round,pad=0.01", facecolor="#1e293b", edgecolor="#334155", linewidth=1.5))
ax.text(0.04, 0.90, "Smart Yeshwanthpur", fontsize=12, fontweight="bold", color="#f8fafc")
ax.text(0.04, 0.86, "GIS Analytics Platform", fontsize=8.5, color="#94a3b8")
ax.text(0.04, 0.82, "Bengaluru, Karnataka", fontsize=8, color="#64748b")

pages = [
    "01 Overview",
    "02 Road Analysis",
    "03 Route Analysis",
    "04 Healthcare Analysis",
    "05 Accessibility Analysis",
    "06 Machine Learning",
    "07 Insights",
]
for idx, page in enumerate(pages):
    bg_p = "#3b82f6" if idx == 0 else "#0f172a"
    tc_p = "#ffffff" if idx == 0 else "#94a3b8"
    ax.add_patch(mpatches.Rectangle((0.035, 0.72 - idx*0.075), 0.19, 0.06, facecolor=bg_p, edgecolor="#475569", linewidth=0.8))
    ax.text(0.05, 0.745 - idx*0.075, page, fontsize=9, color=tc_p, fontweight="bold" if idx == 0 else "normal")

# Main Content Area Mockup
ax.add_patch(mpatches.FancyBboxPatch((0.26, 0.05), 0.72, 0.90, boxstyle="round,pad=0.01", facecolor="#ffffff", edgecolor="#cbd5e1", linewidth=1.5))
ax.text(0.28, 0.90, "Smart Yeshwanthpur - GIS Traffic & Healthcare Analytics", fontsize=13, fontweight="bold", color="#0f172a")
ax.text(0.28, 0.86, "Empirical Spatial Data Science, Network Topology & Healthcare Accessibility Dashboard", fontsize=8.5, color="#64748b")

# KPI Cards
kpis = [
    ("Total Road Length", "983.52 km", "Cleaned road edges"),
    ("Road Density", "50.17 km/km²", "Study area density"),
    ("Healthcare Amenities", "84 Facilities", "37 Hospitals, 15 Clinics"),
    ("Mean Hospital Dist", "532.4 m", "Pop-weighted: 0.53 km"),
]
for kidx, (title, val, sub) in enumerate(kpis):
    kx = 0.28 + kidx * 0.17
    ax.add_patch(mpatches.FancyBboxPatch((kx, 0.73), 0.155, 0.10, boxstyle="round,pad=0.008", facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1))
    ax.text(kx + 0.01, 0.805, title, fontsize=7.5, color="#64748b", fontweight="bold")
    ax.text(kx + 0.01, 0.765, val, fontsize=11, color="#0f2b48", fontweight="bold")
    ax.text(kx + 0.01, 0.74, sub, fontsize=6.5, color="#94a3b8")

# Map Placeholder & Chart Placeholder
ax.add_patch(mpatches.FancyBboxPatch((0.28, 0.10), 0.44, 0.59, boxstyle="round,pad=0.008", facecolor="#f1f5f9", edgecolor="#94a3b8", linewidth=1))
ax.text(0.30, 0.65, "Interactive Geospatial Folium Canvas", fontsize=10, fontweight="bold", color="#1e293b")
ax.text(0.30, 0.62, "Full multi-layer road topology, 250m metric grid choropleth & facility markers", fontsize=7.5, color="#64748b")

# Mini map representation
ax.plot([0.35, 0.65], [0.35, 0.45], color="#1d4ed8", linewidth=2.5)
ax.plot([0.38, 0.60], [0.50, 0.25], color="#e74c3c", linewidth=1.5)
ax.plot([0.35], [0.35], "o", color="#16a34a", markersize=10)
ax.plot([0.65], [0.45], "s", color="#dc2626", markersize=10)

# Right Sidebar Stats / Charts
ax.add_patch(mpatches.FancyBboxPatch((0.74, 0.10), 0.22, 0.59, boxstyle="round,pad=0.008", facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1))
ax.text(0.755, 0.65, "Analytical Filters & Telemetry", fontsize=9.5, fontweight="bold", color="#1e293b")
ax.text(0.755, 0.61, "• Dijkstra shortest routing controls\n• Optimization: Distance / Time\n• Multi-tier accessibility thresholds\n• Road classification selector\n• GeoPackage / GeoJSON export\n• Lat: 13.0285° N, Lon: 77.5400° E\n• UTM Projection: EPSG:32643", fontsize=7.5, color="#475569", linespacing=1.6)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig12_dashboard_overview.png", dpi=300, bbox_inches="tight")
plt.close()

print("All 12 figures successfully generated and saved to outputs/report/figures/!")
