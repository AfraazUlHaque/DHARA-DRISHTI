import matplotlib
matplotlib.use('Agg')
import os
import rasterio
import numpy as np
import csv

def main():
    os.makedirs('outputs/maps', exist_ok=True)
    os.makedirs('outputs/stats', exist_ok=True)
    
    dem_file = 'Murredu_DEM_clip.tif'
    drainage = 'Drainage_Network.tif'
    
    print("Calculating morphometric parameters...")
    
    with rasterio.open(dem_file) as src:
        dem = src.read(1)
        nodata = src.nodata
        res_x, res_y = src.res
        
    dem_valid = dem[dem != nodata] if nodata is not None else dem[dem > -9999]
    min_elev = np.min(dem_valid)
    max_elev = np.max(dem_valid)
    mean_elev = np.mean(dem_valid)
    relief = max_elev - min_elev
    
    # Calculate pixel size in meters
    lat_rad = np.radians(17.5)
    meters_per_deg_lat = 111320.0
    meters_per_deg_lon = 40075000.0 * np.cos(lat_rad) / 360.0
    
    pixel_area_m2 = (res_x * meters_per_deg_lon) * (res_y * meters_per_deg_lat)
    pixel_area_km2 = pixel_area_m2 / 1e6
    
    area_km2 = len(dem_valid) * pixel_area_km2
    
    # Read drainage network
    with rasterio.open(drainage) as src:
        streams = src.read(1)
        stream_nodata = src.nodata
        
    if stream_nodata is not None:
        stream_pixels = streams[(streams != stream_nodata) & (streams > 0)]
    else:
        stream_pixels = streams[streams > 0]
        
    total_stream_pixels = len(stream_pixels)
    
    # Length approximation: average length per pixel is sqrt(area)
    pixel_len_m = np.sqrt(pixel_area_m2)
    stream_length_km = total_stream_pixels * pixel_len_m / 1000.0
    
    drainage_density = stream_length_km / area_km2
    
    print("-" * 50)
    print(f"{'Murredu Watershed - Morphometric Parameters':^50}")
    print("-" * 50)
    print(f"{'Watershed Area':<30} : {area_km2:.2f} km^2")
    print(f"{'Relief':<30} : {relief:.2f} m")
    print(f"{'Mean Elevation':<30} : {mean_elev:.2f} m")
    print(f"{'Min Elevation':<30} : {min_elev:.2f} m")
    print(f"{'Max Elevation':<30} : {max_elev:.2f} m")
    print(f"{'Total Stream Pixels':<30} : {total_stream_pixels}")
    print(f"{'Estimated Stream Length':<30} : {stream_length_km:.2f} km")
    print(f"{'Drainage Density':<30} : {drainage_density:.3f} km/km^2")
    print("-" * 50)
    
    stats_file = 'outputs/stats/morphometric_parameters.csv'
    with open(stats_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Parameter', 'Value', 'Unit'])
        writer.writerow(['Watershed Area', f'{area_km2:.2f}', 'km^2'])
        writer.writerow(['Relief', f'{relief:.2f}', 'm'])
        writer.writerow(['Min Elevation', f'{min_elev:.2f}', 'm'])
        writer.writerow(['Max Elevation', f'{max_elev:.2f}', 'm'])
        writer.writerow(['Mean Elevation', f'{mean_elev:.2f}', 'm'])
        writer.writerow(['Total Stream Pixels', f'{total_stream_pixels}', 'count'])
        writer.writerow(['Estimated Stream Length', f'{stream_length_km:.2f}', 'km'])
        writer.writerow(['Drainage Density', f'{drainage_density:.3f}', 'km/km^2'])
        
    print(f"Saved morphometric parameters to {stats_file}")

if __name__ == '__main__':
    main()
