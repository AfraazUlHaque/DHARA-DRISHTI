import matplotlib
matplotlib.use('Agg')
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs('outputs/maps', exist_ok=True)

with rasterio.open("Murredu_DEM_clip.tif") as src:
    dem = src.read(1).astype("float32")
    profile = src.profile.copy()

    # Pixel size in degrees because DEM is in geographic CRS
    xres = abs(src.transform.a)
    yres = abs(src.transform.e)

# Convert degree resolution approximately to meters
# At Murredu latitude (~17.5°N)
lat = 17.5

meters_per_degree_lat = 111320
meters_per_degree_lon = 111320 * np.cos(np.radians(lat))

dx = xres * meters_per_degree_lon
dy = yres * meters_per_degree_lat

# Calculate elevation gradients
grad_y, grad_x = np.gradient(dem, dy, dx)

# Slope in degrees
slope = np.degrees(
    np.arctan(
        np.sqrt(grad_x**2 + grad_y**2)
    )
)

# Save slope
profile.update(
    dtype="float32",
    count=1,
    nodata=np.nan,
    compress="deflate"
)

with rasterio.open("Slope.tif", "w", **profile) as dst:
    dst.write(slope.astype("float32"), 1)

# Statistics
valid = slope[np.isfinite(slope)]

print("===================================")
print("        SLOPE ANALYSIS")
print("===================================")

print("Minimum slope:", np.min(valid), "degrees")
print("Maximum slope:", np.max(valid), "degrees")
print("Mean slope:", np.mean(valid), "degrees")

print("Slope map saved successfully!")
print("===================================")

# Display
plt.figure(figsize=(12, 8))

plt.imshow(
    slope,
    cmap="terrain",
    vmin=0,
    vmax=np.percentile(valid, 98)
)

plt.colorbar(label="Slope (degrees)")

plt.title("Murredu Watershed - Slope Map")

plt.axis("off")
plt.tight_layout()
plt.savefig('outputs/maps/slope_map.png', dpi=300, bbox_inches='tight')
# # plt.show()
