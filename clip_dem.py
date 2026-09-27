import rasterio
from rasterio.windows import from_bounds

# Murredu working bounding box
WEST = 80.3333
SOUTH = 17.1667
EAST = 80.8333
NORTH = 17.8333

with rasterio.open("Murredu_DEM.tif") as src:

    window = from_bounds(
        WEST, SOUTH,
        EAST, NORTH,
        transform=src.transform
    )

    window = window.round_offsets().round_lengths()

    dem = src.read(1, window=window)

    profile = src.profile.copy()
    profile.update(
        height=dem.shape[0],
        width=dem.shape[1],
        transform=src.window_transform(window),
        compress="deflate"
    )

    with rasterio.open(
        "Murredu_DEM_clip.tif",
        "w",
        **profile
    ) as dst:
        dst.write(dem, 1)

print("Clipped DEM created successfully!")
print("Size:", dem.shape)
print("Output: Murredu_DEM_clip.tif")