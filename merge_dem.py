import rasterio
from rasterio.merge import merge
import glob

files = glob.glob("dem_tiles/*.tif")

print("DEM tiles found:", len(files))

src_files = [rasterio.open(f) for f in files]

mosaic, out_transform = merge(src_files)

out_meta = src_files[0].meta.copy()

out_meta.update({
    "driver": "GTiff",
    "height": mosaic.shape[1],
    "width": mosaic.shape[2],
    "transform": out_transform,
    "compress": "deflate"
})

with rasterio.open("Murredu_DEM.tif", "w", **out_meta) as dest:
    dest.write(mosaic)

for src in src_files:
    src.close()

print("Murredu DEM created successfully!")
print("Size:", mosaic.shape)