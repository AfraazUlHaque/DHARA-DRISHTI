import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling


def read(path):
    with rasterio.open(path) as src:
        return src.read(1).astype("float32"), src.profile


# --------------------------------
# Target grid = Slope grid
# --------------------------------
slope, target_profile = read("Slope.tif")

target_shape = slope.shape
target_transform = target_profile["transform"]
target_crs = target_profile["crs"]


def align_to_target(path):
    with rasterio.open(path) as src:

        output = np.empty(
            target_shape,
            dtype="float32"
        )

        reproject(
            source=src.read(1).astype("float32"),
            destination=output,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=target_transform,
            dst_crs=target_crs,
            resampling=Resampling.bilinear
        )

        return output


# --------------------------------
# Align all layers
# --------------------------------

print("Aligning NDVI...")
ndvi = align_to_target("murredu_data/NDVI_2026.tif")

print("Aligning Water...")
water = align_to_target("murredu_data/Water_Mask.tif")

print("Loading Erosion...")
erosion, _ = read("Erosion_Risk.tif")

# Check dimensions
print("\nGRID CHECK")
print("NDVI   :", ndvi.shape)
print("Water  :", water.shape)
print("Slope  :", slope.shape)
print("Erosion:", erosion.shape)


# --------------------------------
# NDVI score
# --------------------------------
ndvi_score = np.clip(
    (ndvi + 1) / 2,
    0,
    1
)


# --------------------------------
# Water score
# --------------------------------
water_score = np.clip(
    water,
    0,
    1
)


# --------------------------------
# Erosion → health score
# --------------------------------
erosion_score = 1 - np.clip(
    erosion / 4,
    0,
    1
)


# --------------------------------
# Slope → health score
# --------------------------------
slope_score = 1 - np.clip(
    slope / 30,
    0,
    1
)


# --------------------------------
# Watershed Health Index
# --------------------------------
health = (
    0.40 * ndvi_score +
    0.20 * water_score +
    0.25 * erosion_score +
    0.15 * slope_score
)

health = np.clip(
    health,
    0,
    1
)


# --------------------------------
# Save
# --------------------------------
target_profile.update(
    dtype="float32",
    count=1,
    compress="deflate"
)

with rasterio.open(
    "Watershed_Health_Index.tif",
    "w",
    **target_profile
) as dst:

    dst.write(
        health.astype("float32"),
        1
    )


# --------------------------------
# Statistics
# --------------------------------
print("\nWATERSHED HEALTH INDEX")
print("----------------------")

print(
    "Minimum:",
    np.nanmin(health)
)

print(
    "Maximum:",
    np.nanmax(health)
)

print(
    "Mean:",
    np.nanmean(health)
)


very_low = np.sum(health < 0.2)
low = np.sum(
    (health >= 0.2) &
    (health < 0.4)
)

moderate = np.sum(
    (health >= 0.4) &
    (health < 0.6)
)

high = np.sum(
    (health >= 0.6) &
    (health < 0.8)
)

very_high = np.sum(
    health >= 0.8
)

total = health.size


print("\nHEALTH CATEGORIES")
print("-----------------")

print(
    "Very Low :",
    very_low,
    f"({very_low/total*100:.2f}%)"
)

print(
    "Low      :",
    low,
    f"({low/total*100:.2f}%)"
)

print(
    "Moderate :",
    moderate,
    f"({moderate/total*100:.2f}%)"
)

print(
    "High     :",
    high,
    f"({high/total*100:.2f}%)"
)

print(
    "Very High:",
    very_high,
    f"({very_high/total*100:.2f}%)"
)

print("\nSaved: Watershed_Health_Index.tif")