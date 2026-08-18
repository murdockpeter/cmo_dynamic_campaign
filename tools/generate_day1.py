"""Generate the deterministic South China Sea Day 1 CMO build package."""

from __future__ import annotations

import json
import shutil
import uuid
import html as html_lib
from pathlib import Path

try:
    from .navigation import LandIndex, Point, points
except ImportError:
    from navigation import LandIndex, Point, points


ROOT = Path(__file__).resolve().parents[1]
DAY = ROOT / "days" / "day-001"
CMO_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Command - Modern Operations")
DEPLOY = CMO_ROOT / "Lua" / "DynamicCampaign" / "SCS_Day1"
EXPORT = CMO_ROOT / "ImportExport" / "DynamicCampaign" / "SCS"
NAMESPACE = uuid.UUID("4fd9bafa-b625-4ae4-b881-938edec3335f")
LAND_DATA = ROOT / "tools" / "data" / "scs-land.geojson"
HAZARD_DATA = ROOT / "tools" / "data" / "scs-hazards.json"
SURFACE_CLEARANCE_NM = 3.0
SUBMARINE_CLEARANCE_NM = 2.0
SUBMARINE_MIN_WATER_DEPTH_M = 200
CMO_TERRAIN_SAMPLE_NM = 0.5
SHIP_OFFSETS = [(0.0, 0.0), (.05, .04), (-.05, .04), (.04, -.05), (-.04, -.05), (.08, 0), (-.08, 0)]


def guid(campaign_id: str) -> str:
    return str(uuid.uuid5(NAMESPACE, campaign_id))


air_packages = [
    # side, prefix, dbid, base, assigned, ready, ready loadouts
    ("BLUE", "BLU-PH-FA50", 6905, "Basa Air Base", 12, 10, [21785]),
    ("BLUE", "BLU-USAF-F16", 5639, "Basa Air Base", 12, 10, [11128] * 6 + [12075] * 2 + [30385] * 2),
    ("BLUE", "BLU-USMC-F35B-AB", 4701, "Puerto Princesa International Airport/Antonio Bautista AB", 10, 8, [10064] * 6 + [18064] * 2),
    ("BLUE", "BLU-USN-P8", 5759, "Puerto Princesa International Airport/Antonio Bautista AB", 4, 3, [30778]),
    ("BLUE", "BLU-USMC-MQ9", 7473, "Puerto Princesa International Airport/Antonio Bautista AB", 4, 3, [8600]),
    ("BLUE", "BLU-USMC-KC130", 6631, "Puerto Princesa International Airport/Antonio Bautista AB", 2, 1, [8408]),
    ("BLUE", "BLU-USAF-F35A", 3835, "Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport", 12, 10, [1836] * 8 + [35085] * 2),
    ("BLUE", "BLU-USAF-KC135", 6621, "Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport", 4, 3, [8835]),
    ("BLUE", "BLU-USAF-E3", 3853, "Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport", 2, 1, [8076]),
    ("BLUE", "BLU-USAF-RC135", 5832, "Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport", 1, 1, [8824]),
    ("BLUE", "BLU-USAF-C130J", 7008, "Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport", 4, 3, [30209]),
    ("BLUE", "BLU-USAF-HH60W", 4366, "Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport", 4, 3, [29536]),
    ("RED", "RED-PLANAF-J16", 2853, "Lingshui AB (PLAN)", 24, 20, [26234] * 10 + [21743] * 10),
    ("RED", "RED-PLANAF-H6J", 7184, "Lingshui AB (PLAN)", 6, 4, [26241]),
    ("RED", "RED-PLANAF-Y8Q-LS", 7418, "Lingshui AB (PLAN)", 4, 3, [27636]),
    ("RED", "RED-PLANAF-KJ500H", 7176, "Lingshui AB (PLAN)", 2, 1, [18300]),
    ("RED", "RED-PLAAF-GJ2-LS", 4725, "Lingshui AB (PLAN)", 4, 3, [25718]),
    ("RED", "RED-PLAAF-J10-SX", 7658, "Suixi AB  (PLAAF)", 24, 20, [25177]),
    ("RED", "RED-PLAAF-J20", 5014, "Suixi AB  (PLAAF)", 12, 10, [28028]),
    ("RED", "RED-PLAAF-J16D", 4632, "Suixi AB  (PLAAF)", 4, 3, [25212]),
    ("RED", "RED-PLAAF-KJ500", 6004, "Suixi AB  (PLAAF)", 2, 1, [18300]),
    ("RED", "RED-PLAAF-YY20", 4975, "Suixi AB  (PLAAF)", 3, 2, [27886]),
    ("RED", "RED-PLAAF-J10-WI", 7658, "Woody Island", 8, 6, [25178]),
    ("RED", "RED-PLANAF-Y8Q-WI", 7418, "Woody Island", 2, 1, [27636]),
    ("RED", "RED-PLAAF-GJ2-WI", 4725, "Woody Island", 2, 1, [25718]),
    ("RED", "RED-PLAAF-J10-FC", 7658, "Fiery Cross Reef", 8, 6, [25178]),
    ("RED", "RED-PLAAF-GJ2-FC", 4725, "Fiery Cross Reef", 4, 3, [25718]),
    ("RED", "RED-PLANAF-Y9JB", 3692, "Fiery Cross Reef", 2, 1, [21676]),
]

