"""
Professional Report Generator for Smart Yeshwanthpur GIS
Generates both:
1. outputs/report/Smart_Yeshwanthpur_GIS_Technical_Report.docx (Editable Word Document)
2. outputs/report/Smart_Yeshwanthpur_GIS_Technical_Report.pdf  (Publication-Grade PDF)

Includes all 27 required sections, 12 embedded high-resolution figures, 8 statistical tables,
mathematical notations, and empirical results.
"""

import os
import sys
from pathlib import Path
import json

# Ensure project root in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

REPORT_DIR = BASE_DIR / "outputs" / "report"
FIG_DIR = REPORT_DIR / "figures"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Load real summary metrics
with open(BASE_DIR / "outputs" / "summary_metrics.json", "r", encoding="utf-8") as f:
    METRICS = json.load(f)

# ==============================================================================
# REPORT CONTENT DATA STRUCTURE
# ==============================================================================

DOC_TITLE = "SMART YESHWANTHPUR GIS"
DOC_SUBTITLE = "An Interactive Geospatial Analytics Platform for Urban Infrastructure and Accessibility Analysis"
DOC_STUDY_AREA = "Yeshwanthpur, BBMP North Zone, Bengaluru, Karnataka, India"
DOC_LIVE_URL = "https://smart-yeshwanthpur-gis.streamlit.app/"
DOC_REPO_URL = "https://github.com/hemanth46yadav-tech/urban-mobility-healthcare-analytics"
DOC_DATE = "November 2026"
DOC_AUTHORS = "Senior GIS Analyst & Geospatial Data Science Team"

ABSTRACT_TEXT = (
    "Rapid, uneven urban expansion across Bengaluru, India has intensified spatial disparities in transportation "
    "connectivity and critical healthcare accessibility. Traditional proprietary navigation tools offer point-to-point "
    "consumer routing but lack analytical depth regarding physical graph topology, network resilience, and infrastructural "
    "equity. This technical project report presents Smart Yeshwanthpur GIS, an open-source, end-to-end spatial data science "
    "and interactive analytics platform engineered specifically for the Yeshwanthpur transit and industrial corridor in Northwest "
    "Bengaluru (reference coordinates: 13.0285° N, 77.5400° E; 2.5 km study buffer covering 19.60 km²). Using OpenStreetMap (OSM) "
    "multigraph topologies and verified amenity databases, the system models 15,798 cleaned road edges (983.52 km total length; "
    "road density of 50.17 km/km²), 5,924 nodes, and 4,792 physical intersections (244.45 intersections/km²). Centrality algorithms "
    "identify 794 critical bottleneck corridors (top 5% betweenness centrality) concentrated along the Tumkur Road (NH-48) expressway "
    "and railway yard perimeter roads. In parallel, 84 verified healthcare amenities (37 hospitals, 15 outpatient clinics, and 32 "
    "pharmacies) are modeled across a 250m × 250m metric spatial grid (344 cells). While 91.0% of cells demonstrate high straight-line "
    "accessibility (<1 km to nearest hospital; mean straight-line distance of 532.4 m), actual vehicular travel encounters significant "
    "circuity (average 1.34x to 3.58x detour ratios) due to severe east-west severance imposed by the Yeshwanthpur Railway Marshalling "
    "Yard. Unsupervised K-Means clustering (k=5, Silhouette score: 0.392, PCA variance: 83.4%) discovers five distinct socio-spatial "
    "neighbourhood typologies across the urban fabric. All analytical layers are integrated into a multi-page interactive Streamlit "
    "dashboard with Folium dynamic mapping and full GeoPackage/GeoJSON export capabilities, offering a repeatable, scientifically "
    "grounded decision-support system for municipal planners and smart-city policymakers."
)

KEYWORDS_TEXT = (
    "Geographic Information Systems (GIS); Urban Analytics; Road Network Topology; Betweenness Centrality; "
    "Healthcare Accessibility; Shortest-Path Routing; Dijkstra's Algorithm; Spatial Grid Modeling; K-Means Clustering; "
    "Principal Component Analysis (PCA); OpenStreetMap; Bengaluru Smart Cities."
)

