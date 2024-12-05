# Laura Rivera LR28372
# final project for ME 397: Too Big to Excel

# fetch grid region data from .shp file

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box

# from .fetch_hourly_generation_by_location import get_coordinates_from_city_state

# Load the shapefile
shapefile_path = r'us_state_geo_files\tl_2023_us_state.shp'
gdf = gpd.read_file(shapefile_path)

# Print the column names and the first few rows to inspect the data
print(gdf.columns)
print(gdf.head())

# Define the bounding box for the continental US
continental_us_bbox = box(-130, 24, -66, 50)  # (minx, miny, maxx, maxy)

# Filter the GeoDataFrame to include only the continental US
gdf_continental_us = gdf[gdf.geometry.within(continental_us_bbox)]

# Plot the map
fig, ax = plt.subplots(figsize=(10, 10))
gdf_continental_us.plot(ax=ax, color='lightblue', edgecolor='black')

# Add title and labels
ax.set_title('eGRID Subregions - Continental US')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Show the plot
plt.show()