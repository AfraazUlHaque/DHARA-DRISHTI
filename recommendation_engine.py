import rasterio
import numpy as np

health_file = "Watershed_Health_Index.tif"
erosion_file = "Erosion_Risk.tif"
slope_file = "Slope.tif"
ndvi_file = "murredu_data/NDVI_2026.tif"

with rasterio.open(health_file) as src:
    health = src.read(1)
    profile = src.profile.copy()

with rasterio.open(erosion_file) as src:
    erosion = src.read(1)

with rasterio.open(slope_file) as src:
    slope = src.read(1)

# Align NDVI to health grid
from rasterio.warp import reproject, Resampling

with rasterio.open(ndvi_file) as src:
    ndvi = np.empty_like(health, dtype="float32")

    reproject(
        source=src.read(1),
        destination=ndvi,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=profile["transform"],
        dst_crs=profile["crs"],
        resampling=Resampling.bilinear
    )

# --------------------------------
# Identify priority zones
# --------------------------------

priority = np.zeros_like(health, dtype="uint8")

# 1 = vegetation restoration
priority[(ndvi < 0.30) & (health < 0.50)] = 1

# 2 = erosion control
priority[(erosion >= 3) & (slope > 10)] = 2

# 3 = water conservation
priority[(health < 0.45) & (slope < 15)] = 3

# 4 = high-priority multi-factor zone
priority[
    (health < 0.40) &
    (erosion >= 2) &
    (slope > 15)
] = 4

profile.update(
    dtype="uint8",
    count=1,
    compress="deflate",
    nodata=0
)

with rasterio.open(
    "Intervention_Priority.tif",
    "w",
    **profile
) as dst:
    dst.write(priority, 1)

print("\nINTERVENTION PRIORITY")
print("---------------------")

labels = {
    0: "No priority",
    1: "Vegetation restoration",
    2: "Erosion control",
    3: "Water conservation",
    4: "High priority multi-factor"
}

for value, label in labels.items():
    count = np.sum(priority == value)
    percent = count / priority.size * 100
    print(f"{label}: {count} pixels ({percent:.2f}%)")

print("\nSaved: Intervention_Priority.tif")