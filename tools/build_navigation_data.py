"""Build a clipped South China Sea coastline asset from Natural Earth 1:10m data."""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tools" / "data" / "scs-land.geojson"
BOUNDS = {"west": 105.0, "south": 3.0, "east": 130.0, "north": 25.0}
SOURCES = [
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_land.geojson",
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_minor_islands.geojson",
]


def clip_ring(ring: list[list[float]], bounds: dict[str, float]) -> list[list[float]]:
    """Clip a closed lon/lat ring to a rectangular theater boundary."""

    points = [list(point[:2]) for point in ring]
    if points and points[0] == points[-1]:
        points.pop()

    def clip(points_in, inside, intersect):
        if not points_in:
            return []
        result = []
        previous = points_in[-1]
        previous_inside = inside(previous)
        for current in points_in:
            current_inside = inside(current)
            if current_inside:
                if not previous_inside:
                    result.append(intersect(previous, current))
                result.append(current)
            elif previous_inside:
                result.append(intersect(previous, current))
            previous, previous_inside = current, current_inside
        return result

    def vertical(left, right, longitude):
        ratio = (longitude - left[0]) / (right[0] - left[0])
        return [longitude, left[1] + (right[1] - left[1]) * ratio]

    def horizontal(left, right, latitude):
        ratio = (latitude - left[1]) / (right[1] - left[1])
        return [left[0] + (right[0] - left[0]) * ratio, latitude]

    points = clip(points, lambda p: p[0] >= bounds["west"], lambda a, b: vertical(a, b, bounds["west"]))
    points = clip(points, lambda p: p[0] <= bounds["east"], lambda a, b: vertical(a, b, bounds["east"]))
    points = clip(points, lambda p: p[1] >= bounds["south"], lambda a, b: horizontal(a, b, bounds["south"]))
    points = clip(points, lambda p: p[1] <= bounds["north"], lambda a, b: horizontal(a, b, bounds["north"]))
    if len(points) < 3:
        return []
    points.append(points[0])
    return [[round(value, 6) for value in point] for point in points]


def load_collection(source: str) -> dict:
    path = Path(source)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    with urllib.request.urlopen(source, timeout=60) as response:
        return json.load(response)


def clipped_features(collection: dict) -> list[dict]:
    features = []
    for feature in collection.get("features", []):
        geometry = feature.get("geometry") or {}
        kind = geometry.get("type")
        polygons = [geometry.get("coordinates", [])] if kind == "Polygon" else geometry.get("coordinates", [])
        for polygon in polygons if kind in {"Polygon", "MultiPolygon"} else []:
            if not polygon:
                continue
            outer = clip_ring(polygon[0], BOUNDS)
            if not outer:
                continue
            rings = [outer]
            for hole in polygon[1:]:
                clipped = clip_ring(hole, BOUNDS)
                if clipped:
                    rings.append(clipped)
            features.append({"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": rings}})
    return features


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", help="Local combined GeoJSON; repeat for multiple sources")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    sources = args.source or SOURCES
    features = []
    source_labels = []
    for source in sources:
        collection = load_collection(source)
        features.extend(clipped_features(collection))
        source_labels.extend(collection.get("metadata", {}).get("sourceUrls", []) or [source])
    output = {
        "type": "FeatureCollection",
        "metadata": {
            "title": "South China Sea Natural Earth 1:10m land and minor islands",
            "source": "Natural Earth public-domain 1:10m land and minor-islands datasets",
            "source_inputs": sorted(set(source_labels)),
            "bounds": BOUNDS,
            "coordinate_order": "longitude, latitude",
        },
        "features": features,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote {len(features)} clipped polygons to {args.output} ({args.output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
