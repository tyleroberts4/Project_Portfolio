import pandas as pd
import numpy as np

# 1. Define the geographic bounds of the continental US
lat_min, lat_max = 24.0, 50.0
lon_min, lon_max = -125.0, -66.5

# 2. Define the grid resolution (ERA5 native resolution ≈ 0.25°)
resolution = 0.25

# 3. Create evenly spaced latitude and longitude values
lats = np.arange(lat_min, lat_max + resolution, resolution)
lons = np.arange(lon_min, lon_max + resolution, resolution)

# 4. Create all possible (lat, lon) combinations
grid = [(lat, lon) for lat in lats for lon in lons]

# 5. Convert to a DataFrame
df = pd.DataFrame(grid, columns=["lat", "lon"])

# 6. Save to CSV
df.to_csv("era5_us_grid_0p25deg.csv", index=False)
