import matplotlib
matplotlib.use('Agg')
import rasterio
import numpy as np
import matplotlib.pyplot as plt

with rasterio.open("Murredu_DEM.tif") as src:
    dem = src.read(1).astype("float32")

# Remove invalid values
valid = dem[np.isfinite(dem)]

print("===================================")
print("       DEM ANALYSIS")
print("===================================")

print("Minimum elevation:", np.min(valid), "m")
print("Maximum elevation:", np.max(valid), "m")
print("Mean elevation:", np.mean(valid), "m")
print("DEM shape:", dem.shape)

print("===================================")

# Plot DEM
plt.figure(figsize=(12, 8))

plt.imshow(dem, cmap="terrain")

plt.colorbar(label="Elevation (meters)")

plt.title("Murredu Area - Elevation Map")

plt.axis("off")

plt.tight_layout()
# # plt.show()