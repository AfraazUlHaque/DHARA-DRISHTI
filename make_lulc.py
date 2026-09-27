import rasterio
import numpy as np

with rasterio.open("murredu_data/B03.tif") as src:
    green = src.read(1).astype("float32")
    profile = src.profile.copy()

with rasterio.open("murredu_data/B04.tif") as src:
    red = src.read(1).astype("float32")

with rasterio.open("murredu_data/B08.tif") as src:
    nir = src.read(1).astype("float32")

# Indices
ndvi = (nir - red) / (nir + red + 1e-6)
ndwi = (green - nir) / (green + nir + 1e-6)

# LULC classes
# 0 = NoData
# 1 = Water
# 2 = Dense vegetation
# 3 = Moderate vegetation/agriculture
# 4 = Bare soil
# 5 = Built-up/other

lulc = np.zeros(ndvi.shape, dtype="uint8")

# Water
lulc[ndwi > 0.20] = 1

# Dense vegetation
lulc[(ndvi >= 0.60) & (ndwi <= 0.20)] = 2

# Moderate vegetation / agriculture
lulc[
    (ndvi >= 0.30) &
    (ndvi < 0.60) &
    (ndwi <= 0.20)
] = 3

# Bare soil
lulc[
    (ndvi >= 0.05) &
    (ndvi < 0.30) &
    (ndwi <= 0.20)
] = 4

# Built-up / other
lulc[
    (ndvi < 0.05) &
    (ndwi <= 0.20)
] = 5

profile.update(
    dtype="uint8",
    count=1,
    nodata=0,
    compress="deflate"
)

with rasterio.open("LULC.tif", "w", **profile) as dst:
    dst.write(lulc, 1)

print("LULC map created!")

classes = {
    1: "Water",
    2: "Dense vegetation",
    3: "Moderate vegetation/agriculture",
    4: "Bare soil",
    5: "Built-up/other"
}

for value, name in classes.items():
    count = np.sum(lulc == value)
    percentage = count / lulc.size * 100
    print(f"{name}: {count} pixels ({percentage:.2f}%)")