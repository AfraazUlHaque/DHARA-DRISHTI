import matplotlib
matplotlib.use('Agg')
import rasterio
import matplotlib.pyplot as plt
import numpy as np

with rasterio.open("Drainage_Network.tif") as src:
    drainage = src.read(1)

print("Drainage pixels:", np.sum(drainage > 0))
print("Total pixels:", drainage.size)
print("Drainage percentage:",
      (np.sum(drainage > 0) / drainage.size) * 100)

plt.figure(figsize=(12, 8))

plt.imshow(
    drainage,
    cmap="Blues",
    interpolation="none"
)

plt.title("Murredu Watershed - Extracted Drainage Network")
plt.axis("off")
plt.tight_layout()
# # plt.show()