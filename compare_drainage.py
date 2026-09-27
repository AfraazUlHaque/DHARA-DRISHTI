import whitebox
import os

wbt = whitebox.WhiteboxTools()

folder = os.getcwd()
wbt.set_working_dir(folder)
wbt.verbose = True

flow_acc = "Flow_Accumulation.tif"

for threshold in [500, 1000, 2500]:

    output = f"Drainage_{threshold}.tif"

    print(f"\nExtracting drainage with threshold = {threshold}")

    wbt.extract_streams(
        flow_acc,
        output,
        threshold
    )

    print(f"Created: {output}")

print("\nAll drainage networks created!")