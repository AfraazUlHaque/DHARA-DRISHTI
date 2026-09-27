import matplotlib
matplotlib.use('Agg')
import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt

os.makedirs('outputs/maps', exist_ok=True)

with rasterio.open("Murredu_DEM_clip.tif") as src:
    dem = src.read(1).astype("float32")
    profile = src.profile.copy()
    xres = abs(src.transform.a)
    yres = abs(src.transform.e)

lat = 17.5
meters_per_degree_lat = 111320
meters_per_degree_lon = 111320 * np.cos(np.radians(lat))
dx = xres * meters_per_degree_lon
dy = yres * meters_per_degree_lat

grad_y, grad_x = np.gradient(dem, dy, dx)

slope = np.arctan(np.sqrt(grad_x**2 + grad_y**2))
aspect = np.arctan2(grad_y, -grad_x) # Using a standard aspect direction for hillshade formula

azimuth = 315
altitude = 45
zenith_rad = np.radians(90 - altitude)
azimuth_rad = np.radians(azimuth)

# hillshade = 255 * ((cos(zenith) * cos(slope)) + (sin(zenith) * sin(slope) * cos(azimuth - aspect)))
hillshade = 255.0 * (
    np.cos(zenith_rad) * np.cos(slope) + 
    np.sin(zenith_rad) * np.sin(slope) * np.cos(azimuth_rad - aspect)
)
hillshade = np.clip(hillshade, 0, 255).astype("uint8")

profile.update(dtype="uint8", count=1, nodata=0, compress="deflate")
with rasterio.open("Hillshade.tif", "w", **profile) as dst:
    dst.write(hillshade, 1)

plt.figure(figsize=(12, 8))
plt.imshow(hillshade, cmap="gray")
plt.colorbar(label="Hillshade")
plt.title("Murredu Watershed - Hillshade Map")
plt.axis("off")
plt.tight_layout()
plt.savefig('outputs/maps/hillshade_map.png', dpi=300, bbox_inches='tight')
# # plt.show()
