import os
import numpy as np
import rasterio
from rasterio.warp import transform_bounds
from PIL import Image

ROOT = os.getcwd()
OUT = os.path.join(ROOT, "frontend", "public", "layers")
os.makedirs(OUT, exist_ok=True)


def get_bounds(path):
    with rasterio.open(path) as src:
        b = transform_bounds(
            src.crs,
            "EPSG:4326",
            *src.bounds
        )
        return b


def save_rgba(path, output, mode):
    with rasterio.open(path) as src:
        arr = src.read(1).astype("float32")

        if src.nodata is not None:
            valid = arr != src.nodata
        else:
            valid = np.isfinite(arr)

        valid &= np.isfinite(arr)

        h, w = arr.shape

        rgba = np.zeros((h, w, 4), dtype=np.uint8)

        if mode == "ndvi":
            # NDVI: -1 to +1
            x = np.clip((arr + 1) / 2, 0, 1)

            rgba[..., 0] = (255 * (1 - x)).astype(np.uint8)
            rgba[..., 1] = (255 * x).astype(np.uint8)
            rgba[..., 2] = 60
            rgba[..., 3] = np.where(valid, 170, 0)

        elif mode == "water":
            mask = arr > 0

            rgba[..., 0] = 35
            rgba[..., 1] = 120
            rgba[..., 2] = 190
            rgba[..., 3] = np.where(mask & valid, 190, 0)

        elif mode == "drainage":
            mask = arr > 0

            rgba[..., 0] = 30
            rgba[..., 1] = 80
            rgba[..., 2] = 160
            rgba[..., 3] = np.where(mask & valid, 230, 0)

        elif mode == "slope":
            x = np.clip(arr / 35, 0, 1)

            rgba[..., 0] = (255 * x).astype(np.uint8)
            rgba[..., 1] = (180 * (1 - x)).astype(np.uint8)
            rgba[..., 2] = 50
            rgba[..., 3] = np.where(valid, 150, 0)

        elif mode == "erosion":
            # Classes 1-5
            colors = {
                1: (55, 150, 75),
                2: (150, 190, 70),
                3: (240, 190, 60),
                4: (225, 105, 45),
                5: (175, 45, 45),
            }

            for cls, color in colors.items():
                mask = (arr == cls) & valid

                rgba[mask, 0] = color[0]
                rgba[mask, 1] = color[1]
                rgba[mask, 2] = color[2]
                rgba[mask, 3] = 175

        elif mode == "intervention":
            colors = {
                1: (55, 135, 75),      # vegetation
                2: (205, 105, 45),     # erosion
                3: (45, 120, 185),     # water
                4: (145, 60, 110),     # multi-factor
            }

            for cls, color in colors.items():
                mask = (arr == cls) & valid

                rgba[mask, 0] = color[0]
                rgba[mask, 1] = color[1]
                rgba[mask, 2] = color[2]
                rgba[mask, 3] = 190

        elif mode == "lulc":
            colors = {
                1: (40, 115, 190),     # water
                2: (45, 145, 65),      # dense vegetation
                3: (145, 180, 65),     # agriculture
                4: (190, 150, 90),     # bare soil
                5: (150, 75, 65),      # built-up
            }

            for cls, color in colors.items():
                mask = (arr == cls) & valid

                rgba[mask, 0] = color[0]
                rgba[mask, 1] = color[1]
                rgba[mask, 2] = color[2]
                rgba[mask, 3] = 165

        elif mode == "health":
            x = np.clip(arr, 0, 1)

            rgba[..., 0] = (220 * (1 - x)).astype(np.uint8)
            rgba[..., 1] = (180 * x).astype(np.uint8)
            rgba[..., 2] = 70
            rgba[..., 3] = np.where(valid, 155, 0)

        # Resize for browser performance
        max_width = 1600

        if w > max_width:
            new_h = int(h * max_width / w)

            image = Image.fromarray(rgba, "RGBA")
            image = image.resize(
                (max_width, new_h),
                Image.Resampling.BILINEAR
            )
        else:
            image = Image.fromarray(rgba, "RGBA")

        image.save(output, optimize=True)

        print("Created:", output)


layers = [
    (
        os.path.join(ROOT, "murredu_data", "NDVI_2026.tif"),
        "ndvi.png",
        "ndvi",
    ),
    (
        os.path.join(ROOT, "murredu_data", "Water_Mask.tif"),
        "water.png",
        "water",
    ),
    (
        os.path.join(ROOT, "Drainage_1000.tif"),
        "drainage.png",
        "drainage",
    ),
    (
        os.path.join(ROOT, "Slope.tif"),
        "slope.png",
        "slope",
    ),
    (
        os.path.join(ROOT, "Erosion_Risk.tif"),
        "erosion.png",
        "erosion",
    ),
    (
        os.path.join(ROOT, "Intervention_Priority.tif"),
        "intervention.png",
        "intervention",
    ),
    (
        os.path.join(ROOT, "LULC.tif"),
        "lulc.png",
        "lulc",
    ),
    (
        os.path.join(ROOT, "Watershed_Health_Index.tif"),
        "health.png",
        "health",
    ),
]

metadata = {}

for source, filename, mode in layers:

    if not os.path.exists(source):
        print("SKIPPED - not found:", source)
        continue

    output = os.path.join(OUT, filename)

    save_rgba(
        source,
        output,
        mode
    )

    metadata[filename] = get_bounds(source)

print("\n==============================")
print("WEB LAYERS READY")
print("==============================")

for name, bounds in metadata.items():
    print(name, "=>", bounds)