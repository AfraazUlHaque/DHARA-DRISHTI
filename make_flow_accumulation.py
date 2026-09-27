import whitebox
import os

wbt = whitebox.WhiteboxTools()

folder = os.getcwd()
wbt.set_working_dir(folder)
wbt.verbose = True

input_dem = os.path.join(folder, "Murredu_DEM_breached.tif")
output_acc = os.path.join(folder, "Flow_Accumulation.tif")

print("Calculating Flow Accumulation...")

wbt.d8_flow_accumulation(
    input_dem,
    output_acc,
    out_type="cells"
)

print("Flow accumulation completed!")
print("Output:", output_acc)