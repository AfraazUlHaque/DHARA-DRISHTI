import matplotlib
matplotlib.use('Agg')
import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt

os.makedirs('outputs/maps', exist_ok=True)

with rasterio.open("Murredu_DEM_clip.tif") as src:
    dem = src.read(1).astype("float32")

# try to get hillshade background if it exists, otherwise just plot contours on dem
try:
    with rasterio.open("Hillshade.tif") as hs_src:
        hillshade = hs_src.read(1)
        background = hillshade
        cmap_bg = 'gray'
except FileNotFoundError:
    background = dem
    cmap_bg = 'terrain'

plt.figure(figsize=(12, 8))
plt.imshow(background, cmap=cmap_bg, zorder=1)

# Valid data mask
mask = np.isfinite(dem)
valid_dem = dem[mask]
min_elev = np.nanmin(dem)
max_elev = np.nanmax(dem)

# Create 50m intervals
levels = np.arange(np.floor(min_elev/50)*50, np.ceil(max_elev/50)*50 + 50, 50)

contours = plt.contour(dem, levels=levels, colors='brown', linewidths=0.5, alpha=0.7, zorder=2)
plt.clabel(contours, inline=True, fontsize=8, fmt='%1.0f m')

plt.title("Murredu Watershed - Contour Map")
plt.axis("off")
plt.tight_layout()
plt.savefig('outputs/maps/contour_map.png', dpi=300, bbox_inches='tight')
plt.show()