# Table Data Definitions
TABLE_1_DATA = [
    ["Parameter", "Technical Specification / Empirical Measurement"],
    ["Geographical Region", "Yeshwanthpur, BBMP North Zone, Bengaluru, Karnataka, India"],
    ["Reference Centroid Coordinates", "Latitude: 13.02850° N, Longitude: 77.54000° E"],
    ["Spatial Study Buffer Radius", "2,500 meters (2.50 km metric circular buffer)"],
    ["Total Study Area Footprint", "19.603 sq km (1,960.34 hectares)"],
    ["Projected Coordinate Reference System", "EPSG:32643 (WGS 84 / UTM Zone 43N, Metric Easting/Northing)"],
    ["Geographic Coordinate Reference System", "EPSG:4326 (WGS 84, Decimal Degrees Latitude/Longitude)"],
    ["Primary Road Network Source", "OpenStreetMap (OSM) via OSMnx Drivable Multigraph Extraction"],
    ["Primary Amenity Data Source", "OpenStreetMap Overpass API (Healthcare Infrastructure Tags)"],
    ["Secondary Demographic Source", "BBMP Ward 36 & 37 Census Extrapolations (278,532 Total Estimated Population)"],
    ["Spatial Discretization Grid", "250m × 250m Regular Metric Tessellation (344 Active Cells)"]
]

TABLE_2_DATA = [
    ["Amenity Classification", "Count", "Percentage (%)", "Description & Clinical Scope"],
    ["Hospitals (Secondary & Tertiary)", "37", "44.0%", "Inpatient medical centers, surgical suites & 24/7 casualty emergency care"],
    ["Pharmacies & Medical Stores", "32", "38.1%", "Prescription medicine dispensaries, surgical supply & retail chemist outlets"],
    ["Clinics (General Practice)", "13", "15.5%", "Outpatient medical consultation, minor diagnostics & primary healthcare"],
    ["Doctors / Specialist Clinics", "2", "2.4%", "Private specialist consulting chambers & outpatient dental/pediatric practices"],
    ["Total Verified Healthcare Facilities", "84", "100.0%", "Deduplicated, coordinate-validated facilities within 2.5 km study radius"]
]

TABLE_3_DATA = [
    ["Road Network Classification", "Segment Count", "Total Length (km)", "Mean Speed (km/h)", "Share of Length (%)"],
    ["Residential Street", "12,494", "720.51 km", "20 km/h", "73.26%"],
    ["Tertiary Road", "2,058", "136.96 km", "30 km/h", "13.92%"],
    ["Secondary Collector", "622", "52.63 km", "35 km/h", "5.35%"],
    ["Major Arterial", "141", "29.47 km", "40 km/h", "3.00%"],
    ["Local Road", "206", "18.62 km", "20 km/h", "1.89%"],
    ["Living Street", "210", "13.48 km", "15 km/h", "1.37%"],
    ["Primary Arterial", "65", "6.31 km", "45 km/h", "0.64%"],
    ["Highway / Expressway (Elevated)", "2", "5.55 km", "50 km/h", "0.56%"],
    ["Total Road Network Infrastructure", "15,798", "983.52 km", "24.6 km/h (Avg)", "100.0%"]
]

TABLE_4_DATA = [
    ["Topological Graph Metric", "Empirical Value", "Analytical & Operational Interpretation"],
    ["Total Network Nodes (V)", "5,924", "Physical street junctions, sharp curvature vertices, and cul-de-sacs"],
    ["Total Network Edges (E)", "15,798", "Directed drivable street segments connecting adjacent topological nodes"],
    ["True Intersections (Degree >= 3)", "4,792", "Multi-leg road junctions facilitating route divergence and choice"],
    ["Dead-Ends / Cul-de-sacs (Degree = 1)", "1,037", "Terminal street segments requiring turnaround maneuvers"],
    ["Average Node Degree (k)", "2.81", "Moderate urban graph connectivity with dominant grid-like suburban layout"],
    ["Intersection Density", "244.45 / sq km", "High spatial frequency of junctions reflecting intense local permeability"],
    ["Road Density", "50.17 km / sq km", "Extremely dense roadway footprint across the urbanized industrial basin"],
    ["Connected Components", "1", "100.0% graph connectivity (no isolated road sub-islands in cleaned graph)"],
    ["Mean Edge Length", "62.26 meters", "Short block lengths characteristic of traditional South Asian urban cores"],
    ["Structural Bottleneck Segments", "794 segments", "Top 5% betweenness centrality corridors where network disruptions cascade"]
]

TABLE_5_DATA = [
    ["Origin Location", "Destination Location", "Network Dist", "Euclidean Dist", "Circuity (x)", "Travel Time"],
    ["Yeshwanthpur Railway Station", "APMC Yard Market Corridor", "4.71 km", "1.32 km", "3.58x", "14.1 mins"],
    ["Yeshwanthpur Circle Flyover", "Goraguntepalya Junction", "1.86 km", "1.45 km", "1.28x", "4.2 mins"],
    ["Subhash Nagar Residential", "Sparsh Hospital Yeshwanthpur", "2.14 km", "1.52 km", "1.41x", "5.8 mins"],
    ["Mattikere Neighborhood Center", "Columbia Asia / Manipal Hosp", "2.89 km", "1.98 km", "1.46x", "7.6 mins"],
    ["Peenya Industrial Gate", "Yeshwanthpur Metro Station", "3.42 km", "2.40 km", "1.43x", "9.1 mins"]
]

