import geopandas as gpd
import pandas as pd
import random
from shapely.geometry import Point
from pathlib import Path
import sys

_SCRIPT_DIR = Path(__file__).resolve().parent
_DATA_DIR = _SCRIPT_DIR.parent / "data"
_SUBMISSION_ROOT = _SCRIPT_DIR.parent.parent

# The original project generates IECC zone geometry from a shapefile:
#   ClimateZoneDataFiles/ClimateZones.shp
# That shapefile is not included in this submission (report-ready outputs are).
shp = _SUBMISSION_ROOT / "ClimateZoneDataFiles" / "ClimateZones.shp"
if not shp.is_file():
    geojson_path = _DATA_DIR / "iecc_zones.geojson"
    points_path = _DATA_DIR / "iecc_zone_5points.csv"
    if geojson_path.is_file() and points_path.is_file():
        print(
            "ClimateZones.shp not included in the submission. "
            "Using pre-generated outputs from 06_climate_zone_analysis/data/ "
            f"(found: {geojson_path.name}, {points_path.name})."
        )
        sys.exit(0)
    raise FileNotFoundError(f"Missing required input shapefile: {shp}")

gdf = gpd.read_file(shp).to_crs(epsg=4326)

# CONUS filter (prevents Alaska/territories from warping centers)
rp = gdf.geometry.representative_point()
gdf = gdf[rp.y.between(24, 50) & rp.x.between(-125, -66)]

# Use Moisture21 when present, otherwise fall back to Moisture15
gdf["moist"] = gdf["Moisture21"].fillna(gdf["Moisture15"])

# Keep rows even if moisture is missing (Zone 7)
gdf = gdf.dropna(subset=["IECC21"])

# Build zone label:
# - Zones 1–6 keep moisture suffix (e.g., 4A, 6B)
# - Zone 7 is always just "7"
def build_zone(row):
    z = int(row["IECC21"])
    if z == 7:
        return "7"
    m = row["moist"]
    if pd.isna(m) or str(m).strip() == "":
        return str(z)
    return f"{z}{str(m).strip()}"

gdf["zone"] = gdf.apply(build_zone, axis=1)

# Dissolve counties into zone polygons
zones = gdf.dissolve(by="zone")

# Export zone polygons (GeoJSON) for Tableau
out_dir = _DATA_DIR
out_dir.mkdir(parents=True, exist_ok=True)

zones_out = zones.reset_index()[["zone", "geometry"]]
zones_out.to_file(out_dir / "iecc_zones.geojson", driver="GeoJSON")

# ---- 5 points per zone: 1 center + 4 seeded random interior points ----
random.seed(42)  # seeded = same random points every run

def random_interior_points(poly, n=4):
    minx, miny, maxx, maxy = poly.bounds
    pts = []
    while len(pts) < n:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if poly.contains(p):
            pts.append(p)
    return pts

rows = []

for zone, row in zones.iterrows():
    poly = row.geometry

    center = poly.representative_point()
    rows.append({"zone": zone, "sample": "center", "lat": center.y, "lon": center.x})

    for i, p in enumerate(random_interior_points(poly, n=4), start=1):
        rows.append({"zone": zone, "sample": f"rand{i}", "lat": p.y, "lon": p.x})

points_df = pd.DataFrame(rows).sort_values(["zone", "sample"])

print("Number of zones:", points_df["zone"].nunique())
print("Zones:", sorted(points_df["zone"].unique()))
print("Total points:", len(points_df))

out_csv = out_dir / "iecc_zone_5points.csv"
points_df.to_csv(out_csv, index=False)

print(f"CSV written to: {out_csv.resolve()}")
print(f"GeoJSON written to: {(out_dir / 'iecc_zones.geojson').resolve()}")

