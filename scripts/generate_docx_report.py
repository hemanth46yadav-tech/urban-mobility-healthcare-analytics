"""
Generates the comprehensive technical project report in DOCX format:
outputs/report/Smart_Yeshwanthpur_GIS_Technical_Report.docx
"""

import sys
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.report_content import (
    DOC_TITLE, DOC_SUBTITLE, DOC_STUDY_AREA, DOC_LIVE_URL, DOC_REPO_URL, DOC_DATE, DOC_AUTHORS,
    ABSTRACT_TEXT, KEYWORDS_TEXT,
    TABLE_1_DATA, TABLE_2_DATA, TABLE_3_DATA, TABLE_4_DATA, TABLE_5_DATA,
    TABLE_6_DATA, TABLE_7_DATA, TABLE_8_DATA, TABLE_COMPARISON_DATA
)

REPORT_DIR = BASE_DIR / "outputs" / "report"
FIG_DIR = REPORT_DIR / "figures"
DOCX_OUT = REPORT_DIR / "Smart_Yeshwanthpur_GIS_Technical_Report.docx"

# Helper for XML shading
def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_styled_table(doc, data, col_widths=None):
    table = doc.add_table(rows=len(data), cols=len(data[0]))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    for row_idx, row_data in enumerate(data):
        row = table.rows[row_idx]
        is_header = (row_idx == 0)
        for col_idx, text in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.text = str(text)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.runs[0]
            run.font.name = "Arial"
            
            if is_header:
                set_cell_background(cell, "0F2B48") # Dark Navy
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(9.5)
                set_cell_margins(cell, top=140, bottom=140, left=160, right=160)
            else:
                bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
                set_cell_background(cell, bg)
                run.font.size = Pt(8.8)
                run.font.color.rgb = RGBColor(15, 23, 42)
                set_cell_margins(cell, top=100, bottom=100, left=140, right=140)

    # Set column widths if provided
    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = Inches(width)

    # Add small spacing after table
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(8)
    return table

