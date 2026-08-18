"""Offline coastline validation and conservative route repair for generated C:MO courses."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


EARTH_RADIUS_NM = 3440.065
GRID_DEGREES = 1.0


@dataclass(frozen=True)
class Point:
    lat: float
    lon: float

    def pair(self) -> list[float]:
        return [round(self.lat, 6), round(self.lon, 6)]


@dataclass(frozen=True)
class RouteIssue:
    kind: str
    point: Point
    clearance_nm: float
    message: str


def haversine_nm(left: Point, right: Point) -> float:
    lat1, lat2 = math.radians(left.lat), math.radians(right.lat)
    dlat = lat2 - lat1
    dlon = math.radians(right.lon - left.lon)
    value = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_NM * math.asin(math.sqrt(value))


def interpolate(left: Point, right: Point, ratio: float) -> Point:
    """Spherical interpolation along the great-circle leg."""
    if ratio <= 0:
        return left
    if ratio >= 1:
        return right
    left_lat, left_lon = math.radians(left.lat), math.radians(left.lon)
    right_lat, right_lon = math.radians(right.lat), math.radians(right.lon)
    angular = haversine_nm(left, right) / EARTH_RADIUS_NM
    if angular < 1e-12:
        return left
    scale_left = math.sin((1 - ratio) * angular) / math.sin(angular)
    scale_right = math.sin(ratio * angular) / math.sin(angular)
    x = scale_left * math.cos(left_lat) * math.cos(left_lon) + scale_right * math.cos(right_lat) * math.cos(right_lon)
    y = scale_left * math.cos(left_lat) * math.sin(left_lon) + scale_right * math.cos(right_lat) * math.sin(right_lon)
    z = scale_left * math.sin(left_lat) + scale_right * math.sin(right_lat)
    return Point(math.degrees(math.atan2(z, math.hypot(x, y))), math.degrees(math.atan2(y, x)))


def sample_segment(left: Point, right: Point, interval_nm: float) -> list[Point]:
    steps = max(1, math.ceil(haversine_nm(left, right) / interval_nm))
    return [interpolate(left, right, index / steps) for index in range(steps + 1)]


def offset_point(origin: Point, distance_nm: float, bearing: float) -> Point:
    return Point(
        origin.lat + math.cos(bearing) * distance_nm / 60,
        origin.lon + math.sin(bearing) * distance_nm / (60 * max(0.1, math.cos(math.radians(origin.lat)))),
    )


def _ring_contains(point: Point, ring: list[list[float]]) -> bool:
    inside = False
    previous = len(ring) - 1
    for current in range(len(ring)):
        current_lon, current_lat = ring[current]
        previous_lon, previous_lat = ring[previous]
        if ((current_lat > point.lat) != (previous_lat > point.lat)) and (
            point.lon < (previous_lon - current_lon) * (point.lat - current_lat)
            / (previous_lat - current_lat or math.ulp(1.0)) + current_lon
        ):
            inside = not inside
        previous = current
    return inside


def _bounds(points: Iterable[Point]) -> tuple[float, float, float, float]:
    values = list(points)
    return min(p.lon for p in values), min(p.lat for p in values), max(p.lon for p in values), max(p.lat for p in values)


def _grid_keys(bounds: tuple[float, float, float, float], padding_degrees: float = 0) -> Iterable[tuple[int, int]]:
    west, south, east, north = bounds
    for x in range(math.floor((west - padding_degrees) / GRID_DEGREES), math.floor((east + padding_degrees) / GRID_DEGREES) + 1):
        for y in range(math.floor((south - padding_degrees) / GRID_DEGREES), math.floor((north + padding_degrees) / GRID_DEGREES) + 1):
            yield x, y


def _segment_intersection(left_a: Point, right_a: Point, left_b: Point, right_b: Point) -> Point | None:
    rx, ry = right_a.lon - left_a.lon, right_a.lat - left_a.lat
    sx, sy = right_b.lon - left_b.lon, right_b.lat - left_b.lat
    denominator = rx * sy - ry * sx
    if abs(denominator) < 1e-12:
        return None
    ox, oy = left_b.lon - left_a.lon, left_b.lat - left_a.lat
    t = (ox * sy - oy * sx) / denominator
    u = (ox * ry - oy * rx) / denominator
    if 0 <= t <= 1 and 0 <= u <= 1:
        return Point(left_a.lat + ry * t, left_a.lon + rx * t)
    return None


def _point_segment_distance_nm(point: Point, left: Point, right: Point) -> float:
    origin_lat = point.lat
    scale_lon = 60 * math.cos(math.radians(origin_lat))
    start_x, start_y = (left.lon - point.lon) * scale_lon, (left.lat - point.lat) * 60
    end_x, end_y = (right.lon - point.lon) * scale_lon, (right.lat - point.lat) * 60
    dx, dy = end_x - start_x, end_y - start_y
    if dx == 0 and dy == 0:
        return math.hypot(start_x, start_y)
    projection = max(0.0, min(1.0, -(start_x * dx + start_y * dy) / (dx * dx + dy * dy)))
    return math.hypot(start_x + projection * dx, start_y + projection * dy)


class LandIndex:
    def __init__(self, geojson_path: Path, hazards_path: Path | None = None):
        data = json.loads(geojson_path.read_text(encoding="utf-8"))
        self.metadata = data.get("metadata", {})
        self.polygons: list[list[list[list[float]]]] = []
        self.polygon_grid: dict[tuple[int, int], list[int]] = {}
        self.segments: list[tuple[Point, Point]] = []
        self.segment_grid: dict[tuple[int, int], list[int]] = {}
        for feature in data.get("features", []):
            geometry = feature.get("geometry") or {}
            polygons = [geometry.get("coordinates", [])] if geometry.get("type") == "Polygon" else geometry.get("coordinates", [])
            for rings in polygons if geometry.get("type") in {"Polygon", "MultiPolygon"} else []:
                self._add_polygon(rings)
        self.hazards = []
        if hazards_path and hazards_path.is_file():
            hazards = json.loads(hazards_path.read_text(encoding="utf-8"))
            for hazard in hazards.get("hazards", []):
                center = Point(float(hazard["latitude"]), float(hazard["longitude"]))
                ring = [offset_point(center, float(hazard["radius_nm"]), index * 2 * math.pi / 48) for index in range(48)]
                coordinates = [[point.lon, point.lat] for point in ring] + [[ring[0].lon, ring[0].lat]]
                self._add_polygon([coordinates])
                self.hazards.append(hazard)

    def _add_polygon(self, rings: list[list[list[float]]]) -> None:
        if not rings or len(rings[0]) < 4:
            return
        polygon_index = len(self.polygons)
        self.polygons.append(rings)
        outer_points = [Point(lat, lon) for lon, lat in rings[0]]
        for key in _grid_keys(_bounds(outer_points)):
            self.polygon_grid.setdefault(key, []).append(polygon_index)
        for ring in rings:
            for index in range(len(ring) - 1):
                left = Point(ring[index][1], ring[index][0])
                right = Point(ring[index + 1][1], ring[index + 1][0])
                segment_index = len(self.segments)
                self.segments.append((left, right))
                for key in _grid_keys(_bounds((left, right))):
                    self.segment_grid.setdefault(key, []).append(segment_index)

    def _candidate_polygons(self, point: Point) -> Iterable[list[list[list[float]]]]:
        for index in self.polygon_grid.get((math.floor(point.lon), math.floor(point.lat)), []):
            yield self.polygons[index]

    def _candidate_segments(self, bounds: tuple[float, float, float, float], padding_nm: float = 0) -> Iterable[tuple[Point, Point]]:
        indices = set()
        padding_degrees = padding_nm / 45
        for key in _grid_keys(bounds, padding_degrees):
            indices.update(self.segment_grid.get(key, []))
        for index in indices:
            yield self.segments[index]

    def point_on_land(self, point: Point) -> bool:
        for rings in self._candidate_polygons(point):
            if _ring_contains(point, rings[0]) and not any(_ring_contains(point, hole) for hole in rings[1:]):
                return True
        return False

    def clearance_nm(self, point: Point, search_nm: float = 120) -> float:
        if self.point_on_land(point):
            return -min((_point_segment_distance_nm(point, *segment) for segment in self._candidate_segments(_bounds((point,)), search_nm)), default=0.0)
        nearest = min((_point_segment_distance_nm(point, *segment) for segment in self._candidate_segments(_bounds((point,)), search_nm)), default=search_nm)
        return nearest

    def first_intersection(self, left: Point, right: Point) -> Point | None:
        if self.point_on_land(left):
            return left
        geodesic = sample_segment(left, right, 5)
        for route_left, route_right in zip(geodesic, geodesic[1:]):
            intersections = []
            for coast_left, coast_right in self._candidate_segments(_bounds((route_left, route_right))):
                intersection = _segment_intersection(route_left, route_right, coast_left, coast_right)
                if intersection:
                    intersections.append(intersection)
            if intersections:
                return min(intersections, key=lambda point: haversine_nm(route_left, point))
        return right if self.point_on_land(right) else None

    def leg_issue(self, left: Point, right: Point, clearance_nm: float, sample_nm: float = 0.25) -> RouteIssue | None:
        crossing = self.first_intersection(left, right)
        if crossing:
            return RouteIssue("land-crossing", crossing, 0.0, "route leg intersects mapped land")
        nearest_point, nearest_clearance = min(
            ((point, self.clearance_nm(point, max(20, clearance_nm * 4))) for point in sample_segment(left, right, sample_nm)),
            key=lambda item: item[1],
        )
        if nearest_clearance < clearance_nm:
            return RouteIssue("clearance", nearest_point, nearest_clearance, f"route leg has only {nearest_clearance:.2f} nm land clearance")
        return None

    def validate_route(self, points: list[Point], clearance_nm: float) -> list[RouteIssue]:
        issues = []
        for index, point in enumerate(points):
            point_clearance = self.clearance_nm(point)
            if point_clearance < clearance_nm:
                kind = "point-on-land" if point_clearance <= 0 else "point-clearance"
                issues.append(RouteIssue(kind, point, point_clearance, f"route point {index + 1} has {point_clearance:.2f} nm land clearance"))
        for left, right in zip(points, points[1:]):
            issue = self.leg_issue(left, right, clearance_nm)
            if issue:
                issues.append(issue)
        return issues

    def minimum_route_clearance(self, points: list[Point], sample_nm: float = 0.25) -> float:
        samples = points[:1]
        for left, right in zip(points, points[1:]):
            samples.extend(sample_segment(left, right, sample_nm)[1:])
        return min(self.clearance_nm(point) for point in samples)

    def _repair_leg(self, left: Point, right: Point, clearance_nm: float, max_detours: int, max_radius_nm: float) -> list[Point]:
        route = [left]
        cursor = left
        for _ in range(max_detours):
            issue = self.leg_issue(cursor, right, clearance_nm)
            if not issue:
                route.append(right)
                return self._simplify(route, clearance_nm)
            candidates = []
            direct_candidates = []
            step = max(1.0, clearance_nm / 2)
            radius = max(step, clearance_nm)
            while radius <= max_radius_nm:
                angular_steps = max(32, math.ceil(radius * 3))
                for index in range(angular_steps):
                    candidate = offset_point(issue.point, radius, index * 2 * math.pi / angular_steps)
                    if self.clearance_nm(candidate, max(20, clearance_nm * 4)) < clearance_nm:
                        continue
                    if haversine_nm(candidate, right) >= haversine_nm(cursor, right) - 0.25:
                        continue
                    if self.leg_issue(cursor, candidate, clearance_nm):
                        continue
                    score = haversine_nm(cursor, candidate) + haversine_nm(candidate, right)
                    next_issue = self.leg_issue(candidate, right, clearance_nm)
                    if not next_issue:
                        direct_candidates.append((score, candidate))
                    else:
                        safe_ahead = haversine_nm(candidate, next_issue.point)
                        candidates.append((-safe_ahead, score, candidate))
                if direct_candidates:
                    break
                radius += step
            if direct_candidates:
                cursor = min(direct_candidates, key=lambda item: item[0])[1]
            elif candidates:
                cursor = min(candidates, key=lambda item: (item[0], item[1]))[2]
            else:
                raise ValueError(f"unable to find a safe detour within {max_radius_nm:g} nm near {issue.point.pair()}")
            route.append(cursor)
        raise ValueError(f"route repair exceeded {max_detours} detours between {left.pair()} and {right.pair()}")

    def _simplify(self, route: list[Point], clearance_nm: float) -> list[Point]:
        simplified = [route[0]]
        index = 0
        while index < len(route) - 1:
            target = len(route) - 1
            while target > index + 1 and self.leg_issue(route[index], route[target], clearance_nm):
                target -= 1
            simplified.append(route[target])
            index = target
        return simplified

    def nearest_safe_water(self, origin: Point, clearance_nm: float, max_radius_nm: float = 30) -> Point | None:
        step = max(0.5, clearance_nm / 3)
        radius = step
        while radius <= max_radius_nm:
            angular_steps = max(36, math.ceil(radius * 4))
            candidates = []
            for index in range(angular_steps):
                candidate = offset_point(origin, radius, index * 2 * math.pi / angular_steps)
                if self.clearance_nm(candidate, max(20, clearance_nm * 4)) >= clearance_nm:
                    candidates.append(candidate)
            if candidates:
                return min(candidates, key=lambda candidate: haversine_nm(origin, candidate))
            radius += step
        return None

    def repair_route(self, points: list[Point], clearance_nm: float, max_detours: int = 24, max_radius_nm: float = 120) -> list[Point]:
        if len(points) < 2:
            raise ValueError("route requires a start and at least one waypoint")
        if self.clearance_nm(points[0]) < clearance_nm:
            raise ValueError(f"route start is invalid and cannot be silently moved: {points[0].pair()}")
        repaired = [points[0]]
        for destination in points[1:]:
            if self.clearance_nm(destination) < clearance_nm:
                relocated = self.nearest_safe_water(destination, clearance_nm)
                if not relocated:
                    raise ValueError(f"unable to relocate invalid authored destination: {destination.pair()}")
                destination = relocated
            leg = self._repair_leg(repaired[-1], destination, clearance_nm, max_detours, max_radius_nm)
            repaired.extend(leg[1:])
        remaining = self.validate_route(repaired, clearance_nm)
        if remaining:
            raise ValueError(f"route repair left {len(remaining)} unresolved navigation issues")
        return repaired


def points(values: Iterable[Iterable[float]]) -> list[Point]:
    return [Point(float(value[0]), float(value[1])) for value in values]
