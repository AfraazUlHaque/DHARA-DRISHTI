import whitebox
import os

wbt = whitebox.WhiteboxTools()

folder = os.getcwd()

input_dem = os.path.join(folder, "Murredu_DEM_clip.tif")
output_dem = os.path.join(folder, "Murredu_DEM_breached.tif")

print("Input:", input_dem)
print("Input exists:", os.path.exists(input_dem))

wbt.set_working_dir(folder)
wbt.verbose = True

wbt.breach_depressions(
    input_dem,
    output_dem
)

print("Finished!")
print("Output exists:", os.path.exists(output_dem))