from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.navigation import LandIndex, Point, points


ROOT = Path(__file__).resolve().parents[1]


class NavigationGeometryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.geojson = Path(self.temp.name) / "land.geojson"
        self.geojson.write_text(json.dumps({
            "type": "FeatureCollection",
            "metadata": {"title": "synthetic"},
            "features": [{
                "type": "Feature", "properties": {},
                "geometry": {"type": "Polygon", "coordinates": [[
                    [0.8, -0.2], [1.2, -0.2], [1.2, 0.2], [0.8, 0.2], [0.8, -0.2],
                ]]},
            }],
        }), encoding="utf-8")
        self.land = LandIndex(self.geojson)

    def test_detects_points_and_exact_leg_crossing(self):
        self.assertTrue(self.land.point_on_land(Point(0, 1)))
        self.assertFalse(self.land.point_on_land(Point(0, 0)))
        crossing = self.land.first_intersection(Point(0, 0), Point(0, 2))
        self.assertIsNotNone(crossing)
        self.assertAlmostEqual(crossing.lon, 0.8, places=6)

    def test_repairs_with_multiple_clear_waypoints_and_revalidates(self):
        original = points([[0, 0], [0, 2]])
        repaired = self.land.repair_route(original, clearance_nm=2, max_radius_nm=60)
        self.assertGreater(len(repaired), 2)
        self.assertEqual(self.land.validate_route(repaired, 2), [])
        self.assertEqual(repaired[0], original[0])
        self.assertEqual(repaired[-1], original[-1])

    def test_relocates_an_invalid_authored_waypoint(self):
        original = points([[0, 0], [0, 1], [0, 2]])
        repaired = self.land.repair_route(original, clearance_nm=2, max_radius_nm=60)
        self.assertNotIn(original[1], repaired)
        self.assertEqual(self.land.validate_route(repaired, 2), [])


class SouthChinaSeaDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.land = LandIndex(ROOT / "tools/data/scs-land.geojson", ROOT / "tools/data/scs-hazards.json")

    def test_supplemental_hazard_catches_scarborough_route(self):
        route = points([[15.4, 117.8], [14.5, 117.6]])
        self.assertTrue(any(issue.kind == "land-crossing" for issue in self.land.validate_route(route, 2)))

    def test_current_known_problem_routes_are_automatically_repaired(self):
        routes = [
            (3, [[12.5, 113.8], [11.8, 114.0], [10.8, 114.5]]),
            (3, [[17.8, 111.8], [17.0, 112.3], [16.0, 112.9]]),
            (2, [[16.2, 118.4], [15.4, 117.8], [14.5, 117.6]]),
        ]
        for clearance, raw in routes:
            with self.subTest(route=raw):
                original = points(raw)
                self.assertTrue(self.land.validate_route(original, clearance))
                repaired = self.land.repair_route(original, clearance)
                self.assertEqual(self.land.validate_route(repaired, clearance), [])


if __name__ == "__main__":
    unittest.main()
