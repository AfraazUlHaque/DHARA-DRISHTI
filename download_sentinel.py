from pystac_client import Client
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
import os

# Murredu watershed approximate bounding box
WEST = 80.3333
SOUTH = 17.1667
EAST = 80.8333
NORTH = 17.8333

# Earth Search STAC
catalog = Client.open(
    "https://earth-search.aws.element84.com/v1"
)

search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=[WEST, SOUTH, EAST, NORTH],
    datetime="2026-03-01/2026-03-31",
    query={"eo:cloud_cover": {"lt": 30}},
)

items = list(search.items())

print("Scenes found:", len(items))

for i, item in enumerate(items[:10]):
    print(
        i,
        item.id,
        "Cloud:",
        item.properties.get("eo:cloud_cover")
    )

if not items:
    raise Exception("No suitable Sentinel-2 scene found.")

# Lowest cloud-cover scene
item = sorted(
    items,
    key=lambda x: x.properties.get("eo:cloud_cover", 100)
)[0]

print("\nSelected:")
print(item.id)
print("Cloud:", item.properties.get("eo:cloud_cover"))

os.makedirs("murredu_data", exist_ok=True)

# Required bands
bands = {
    "B03": "green",
    "B04": "red",
    "B08": "nir",
    "SCL": "scl"
}

for band_name, asset_name in bands.items():

    url = item.assets[asset_name].href

    output = f"murredu_data/{band_name}.tif"

    print(f"\nDownloading {band_name}...")

    with rasterio.open(url) as src:

        # Convert our geographic bbox to image CRS
        left, bottom, right, top = transform_bounds(
            "EPSG:4326",
            src.crs,
            WEST,
            SOUTH,
            EAST,
            NORTH
        )

        window = from_bounds(
            left,
            bottom,
            right,
            top,
            src.transform
        )

        data = src.read(1, window=window)

        transform = src.window_transform(window)

        profile = src.profile.copy()
        profile.update(
            width=data.shape[1],
            height=data.shape[0],
            transform=transform,
            compress="deflate"
        )

        with rasterio.open(output, "w", **profile) as dst:
            dst.write(data, 1)

    print("Saved:", output)

print("\nDONE!")