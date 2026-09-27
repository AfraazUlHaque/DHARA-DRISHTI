import json
from pathlib import Path

from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.ops import transform
from pyproj import Transformer

BASE_DIR = Path(__file__).resolve().parent
INPUT = BASE_DIR / "Murredu_Watershed.geojson"
OUTPUT = BASE_DIR / "Murredu_Watershed_CLEAN.geojson"

# WGS84 -> UTM Zone 44N, suitable for the Murredu area.
to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32644", always_xy=True).transform
to_wgs84 = Transformer.from_crs("EPSG:32644", "EPSG:4326", always_xy=True).transform

# Remove tiny disconnected pieces below this area.
MIN_PART_AREA_M2 = 50_000  # 0.05 km²


def clean_polygon(poly):
    # The unwanted dots in the screenshot are tiny interior rings.
    # A watershed boundary should be represented by its outer outline,
    # so remove all interior holes/rings.
    return Polygon(poly.exterior)


def clean_geometry(geom):
    projected = transform(to_utm, geom)

    if isinstance(projected, Polygon):
        cleaned = clean_polygon(projected)

    elif isinstance(projected, MultiPolygon):
        parts = [
            clean_polygon(p)
            for p in projected.geoms
            if p.area >= MIN_PART_AREA_M2
        ]

        if not parts:
            raise ValueError("No polygon remains after removing tiny parts.")

        # Keep all meaningful watershed parts.
        cleaned = MultiPolygon(parts) if len(parts) > 1 else parts[0]

    else:
        raise ValueError(f"Unsupported geometry type: {projected.geom_type}")

    cleaned = transform(to_wgs84, cleaned)

    # Final validity repair if needed.
    cleaned = cleaned.buffer(0)

    return cleaned


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Input not found: {INPUT}")

    data = json.loads(INPUT.read_text(encoding="utf-8"))

    if data.get("type") == "FeatureCollection":
        if not data.get("features"):
            raise ValueError("FeatureCollection contains no features.")

        feature = data["features"][0]
        geom = shape(feature["geometry"])
        props = feature.get("properties", {})

    elif data.get("type") == "Feature":
        geom = shape(data["geometry"])
        props = data.get("properties", {})

    else:
        geom = shape(data)
        props = {}

    cleaned = clean_geometry(geom)

    output = {
        "type": "Feature",
        "properties": {
            **props,
            "cleaned": True,
            "cleaning": "Removed interior rings and tiny disconnected polygon parts",
        },
        "geometry": mapping(cleaned),
    }

    OUTPUT.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Clean boundary created:")
    print(OUTPUT)
    print(f"Original geometry: {geom.geom_type}")
    print(f"Cleaned geometry:  {cleaned.geom_type}")


if __name__ == "__main__":
    main()
