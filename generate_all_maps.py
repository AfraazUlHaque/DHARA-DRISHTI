import matplotlib
matplotlib.use('Agg')
import os
import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show
import numpy as np
import matplotlib.colors as mcolors

def setup_map(ax, title):
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_xlabel('Easting', fontsize=12)
    ax.set_ylabel('Northing', fontsize=12)

def generate_elevation_map():
    in_file = 'Murredu_DEM_clip.tif'
    out_file = 'outputs/maps/elevation_map.png'
    print(f"Generating {out_file}...")
    try:
        with rasterio.open(in_file) as src:
            data = src.read(1)
            data_masked = np.ma.masked_invalid(data)
            fig, ax = plt.subplots(figsize=(14, 10))
            img = show(src, ax=ax, cmap='terrain', title='')
            setup_map(ax, 'Murredu Watershed - Elevation Map')
            cbar = plt.colorbar(img.get_images()[0], ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('Elevation (m)', fontsize=12)
            plt.savefig(out_file, dpi=300, bbox_inches='tight')
            plt.close()
        return True
    except Exception as e:
        print(f"Error generating elevation map: {e}")
        return False

def generate_slope_map():
    in_file = 'outputs/Slope.tif'
    out_file = 'outputs/maps/slope_map.png'
    print(f"Generating {out_file}...")
    try:
        with rasterio.open(in_file) as src:
            fig, ax = plt.subplots(figsize=(14, 10))
            img = show(src, ax=ax, cmap='YlOrBr', title='')
            setup_map(ax, 'Murredu Watershed - Slope Map')
            cbar = plt.colorbar(img.get_images()[0], ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('Slope (degrees)', fontsize=12)
            plt.savefig(out_file, dpi=300, bbox_inches='tight')
            plt.close()
        return True
    except Exception as e:
        print(f"Error generating slope map: {e}")
        return False

def generate_slope_classes_map():
    in_file = 'outputs/Slope_Classes.tif'
    out_file = 'outputs/maps/slope_classes_map.png'
    print(f"Generating {out_file}...")
    try:
        with rasterio.open(in_file) as src:
            data = src.read(1)
            data_masked = np.ma.masked_invalid(data)
            fig, ax = plt.subplots(figsize=(14, 10))
            cmap = mcolors.ListedColormap(['green', 'yellow', 'orange', 'red'])
            bounds = [0, 1, 2, 3, 4]
            norm = mcolors.BoundaryNorm(bounds, cmap.N)
            img = show((src, 1), ax=ax, cmap=cmap, norm=norm, title='')
            setup_map(ax, 'Murredu Watershed - Slope Classes Map')
            
            cbar = plt.colorbar(img.get_images()[0], ax=ax, fraction=0.046, pad=0.04, ticks=[0.5, 1.5, 2.5, 3.5])
            cbar.ax.set_yticklabels(['0-5° (Flat)', '5-15° (Moderate)', '15-30° (Steep)', '>30° (Very Steep)'])
            cbar.set_label('Slope Class', fontsize=12)
            plt.savefig(out_file, dpi=300, bbox_inches='tight')
            plt.close()
        return True
    except Exception as e:
        print(f"Error generating slope classes map: {e}")
        return False

def generate_drainage_comparison_map():
    out_file = 'outputs/maps/drainage_comparison_map.png'
    print(f"Generating {out_file}...")
    try:
        fig, axes = plt.subplots(1, 3, figsize=(24, 8))
        thresholds = [500, 1000, 2500]
        for i, threshold in enumerate(thresholds):
            in_file = f'outputs/Drainage_Network_{threshold}.tif'
            try:
                with rasterio.open(in_file) as src:
                    show(src, ax=axes[i], cmap='Blues', title='')
                    axes[i].set_title(f'Threshold: {threshold}', fontsize=14)
            except Exception as e:
                axes[i].set_title(f'Threshold: {threshold} (Missing)', fontsize=14)
                print(f"Warning: {in_file} missing")
        fig.suptitle('Murredu Watershed - Drainage Network Comparison', fontsize=20, y=1.05)
        plt.tight_layout()
        plt.savefig(out_file, dpi=300, bbox_inches='tight')
        plt.close()
        return True
    except Exception as e:
        print(f"Error generating drainage comparison map: {e}")
        return False

def generate_ndvi_map():
    in_file = 'murredu_data/NDVI.tif'
    out_file = 'outputs/maps/ndvi_map.png'
    print(f"Generating {out_file}...")
    try:
        with rasterio.open(in_file) as src:
            fig, ax = plt.subplots(figsize=(14, 10))
            img = show(src, ax=ax, cmap='RdYlGn', title='')
            setup_map(ax, 'Murredu Watershed - NDVI Map')
            cbar = plt.colorbar(img.get_images()[0], ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('NDVI', fontsize=12)
            plt.savefig(out_file, dpi=300, bbox_inches='tight')
            plt.close()
        return True
    except Exception as e:
        print(f"Error generating NDVI map: {e}")
        return False

def generate_ndwi_map():
    in_file = 'murredu_data/NDWI.tif'
    out_file = 'outputs/maps/ndwi_map.png'
    print(f"Generating {out_file}...")
    try:
        with rasterio.open(in_file) as src:
            fig, ax = plt.subplots(figsize=(14, 10))
            img = show(src, ax=ax, cmap='RdYlBu', title='')
            setup_map(ax, 'Murredu Watershed - NDWI Map')
            cbar = plt.colorbar(img.get_images()[0], ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('NDWI', fontsize=12)
            plt.savefig(out_file, dpi=300, bbox_inches='tight')
            plt.close()
        return True
    except Exception as e:
        print(f"Error generating NDWI map: {e}")
        return False

def generate_water_bodies_map():
    in_file = 'murredu_data/Water_Mask.tif'
    out_file = 'outputs/maps/water_bodies_map.png'
    print(f"Generating {out_file}...")
    try:
        with rasterio.open(in_file) as src:
            fig, ax = plt.subplots(figsize=(14, 10))
            cmap = mcolors.ListedColormap(['white', 'blue'])
            bounds = [0, 0.5, 1.5]
            norm = mcolors.BoundaryNorm(bounds, cmap.N)
            img = show(src, ax=ax, cmap=cmap, norm=norm, title='')
            setup_map(ax, 'Murredu Watershed - Water Bodies Map')
            cbar = plt.colorbar(img.get_images()[0], ax=ax, fraction=0.046, pad=0.04, ticks=[0.25, 1.0])
            cbar.ax.set_yticklabels(['Non-Water', 'Water'])
            plt.savefig(out_file, dpi=300, bbox_inches='tight')
            plt.close()
        return True
    except Exception as e:
        print(f"Error generating water bodies map: {e}")
        return False

def main():
    os.makedirs('outputs/maps', exist_ok=True)
    results = {}
    
    results['Elevation'] = generate_elevation_map()
    results['Slope'] = generate_slope_map()
    results['Slope Classes'] = generate_slope_classes_map()
    results['Drainage Comparison'] = generate_drainage_comparison_map()
    results['NDVI'] = generate_ndvi_map()
    results['NDWI'] = generate_ndwi_map()
    results['Water Bodies'] = generate_water_bodies_map()
    
    print("\n" + "="*30)
    print("Map Generation Summary")
    print("="*30)
    for map_name, status in results.items():
        print(f"{map_name}: {'Success' if status else 'Failed/Skipped'}")

if __name__ == '__main__':
    main()
