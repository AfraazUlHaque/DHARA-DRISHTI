import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling

# -----------------------------
# Read Slope - TARGET GRID
# -----------------------------
with rasterio.open("Slope.tif") as src:
    slope = src.read(1).astype("float32")
    profile = src.profile.copy()
    target_transform = src.transform
    target_crs = src.crs
    target_height = src.height
    target_width = src.width

print("Target grid:", target_height, target_width)

# -----------------------------
# Read LULC and align to Slope
# -----------------------------
with rasterio.open("LULC.tif") as src:
    lulc_source = src.read(1)
    lulc = np.zeros(
        (target_height, target_width),
        dtype="uint8"
    )

    reproject(
        source=lulc_source,
        destination=lulc,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=target_transform,
        dst_crs=target_crs,
        resampling=Resampling.nearest
    )

print("LULC aligned:", lulc.shape)

# -----------------------------
# Read Flow Accumulation
# -----------------------------
with rasterio.open("Flow_Accumulation.tif") as src:
    flow = src.read(1).astype("float32")

print("Flow:", flow.shape)

# Safety check
if slope.shape != flow.shape:
    raise ValueError(
        f"Slope and Flow dimensions differ: "
        f"{slope.shape} vs {flow.shape}"
    )

# -----------------------------
# Slope score
# -----------------------------
slope_score = np.clip(slope / 30.0, 0, 1)

# -----------------------------
# Flow accumulation score
# -----------------------------
flow_log = np.log1p(np.maximum(flow, 0))

flow_min = np.nanmin(flow_log)
flow_max = np.nanmax(flow_log)

flow_score = (
    (flow_log - flow_min) /
    (flow_max - flow_min + 1e-6)
)

# -----------------------------
# LULC erosion susceptibility
# -----------------------------
lulc_score = np.zeros(
    lulc.shape,
    dtype="float32"
)

# Water
lulc_score[lulc == 1] = 0.0

# Dense vegetation
lulc_score[lulc == 2] = 0.15

# Moderate vegetation/agriculture
lulc_score[lulc == 3] = 0.45

# Bare soil
lulc_score[lulc == 4] = 0.90

# Built-up/other
lulc_score[lulc == 5] = 0.60

# -----------------------------
# Erosion Risk Index
# -----------------------------
risk = (
    0.50 * slope_score +
    0.20 * flow_score +
    0.30 * lulc_score
)

# -----------------------------
# Risk classes
# -----------------------------
erosion = np.zeros(
    risk.shape,
    dtype="uint8"
)

erosion[risk < 0.20] = 1

erosion[
    (risk >= 0.20) &
    (risk < 0.40)
] = 2

erosion[
    (risk >= 0.40) &
    (risk < 0.60)
] = 3

erosion[
    (risk >= 0.60) &
    (risk < 0.80)
] = 4

erosion[risk >= 0.80] = 5

# -----------------------------
# Save
# -----------------------------
profile.update(
    dtype="uint8",
    count=1,
    nodata=0,
    compress="deflate"
)

with rasterio.open(
    "Erosion_Risk.tif",
    "w",
    **profile
) as dst:
    dst.write(erosion, 1)

print("\nErosion Risk Map created successfully!")

names = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High"
}

for value, name in names.items():
    pixels = np.sum(erosion == value)
    percentage = pixels / erosion.size * 100

    print(
        f"{name}: "
        f"{pixels} pixels "
        f"({percentage:.2f}%)"
    )