import rasterio
import numpy as np

for threshold in [500, 1000, 2500]:

    filename = f"Drainage_{threshold}.tif"

    with rasterio.open(filename) as src:
        data = src.read(1)

    stream_pixels = np.sum(data > 0)
    total_pixels = data.size
    percentage = (stream_pixels / total_pixels) * 100

    print("\nThreshold:", threshold)
    print("Stream pixels:", stream_pixels)
    print("Total pixels:", total_pixels)
    print("Coverage:", percentage, "%")