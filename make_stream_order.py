import matplotlib
matplotlib.use('Agg')
import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from whitebox import WhiteboxTools

def main():
    os.makedirs('outputs/maps', exist_ok=True)
    os.makedirs('outputs/stats', exist_ok=True)
    
    wbt = WhiteboxTools()
    
    dem_breached = 'Murredu_DEM_breached.tif'
    flow_dir = 'Flow_Direction.tif'
    drainage = 'Drainage_Network.tif'
    stream_order = 'Stream_Order.tif'
    
    if not os.path.exists(flow_dir):
        print("Running D8 Pointer...")
        wbt.d8_pointer(dem_breached, flow_dir)
        
    print("Running Strahler Stream Order...")
    wbt.strahler_stream_order(flow_dir, drainage, stream_order)
    
    # Read stream order
    print("Reading stream order data...")
    with rasterio.open(stream_order) as src:
        order_data = src.read(1)
        nodata = src.nodata
        
    if nodata is not None:
        valid_orders = order_data[order_data != nodata]
    else:
        # Assuming 0 is background if nodata not set
        valid_orders = order_data[order_data > 0]
        
    unique, counts = np.unique(valid_orders, return_counts=True)
    unique = unique[unique > 0] # ensure no background
    counts = counts[np.in1d(unique, unique[unique > 0])]
    
    print("Stream Order Statistics:")
    for u, c in zip(unique, counts):
        print(f"Order {int(u)}: {c} pixels")
        
    # Mask out background for plotting
    plot_data = np.where((order_data == nodata) | (order_data == 0), np.nan, order_data)
    
    print("Plotting stream order map...")
    plt.figure(figsize=(10, 8))
    # discrete colormap
    try:
        cmap = plt.cm.get_cmap('jet', len(unique))
    except AttributeError:
        # for newer matplotlib versions
        import matplotlib
        cmap = matplotlib.colormaps['jet'].resampled(len(unique))
        
    img = plt.imshow(plot_data, cmap=cmap)
    plt.title('Murredu Watershed - Strahler Stream Order')
    plt.colorbar(img, ticks=unique, label='Stream Order')
    plt.savefig('outputs/maps/stream_order_map.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved stream_order_map.png")

if __name__ == '__main__':
    main()
