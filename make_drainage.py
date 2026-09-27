from pysheds.grid import Grid
import rasterio
import numpy as np

print("Loading DEM...")

grid = Grid.from_raster(
    "Murredu_DEM_clip.tif",
    data_name="dem"
)

dem = grid.read_raster(
    "Murredu_DEM_clip.tif",
    data_name="dem"
)

print("Filling pits...")
pit_filled = grid.fill_pits(dem)

print("Filling depressions...")
flooded = grid.fill_depressions(pit_filled)

print("Resolving flats...")
inflated = grid.resolve_flats(flooded)

print("Calculating flow direction...")

dirmap = (64, 128, 1, 2, 4, 8, 16, 32)

fdir = grid.flowdir(
    inflated,
    dirmap=dirmap
)

print("Calculating flow accumulation...")

acc = grid.accumulation(
    fdir,
    dirmap=dirmap
)

# Save Flow Direction
with rasterio.open("Flow_Direction.tif", "w",
                   driver="GTiff",
                   height=fdir.shape[0],
                   width=fdir.shape[1],
                   count=1,
                   dtype=fdir.dtype,
                   crs=grid.crs,
                   transform=grid.affine) as dst:
    dst.write(fdir, 1)

# Save Flow Accumulation
with rasterio.open("Flow_Accumulation.tif", "w",
                   driver="GTiff",
                   height=acc.shape[0],
                   width=acc.shape[1],
                   count=1,
                   dtype="float32",
                   crs=grid.crs,
                   transform=grid.affine) as dst:
    dst.write(acc.astype("float32"), 1)

print("Drainage analysis completed!")
print("Flow Direction saved!")
print("Flow Accumulation saved!")

print("Maximum accumulation:", np.max(acc))