import rasterio
import numpy as np

# Files
ndwi_file = "murredu_data/NDWI.tif"
water_output = "murredu_data/Water_Mask.tif"

with rasterio.open(ndwi_file) as src:
    ndwi = src.read(1).astype("float32")
    profile = src.profile.copy()

# Water detection
# NDWI > 0.20 = probable water
water = (ndwi > 0.20).astype("uint8")

# Save mask
profile.update(
    dtype="uint8",
    count=1,
    compress="deflate",
    nodata=0
)

with rasterio.open(water_output, "w", **profile) as dst:
    dst.write(water, 1)

# Statistics
water_pixels = np.sum(water == 1)
total_pixels = water.size

pixel_area_m2 = abs(profile["transform"].a * profile["transform"].e)

water_area_km2 = water_pixels * pixel_area_m2 / 1_000_000
water_percent = water_pixels / total_pixels * 100

print("\nWATER STATISTICS")
print("----------------")
print("Water pixels:", water_pixels)
print("Total pixels:", total_pixels)
print("Water coverage:", round(water_percent, 2), "%")
print("Estimated water area:", round(water_area_km2, 3), "km²")
print("\nWater mask saved:", water_output)