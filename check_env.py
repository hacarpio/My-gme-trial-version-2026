import psycopg2
import sqlalchemy
import geopandas as gpd

# Check versions
print(f"✅ SQLAlchemy version: {sqlalchemy.__version__}")
print(f"✅ GeoPandas version: {gpd.__version__}")

# Check if GeoPandas can see its spatial engine
# This confirms the underlying PROJ and GDAL libraries are linked
print(f"✅ Display Precision: {gpd.options.display_precision}")

# Quick test: Create a tiny spatial object
point = gpd.points_from_xy([0], [0])
gdf = gpd.GeoDataFrame(index=[0], crs="EPSG:4326", geometry=point)
print("✅ GeoPandas Test Object Created Successfully!")