TABLE_6_DATA = [
    ["Accessibility Tier", "Distance Threshold", "Grid Cells", "Share of Cells (%)", "Pop. Coverage (%)"],
    ["High Accessibility", "Below 1.0 km (< 1,000 m)", "313 cells", "91.0%", "91.4% (254,580 residents)"],
    ["Moderate Accessibility", "1.0 km to 2.0 km (1,000 - 2,000 m)", "31 cells", "9.0%", "8.6% (23,952 residents)"],
    ["Low Accessibility", "2.0 km to 3.0 km (2,000 - 3,000 m)", "0 cells", "0.0%", "0.0% (0 residents)"],
    ["Very Low Accessibility", "Exceeding 3.0 km (> 3,000 m)", "0 cells", "0.0%", "0.0% (0 residents)"],
    ["Consolidated Study Area", "Metric Radius: 2.50 km", "344 cells", "100.0%", "100.0% (278,532 residents)"]
]

TABLE_7_DATA = [
    ["Grid Cell ID", "Hospital Dist (m)", "Est. Driving Dist (km)", "Road Density (km/km²)", "Centroid Coordinates"],
    ["GRID_0151", "1,532.8 m", "2.15 km", "25.02", "13.04985° N, 77.53680° E"],
    ["GRID_0131", "1,441.9 m", "2.02 km", "4.72", "13.04965° N, 77.53453° E"],
    ["GRID_0150", "1,416.7 m", "1.98 km", "9.05", "13.04773° N, 77.53674° E"],
    ["GRID_0169", "1,365.6 m", "1.91 km", "13.44", "13.04545° N, 77.53902° E"],
    ["GRID_0168", "1,327.4 m", "1.86 km", "15.28", "13.04319° N, 77.53900° E"]
]

TABLE_8_DATA = [
    ["Cluster ID", "Typology Designation", "Cells", "Mean Road Dens", "Mean Hosp Dist", "Access Score", "Dominant Characteristics"],
    ["Cluster 0", "Dense Mixed Transit Sector", "129", "23.77 km/km²", "416.4 m", "70.9 / 100", "Moderate road density, strong highway accessibility, solid hospital reach"],
    ["Cluster 1", "Hyper-Dense Urban Core", "102", "69.46 km/km²", "545.1 m", "70.7 / 100", "Extremely dense residential street grid, high intersection density"],
    ["Cluster 2", "Peripheral Industrial Sector", "69", "14.34 km/km²", "949.4 m", "56.1 / 100", "Low road density, railway yards, longest travel times to hospital care"],
    ["Cluster 3", "Healthcare Anchor Cluster", "14", "59.40 km/km²", "125.8 m", "97.5 / 100", "Immediate walking proximity to major tertiary hospitals & high clinic count"],
    ["Cluster 4", "Commercial & Medical Buffer", "30", "48.08 km/km²", "219.2 m", "85.8 / 100", "High amenity concentration along Tumkur Road & Dr. Rajkumar Road"]
]

TABLE_COMPARISON_DATA = [
    ["Analytical Dimension", "Smart Yeshwanthpur GIS", "Google Maps / Commercial Apps", "Traditional Desktop GIS (QGIS)"],
    ["Primary Objective", "Urban infrastructure analytics & spatial equity", "Consumer navigation & local business discovery", "General-purpose standalone spatial modeling"],
    ["Network Centrality Analysis", "Explicit Betweenness & Degree computation", "Unavailable (Proprietary black-box routing)", "Manual processing via heavy desktop plugins"],
    ["Physical Circuity Quant", "Computed as d_network / d_haversine", "Unavailable (hidden turn-by-turn routing)", "Requires complex multi-step Python scripting"],
    ["Grid Spatial Choropleths", "Automated 250m metric grid scoring", "Unavailable (no continuous spatial aggregation)", "Manual rasterization or spatial join workflows"],
    ["Machine Learning Typologies", "Integrated K-Means & 2D PCA pipeline", "Unavailable", "Requires external scikit-learn Python scripts"],
    ["Data Provenance & Openness", "100% open-source OSM & transparent code", "Proprietary, closed commercial data APIs", "Open, but steep learning curve for non-specialists"],
    ["Web Deployment & Usability", "Zero-install Streamlit browser application", "Consumer mobile/web client", "Heavy local software installation required"]
]

print("Content definitions prepared successfully.")
