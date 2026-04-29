import geopandas as gpd 
from sqlalchemy import create_engine 
from shapely.geometry import MultiPolygon, Polygon

# Database connection parameters 
host = "localhost" 
port = "5432" 
dbname = "environmental_setup" 
user = "postgres" 
password = "zeroeyteen018" 

# Create the database engine 
conn_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}" 
engine = create_engine(conn_str)

# 1. Load basic parcel data
sql_parcel_base = "SELECT parcel_pin, ST_Transform(geom, 3395) as geom FROM public.parcel"
parcel = gpd.read_postgis(sql_parcel_base, engine, geom_col='geom')
parcel['total_area'] = parcel.geometry.area 

# 2. Run the Spatial Overlay Query 
sql_overlay = """ 
WITH overlay AS ( 
    SELECT 
        p.parcel_pin, 
        l.name, 
        ST_Intersection(ST_MakeValid(p.geom), ST_MakeValid(l.geom)) AS intersect_geom 
    FROM public.parcel p 
    JOIN public.landuse l 
    ON ST_Intersects(p.geom, l.geom) 
) 
SELECT 
    parcel_pin, 
    name, 
    ST_Transform(intersect_geom, 3395) AS geom, 
    ST_Area(ST_Transform(intersect_geom, 3395)) AS landuse_area 
FROM overlay 
""" 

# Fetch results - Note: geom_col must match the alias 'geom' in your SELECT statement
overlay_result = gpd.read_postgis(sql_overlay, engine, geom_col='geom') 

# 3. Calculate Percentages
overlay_result = overlay_result.merge(parcel[['parcel_pin', 'total_area']], on='parcel_pin') 
overlay_result['percentage'] = round((overlay_result['landuse_area'] / overlay_result['total_area']) * 100, 2)

# --- FIXES START HERE ---

# 1. Use 'geom' because that is the column name returned by your SQL query
overlay_result = overlay_result.set_geometry('geom') 

# 2. Ensure CRS is set to World Mercator (3395) so PostGIS recognizes it
overlay_result.set_crs(epsg=3395, allow_override=True, inplace=True)

# 3. Optional: Cast all geometries to MultiPolygon 
# (PostGIS often complains if a table has a mix of Polygon and MultiPolygon)
overlay_result['geom'] = [MultiPolygon([feature]) if isinstance(feature, Polygon) else feature for feature in overlay_result['geom']]

# 4. Save the result
overlay_result.to_postgis(
    'parcel_landuse_percentage', 
    engine, 
    if_exists='replace', 
    index=True,
    index_label='id'
) 

print("Success! Data saved to table 'parcel_landuse_percentage'.")
print(overlay_result.head())