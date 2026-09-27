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
    basins = 'Watershed_Basins.tif'
    
    # 1. Flow Direction (D8 Pointer)
    print("Running D8 Pointer...")
    wbt.d8_pointer(dem_breached, flow_dir)
    
    # 2. Extract Basins
    print("Extracting Basins...")
    wbt.basins(flow_dir, basins)
    
    # Read the basins and find the main one (largest area)
    print("Analyzing basins...")
    with rasterio.open(basins) as src:
        basins_data = src.read(1)
        basins_data = np.where(basins_data == src.nodata, np.nan, basins_data)
        
    # Find unique basins and their counts, ignoring NaN
    unique, counts = np.unique(basins_data[~np.isnan(basins_data)], return_counts=True)
    if len(unique) > 0:
        main_basin_val = unique[np.argmax(counts)]
        print(f"Main basin ID: {main_basin_val} with {np.max(counts)} pixels")
        main_basin_mask = np.where(basins_data == main_basin_val, 1, np.nan)
    else:
        main_basin_mask = basins_data

    # Plot
    print("Plotting watershed boundary map...")
    plt.figure(figsize=(10, 8))
    plt.imshow(main_basin_mask, cmap='viridis')
    plt.title('Murredu Watershed - Main Basin Boundary')
    plt.colorbar(label='Basin Mask')
    plt.savefig('outputs/maps/watershed_boundary_map.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved watershed_boundary_map.png")

if __name__ == '__main__':
    main()
