import rasterio
import numpy as np

# -----------------------------
# 2023 NDVI
# -----------------------------
with rasterio.open("murredu_2023/B04_2023.tif") as red_src, \
     rasterio.open("murredu_2023/B08_2023.tif") as nir_src:

    red = red_src.read(1).astype("float32")
    nir = nir_src.read(1).astype("float32")

    ndvi_2023 = (nir - red) / (nir + red + 1e-6)

    profile = red_src.profile.copy()
    profile.update(dtype="float32", count=1, compress="deflate")

    with rasterio.open("murredu_2023/NDVI_2023.tif", "w", **profile) as dst:
        dst.write(ndvi_2023, 1)

print("2023 NDVI created")
print("2023 NDVI min:", np.nanmin(ndvi_2023))
print("2023 NDVI max:", np.nanmax(ndvi_2023))
print("2023 NDVI mean:", np.nanmean(ndvi_2023))


# -----------------------------
# 2026 NDVI
# -----------------------------
with rasterio.open("murredu_data/B04.tif") as red_src, \
     rasterio.open("murredu_data/B08.tif") as nir_src:

    red = red_src.read(1).astype("float32")
    nir = nir_src.read(1).astype("float32")

    ndvi_2026 = (nir - red) / (nir + red + 1e-6)

    profile = red_src.profile.copy()
    profile.update(dtype="float32", count=1, compress="deflate")

    with rasterio.open("murredu_data/NDVI_2026.tif", "w", **profile) as dst:
        dst.write(ndvi_2026, 1)

print("2026 NDVI created")


# -----------------------------
# Reproject 2023 to 2026 grid
# -----------------------------
from rasterio.warp import reproject, Resampling

with rasterio.open("murredu_data/NDVI_2026.tif") as src2026:

    ndvi26 = src2026.read(1)

    aligned_2023 = np.empty_like(ndvi26, dtype="float32")

    with rasterio.open("murredu_2023/NDVI_2023.tif") as src2023:

        reproject(
            source=src2023.read(1),
            destination=aligned_2023,
            src_transform=src2023.transform,
            src_crs=src2023.crs,
            dst_transform=src2026.transform,
            dst_crs=src2026.crs,
            resampling=Resampling.bilinear
        )

    # -----------------------------
    # Change = 2026 - 2023
    # -----------------------------
    change = ndvi26 - aligned_2023

    profile = src2026.profile.copy()
    profile.update(dtype="float32", count=1, compress="deflate")

    with rasterio.open(
        "murredu_data/NDVI_Change_2023_2026.tif",
        "w",
        **profile
    ) as dst:
        dst.write(change, 1)

print("NDVI change map created")

print("Change min:", np.nanmin(change))
print("Change max:", np.nanmax(change))
print("Change mean:", np.nanmean(change))

# -----------------------------
# Gain / Loss statistics
# -----------------------------
valid = np.isfinite(change)

gain = np.sum(change[valid] > 0.10)
loss = np.sum(change[valid] < -0.10)
stable = np.sum(np.abs(change[valid]) <= 0.10)

total = gain + loss + stable

print("\nCHANGE STATISTICS")
print("-----------------")
print("Vegetation gain :", gain, f"({gain/total*100:.2f}%)")
print("Vegetation loss :", loss, f"({loss/total*100:.2f}%)")
print("Stable          :", stable, f"({stable/total*100:.2f}%)")