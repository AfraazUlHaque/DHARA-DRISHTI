import matplotlib
matplotlib.use('Agg')
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs('outputs/maps', exist_ok=True)

with rasterio.open("Slope.tif") as src:
    slope = src.read(1).astype("float32")
    profile = src.profile.copy()

valid = np.isfinite(slope)

# Classes:
# 1 = Low       0-5°
# 2 = Moderate  5-15°
# 3 = High      15-30°
# 4 = Very High >30°

slope_class = np.zeros(slope.shape, dtype="uint8")

slope_class[(slope >= 0) & (slope < 5)] = 1
slope_class[(slope >= 5) & (slope < 15)] = 2
slope_class[(slope >= 15) & (slope < 30)] = 3
slope_class[slope >= 30] = 4

profile.update(
    dtype="uint8",
    count=1,
    nodata=0,
    compress="deflate"
)

with rasterio.open("Slope_Classes.tif", "w", **profile) as dst:
    dst.write(slope_class, 1)

total = np.sum(valid)

print("===================================")
print("       SLOPE CLASSIFICATION")
print("===================================")

classes = {
    1: "Low (0-5°)",
    2: "Moderate (5-15°)",
    3: "High (15-30°)",
    4: "Very High (>30°)"
}

for number, name in classes.items():
    pixels = np.sum(slope_class == number)
    percentage = pixels / total * 100
    print(f"{name}: {pixels} pixels | {percentage:.2f}%")

print("===================================")
print("Slope classes saved successfully!")
print("===================================")

# Display
plt.figure(figsize=(12, 8))
plt.imshow(slope_class, cmap="terrain", vmin=1, vmax=4)
plt.colorbar(
    ticks=[1, 2, 3, 4],
    label="Slope Class"
)
plt.title("Murredu Watershed - Slope Classes Map")
plt.axis("off")
plt.tight_layout()
plt.savefig('outputs/maps/slope_classes_map.png', dpi=300, bbox_inches='tight')
# # plt.show()