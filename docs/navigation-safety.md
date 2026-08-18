# Navigation safety

The Day 1 generator now treats navigation safety as a build gate rather than a
visual-review convention. The implementation adapts the layered approach used by
the Global Conflict: Blue Horizon mission-map validator.

## Validation layers

### Offline preflight

`tools/navigation.py` validates all 27 individual ship starts, ten submarine
starts, six surface-group routes, and ten submarine routes before `build.lua` is
written.

The offline layer uses:

- a clipped copy of the public-domain Natural Earth 1:10m land and minor-island
  polygons in `tools/data/scs-land.geojson`;
- conservative supplemental hazard buffers for selected South China Sea reefs,
  shoals, and artificial-island features in `tools/data/scs-hazards.json`;
- exact segment/coast intersection tests;
- great-circle densification plus sampled distance-to-land clearance tests at
  0.25 nm intervals;
- 3 nm minimum clearance for surface groups;
- 2 nm minimum horizontal clearance for submarines.

Invalid intermediate waypoints are moved to the nearest safe water. Unsafe legs
receive one or more detour waypoints. Every repaired route is simplified where
possible and then passed through the complete validator again. Generation stops
if a start is unsafe, a destination cannot be relocated, a detour cannot be
found, or any repaired leg remains invalid.

The result is written to both:

- `days/day-001/route-audit.json`, for machines and regression checks;
- `days/day-001/route-audit.html`, for human map/table review.

### C:MO terrain corroboration

Natural Earth is not the simulation's terrain authority. The generated
`preflight.lua` therefore creates a fresh blank scenario and samples every
emitted route at 0.5 nm intervals with CMO's `World_GetElevation()`. Sample points
are advanced along the great-circle leg with `Tool_Bearing()` and
`World_GetPointFromBearing()` rather than linearly interpolating latitude and
longitude.

- Surface routes fail when any sample returns land elevation (`>= 0 m`).
- Submarine routes fail on land or water shallower than 200 m.
- A terrain lookup failure is fatal.
- Successful checks print `DCNAV|PASS|...`,
  `DCNAV|COMPLETE|routes=16|failures=0`, and
  `DCPREFLIGHT|COMPLETE|routes=16` to Lua history.

The preflight sets a scenario key only after every route passes. The separate
`build.lua` invocation fails immediately if that key is absent. This split is
required by the recreational Lua console's execution budget and keeps the
engine safety gate fail-closed.

This makes the installed C:MO terrain model the final generation-time authority.

### Post-build validation

`validate.lua` now checks stable GUID and DBID as well as unit presence. It also
retrieves each actual group/submarine course from C:MO, verifies the expected
number of waypoints, and reruns the engine terrain/depth sampling against the
actual assigned course.

## Data regeneration

The checked-in theater crop makes normal generation offline and deterministic.
To rebuild it directly from Natural Earth:

```powershell
python tools/build_navigation_data.py
```

The builder can also consume an existing combined GeoJSON file:

```powershell
python tools/build_navigation_data.py --source C:\path\to\global-land.geojson
```

## Tests

```powershell
python -m unittest discover -s tests -v
```

Tests cover point-on-land detection, exact route intersections, multi-waypoint
repair, invalid-waypoint relocation, supplemental Scarborough Shoal detection,
and regression checks for the three Day 1 routes that currently require repair.

## Guarantee and limits

The build guarantees that every generated initial start/course passes the
offline data and, once run inside C:MO, the engine's sampled terrain/depth test.
It does not control routes later changed by a player, mission AI, Lua events, or
other runtime behavior. Natural Earth is not harbor-chart resolution; the
supplemental hazards and engine corroboration are therefore essential rather
than optional duplicates.
