import os
import sys
import subprocess
import time

def run_script(script_path, cwd=None):
    if not os.path.exists(os.path.join(cwd or '.', script_path)):
        print(f"Warning: Script {script_path} not found in {cwd or 'current directory'}")
        return False, 0
    
    print(f"\n{'='*10} Running: {script_path} {'='*10}")
    start_time = time.time()
    try:
        subprocess.run([sys.executable, script_path], check=True, cwd=cwd)
        elapsed = time.time() - start_time
        print(f"Success! Time taken: {elapsed:.2f}s")
        return True, elapsed
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"Failed! Error: {e}")
        return False, elapsed

def main():
    scripts = [
        # Phase 1: DEM Processing (skip if outputs already exist)
        ('download_dem.py', None, 'Murredu_DEM.tif'),
        ('merge_dem.py', None, 'Murredu_DEM.tif'),
        ('clip_dem.py', None, 'Murredu_DEM_clip.tif'),
        ('prepare_dem.py', None, 'Murredu_DEM_breached.tif'),
        
        # Phase 2: Terrain Analysis
        ('make_slope.py', None, None),
        ('make_slope_classes.py', None, None),
        ('make_aspect.py', None, None),
        ('make_hillshade.py', None, None),
        ('make_contours.py', None, None),
        
        # Phase 3: Hydrology
        ('make_flow_accumulation.py', None, 'Flow_Accumulation.tif'),
        ('extract_streams.py', None, None),
        ('compare_drainage.py', None, None),
        ('compare_drainage_stats.py', None, None),
        ('make_watershed_boundary.py', None, None),
        ('make_stream_order.py', None, None),
        ('morphometric_analysis.py', None, None),
        
        # Phase 4: Remote Sensing
        ('make_false_color.py', 'murredu_data', None),
        ('make_lulc.py', 'murredu_data', None),
        ('make_vegetation_classes.py', 'murredu_data', None),
        ('calculate_water_area.py', 'murredu_data', None),
        
        # Phase 5: Generate all maps
        ('generate_all_maps.py', None, None),
        
        # Phase 6: Generate report
        ('watershed_report.py', None, None),
    ]

    total_run = 0
    succeeded = 0
    failed = 0
    total_time = 0

    for script, cwd, target_output in scripts:
        if target_output:
            full_target = os.path.join(cwd or '.', target_output)
            if os.path.exists(full_target):
                print(f"\nSkipping {script}: Output {full_target} already exists.")
                continue
                
        success, elapsed = run_script(script, cwd)
        total_run += 1
        if success:
            succeeded += 1
        else:
            failed += 1
        total_time += elapsed

    print(f"\n{'='*30}")
    print("Pipeline Execution Summary")
    print(f"{'='*30}")
    print(f"Total scripts run: {total_run}")
    print(f"Succeeded:         {succeeded}")
    print(f"Failed:            {failed}")
    print(f"Total time taken:  {total_time:.2f}s")
    print(f"{'='*30}")

if __name__ == '__main__':
    main()