ship_groups = [
    ("BLUE", "TG B-1 George Washington CSG", 15.0, 125.1, [
        ("BLU-USN-CVN-0001", 5167), ("BLU-USN-DDG-0001", 2718),
        ("BLU-USN-DDG-0002", 5110), ("BLU-USN-DDG-0003", 5122),
        ("BLU-USN-AOE-0001", 5036)]),
    ("BLUE", "TG B-2 Philippine West Sea SAG", 10.8, 117.8, [
        ("BLU-PHN-FFG-0001", 3545), ("BLU-PHN-FFG-0002", 3545),
        ("BLU-PHN-COR-0001", 3325)]),
    ("BLUE", "TG B-3 America ARG", 10.2, 121.1, [
        ("BLU-USN-LHA-0001", 3563), ("BLU-USN-LPD-0001", 4300),
        ("BLU-USN-DDG-0004", 5169)]),
    ("RED", "TG R-1 Shandong CSG", 16.3, 114.5, [
        ("RED-PLAN-CV-0001", 3187), ("RED-PLAN-DDG-0001", 3883),
        ("RED-PLAN-DDG-0002", 4719), ("RED-PLAN-DDG-0003", 4937),
        ("RED-PLAN-FFG-0001", 4725), ("RED-PLAN-AOE-0001", 2980)]),
    ("RED", "TG R-2 Southern Theater SAG", 12.5, 113.8, [
        ("RED-PLAN-DDG-0004", 3883), ("RED-PLAN-DDG-0005", 4719),
        ("RED-PLAN-DDG-0006", 4937), ("RED-PLAN-FFG-0002", 4725),
        ("RED-PLAN-AOR-0001", 2927)]),
    ("RED", "TG R-3 Hainan Amphibious Group", 17.8, 111.8, [
        ("RED-PLAN-LHD-0001", 3153), ("RED-PLAN-LPD-0001", 4922),
        ("RED-PLAN-LPD-0002", 2006), ("RED-PLAN-DDG-0007", 4719),
        ("RED-PLAN-FFG-0003", 4725)]),
]

group_courses = [
    ("BLUE", "TG B-1 George Washington CSG", (15.0, 125.1), [(14.5, 124.9), (13.8, 124.5)]),
    ("BLUE", "TG B-2 Philippine West Sea SAG", (10.8, 117.8), [(11.4, 117.3), (12.0, 116.9)]),
    # Route south around Palawan; C:MO's detailed islets make the northern passages unsafe.
    ("BLUE", "TG B-3 America ARG", (10.2, 121.1), [(9.0, 120.5), (7.5, 118.5), (7.5, 117.0), (8.5, 116.5), (9.5, 117.2), (10.5, 118.2), (11.0, 118.7), (11.6, 119.5), (11.310439, 119.78204), (11.2, 119.7)]),
    ("RED", "TG R-1 Shandong CSG", (16.3, 114.5), [(15.5, 114.2), (14.7, 114.0)]),
    ("RED", "TG R-2 Southern Theater SAG", (12.5, 113.8), [(11.8, 114.0), (10.8, 114.5)]),
    ("RED", "TG R-3 Hainan Amphibious Group", (17.8, 111.8), [(17.0, 112.3), (16.0, 112.9)]),
]

submarines = [
    ("BLUE", "BLU-USN-SSN-0001", 828, 16.2, 118.4, [(15.4, 117.8), (14.5, 117.6)]),
    ("BLUE", "BLU-USN-SSN-0002", 827, 12.7, 115.7, [(11.8, 115.2), (11.0, 115.8)]),
    ("BLUE", "BLU-USN-SSN-0003", 830, 10.6, 116.4, [(10.3, 116.4), (9.8, 116.2), (9.2, 115.7)]),
    ("BLUE", "BLU-USN-SSN-0004", 837, 9.5, 117.4, [(10.2, 117.1), (10.6, 117.6), (11.0, 117.2)]),
    ("RED", "RED-PLAN-SSN-0001", 665, 17.0, 116.0, [(16.0, 116.4), (15.0, 116.0)]),
    ("RED", "RED-PLAN-SSN-0002", 665, 13.5, 117.3, [(12.8, 117.0), (12.0, 117.5)]),
    ("RED", "RED-PLAN-SSK-0001", 695, 11.2, 114.8, [(11.2, 115.2), (10.5, 115.3), (9.8, 115.0)]),
    ("RED", "RED-PLAN-SSK-0002", 695, 9.6, 115.5, [(9.0, 115.1), (8.5, 115.7)]),
    ("RED", "RED-PLAN-SSK-0003", 580, 15.0, 119.0, [(14.3, 118.5), (13.5, 118.8)]),
    ("RED", "RED-PLAN-SSBN-0001", 773, 18.1, 111.0, [(17.8, 111.4), (17.2, 111.5), (17.7, 111.8)]),
]

embarked_packages = [
    ("BLUE", "BLU-USN-F35C", 4874, "TG B-1 George Washington CSG", 10, 10, [10098] * 6 + [33864] * 4),
    ("BLUE", "BLU-USN-FA18E", 3483, "TG B-1 George Washington CSG", 16, 16, [15483] * 12 + [22742] * 4),
    ("BLUE", "BLU-USN-FA18F", 3482, "TG B-1 George Washington CSG", 8, 8, [15485] * 4 + [22742] * 4),
    ("BLUE", "BLU-USN-EA18G", 4518, "TG B-1 George Washington CSG", 5, 5, [22929] * 3 + [27345] * 2),
    ("BLUE", "BLU-USN-E2D", 7114, "TG B-1 George Washington CSG", 5, 5, [14629]),
    ("BLUE", "BLU-USN-MH60R", 5338, "TG B-1 George Washington CSG", 6, 6, [1101]),
    ("BLUE", "BLU-USN-MH60S", 5337, "TG B-1 George Washington CSG", 4, 4, [25707]),
    ("BLUE", "BLU-USN-CMV22", 4558, "TG B-1 George Washington CSG", 3, 3, [23143]),
    ("BLUE", "BLU-USMC-F35B-ARG", 4701, "TG B-3 America ARG", 10, 10, [10064] * 6 + [18064] * 4),
    ("BLUE", "BLU-USMC-MV22", 7516, "TG B-3 America ARG", 6, 6, [3557]),
    ("BLUE", "BLU-USMC-CH53K", 4029, "TG B-3 America ARG", 2, 2, [20057]),
    ("BLUE", "BLU-USMC-AH1Z", 7514, "TG B-3 America ARG", 2, 2, [26107]),
    ("BLUE", "BLU-USMC-UH1Y", 7515, "TG B-3 America ARG", 2, 2, [13983]),
    ("RED", "RED-PLANAF-J15", 7139, "TG R-1 Shandong CSG", 24, 24, [30185] * 16 + [34295] * 8),
    ("RED", "RED-PLANAF-J15D", 4817, "TG R-1 Shandong CSG", 4, 4, [25212]),
    ("RED", "RED-PLANAF-Z18J", 7357, "TG R-1 Shandong CSG", 2, 2, [17471]),
    ("RED", "RED-PLANAF-Z18F", 7359, "TG R-1 Shandong CSG", 4, 4, [18368]),
    ("RED", "RED-PLANAF-Z9D", 7349, "TG R-1 Shandong CSG", 4, 4, [11837]),
]

