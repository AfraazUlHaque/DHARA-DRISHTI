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

# Compute aspect (0-360) where 0 is North
# arctan2(grad_x, grad_y) would give angles from Y axis
# arctan2(-x, y) gives counterclockwise from North maybe? 
# Usually, aspect = np.degrees(np.arctan2(-grad_x, grad_y)) or similar
# Wait, let's use standard formula:
# Aspect = 180.0 / PI * atan2(grad_x, grad_y) ... actually:
# if gradient is positive in x (going East), slope faces West.
# Let's just use np.degrees(np.arctan2(grad_x, -grad_y)) + 180
# Or just standard numpy aspect:
# atan2(grad_y, -grad_x) ? Let's make it simple.
# The user said: Compute aspect (direction of slope) from Murredu_DEM_clip.tif using numpy gradient. 
# Use arctan2 to get compass direction (0-360).
aspect = np.degrees(np.arctan2(-grad_x, grad_y)) % 360
# Actually, if we want North=0, East=90, South=180, West=270:
# grad_x is negative if slope faces East? No, grad_x = df/dx.
# Let's just do standard aspect formula:
aspect = 180 + np.degrees(np.arctan2(grad_x, grad_y))

profile.update(dtype="float32", count=1, nodata=np.nan, compress="deflate")
with rasterio.open("Aspect.tif", "w", **profile) as dst:
    dst.write(aspect.astype("float32"), 1)

# Classes:
# 0: Flat (-1, or where slope is ~0, but let's just use slope if needed, or if grad_x==0 and grad_y==0. User didn't specify flat threshold, just 9 classes. Let's assume aspect < 0 is flat? We can use np.where(np.sqrt(grad_x**2 + grad_y**2) < 0.001, -1, aspect))
# Actually, just basic directions: N, NE, E, SE, S, SW, W, NW.
# 1: N (337.5-360, 0-22.5)
# 2: NE (22.5-67.5)
# 3: E (67.5-112.5)
# 4: SE (112.5-157.5)
# 5: S (157.5-202.5)
# 6: SW (202.5-247.5)
# 7: W (247.5-292.5)
# 8: NW (292.5-337.5)
# 0: Flat (slope < 0.0001)

slope = np.sqrt(grad_x**2 + grad_y**2)
aspect_class = np.zeros_like(aspect, dtype="uint8")

aspect_class[(aspect >= 337.5) | (aspect < 22.5)] = 1  # N
aspect_class[(aspect >= 22.5) & (aspect < 67.5)] = 2   # NE
aspect_class[(aspect >= 67.5) & (aspect < 112.5)] = 3  # E
aspect_class[(aspect >= 112.5) & (aspect < 157.5)] = 4 # SE
aspect_class[(aspect >= 157.5) & (aspect < 202.5)] = 5 # S
aspect_class[(aspect >= 202.5) & (aspect < 247.5)] = 6 # SW
aspect_class[(aspect >= 247.5) & (aspect < 292.5)] = 7 # W
aspect_class[(aspect >= 292.5) & (aspect < 337.5)] = 8 # NW
aspect_class[slope < 0.001] = 0 # Flat

profile.update(dtype="uint8", nodata=255)
with rasterio.open("Aspect_Classes.tif", "w", **profile) as dst:
    dst.write(aspect_class, 1)

print("===================================")
print("        ASPECT ANALYSIS")
print("===================================")
classes_map = {0: "Flat", 1: "N", 2: "NE", 3: "E", 4: "SE", 5: "S", 6: "SW", 7: "W", 8: "NW"}
total = np.sum(np.isfinite(dem))
for i in range(9):
    pixels = np.sum(aspect_class == i)
    print(f"{classes_map[i]}: {pixels} pixels | {pixels/total*100:.2f}%")
print("===================================")

plt.figure(figsize=(12, 8))
plt.imshow(aspect, cmap="hsv", vmin=0, vmax=360)
plt.colorbar(label="Aspect (degrees)")
plt.title("Murredu Watershed - Aspect Map")
plt.axis("off")
plt.tight_layout()
plt.savefig('outputs/maps/aspect_map.png', dpi=300, bbox_inches='tight')
# # plt.show()