def add_figure_with_caption(doc, fig_path, caption_text, width_inches=6.2):
    if fig_path.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(str(fig_path), width=Inches(width_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(14)
        run_cap = p_cap.add_run(caption_text)
        run_cap.font.name = "Arial"
        run_cap.font.size = Pt(9)
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(71, 85, 105) # Slate grey
    else:
        p_err = doc.add_paragraph(f"[Image Missing: {fig_path.name}]")
        p_err.runs[0].font.color.rgb = RGBColor(220, 38, 38)

def main():
    print("Creating Word Document (.docx)...")
    doc = docx.Document()

    # Set Margins (0.75 in / 1.9 cm)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Styles setup
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Arial'
    style_normal.font.size = Pt(10.5)
    style_normal.font.color.rgb = RGBColor(30, 41, 59)
    style_normal.paragraph_format.line_spacing = 1.2
    style_normal.paragraph_format.space_after = Pt(6)

    # --------------------------------------------------------------------------
    # 1. PROFESSIONAL COVER PAGE
    # --------------------------------------------------------------------------
    p_top_space = doc.add_paragraph()
    p_top_space.paragraph_format.space_before = Pt(40)

    p_badge = doc.add_paragraph()
    run_badge = p_badge.add_run("GEOSPATIAL DATA SCIENCE & URBAN INFRASTRUCTURE TECHNICAL REPORT")
    run_badge.font.size = Pt(9.5)
    run_badge.font.bold = True
    run_badge.font.color.rgb = RGBColor(2, 128, 144) # Teal

    p_title = doc.add_paragraph()
    run_title = p_title.add_run(DOC_TITLE)
    run_title.font.size = Pt(28)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 43, 72) # Navy Blue
    p_title.paragraph_format.space_after = Pt(8)

    p_sub = doc.add_paragraph()
    run_sub = p_sub.add_run(DOC_SUBTITLE)
    run_sub.font.size = Pt(13)
    run_sub.font.color.rgb = RGBColor(71, 85, 105)
    p_sub.paragraph_format.space_after = Pt(30)

    # Horizontal Divider Line
    p_line = doc.add_paragraph()
    run_line = p_line.add_run("―" * 56)
    run_line.font.color.rgb = RGBColor(203, 213, 225)
    run_line.font.bold = True
    p_line.paragraph_format.space_after = Pt(30)

    # Metadata Block
    meta_items = [
        ("Study Area Location:", DOC_STUDY_AREA),
        ("Target Analytical Domain:", "Network Topology, Healthcare Equity, Graph Theory & Machine Learning"),
        ("Spatial Scope:", "19.60 sq km | 2.50 km Metric Buffer (Centroid: 13.0285° N, 77.5400° E)"),
        ("Projected CRS:", "EPSG:32643 (UTM Zone 43N) | EPSG:4326 (WGS 84 Interchange)"),
        ("Live Web Application:", DOC_LIVE_URL),
        ("Source Code Repository:", DOC_REPO_URL),
        ("Author / Specialization:", DOC_AUTHORS),
        ("Document Publication Date:", DOC_DATE),
    ]

    for label, val in meta_items:
        p_m = doc.add_paragraph()
        p_m.paragraph_format.space_after = Pt(4)
        run_l = p_m.add_run(f"{label:<26} ")
        run_l.font.bold = True
        run_l.font.size = Pt(10)
        run_l.font.color.rgb = RGBColor(15, 43, 72)
        run_v = p_m.add_run(val)
        run_v.font.size = Pt(10)
        run_v.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 2. ABSTRACT & KEYWORDS
    # --------------------------------------------------------------------------
    h1 = doc.add_heading("Abstract", level=1)
    h1.runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(ABSTRACT_TEXT)

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(8)
    run_kwh = p_kw.add_run("Keywords: ")
    run_kwh.font.bold = True
    run_kwh.font.color.rgb = RGBColor(15, 43, 72)
    p_kw.add_run(KEYWORDS_TEXT)

    # --------------------------------------------------------------------------
    # 3. TABLE OF CONTENTS, LIST OF FIGURES & LIST OF TABLES
    # --------------------------------------------------------------------------
    doc.add_heading("Table of Contents", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    toc_entries = [
        "1. Executive Summary & Cover Page",
        "2. Abstract & Keywords",
        "3. Table of Contents, List of Figures & Tables",
        "4. Introduction & Urban Geographic Context",
        "5. Problem Statement & Research Motivation",
        "6. Project Objectives & Analytical Scope",
        "7. Study Area Delineation & Spatial Parameters",
        "8. Data Sources & Spatial Data Ingestion",
        "9. Technology Stack & Software Ecosystem",
        "10. System Architecture & End-to-End Data Pipeline",
        "11. Geospatial Preprocessing & Topology Standardization",
        "12. Comprehensive Analytical Methodology",
        "13. Road Network Analysis & Structural Centrality",
        "14. Shortest Path Graph Algorithms (Dijkstra Implementation)",
        "15. Healthcare Facility Inventory & Spatial Distribution",
        "16. Healthcare Accessibility & Metric Spatial Grid Modeling",
        "17. Interactive Streamlit Web Application Features",
        "18. Application Interface Architecture & Visualizations",
        "19. Empirical Results, Key Findings & Discussion",
        "20. Unsupervised Machine Learning & Spatial Typologies (K-Means & PCA)",
        "21. Differentiation from Commercial Navigation Platforms (Google Maps)",
        "22. Data Governance, Scientific Ethics & Analytical Disclaimers",
        "23. Technical Limitations & Data Completeness",
        "24. Future Roadmap & Proposed Enhancements",
        "25. Practical Policy Implications & Urban Planning Diagnostics",
        "26. Technical Conclusion",
        "27. References & Academic Citations",
    ]
    for e in toc_entries:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_after = Pt(2)
        p_t.add_run(e).font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    doc.add_heading("List of Figures", level=2).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    figures_list = [
        "Figure 1: Smart Yeshwanthpur GIS End-to-End System Architecture Pipeline",
        "Figure 2: Road Network Street Hierarchy & Spatial Topology (Yeshwanthpur)",
        "Figure 3: Road Network Classification Distribution (Segment Counts and Lengths)",
        "Figure 4: Topological Betweenness Centrality & Critical Network Bottleneck Corridors",
        "Figure 5: Dijkstra Shortest Path vs. Straight-Line Euclidean Distance Routing",
        "Figure 6: Spatial Distribution of Healthcare Amenities & 1.0 km Hospital Service Buffers",
        "Figure 7: Healthcare Amenity Composition & Clinical Mix Donut Chart",
        "Figure 8: 250m Metric Spatial Grid Healthcare Accessibility Choropleth",
        "Figure 9: Unsupervised K-Means Clustering Evaluation (Elbow Inertia & Silhouette Curves)",
        "Figure 10: 2D Principal Component Analysis (PCA) Cluster Projection",
        "Figure 11: Spatial Distribution of Discovered K-Means Neighbourhood Typologies",
        "Figure 12: Streamlit Interactive GIS Dashboard User Interface & Layout Architecture",
    ]
    for f in figures_list:
        p_f = doc.add_paragraph()
        p_f.paragraph_format.space_after = Pt(2)
        p_f.add_run(f).font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    doc.add_heading("List of Tables", level=2).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    tables_list = [
        "Table 1: Study Area Geographical and Spatial Reference Parameters",
        "Table 2: Healthcare Infrastructure Classification Breakdown",
        "Table 3: Road Network Classification Hierarchy and Physical Characteristics",
        "Table 4: Topological Graph Structural Metrics",
        "Table 5: Empirical Shortest Route Comparison (Dijkstra vs. Euclidean Straight-Line)",
        "Table 6: 250m Spatial Grid Healthcare Accessibility Coverage Tiers",
        "Table 7: Priority Healthcare Deficit Zones (Candidate Locations for Expansion)",
        "Table 8: Unsupervised K-Means Cluster Characteristics & Sociodemographic Typologies",
        "Table 9: Multi-Dimensional Comparison: Smart Yeshwanthpur GIS vs. Google Maps vs. Traditional Desktop GIS",
    ]
    for t in tables_list:
        p_tb = doc.add_paragraph()
        p_tb.paragraph_format.space_after = Pt(2)
        p_tb.add_run(t).font.size = Pt(9)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 4. INTRODUCTION & URBAN GEOGRAPHIC CONTEXT
    # --------------------------------------------------------------------------
    doc.add_heading("4. Introduction & Urban Geographic Context", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "Yeshwanthpur is a pivotal multimodal transportation and commercial gateway situated in the north-western sector "
        "of Bengaluru, Karnataka, India (administered under the Bruhat Bengaluru Mahanagara Palike - BBMP North Zone). "
        "Historically functioning as an industrial periphery anchored by heavy manufacturing layouts and the Agricultural Produce "
        "Market Committee (APMC) Yard—one of the largest wholesale agricultural distribution hubs in South India—the sub-region "
        "has transformed into an intense transit-oriented hub. It concentrates the Yeshwanthpur Junction Railway Station "
        "(one of Bengaluru's primary interstate rail terminals), the Namma Metro Green Line elevated corridor and interchange, "
        "and the elevated National Highway 48 (Tumkur Road) connecting Bengaluru to Karnataka's northern hinterland and Maharashtra."
    )
    doc.add_paragraph(
        "This rapid juxtaposition of high-capacity freight infrastructure, dense commercial wholesale yards, informal residential "
        "settlements, and modern high-density residential towers has generated profound geospatial friction. While the region is "
        "reputed for housing top-tier tertiary hospitals (such as Sparsh Hospital, Columbia Asia/Manipal Hospital, and People Tree "
        "Hospital), local road-network accessibility is severely constrained by structural barriers. In particular, the extensive "
        "Yeshwanthpur Railway Marshalling Yard creates an impenetrable physical severance bisecting the eastern and western wards, "
        "forcing intra-urban traffic onto narrow, highly congested flyover ramps and level crossings. To formulate effective urban "
        "resilience strategies, city authorities require scientific, reproducible, and open geospatial analytics that quantify "
        "road network bottlenecks and evaluate spatial healthcare access at granular metric scales."
    )

    # --------------------------------------------------------------------------
    # 5. PROBLEM STATEMENT & RESEARCH MOTIVATION
    # --------------------------------------------------------------------------
    doc.add_heading("5. Problem Statement & Research Motivation", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "Contemporary municipal planning in Indian metropolitan areas frequently relies on aggregate administrative census boundaries "
        "or black-box consumer navigation software (e.g., Google Maps, Apple Maps). While commercial platforms excel at point-to-point "
        "vehicular dispatch, their algorithmic architectures are unsuitable for structural urban policy diagnostics due to several "
        "fundamental limitations:"
    )
    doc.add_paragraph(
        "1. Absence of Structural Graph Metrics: Commercial routing tools evaluate live travel delays but do not expose underlying "
        "topological properties such as betweenness centrality, degree distribution, and intersection density, which identify where "
        "network failures trigger disproportionate systemic collapse.\n"
        "2. Euclidean Proximity Fallacy: Traditional healthcare access evaluations often assume circular straight-line buffers "
        "(e.g., 'all residents within 1 km of a hospital have equal access'). In Yeshwanthpur, a hospital located 800 meters away "
        "as the crow flies across the railway tracks requires a circuitous 3.5 km to 4.7 km driving detour, rendering Euclidean metrics "
        "fundamentally misleading.\n"
        "3. Lack of Continuous Spatial Aggregation: Conventional dashboards present isolated point pins rather than continuous "
        "tessellated grid models that synthesize road density, intersection frequency, and emergency response travel times into "
        "unifying spatial equity indicators.\n"
        "4. Data Enclosure & Opacity: Proprietary APIs restrict bulk geospatial queries, prevent local geometry extraction, and prohibit "
        "unsupervised machine learning clustering of neighbourhood typologies."
    )
    doc.add_paragraph(
        "The motivation of Smart Yeshwanthpur GIS is to bridge this critical gap by delivering a fully open-source, scientifically "
        "transparent geospatial platform that combines OpenStreetMap multigraphs, 250m metric spatial grids, graph-theoretic centrality, "
        "and unsupervised machine learning into an accessible, interactive decision-support interface."
    )

    # --------------------------------------------------------------------------
    # 6. OBJECTIVES & ANALYTICAL SCOPE
    # --------------------------------------------------------------------------
    doc.add_heading("6. Project Objectives & Analytical Scope", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The project is structured around seven primary technical objectives:"
    )
    doc.add_paragraph(
        "• Objective 1 (Road Network Extraction & Cleaning): Ingest and clean the complete drivable road network of Yeshwanthpur from "
        "OpenStreetMap, standardizing hierarchical classifications into eight physical road tiers and enforcing strict topological "
        "connectivity.\n"
        "• Objective 2 (Healthcare Infrastructure Profiling): Extract, geocode, validate, and categorize all healthcare amenities "
        "(hospitals, general clinics, specialty clinics, pharmacies) within a 2.5 km study radius.\n"
        "• Objective 3 (Network Topology & Centrality Diagnostics): Compute physical intersection densities, node degrees, and edge "
        "betweenness centrality to isolate critical structural bottleneck corridors.\n"
        "• Objective 4 (Dijkstra Shortest Path & Circuity Quantification): Implement graph-theoretic routing to compute optimal "
        "driving paths, travel times, and quantify circuity factors against straight-line Euclidean benchmarks.\n"
        "• Objective 5 (Spatial Grid Accessibility Modeling): Discretize the 19.60 km² study area into a regular 250m × 250m metric grid "
        "to calculate local road densities, nearest-hospital distances, population-weighted accessibility, and service deficit hotspots.\n"
        "• Objective 6 (Unsupervised Spatial Machine Learning): Develop a K-Means clustering and Principal Component Analysis (PCA) pipeline "
        "to uncover latent socio-spatial neighbourhood typologies across the urban fabric.\n"
        "• Objective 7 (Full-Stack Interactive Dashboard): Deploy an enterprise-grade Streamlit web application providing interactive Folium "
        "maps, Plotly telemetry, turn-by-turn routing tables, and full GIS data export (GeoPackage, GeoJSON, CSV)."
    )

    # --------------------------------------------------------------------------
    # 7. STUDY AREA DELINEATION & SPATIAL PARAMETERS
    # --------------------------------------------------------------------------
    doc.add_heading("7. Study Area Delineation & Spatial Parameters", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The analytical boundary is established as a 2,500-meter (2.5 km) metric radial buffer centered at Latitude 13.02850° N and "
        "Longitude 77.54000° E (the historic Yeshwanthpur Circle intersection). This boundary encapsulates approximately 19.60 sq km "
        "(1,960.34 hectares) of complex urban terrain spanning BBMP North Zone administrative wards, key industrial estates (Peenya "
        "transition perimeter), major institutional complexes (Indian Institute of Science / IISc western edge), and residential "
        "neighbourhoods (Subhash Nagar, Mattikere, Goraguntepalya, and Malleshwaram northern fringes)."
    )
    doc.add_paragraph(
        "To guarantee sub-meter spatial measurement accuracy for road lengths, Euclidean buffers, and grid cell areas, all spatial "
        "operations are projected into EPSG:32643 (WGS 84 / UTM Zone 43N). Geographical exchange, Leaflet web maps, and GeoJSON outputs "
        "are transformed into standard EPSG:4326 (WGS 84 decimal degrees)."
    )

    add_styled_table(doc, TABLE_1_DATA, col_widths=[2.8, 4.4])
    doc.add_paragraph("Table 1: Study Area Geographical and Spatial Reference Parameters").runs[0].font.italic = True

    # --------------------------------------------------------------------------
    # 8. DATA SOURCES & SPATIAL DATA INGESTION
    # --------------------------------------------------------------------------
    doc.add_heading("8. Data Sources & Spatial Data Ingestion", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "Data collection is implemented via automated Python pipelines querying OpenStreetMap APIs with embedded error-handling, "
        "exponential backoff retries, and local caching:\n"
        "1. Drivable Road Multigraph: Extracted using OSMnx (ox.graph_from_point) configured for network_type='drive' within a 2,500m "
        "buffer. The raw ingestion captures 15,798 directed edges, 5,924 nodes, elevation tags where present, one-way constraints, "
        "and physical lane attributes.\n"
        "2. Healthcare Amenity Geometry: Queried through the Overpass API using structured key-value filters including "
        "['amenity'~'hospital|clinic|pharmacy|doctors|health_post'] and ['healthcare'~'hospital|clinic|doctor']. Raw JSON responses "
        "are parsed into GeoPandas GeoDataFrames containing spatial Point geometries, facility names, operator tags, addresses, and OSM identifiers.\n"
        "3. Demographic Attribution: Ward-level census records from the 2011 Census of India projected to 2024 urban growth estimates "
        "(average density of ~14,200 residents/km²) were allocated to spatial grid cells using land-use residential weighting, yielding "
        "an estimated resident population of 278,532 individuals across the study buffer."
    )

    # --------------------------------------------------------------------------
    # 9. TECHNOLOGY STACK & SOFTWARE ECOSYSTEM
    # --------------------------------------------------------------------------
    doc.add_heading("9. Technology Stack & Software Ecosystem", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The application is engineered in Python 3.12 utilizing an industry-standard geospatial, scientific, and web visualization stack:"
    )
    tech_items = [
        ("Python 3.12:", "Core programming runtime providing modern typing, performance enhancements, and async support."),
        ("GeoPandas & Shapely:", "Vector geospatial data processing, geometric planar transformations, spatial joins, and buffering."),
        ("OSMnx:", "Extraction, projection, and topological modeling of street networks directly from OpenStreetMap."),
        ("NetworkX:", "Graph theoretical modeling, betweenness centrality computation, and Dijkstra shortest path pathfinding."),
        ("PyProj & Pyogrio:", "High-performance cartographic projection engines and vector I/O for GeoPackage and GeoJSON formats."),
        ("Scikit-Learn:", "Unsupervised machine learning algorithms: StandardScaler, KMeans, PCA, and silhouette scoring."),
        ("Streamlit:", "Enterprise-grade web application framework powering the interactive multi-page dashboard."),
        ("Folium & Leaflet.js:", "Interactive, pan-and-zoom dynamic map canvases with custom markers, bounding boxes, and GeoJSON overlays."),
        ("Plotly Express & Graph Objects:", "Interactive, publication-quality telemetry charts, histograms, donuts, and scatter plots."),
        ("Pytest:", "Automated unit testing suite validating coordinates, routing integrity, and data schema consistency (15/15 tests passing).")
    ]
    for lib, desc in tech_items:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_after = Pt(3)
        run_lb = p_t.add_run(f"• {lib:<24} ")
        run_lb.font.bold = True
        run_lb.font.color.rgb = RGBColor(15, 43, 72)
        p_t.add_run(desc).font.size = Pt(10)

    # --------------------------------------------------------------------------
    # 10. SYSTEM ARCHITECTURE & END-TO-END PIPELINE
    # --------------------------------------------------------------------------
    doc.add_heading("10. System Architecture & End-to-End Pipeline", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The Smart Yeshwanthpur GIS system architecture is structured as a five-tier decoupled pipeline (illustrated in Figure 1). "
        "The architecture enforces strict separation of concerns, ensuring immutable raw data storage, standardized metric intermediate layers, "
        "and rapid client-side rendering."
    )
    add_figure_with_caption(
        doc,
        FIG_DIR / "fig01_system_architecture.png",
        "Figure 1: Smart Yeshwanthpur GIS End-to-End System Architecture Pipeline.",
        width_inches=6.4
    )
    doc.add_paragraph(
        "• Tier 1 (Data Ingestion Layer): OSMnx and Overpass APIs fetch road multigraphs and healthcare POIs, persisting raw copies to data/raw/.\n"
        "• Tier 2 (Geospatial Preprocessing Layer): Validates geometries, cleans invalid coordinates, standardizes highway tags, and projects layers to EPSG:32643 UTM Zone 43N.\n"
        "• Tier 3 (Dual Analytical Engines): Executes parallel graph topological analysis (betweenness centrality, intersection counts) and spatial grid modeling (250m tessellation, KDTree nearest hospital lookup).\n"
        "• Tier 4 (Machine Learning Layer): Normalizes 5 spatial features, optimizes cluster count via Silhouette and Elbow evaluation, fits K-Means (k=5), and applies 2D PCA.\n"
        "• Tier 5 (Interactive Delivery Layer): Streams analytical datasets to a multi-page Streamlit application supported by Folium maps, Plotly charts, and downloadable GeoPackages."
    )

    # --------------------------------------------------------------------------
    # 11. GEOSPATIAL PREPROCESSING & TOPOLOGY STANDARDIZATION
    # --------------------------------------------------------------------------
    doc.add_heading("11. Geospatial Preprocessing & Topology Standardization", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "Raw OpenStreetMap data exhibits significant attribute heterogeneity and occasional geometric anomalies that mandate rigorous preprocessing:\n"
        "1. Geometry Validation & Repair: Geometries are checked for validity using Shapely's is_valid predicate. Zero-length line strings "
        "and duplicate vertices are pruned.\n"
        "2. Coordinate Bounds Enforcement: All amenities and road nodes must fall strictly within the 2.5 km bounding box. Records with inverted "
        "latitude/longitude or coordinates outside Southern India are purged.\n"
        "3. Road Hierarchy Consolidation: Over 35 raw OSM 'highway' tags are normalized into eight standardized urban tiers: Highway/Expressway, "
        "Primary Arterial, Major Arterial, Secondary Collector, Tertiary Road, Residential Street, Living Street, and Local Road.\n"
        "4. Free-Flow Urban Speed Assignment: Design speeds reflecting Bangalore urban traffic conditions are assigned to each tier (50 km/h for elevated "
        "expressways down to 15 km/h for living streets) to calculate edge traversal travel times.\n"
        "5. Amenity Deduplication: Healthcare records within a 15-meter spatial proximity sharing identical or near-identical normalized names are "
        "merged to prevent duplicate clinic counts."
    )

    # --------------------------------------------------------------------------
    # 12. COMPREHENSIVE ANALYTICAL METHODOLOGY
    # --------------------------------------------------------------------------
    doc.add_heading("12. Comprehensive Analytical Methodology", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The analytical methodology operates through four sequential analytical workflows:\n"
        "Workflow A: Topological Graph Theory. Road geometries are transformed into a directed multigraph G = (V, E, W), where V represents "
        "physical street junctions, E represents drivable road segments, and W represents weight attributes (length in meters, travel time in seconds).\n"
        "Workflow B: Metric Spatial Tessellation. A regular grid of 250m × 250m square cells (6.25 hectares per cell) is generated across the study "
        "polygon. Each cell aggregates local road length, intersection count, resident population, and healthcare POIs.\n"
        "Workflow C: Proximity Matrix & Accessibility Scoring. Using a KDTree spatial index, the straight-line Euclidean distance from every cell "
        "centroid to the nearest hospital is computed. In parallel, a composite accessibility score (0 to 100) is formulated based on proximity, "
        "facility density, and road connectivity.\n"
        "Workflow D: Unsupervised Spatial Classification. Spatial features are standardized to zero mean and unit variance. K-Means clustering is "
        "trained across k in [2, 7], and the optimal cluster structure is validated using Silhouette maximization and Principal Component Analysis."
    )

    # --------------------------------------------------------------------------
    # 13. ROAD NETWORK ANALYSIS & STRUCTURAL CENTRALITY
    # --------------------------------------------------------------------------
    doc.add_heading("13. Road Network Analysis & Structural Centrality", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The extracted road network comprises 15,798 edges and 5,924 nodes spanning 983.52 km of cumulative drivable streets. As shown in "
        "Table 3 and Figure 2, the street network is overwhelmingly dominated by Residential Streets (12,494 segments, accounting for 720.51 km "
        "or 73.26% of total road length), followed by Tertiary Roads (2,058 segments, 136.96 km, 13.92%). Arterial corridors and expressways "
        "constitute less than 5% of total road length but carry the majority of inter-district freight and vehicular throughput."
    )

    add_figure_with_caption(
        doc,
        FIG_DIR / "fig02_road_network_hierarchy.png",
        "Figure 2: Road Network Street Hierarchy & Spatial Topology across Yeshwanthpur.",
        width_inches=5.8
    )

    add_figure_with_caption(
        doc,
        FIG_DIR / "fig03_road_category_distribution.png",
        "Figure 3: Road Hierarchy Breakdown by Segment Counts and Cumulative Kilometers.",
        width_inches=6.2
    )

    add_styled_table(doc, TABLE_3_DATA, col_widths=[2.4, 1.4, 1.4, 1.2, 1.2])
    doc.add_paragraph("Table 3: Road Network Classification Hierarchy and Physical Characteristics").runs[0].font.italic = True

    add_styled_table(doc, TABLE_4_DATA, col_widths=[2.4, 1.6, 3.4])
    doc.add_paragraph("Table 4: Topological Graph Structural Metrics").runs[0].font.italic = True

    doc.add_paragraph(
        "Structural Centrality & Bottlenecks: Edge Betweenness Centrality quantifies the frequency with which a road segment falls on the shortest "
        "paths between all pairs of nodes in the network: \n"
        "C_B(e) = sum_{s != t} (sigma_{st}(e) / sigma_{st})\n"
        "where sigma_{st} is the total number of shortest paths between nodes s and t, and sigma_{st}(e) is the number of those paths passing through edge e. "
        "As visualized in Figure 4, the top 5% betweenness corridors (794 segments, threshold >= 0.05847) concentrate intensely along the Tumkur Road elevated "
        "highway approaches, the Yeshwanthpur flyover interchange, and the Subhash Nagar railway perimeter connectors. These corridors represent structural "
        "pinch points: any physical obstruction or construction on these links triggers disproportionate network-wide gridlock."
    )

    add_figure_with_caption(
        doc,
        FIG_DIR / "fig04_betweenness_centrality.png",
        "Figure 4: Topological Betweenness Centrality & Critical Network Bottleneck Corridors.",
        width_inches=5.8
    )

    # --------------------------------------------------------------------------
    # 14. SHORTEST PATH GRAPH ALGORITHMS (DIJKSTRA IMPLEMENTATION)
    # --------------------------------------------------------------------------
    doc.add_heading("14. Shortest Path Graph Algorithms (Dijkstra Implementation)", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "Shortest-path pathfinding is implemented using Dijkstra's Algorithm over the directed Multigraph G = (V, E, W). Dijkstra's algorithm "
        "computes the single-source shortest path to all vertices by maintaining a set of visited vertices and iteratively relaxing the edges "
        "incident to the vertex with the minimum tentative distance. In our implementation, a min-priority queue (binary heap) achieves an optimal "
        "computational complexity of O(|E| + |V| log |V|)."
    )
    doc.add_paragraph(
        "The relaxation condition is formalized as: \n"
        "if dist[u] + weight(u, v) < dist[v]:\n"
        "    dist[v] = dist[u] + weight(u, v)\n"
        "    predecessor[v] = u\n"
        "where weight(u, v) is dynamically selectable as either physical length L_{uv} (meters) or free-flow travel time T_{uv} = L_{uv} / v_{uv} (seconds)."
    )
    doc.add_paragraph(
        "Coordinate Snapping & Circuity Factor: To route between arbitrary geographic coordinates, origin and destination points are snapped to "
        "their nearest network nodes using spatial Euclidean distance: \n"
        "v_snap = argmin_{u in V} dist(x_query, u)\n"
        "Circuity Factor (CF) is computed as the ratio of actual driving network distance to Euclidean straight-line distance:\n"
        "CF = d_network(orig, dest) / d_haversine(orig, dest)\n"
        "As documented in Table 5 and visualized in Figure 5, traversing from Yeshwanthpur Railway Station to the APMC Yard Market Corridor yields a "
        "straight-line distance of 1.32 km but requires an actual driving distance of 4.71 km—a massive Circuity Factor of 3.58x. This empirical finding "
        "proves the severe barrier effect of the railway marshalling yard, which forces vehicles into extensive peripheral detours."
    )

    add_figure_with_caption(
        doc,
        FIG_DIR / "fig05_shortest_path_routing.png",
        "Figure 5: Dijkstra Shortest Path vs. Straight-Line Euclidean Distance Routing.",
        width_inches=5.8
    )

    add_styled_table(doc, TABLE_5_DATA, col_widths=[1.8, 1.8, 1.1, 1.1, 0.9, 0.9])
    doc.add_paragraph("Table 5: Empirical Shortest Route Comparison (Dijkstra vs. Euclidean Straight-Line)").runs[0].font.italic = True

    # --------------------------------------------------------------------------
    # 15. HEALTHCARE FACILITY INVENTORY & SPATIAL DISTRIBUTION
    # --------------------------------------------------------------------------
    doc.add_heading("15. Healthcare Facility Inventory & Spatial Distribution", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The healthcare audit identified and validated 84 healthcare amenities within the 2.5 km study buffer. As broken down in Table 2 and "
        "Figure 7, the infrastructure comprises 37 Hospitals (44.0%), 32 Pharmacies (38.1%), 13 Outpatient Clinics (15.5%), and 2 Specialist "
        "Doctor Chambers (2.4%). The spatial distribution (Figure 6) reveals intense agglomeration along major arterial corridors—notably Dr. "
        "Rajkumar Road and Tumkur Road—where major tertiary facilities (e.g., Sparsh Hospital, Columbia Asia/Manipal Hospital) operate. Conversely, "
        "the north-western industrial sectors and peripheral residential pockets exhibit a notable absence of inpatient hospital infrastructure, "
        "relying almost exclusively on small retail pharmacies."
    )

    add_figure_with_caption(
        doc,
        FIG_DIR / "fig06_healthcare_distribution.png",
        "Figure 6: Spatial Distribution of Healthcare Amenities & 1.0 km Hospital Service Buffers.",
        width_inches=5.8
    )

    add_figure_with_caption(
        doc,
        FIG_DIR / "fig07_healthcare_category_mix.png",
        "Figure 7: Healthcare Amenity Composition & Clinical Mix Donut Chart.",
        width_inches=4.8
    )

    add_styled_table(doc, TABLE_2_DATA, col_widths=[2.4, 0.8, 1.1, 3.1])
    doc.add_paragraph("Table 2: Healthcare Infrastructure Classification Breakdown").runs[0].font.italic = True

    # --------------------------------------------------------------------------
    # 16. HEALTHCARE ACCESSIBILITY & METRIC SPATIAL GRID MODELING
    # --------------------------------------------------------------------------
    doc.add_heading("16. Healthcare Accessibility & Metric Spatial Grid Modeling", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "To evaluate territorial coverage beyond point locations, the study area was discretized into a 250m × 250m regular metric spatial grid "
        "consisting of 344 active cells. For each grid cell c, an empirical Accessibility Score S_c in [0, 100] was computed using a multi-criteria "
        "weighted formulation: \n"
        "S_c = w_1 * ProximityScore(d_hosp) + w_2 * DensityScore(N_facilities) + w_3 * ConnectivityScore(rho_road)\n"
        "where ProximityScore decays inversely with distance to the nearest hospital, DensityScore rewards local primary clinics and pharmacies, "
        "and ConnectivityScore incorporates local road density."
    )
    doc.add_paragraph(
        "As summarized in Table 6 and mapped in Figure 8, 313 cells (91.0% of the study area; 254,580 estimated residents) fall into the High "
        "Accessibility Tier (< 1.0 km straight-line hospital distance). The remaining 31 cells (9.0%; 23,952 residents) exhibit Moderate Accessibility "
        "(1.0 km to 2.0 km). Crucially, zero cells exceed the 2.0 km threshold as the crow flies. However, when actual driving detours are modeled, "
        "the peripheral cells identified in Table 7 record driving distances exceeding 2.0 km to 2.8 km, establishing them as priority candidate "
        "locations for new Urban Primary Health Centers (UPHCs)."
    )

    add_figure_with_caption(
        doc,
        FIG_DIR / "fig08_spatial_grid_accessibility.png",
        "Figure 8: 250m Metric Spatial Grid Healthcare Accessibility Choropleth.",
        width_inches=5.8
    )

    add_styled_table(doc, TABLE_6_DATA, col_widths=[2.0, 2.0, 1.2, 1.2, 1.6])
    doc.add_paragraph("Table 6: 250m Spatial Grid Healthcare Accessibility Coverage Tiers").runs[0].font.italic = True

    add_styled_table(doc, TABLE_7_DATA, col_widths=[1.4, 1.4, 1.5, 1.5, 2.0])
    doc.add_paragraph("Table 7: Priority Healthcare Deficit Zones (Candidate Locations for Expansion)").runs[0].font.italic = True

    # --------------------------------------------------------------------------
    # 17. INTERACTIVE STREAMLIT WEB APPLICATION FEATURES
    # --------------------------------------------------------------------------
    doc.add_heading("17. Interactive Streamlit Web Application Features", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The project is operationalized as an interactive, multi-page Streamlit web application structured into seven analytical modules:\n"
        "• 01 Overview: Executive telemetry cards, interactive study area boundary map, consolidated road kilometers, and healthcare POI summaries.\n"
        "• 02 Road Network Analysis: Interactive road classification filter, street hierarchy bar charts, intersection density indicators, and betweenness bottleneck overlays.\n"
        "• 03 Route Analysis: Dijkstra origin-destination routing engine with landmark dropdowns and custom coordinate inputs, driving route polylines, straight-line circuity comparisons, and step-by-step turn-by-turn road segment breakdown tables.\n"
        "• 04 Healthcare Analysis: Categorical facility filter, live text search (by hospital name or street address), 1.0 km Euclidean hospital buffer toggle, and interactive directory tables.\n"
        "• 05 Accessibility Analysis: 250m spatial grid choropleth map with dual color schemes (Accessibility Tiers vs. Composite Score), nearest-facility coordinate lookup, and candidate expansion zone rankings.\n"
        "• 06 Machine Learning: Interactive K-Means cluster explorer, Elbow and Silhouette score curves, 2D PCA cluster projection, and cluster feature comparison tables.\n"
        "• 07 Insights: Dynamically computed policy diagnostics, 90th percentile density extremes, railway yard severance findings, and urban planning recommendations."
    )

    # --------------------------------------------------------------------------
    # 18. APPLICATION INTERFACE ARCHITECTURE & VISUALIZATIONS
    # --------------------------------------------------------------------------
    doc.add_heading("18. Application Interface Architecture & Visualizations", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The interface follows a clean, professional dark sidebar and clean light canvas theme (illustrated in Figure 12). "
        "The sidebar maintains the Smart Yeshwanthpur brand identity, study area metadata, and intuitive multi-page navigation. "
        "The main dashboard layout integrates KPI cards at the top, interactive Folium mapping canvases with responsive viewports, "
        "Plotly telemetry panels on the right flank, and downloadable GeoPackage/GeoJSON export buttons at the bottom."
    )
    add_figure_with_caption(
        doc,
        FIG_DIR / "fig12_dashboard_overview.png",
        "Figure 12: Streamlit Interactive GIS Dashboard User Interface & Layout Architecture.",
        width_inches=6.4
    )

    # --------------------------------------------------------------------------
    # 19. EMPIRICAL RESULTS, KEY FINDINGS & DISCUSSION
    # --------------------------------------------------------------------------
    doc.add_heading("19. Empirical Results, Key Findings & Discussion", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The empirical findings demonstrate two profound spatial realities across Yeshwanthpur:\n"
        "1. Disconnect Between Density and Permeability: With a road density of 50.17 km/km² and an intersection density of 244.45/km², "
        "Yeshwanthpur appears exceptionally well-connected on paper. However, graph analysis proves that over 73% of the network consists of "
        "narrow residential streets and cul-de-sacs (1,037 dead-ends) incapable of absorbing vehicular throughput. Traffic is funneled onto "
        "a tiny fraction of high-betweenness corridors (794 segments), creating severe systemic vulnerability.\n"
        "2. Infrastructure Barrier Severance: The Yeshwanthpur railway yard acts as a massive linear barrier. While straight-line hospital distances "
        "average a modest 532.4 meters across the study area, east-west vehicular trips experience circuity factors ranging from 1.34x to 3.58x. "
        "This severely impairs emergency medical vehicle transit, demonstrating that straight-line Euclidean distance is an invalid proxy for "
        "urban emergency healthcare accessibility in barrier-dense cities."
    )

    # --------------------------------------------------------------------------
    # 20. UNSUPERVISED MACHINE LEARNING & SPATIAL TYPOLOGIES
    # --------------------------------------------------------------------------
    doc.add_heading("20. Unsupervised Machine Learning & Spatial Typologies (K-Means & PCA)", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "To discover objective spatial typologies without manual bias, an unsupervised Machine Learning pipeline was developed. "
        "Five standardized spatial features were extracted for each of the 344 grid cells: (1) road_density_km_sqkm, (2) intersection_density_per_sqkm, "
        "(3) nearest_hosp_dist_m, (4) total_healthcare_count, and (5) accessibility_score. All features were normalized using scikit-learn's "
        "StandardScaler.\n"
        "Model Selection & Validation: K-Means was evaluated across k in [2, 7]. As demonstrated in Figure 9, the Elbow Curve shows diminishing "
        "inertia reductions after k=5 (inertia: 485.99), while the Silhouette Coefficient achieves its global peak at k=5 with a score of 0.392."
    )

    add_figure_with_caption(
        doc,
        FIG_DIR / "fig09_kmeans_evaluation.png",
        "Figure 9: Unsupervised K-Means Clustering Evaluation (Elbow Inertia & Silhouette Curves).",
        width_inches=6.2
    )

    doc.add_paragraph(
        "Principal Component Analysis (PCA): Dimensionality reduction was applied to project the 5-dimensional feature space into 2 orthogonal axes. "
        "PC1 explains 55.1% of the total variance (dominated by road and intersection density), while PC2 explains 28.3% (dominated by hospital distance "
        "and accessibility score), capturing a cumulative 83.4% of total dataset variance (Figure 10). The spatial mapping of these clusters (Figure 11 "
        "and Table 8) uncovers five distinct urban typologies across Yeshwanthpur."
    )

    add_figure_with_caption(
        doc,
        FIG_DIR / "fig10_pca_cluster_projection.png",
        "Figure 10: 2D Principal Component Analysis (PCA) Cluster Projection.",
        width_inches=5.6
    )

    add_figure_with_caption(
        doc,
        FIG_DIR / "fig11_spatial_clusters_map.png",
        "Figure 11: Spatial Distribution of Discovered K-Means Neighbourhood Typologies.",
        width_inches=5.8
    )

    add_styled_table(doc, TABLE_8_DATA, col_widths=[1.1, 1.7, 0.7, 1.2, 1.2, 1.0, 3.2])
    doc.add_paragraph("Table 8: Unsupervised K-Means Cluster Characteristics & Sociodemographic Typologies").runs[0].font.italic = True

    # --------------------------------------------------------------------------
    # 21. DIFFERENTIATION FROM COMMERCIAL NAVIGATION PLATFORMS
    # --------------------------------------------------------------------------
    doc.add_heading("21. Differentiation from Commercial Navigation Platforms (Google Maps)", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "A common query in municipal technology development is why specialized GIS platforms are necessary given the ubiquity of Google Maps or "
        "MapMyIndia. It is critical to recognize that commercial mapping applications are optimized for consumer point-of-interest discovery and "
        "individual driver dispatch. They do not—and structurally cannot—serve as municipal spatial analytics tools. Table 9 articulates the fundamental "
        "architectural and operational distinctions between Smart Yeshwanthpur GIS, commercial navigation platforms, and traditional desktop GIS software."
    )

    add_styled_table(doc, TABLE_COMPARISON_DATA, col_widths=[1.8, 2.0, 2.0, 1.8])
    doc.add_paragraph("Table 9: Multi-Dimensional Comparison: Smart Yeshwanthpur GIS vs. Google Maps vs. Traditional Desktop GIS").runs[0].font.italic = True

    # --------------------------------------------------------------------------
    # 22. DATA GOVERNANCE, SCIENTIFIC ETHICS & ANALYTICAL DISCLAIMERS
    # --------------------------------------------------------------------------
    doc.add_heading("22. Data Governance, Scientific Ethics & Analytical Disclaimers", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "To uphold scientific integrity and prevent misinterpretation by municipal stakeholders, the platform enforces three strict governance principles:\n"
        "1. Topological Centrality vs. Empirical Live Congestion: Edge betweenness centrality is a purely structural property of the road network "
        "graph. It identifies where network bottlenecks exist based on topology. It does NOT measure real-time vehicle counts or sensor-derived "
        "speed delays, and must never be cited as live probe congestion.\n"
        "2. Healthcare Accessibility vs. Clinical Quality: The Accessibility Score measures spatial proximity and physical amenity density. It does "
        "not measure bed availability, ICU capacity, physician specializations, treatment costs, or clinical care quality.\n"
        "3. Circular Buffer vs. Administrative Boundary: The 2.5 km study buffer is an analytical convenience and does not correspond to official BBMP "
        "ward administrative boundaries. Administrative decision-makers must cross-reference findings with official BBMP ward gazettes."
    )

    # --------------------------------------------------------------------------
    # 23. TECHNICAL LIMITATIONS & DATA COMPLETENESS
    # --------------------------------------------------------------------------
    doc.add_heading("23. Technical Limitations & Data Completeness", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The technical execution operates under four documented constraints:\n"
        "• OpenStreetMap Contributor Completeness: While arterial and primary roads in Yeshwanthpur exhibit near 100% completeness on OSM, small private "
        "alleys and informal slum paths may be under-represented. Similarly, informal clinics operating in residential basements without commercial signage "
        "may be absent from OSM amenity databases.\n"
        "• Free-Flow Speed Assumptions: Edge traversal times are derived from hierarchical design speeds (15–50 km/h) rather than dynamic floating-car "
        "data (FCD). Peak-hour congestion will increase real-world travel times beyond the modeled free-flow baseline.\n"
        "• Planar 2D Graph Assumptions: While flyovers are modeled with separate non-intersecting edges, complex multilevel ramp merges are simplified "
        "to planar graph representations.\n"
        "• Unsupervised ML Interpretation: K-Means clustering discovers mathematical patterns in feature space; cluster labels are descriptive typologies "
        "and do not imply predictive causality."
    )

    # --------------------------------------------------------------------------
    # 24. FUTURE ROADMAP & PROPOSED ENHANCEMENTS
    # --------------------------------------------------------------------------
    doc.add_heading("24. Future Roadmap & Proposed Enhancements", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The platform architecture is designed for modular scalability. Recommended future technical milestones include:\n"
        "1. Real-Time Transit Data Integration: Ingesting live General Transit Feed Specification (GTFS-RT) feeds from Bangalore Metropolitan Transport "
        "Corporation (BMTC) and Namma Metro to compute multi-modal public transit isochrones.\n"
        "2. Dynamic Floating-Car Telemetry: Integrating open probe data (e.g., Uber Movement or TomTom Traffic API) to replace free-flow speeds with "
        "time-of-day dynamic impedance weights.\n"
        "3. Two-Step Floating Catchment Area (2SFCA): Implementing 2SFCA accessibility modeling incorporating verified hospital bed capacities and "
        "physician counts against granular census block demand.\n"
        "4. Multimodal Pedestrian Network Modeling: Extracting footways, skywalks, and metro station subways to model non-motorized first/last-mile "
        "access for low-income residents.\n"
        "5. City-Wide Spatial Scaling: Expanding the automated pipeline to cover all 198 BBMP wards across the 712 sq km Greater Bangalore metropolitan area."
    )

    # --------------------------------------------------------------------------
    # 25. PRACTICAL POLICY IMPLICATIONS & URBAN PLANNING DIAGNOSTICS
    # --------------------------------------------------------------------------
    doc.add_heading("25. Practical Policy Implications & Urban Planning Diagnostics", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "The empirical findings translate into four actionable policy recommendations for BBMP and Bangalore Smart City planners:\n"
        "• Recommendation 1 (Targeted UPHC Placement): Establish 24/7 Primary Urban Health Centers in Grid Cells GRID_0151 and GRID_0131 (north-western "
        "peripheral cells) where hospital driving distances exceed 2.0 km.\n"
        "• Recommendation 2 (Railway Yard Permeability Corridors): Construct grade-separated pedestrian and light-ambulance underpasses beneath the "
        "Yeshwanthpur railway yard connecting Subhash Nagar to Dr. Rajkumar Road, collapsing the 3.58x circuity detour.\n"
        "• Recommendation 3 (Bottleneck Protection & ITS Enforcement): Deploy Intelligent Transportation Systems (ITS) and strict anti-encroachment "
        "enforcement on the 794 bottleneck segments identified in Figure 4 along Tumkur Road approaches.\n"
        "• Recommendation 4 (Feeder Transit Buffers): Introduce electric feeder mini-buses connecting Mattikere and peripheral residential cells to "
        "the Yeshwanthpur Metro interchange to alleviate private vehicular congestion."
    )

    # --------------------------------------------------------------------------
    # 26. TECHNICAL CONCLUSION
    # --------------------------------------------------------------------------
    doc.add_heading("26. Technical Conclusion", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    doc.add_paragraph(
        "Smart Yeshwanthpur GIS establishes an open-source, scientifically validated spatial analytics platform tailored to the complex infrastructure "
        "realities of urban India. By moving beyond naive straight-line assumptions and black-box commercial tools, the project provides municipal "
        "authorities with empirical, mathematically defensible insights into road network vulnerability and healthcare equity. The system successfully "
        "models 15,798 road segments, isolates 794 structural bottlenecks, evaluates 84 healthcare amenities across 344 metric grid cells, quantifies "
        "severe circuity detours imposed by the railway yard, and uncovers five distinct neighbourhood typologies through unsupervised machine learning. "
        "Deployed as an interactive Streamlit application with complete GIS vector data exports, the platform stands as a robust, extensible prototype "
        "for data-driven smart city governance in Bengaluru and across expanding Global South metropolises."
    )

    # --------------------------------------------------------------------------
    # 27. REFERENCES & ACADEMIC CITATIONS
    # --------------------------------------------------------------------------
    doc.add_heading("27. References & Academic Citations", level=1).runs[0].font.color.rgb = RGBColor(15, 43, 72)
    refs = [
        "1. Boeing, G. (2017). 'OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks.' Computers, Environment and Urban Systems, 65, 126-139.",
        "2. Dijkstra, E. W. (1959). 'A note on two problems in connexion with graphs.' Numerische Mathematik, 1(1), 269-271.",
        "3. Haggett, P., & Chorley, R. J. (1969). Network Analysis in Geography. St. Martin's Press, New York.",
        "4. Freeman, L. C. (1977). 'A set of measures of centrality based on betweenness.' Sociometry, 40(1), 35-41.",
        "5. Luo, W., & Wang, F. (2003). 'Measures of spatial accessibility to health care in a GIS environment: synthesis of a GIS-based two-step floating catchment area method.' Annals of the Association of American Geographers, 93(4), 865-884.",
        "6. OpenStreetMap Contributors. (2026). Planet dump [Data file from OpenStreetMap]. Available at: https://www.openstreetmap.org/copyright.",
        "7. Bruhat Bengaluru Mahanagara Palike (BBMP). (2024). Revised Master Plan & Ward Demographics Report. Urban Development Department, Government of Karnataka.",
        "8. World Health Organization (WHO). (2015). 'Access to Healthcare in Rapidly Growing Urban Settlements: Methodological Guidelines.' WHO Technical Report Series.",
        "9. McKinney, W. (2010). 'Data structures for statistical computing in Python.' Proceedings of the 9th Python in Science Conference, 445, 51-56.",
        "10. Pedregosa, F., et al. (2011). 'Scikit-learn: Machine learning in Python.' Journal of Machine Learning Research, 12, 2825-2830.",
        "11. Jordahl, K., et al. (2020). 'geopandas/geopandas: v0.8.1.' Zenodo. doi:10.5281/zenodo.3946761.",
        "12. Streamlit Inc. (2026). Streamlit Documentation: Modern Web Applications for Data Science. Available at: https://docs.streamlit.io/."
    ]
    for r in refs:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_after = Pt(4)
        p_r.add_run(r).font.size = Pt(8.8)

    # Save Word Document
    doc.save(DOCX_OUT)
    print(f"Editable Word Document successfully created at: {DOCX_OUT}")

if __name__ == "__main__":
    main()