templates = [
    ("BLUE", "Philippines/Basa Air Base 2011.inst"),
    ("BLUE", "Philippines/Puerto Princesa International Airport-Antonio Bautista AB.inst"),
    ("BLUE", "Philippines/Benito Ebeun (Mactan) AB Mactan-Cebu International Airport 2011.inst"),
    ("RED", "China/Hainan Island/PLAN Lingshui AB 2011.inst"),
    ("RED", "China/Guangzhou/PLAAF Suixi AB 2011.inst"),
    ("RED", "China/South China Sea Islands and Reefs/Woody Island 2022.inst"),
    ("RED", "China/South China Sea Islands and Reefs/Fiery Cross Reef 2022.inst"),
]

mission_specs = [
    {"side": "BLUE", "name": "BLUE West Luzon CAP", "display_name": "West Luzon CAP", "kind": "Patrol", "type": "AAW", "points": [[14.0, 117.5], [18.0, 117.5], [18.0, 120.0], [14.0, 120.0]], "onstation": 2, "active": True, "units": ["BLU-USAF-F16-01", "BLU-USAF-F16-02", "BLU-USAF-F16-03", "BLU-USAF-F16-04", "BLU-USAF-F16-05", "BLU-USAF-F16-06", "BLU-PH-FA50-01", "BLU-PH-FA50-02"]},
    {"side": "BLUE", "name": "BLUE Palawan CAP", "display_name": "Palawan CAP", "kind": "Patrol", "type": "AAW", "points": [[8.0, 116.8], [12.5, 116.8], [12.5, 119.3], [8.0, 119.3]], "onstation": 2, "active": True, "units": ["BLU-USMC-F35B-AB-01", "BLU-USMC-F35B-AB-02", "BLU-USMC-F35B-AB-03", "BLU-USMC-F35B-AB-04", "BLU-USMC-F35B-AB-05", "BLU-USMC-F35B-AB-06"]},
    {"side": "BLUE", "name": "BLUE AEW Central", "display_name": "AEW Central", "kind": "Support", "type": "AEW", "points": [[12.3, 122.0], [14.0, 122.0]], "onstation": 1, "units": ["BLU-USAF-E3-01"]},
    {"side": "BLUE", "name": "BLUE Tanker Central", "display_name": "Tanker Central", "kind": "Support", "type": "TANKER", "points": [[11.5, 122.5], [14.5, 122.5]], "onstation": 1, "units": ["BLU-USAF-KC135-01", "BLU-USAF-KC135-02", "BLU-USMC-KC130-01"]},
    {"side": "BLUE", "name": "BLUE Palawan ASW", "display_name": "Palawan ASW", "kind": "Patrol", "type": "ASW", "points": [[8.0, 115.0], [12.5, 115.0], [12.5, 117.5], [8.0, 117.5]], "onstation": 1, "active": True, "units": ["BLU-USN-P8-01", "BLU-USN-P8-02", "BLU-USN-P8-03"]},
    {"side": "RED", "name": "RED Hainan CAP", "display_name": "Hainan CAP", "kind": "Patrol", "type": "AAW", "points": [[16.5, 109.5], [22.0, 109.5], [22.0, 114.0], [16.5, 114.0]], "onstation": 4, "active": True, "units": ["RED-PLANAF-J16-01", "RED-PLANAF-J16-02", "RED-PLANAF-J16-03", "RED-PLANAF-J16-04", "RED-PLAAF-J10-SX-01", "RED-PLAAF-J10-SX-02", "RED-PLAAF-J20-01", "RED-PLAAF-J20-02"]},
    {"side": "RED", "name": "RED Spratly CAP", "display_name": "Spratly CAP", "kind": "Patrol", "type": "AAW", "points": [[8.0, 111.0], [12.0, 111.0], [12.0, 115.0], [8.0, 115.0]], "onstation": 2, "active": True, "units": ["RED-PLAAF-J10-FC-01", "RED-PLAAF-J10-FC-02", "RED-PLAAF-J10-FC-03", "RED-PLAAF-J10-FC-04"]},
    {"side": "RED", "name": "RED AEW Hainan", "display_name": "AEW Hainan", "kind": "Support", "type": "AEW", "points": [[17.0, 112.0], [19.0, 112.0]], "onstation": 1, "units": ["RED-PLANAF-KJ500H-01", "RED-PLAAF-KJ500-01"]},
    {"side": "RED", "name": "RED Tanker Hainan", "display_name": "Tanker Hainan", "kind": "Support", "type": "TANKER", "points": [[18.0, 113.0], [20.0, 113.0]], "onstation": 1, "units": ["RED-PLAAF-YY20-01", "RED-PLAAF-YY20-02"]},
    {"side": "RED", "name": "RED Central Basin ASW", "display_name": "Central Basin ASW", "kind": "Patrol", "type": "ASW", "points": [[11.0, 114.0], [17.0, 114.0], [17.0, 118.0], [11.0, 118.0]], "onstation": 1, "active": True, "units": ["RED-PLANAF-Y8Q-LS-01", "RED-PLANAF-Y8Q-LS-02", "RED-PLANAF-Y8Q-WI-01"]},
]

boundaries = [
    {"name": "Mainland strike restriction", "note": "Attacks require an explicit escalation event.", "points": [[18.0, 108.2], [23.0, 108.2], [23.0, 117.5], [18.0, 117.5]]},
]


