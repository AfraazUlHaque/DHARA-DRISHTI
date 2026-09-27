import requests
import os

tiles = [
    ("N17_00_E080_00", "Copernicus_DSM_COG_10_N17_00_E080_00_DEM"),
    ("N17_00_E081_00", "Copernicus_DSM_COG_10_N17_00_E081_00_DEM"),
    ("N18_00_E080_00", "Copernicus_DSM_COG_10_N18_00_E080_00_DEM"),
    ("N18_00_E081_00", "Copernicus_DSM_COG_10_N18_00_E081_00_DEM"),
]

base = "https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com"

os.makedirs("dem_tiles", exist_ok=True)

for tile_name, folder in tiles:

    filename = folder + ".tif"
    url = f"{base}/{folder}/{filename}"
    output = os.path.join("dem_tiles", filename)

    print("\nDownloading:", filename)

    r = requests.get(url, stream=True)

    print("Status:", r.status_code)

    if r.status_code == 200:
        with open(output, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        print("Saved:", output)
    else:
        print("Download failed:", url)

print("\nDEM download process complete!")