import whitebox
import os

wbt = whitebox.WhiteboxTools()

folder = os.getcwd()
wbt.set_working_dir(folder)
wbt.verbose = True

flow_acc = "Flow_Accumulation.tif"
streams = "Drainage_Network.tif"

# Working threshold
threshold = 1000

print("Extracting drainage network...")

wbt.extract_streams(
    flow_acc,
    streams,
    threshold
)

print("Drainage network created!")
print("Output:", os.path.join(folder, streams))