def lua_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def write_route_audit(audit: dict[str, object]) -> None:
    (DAY / "route-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    land_data = json.loads(LAND_DATA.read_text(encoding="utf-8"))
    bounds = land_data["metadata"]["bounds"]
    width, height = 1100, 720

    def xy(pair: list[float]) -> tuple[float, float]:
        lon, lat = pair
        x = (lon - bounds["west"]) / (bounds["east"] - bounds["west"]) * width
        y = height - (lat - bounds["south"]) / (bounds["north"] - bounds["south"]) * height
        return x, y

    land_paths = []
    for feature in land_data.get("features", []):
        for ring in feature["geometry"]["coordinates"][:1]:
            coords = " ".join(f"{xy(point)[0]:.1f},{xy(point)[1]:.1f}" for point in ring)
            land_paths.append(f'<polygon points="{coords}" class="land"/>')
    route_paths = []
    for route in audit["routes"]:
        css = "blue" if route["side"] == "BLUE" else "red"
        original = " ".join(f"{xy([point[1], point[0]])[0]:.1f},{xy([point[1], point[0]])[1]:.1f}" for point in route["original_points"])
        resolved = " ".join(f"{xy([point[1], point[0]])[0]:.1f},{xy([point[1], point[0]])[1]:.1f}" for point in route["resolved_points"])
        if route["changed"]:
            route_paths.append(f'<polyline points="{original}" class="original"/>')
        route_paths.append(f'<polyline points="{resolved}" class="route {css}"/>')
    hazard_marks = []
    for hazard in audit["supplemental_hazards"]:
        x, y = xy([hazard["longitude"], hazard["latitude"]])
        radius = hazard["radius_nm"] / 60 / (bounds["east"] - bounds["west"]) * width
        hazard_marks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(2, radius):.1f}" class="hazard"><title>{html_lib.escape(hazard["name"])}</title></circle>')
    rows = []
    for route in audit["routes"]:
        issues = "<br>".join(html_lib.escape(issue["message"]) for issue in route["initial_issues"]) or "None"
        rows.append(
            f"<tr><td><b>{html_lib.escape(route['id'])}</b><small>{route['side']} · {route['domain']}</small></td>"
            f"<td>{'REPAIRED' if route['changed'] else 'UNCHANGED'}</td><td>{len(route['original_points'])} → {len(route['resolved_points'])}</td>"
            f"<td>{route['minimum_resolved_clearance_nm']:.3f} nm</td><td>{issues}</td></tr>"
        )
    changed = sum(1 for route in audit["routes"] if route["changed"])
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SCS-2026 Route Safety Audit</title><style>
:root{{--bg:#061117;--panel:#0b1d25;--line:#25434d;--ink:#dfebed;--muted:#8da4aa;--cyan:#45d7dc;--red:#ff6974;--blue:#58a9ff;--amber:#efad55}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 Segoe UI,Arial,sans-serif}}main{{max-width:1400px;margin:auto;padding:55px 34px}}.eyebrow{{color:var(--cyan);font:800 11px Consolas,monospace;letter-spacing:.16em}}h1{{font-size:52px;line-height:1;margin:12px 0}}p{{color:var(--muted)}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);margin:28px 0}}.stats div{{padding:18px;border-right:1px solid var(--line)}}.stats b{{display:block;font-size:27px}}.stats span,small{{display:block;color:var(--muted);font:10px Consolas,monospace;text-transform:uppercase}}.map{{border:1px solid var(--line);background:#071820;padding:10px;overflow:auto}}svg{{width:100%;height:auto}}.land{{fill:#18343a;stroke:#34545b;stroke-width:.45}}.route{{fill:none;stroke-width:2.3}}.route.blue{{stroke:var(--blue)}}.route.red{{stroke:var(--red)}}.original{{fill:none;stroke:var(--amber);stroke-width:1.4;stroke-dasharray:6 4}}.hazard{{fill:rgba(239,173,85,.35);stroke:var(--amber)}}table{{width:100%;border-collapse:collapse;margin-top:28px;background:var(--panel)}}th,td{{padding:13px;border:1px solid var(--line);text-align:left;vertical-align:top}}th{{color:var(--cyan);font:800 10px Consolas,monospace;text-transform:uppercase}}td{{color:var(--muted)}}td b{{color:var(--ink)}}.note{{padding:17px;border-left:3px solid var(--amber);background:rgba(239,173,85,.07);margin:25px 0}}@media(max-width:700px){{h1{{font-size:36px}}.stats{{grid-template-columns:1fr 1fr}}table{{display:block;overflow:auto}}}}@media print{{body{{background:white;color:#15272b}}main{{padding:10px}}.map,table{{background:white}}}}
</style></head><body><main><div class="eyebrow">FAULT LINE / GENERATED PREFLIGHT</div><h1>Navigation route safety audit</h1><p>Offline Natural Earth coastline checks plus conservative South China Sea reef/shoal hazards. Orange dashed lines are authored routes that required repair; solid lines are the routes emitted into C:MO.</p><div class="stats"><div><b>{len(audit['routes'])}</b><span>routes passed</span></div><div><b>{changed}</b><span>routes repaired</span></div><div><b>{len(audit['spawn_checks'])}</b><span>starts passed</span></div><div><b>{audit['settings']['cmo_terrain_sample_nm']} nm</b><span>engine sample interval</span></div></div><div class="map"><svg viewBox="0 0 {width} {height}" role="img" aria-label="South China Sea validated route map">{''.join(land_paths)}{''.join(hazard_marks)}{''.join(route_paths)}</svg></div><div class="note"><b>Second gate:</b> C:MO samples all emitted routes with World_GetElevation during build. Submarine routes additionally require at least {SUBMARINE_MIN_WATER_DEPTH_M} m of water. A failing engine-terrain check aborts before Day1.scen is saved.</div><table><thead><tr><th>Route</th><th>Disposition</th><th>Points</th><th>Minimum clearance</th><th>Original findings</th></tr></thead><tbody>{''.join(rows)}</tbody></table></main></body></html>"""
    (DAY / "route-audit.html").write_text(document, encoding="utf-8")


def resolve_navigation_routes() -> tuple[list[dict[str, object]], dict[str, list[Point]]]:
    if not LAND_DATA.is_file():
        raise SystemExit(f"Navigation coastline data is missing: {LAND_DATA}\nRun: python tools/build_navigation_data.py")
    land = LandIndex(LAND_DATA, HAZARD_DATA)
    audit_routes: list[dict[str, object]] = []
    resolved: dict[str, list[Point]] = {}
    spawn_checks: list[dict[str, object]] = []

    for side, group, lat, lon, members in ship_groups:
        for index, (cid, _dbid) in enumerate(members):
            dy, dx = SHIP_OFFSETS[index]
            position = Point(lat + dy, lon + dx)
            clearance = land.clearance_nm(position)
            if clearance < SURFACE_CLEARANCE_NM:
                raise SystemExit(f"Navigation validation failed: ship start {cid} has {clearance:.2f} nm land clearance")
            spawn_checks.append({"id": cid, "side": side, "group": group, "domain": "surface", "point": position.pair(), "clearance_nm": round(clearance, 3), "status": "pass"})
    for side, cid, _dbid, lat, lon, _course in submarines:
        position = Point(lat, lon)
        clearance = land.clearance_nm(position)
        if clearance < SUBMARINE_CLEARANCE_NM:
            raise SystemExit(f"Navigation validation failed: submarine start {cid} has {clearance:.2f} nm land clearance")
        spawn_checks.append({"id": cid, "side": side, "domain": "submarine", "point": position.pair(), "clearance_nm": round(clearance, 3), "status": "pass"})

    def resolve(route_id: str, side: str, domain: str, raw: list[list[float]], clearance_nm: float) -> None:
        original = points(raw)
        initial_issues = land.validate_route(original, clearance_nm)
        final = land.repair_route(original, clearance_nm) if initial_issues else original
        remaining = land.validate_route(final, clearance_nm)
        if remaining:
            raise SystemExit(f"Navigation validation failed for {route_id}: {remaining[0].message}")
        resolved[route_id] = final
        audit_routes.append({
            "id": route_id,
            "side": side,
            "domain": domain,
            "clearance_nm": clearance_nm,
            "original_points": [point.pair() for point in original],
            "resolved_points": [point.pair() for point in final],
            "changed": final != original,
            "initial_issues": [
                {"kind": issue.kind, "point": issue.point.pair(), "clearance_nm": round(issue.clearance_nm, 3), "message": issue.message}
                for issue in initial_issues
            ],
            "minimum_resolved_clearance_nm": round(land.minimum_route_clearance(final), 3),
            "offline_status": "pass",
        })

    for side, group, start, course in group_courses:
        resolve(group, side, "surface", [list(start), *[list(point) for point in course]], SURFACE_CLEARANCE_NM)
    for side, cid, _dbid, lat, lon, course in submarines:
        resolve(cid, side, "submarine", [[lat, lon], *[list(point) for point in course]], SUBMARINE_CLEARANCE_NM)

    audit = {
        "campaign": "SCS-2026",
        "day": 1,
        "status": "pass",
        "coastline": land.metadata,
        "supplemental_hazards": land.hazards,
        "settings": {
            "surface_clearance_nm": SURFACE_CLEARANCE_NM,
            "submarine_clearance_nm": SUBMARINE_CLEARANCE_NM,
            "submarine_min_water_depth_m": SUBMARINE_MIN_WATER_DEPTH_M,
            "cmo_terrain_sample_nm": CMO_TERRAIN_SAMPLE_NM,
        },
        "spawn_checks": spawn_checks,
        "routes": audit_routes,
    }
    write_route_audit(audit)
    return audit_routes, resolved


def lua_course(route: list[Point]) -> str:
    return ",".join(f"{{latitude={point.lat:.6f},longitude={point.lon:.6f}}}" for point in route)


def terrain_validation_lua(routes: list[dict[str, object]]) -> list[str]:
    lines = [
        "local function navDistanceNm(a,b) local r=math.pi/180; local dlat=(b.latitude-a.latitude)*r; local dlon=(b.longitude-a.longitude)*r; local la=a.latitude*r; local lb=b.latitude*r; local h=math.sin(dlat/2)^2+math.cos(la)*math.cos(lb)*math.sin(dlon/2)^2; return 3440.065*2*math.asin(math.sqrt(h)) end",
        "local function navPoint(a,b,distance,bearing,t) if t<=0 then return a end; if t>=1 then return b end; local q=World_GetPointFromBearing({latitude=a.latitude,longitude=a.longitude,distance=distance*t,bearing=bearing}); return {latitude=q.latitude or q.Latitude,longitude=q.longitude or q.Longitude} end",
        "local navFailures=0",
        f"local function validateTerrainRoute(label,pts,minDepth) local checked=0; for i=1,#pts-1 do local a=pts[i]; local b=pts[i+1]; local distance=navDistanceNm(a,b); local bearing=Tool_Bearing(a,b); local steps=math.max(1,math.ceil(distance/{CMO_TERRAIN_SAMPLE_NM})); for n=0,steps do local p=navPoint(a,b,distance,bearing,n/steps); local e=World_GetElevation(p); if type(e)~='number' then print('DCNAV|FAIL|'..label..'|lookup|'..p.latitude..'|'..p.longitude); return false end; if e>=0 then print('DCNAV|FAIL|'..label..'|land|'..p.latitude..'|'..p.longitude..'|'..e); return false end; if minDepth and -e<minDepth then print('DCNAV|FAIL|'..label..'|shallow|'..p.latitude..'|'..p.longitude..'|'..(-e)); return false end; checked=checked+1 end end; print('DCNAV|PASS|'..label..'|samples='..checked); return true end",
    ]
    for route in routes:
        resolved_points = points(route["resolved_points"])
        depth = str(SUBMARINE_MIN_WATER_DEPTH_M) if route["domain"] == "submarine" else "nil"
        lines.append(f"if not validateTerrainRoute({lua_string(str(route['id']))},{{{lua_course(resolved_points)}}},{depth}) then navFailures=navFailures+1 end")
    lines.append(f"if navFailures>0 then print('DCNAV|SUMMARY|routes={len(routes)}|failures='..navFailures); error('navigation preflight failed') end")
    lines.append(f"print('DCNAV|COMPLETE|routes={len(routes)}|failures=0')")
    return lines


def generate() -> None:
    DAY.mkdir(parents=True, exist_ok=True)
    EXPORT.mkdir(parents=True, exist_ok=True)
    navigation_routes, resolved_routes = resolve_navigation_routes()
    manifest: list[dict[str, object]] = []
    lines = [
        "-- Generated by tools/generate_day1.py; do not hand-edit.",
        "Tool_EmulateNoConsole(true)",
        "local function must(v, label) if v == nil or v == false then error(label .. ': ' .. tostring(_errmsg_)) end return v end",
        "if ScenEdit_GetKeyValue('dc.navigation.preflight') ~= 'true' then error('navigation preflight missing; run preflight.lua first') end",
        "SetScenarioTitle('Fault Line - South China Sea Day 1')",
        "ScenEdit_SetTime({dateformat='YYYYMMDD', date='2026.08.15', time='00:00:00', StartDate='2026.08.15', StartTime='00:00:00', Duration='30:00:00'})",
        "ScenEdit_SetWeather(28, 3, 0.35, 3)",
        "must(ScenEdit_AddSide({side='BLUE'}), 'add BLUE')",
        "must(ScenEdit_AddSide({side='RED'}), 'add RED')",
        "ScenEdit_SetSidePosture('BLUE','RED','H')",
        "ScenEdit_SetSidePosture('RED','BLUE','H')",
        "ScenEdit_SetSideOptions({side='BLUE', awareness='normal', proficiency='Regular', switchto=true})",
        "ScenEdit_SetSideOptions({side='RED', awareness='normal', proficiency='Regular', computerControlledOnly=true})",
        "ScenEdit_SetKeyValue('dc.campaign','SCS-2026')",
        "ScenEdit_SetKeyValue('dc.day','001')",
        "ScenEdit_SetKeyValue('dc.mainland_strikes','false')",
        "ScenEdit_SetKeyValue('dc.guam_strikes','false')",
        "local U = {}",
        "local function add(cid, spec)",
        "  local u = must(ScenEdit_AddUnit(spec), 'add '..cid)",
        "  U[cid] = u.guid",
        "  ScenEdit_SetKeyValue('dc.unit.'..u.guid, cid)",
        "  return u",
        "end",
    ]
    for side, filename in templates:
        lines.append(f"must(ScenEdit_ImportInst({lua_string(side)}, {lua_string(filename)}) > 0, 'import {filename}')")

    def emit_air(pkg: tuple) -> None:
        side, prefix, dbid, base, assigned, ready, loadouts = pkg
        for i in range(1, assigned + 1):
            cid = f"{prefix}-{i:02d}"
            loadout = loadouts[(i - 1) % len(loadouts)] if i <= ready else 4
            pguid = guid(cid)
            lines.append(
                f"add({lua_string(cid)},{{side={lua_string(side)},type='Air',unitname={lua_string(cid)},"
                f"dbid={dbid},loadoutid={loadout},base={lua_string(base)},guid={lua_string(pguid)},proficiency='Regular'}})"
            )
            manifest.append({"campaign_id": cid, "side": side, "kind": "aircraft", "dbid": dbid,
                             "loadout_id": loadout, "base": base, "planned_guid": pguid})

    for pkg in air_packages:
        emit_air(pkg)

    for side, group, lat, lon, members in ship_groups:
        for index, (cid, dbid) in enumerate(members):
            dy, dx = SHIP_OFFSETS[index]
            pguid = guid(cid)
            lines.append(
                f"add({lua_string(cid)},{{side={lua_string(side)},type='Ship',unitname={lua_string(cid)},"
                f"dbid={dbid},latitude={lat+dy:.4f},longitude={lon+dx:.4f},heading=225,speed=15,"
                f"group={lua_string(group)},guid={lua_string(pguid)},proficiency='Regular'}})"
            )
            manifest.append({"campaign_id": cid, "side": side, "kind": "ship", "dbid": dbid,
                             "group": group, "planned_guid": pguid, "start": [round(lat + dy, 4), round(lon + dx, 4)]})

    for side, group, _start, _course in group_courses:
        resolved = resolved_routes[group]
        course_lua = lua_course(resolved[1:])
        lines.append(
            f"local g=must(ScenEdit_GetUnit({{side={lua_string(side)},unitname={lua_string(group)}}}),"
            f"'get group {group}'); g.course={{{course_lua}}}"
        )

    for side, cid, dbid, lat, lon, course in submarines:
        pguid = guid(cid)
        resolved = resolved_routes[cid]
        resolved_course = resolved[1:]
        course_lua = lua_course(resolved_course)
        lines.append(
            f"local su=add({lua_string(cid)},{{side={lua_string(side)},type='Submarine',unitname={lua_string(cid)},"
            f"dbid={dbid},latitude={lat},longitude={lon},heading=210,speed=8,guid={lua_string(pguid)},"
            f"proficiency='Regular'}}); su.course={{{course_lua}}}; su.manualAltitude=-150"
        )
        manifest.append({"campaign_id": cid, "side": side, "kind": "submarine", "dbid": dbid,
                         "planned_guid": pguid, "start": [lat, lon], "course": [point.pair() for point in resolved_course],
                         "planned_depth_m": -150, "minimum_water_depth_m": SUBMARINE_MIN_WATER_DEPTH_M})

    for pkg in embarked_packages:
        emit_air(pkg)

    lines.extend(mission_lua(mission_specs))
    final_save = (DAY / "day-001-final.save").as_posix()
    build_save = (DAY / "Day1.scen").as_posix()
    finalizer = finalizer_lua(final_save)
    lines.extend([
        "ScenEdit_AddSpecialAction({side='BLUE',ActionNameOrID='Finalize Game-Day 1',"
        "description='Pause at the 24-hour boundary, then execute this once to save and export campaign state.',"
        f"IsActive=true,IsRepeatable=false,ScriptText={lua_string(finalizer)}}})",
        "ScenEdit_SetKeyValue('dc.build.complete','true')",
        f"print('DCBUILD|COMPLETE|tracked={len(manifest)}')",
        f"Command_SaveScen({lua_string(build_save)})",
        "ScenEdit_SpecialMessage('BLUE','Day 1 build complete. Inspect missions and save once through Editor > Save As Scenario before play.')",
    ])
    (DAY / "build.lua").write_text("\n".join(lines) + "\n", encoding="utf-8")
    preflight_lines = [
        "-- Generated by tools/generate_day1.py; do not hand-edit.",
        "Tool_EmulateNoConsole(true)",
        "local function must(v, label) if v == nil or v == false then error(label .. ': ' .. tostring(_errmsg_)) end return v end",
        "must(Tool_BuildBlankScenario('DB3K_515.db3'), 'blank scenario')",
        *terrain_validation_lua(navigation_routes),
        "ScenEdit_SetKeyValue('dc.navigation.preflight','true')",
        "print('DCPREFLIGHT|COMPLETE|routes=16')",
    ]
    (DAY / "preflight.lua").write_text("\n".join(preflight_lines) + "\n", encoding="utf-8")
    (DAY / "manifest.json").write_text(json.dumps({"campaign": "SCS-2026", "day": 1, "database": "DB3K_515.db3",
                                                   "units": manifest}, indent=2) + "\n", encoding="utf-8")
    input_data = {
        "campaign": "SCS-2026", "day": 1, "title": "Fault Line - South China Sea Day 1",
        "start": "2026-08-15T00:00:00Z", "operational_pause": "2026-08-16T00:00:00Z",
        "database": "DB3K_515.db3", "player_side": "BLUE",
        "rules": {"mainland_strikes": False, "guam_strikes": False},
        "templates": [{"side": s, "file": f} for s, f in templates],
        "navigation": {
            "audit": "route-audit.json",
            "audit_report": "route-audit.html",
            "routes": [{"side": route["side"], "name": route["id"], "domain": route["domain"], "points": route["resolved_points"], "changed": route["changed"]} for route in navigation_routes],
        },
        "missions": [{key: value for key, value in mission.items() if key != "units"} for mission in mission_specs],
        "boundaries": boundaries,
        "tracked_unit_count": len(manifest),
    }
    (DAY / "input.json").write_text(json.dumps(input_data, indent=2) + "\n", encoding="utf-8")
    (DAY / "validate.lua").write_text(validation_lua(manifest, navigation_routes), encoding="utf-8")
    (DAY / "RUNME.txt").write_text(
        "CMO Scenario Editor instructions\n\n"
        "1. Review route-audit.html. All routes and starts must pass before continuing.\n"
        "2. Open CMO and enter Scenario Editor mode.\n"
        "3. Open Editor > Lua Script Console.\n"
        "4. Run the C:MO-native terrain/depth preflight:\n"
        "   ScenEdit_RunScript('DynamicCampaign/SCS_Day1/preflight.lua')\n"
        "5. Wait for DCPREFLIGHT|COMPLETE, then run the scenario build:\n"
        "   ScenEdit_RunScript('DynamicCampaign/SCS_Day1/build.lua')\n"
        "6. Wait for the Day 1 build-complete message. A missing preflight aborts the build.\n"
        "7. Run post-build identity and navigation validation:\n"
        "   ScenEdit_RunScript('DynamicCampaign/SCS_Day1/validate.lua')\n"
        f"8. Use Editor > Save As Scenario and save to:\n   {DAY / 'Day1.scen'}\n",
        encoding="utf-8",
    )
    DEPLOY.mkdir(parents=True, exist_ok=True)
    for name in ("preflight.lua", "build.lua", "validate.lua"):
        shutil.copy2(DAY / name, DEPLOY / name)


def mission_lua(specs: list[dict[str, object]]) -> list[str]:
    lines = [
        "local function zone(side,prefix,pts) local z={} for i,p in ipairs(pts) do local n=prefix..'-'..i; "
        "must(ScenEdit_AddReferencePoint({side=side,name=n,latitude=p[1],longitude=p[2]}),'rp '..n); z[#z+1]=n end return z end",
        "local function patrol(side,name,subtype,pts,onstation,active) local m=must(ScenEdit_AddMission(side,name,'Patrol',{type=subtype,zone=zone(side,name,pts)}),'mission '..name); "
        "ScenEdit_SetMission(side,m.guid,{isactive=active,OneThirdRule=true,OnStation=onstation,CheckOPA=true,CheckWWR=true}); return m.guid end",
        "local function support(side,name,pts,onstation) local m=must(ScenEdit_AddMission(side,name,'Support',{zone=zone(side,name,pts)}),'mission '..name); "
        "ScenEdit_SetMission(side,m.guid,{isactive=true,OneThirdRule=true,OnStation=onstation,LoopType=1}); return m.guid end",
        "local function assign(ids,m) for _,id in ipairs(ids) do if U[id] then ScenEdit_AssignUnitToMission(U[id],m) end end end",
    ]
    for index, mission in enumerate(specs, 1):
        coordinates = ",".join("{" + f"{point[0]},{point[1]}" + "}" for point in mission["points"])
        variable = f"mission{index}"
        if mission["kind"] == "Patrol":
            active = "true" if mission.get("active", True) else "false"
            lines.append(
                f"local {variable}=patrol({lua_string(str(mission['side']))},{lua_string(str(mission['name']))},"
                f"{lua_string(str(mission['type']))},{{{coordinates}}},{mission['onstation']},{active})"
            )
        else:
            lines.append(
                f"local {variable}=support({lua_string(str(mission['side']))},{lua_string(str(mission['name']))},"
                f"{{{coordinates}}},{mission['onstation']})"
            )
        unit_ids = ",".join(lua_string(str(unit_id)) for unit_id in mission["units"])
        lines.append(f"assign({{{unit_ids}}},{variable})")
    lines.extend([
        "for _,id in ipairs({'BLU-USN-SSN-0001','BLU-USN-SSN-0002','BLU-USN-SSN-0003','BLU-USN-SSN-0004'}) do ScenEdit_SetEMCON('Unit',U[id],'Radar=Passive;Sonar=Passive') end",
        "for _,id in ipairs({'RED-PLAN-SSN-0001','RED-PLAN-SSN-0002','RED-PLAN-SSK-0001','RED-PLAN-SSK-0002','RED-PLAN-SSK-0003','RED-PLAN-SSBN-0001'}) do ScenEdit_SetEMCON('Unit',U[id],'Radar=Passive;Sonar=Passive') end",
        "ScenEdit_SetEMCON('Group','TG B-1 George Washington CSG','Radar=Passive;Sonar=Passive;OECM=Passive')",
        "ScenEdit_SetEMCON('Group','TG R-1 Shandong CSG','Radar=Passive;Sonar=Passive;OECM=Passive')",
    ])
    return lines


def finalizer_lua(final_save: str) -> str:
    return f"""Tool_EmulateNoConsole(true)
if ScenEdit_GetKeyValue('dc.day001.finalized') == 'true' then ScenEdit_MsgBox('Day 1 was already finalized.',0); return end
ScenEdit_SetKeyValue('dc.day001.finalized','true')
local function report(sideName)
  local s=VP_GetSide({{side=sideName}})
  print('DCREPORT|SIDE|'..sideName)
  for _,v in ipairs(s.losses or {{}}) do print('DCREPORT|LOSS|'..sideName..'|'..tostring(v.type)..'|'..tostring(v.dbid)..'|'..tostring(v.number)..'|'..tostring(v.name)) end
  for _,v in ipairs(s.expenditures or {{}}) do print('DCREPORT|EXP|'..sideName..'|'..tostring(v.type)..'|'..tostring(v.dbid)..'|'..tostring(v.number)..'|'..tostring(v.name)) end
  local ids={{}}
  for _,v in ipairs(s.units or {{}}) do
    local u=ScenEdit_GetUnit({{guid=v.guid}})
    if u then
      ids[#ids+1]=u.guid
      local d=u.damage or {{}}
      print('DCUNIT|'..sideName..'|'..tostring(u.guid)..'|'..tostring(u.name)..'|'..tostring(u.dbid)..'|'..tostring(u.latitude)..'|'..tostring(u.longitude)..'|'..tostring(d.DP_PERCENT_NOW or d.DP_PERCENT or 0)..'|'..tostring(u.fuelstate)..'|'..tostring(u.weaponstate))
    end
  end
  ScenEdit_ExportInst(sideName,ids,{{filename='DynamicCampaign/SCS/day001_'..string.lower(sideName)..'_final.inst',name='SCS Day 1 '..sideName..' final'}})
end
report('BLUE')
report('RED')
Command_SaveScen({lua_string(final_save)})
print('DCREPORT|FINALIZED|001|'..tostring(ScenEdit_CurrentTime()))
ScenEdit_MsgBox('Day 1 final save and exports were created. You may now return to the campaign workspace.',0)"""


def validation_lua(manifest: list[dict[str, object]], routes: list[dict[str, object]]) -> str:
    expected = ",".join(
        "{" + f"id={lua_string(str(row['campaign_id']))},side={lua_string(str(row['side']))},guid={lua_string(str(row['planned_guid']))},dbid={row['dbid']}" + "}"
        for row in manifest
    )
    route_specs = ",".join(
        "{" + f"name={lua_string(str(route['id']))},side={lua_string(str(route['side']))},expected={len(route['resolved_points']) - 1},minDepth={'200' if route['domain'] == 'submarine' else 'nil'}" + "}"
        for route in routes
    )
    return f"""Tool_EmulateNoConsole(true)
local expected={{{expected}}}
local errors=0
for _,row in ipairs(expected) do
  local u=ScenEdit_GetUnit({{side=row.side,unitname=row.id}})
  if not u then errors=errors+1 print('DCVALIDATE|MISSING|'..row.id)
  else
    if tostring(u.guid)~=row.guid then errors=errors+1 print('DCVALIDATE|GUID|'..row.id..'|expected='..row.guid..'|actual='..tostring(u.guid)) end
    if tonumber(u.dbid)~=tonumber(row.dbid) then errors=errors+1 print('DCVALIDATE|DBID|'..row.id..'|expected='..row.dbid..'|actual='..tostring(u.dbid)) end
  end
end
local function navDistanceNm(a,b) local r=math.pi/180; local dlat=(b.latitude-a.latitude)*r; local dlon=(b.longitude-a.longitude)*r; local la=a.latitude*r; local lb=b.latitude*r; local h=math.sin(dlat/2)^2+math.cos(la)*math.cos(lb)*math.sin(dlon/2)^2; return 3440.065*2*math.asin(math.sqrt(h)) end
local function navPoint(a,b,distance,bearing,t) if t<=0 then return a end; if t>=1 then return b end; local q=World_GetPointFromBearing({{latitude=a.latitude,longitude=a.longitude,distance=distance*t,bearing=bearing}}); return {{latitude=q.latitude or q.Latitude,longitude=q.longitude or q.Longitude}} end
local function validateRoute(spec)
  local u=ScenEdit_GetUnit({{side=spec.side,unitname=spec.name}})
  if not u then print('DCVALIDATE|NAV-MISSING|'..spec.name); return false end
  local pts={{{{latitude=u.latitude,longitude=u.longitude}}}}
  for _,wp in ipairs(u.course or {{}}) do pts[#pts+1]={{latitude=wp.latitude,longitude=wp.longitude}} end
  if #pts-1<spec.expected then print('DCVALIDATE|NAV-COURSE|'..spec.name..'|expected='..spec.expected..'|actual='..(#pts-1)); return false end
  for i=1,#pts-1 do local a=pts[i]; local b=pts[i+1]; local distance=navDistanceNm(a,b); local bearing=Tool_Bearing(a,b); local steps=math.max(1,math.ceil(distance/{CMO_TERRAIN_SAMPLE_NM})); for n=0,steps do local p=navPoint(a,b,distance,bearing,n/steps); local e=World_GetElevation(p); if type(e)~='number' or e>=0 or (spec.minDepth and -e<spec.minDepth) then print('DCVALIDATE|NAV-TERRAIN|'..spec.name..'|'..p.latitude..'|'..p.longitude..'|'..tostring(e)); return false end end end
  print('DCVALIDATE|NAV-PASS|'..spec.name); return true
end
local routeSpecs={{{route_specs}}}
for _,spec in ipairs(routeSpecs) do if not validateRoute(spec) then errors=errors+1 end end
print('DCVALIDATE|SUMMARY|expected={len(manifest)}|routes={len(routes)}|errors='..tostring(errors))
if errors==0 then ScenEdit_MsgBox('Day 1 validation passed: {len(manifest)} tracked elements and {len(routes)} navigation routes verified.',0) else ScenEdit_MsgBox('Day 1 validation failed. Errors: '..errors..'. Review Lua history.',0) end
"""


if __name__ == "__main__":
    generate()
