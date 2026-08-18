# SCS-2026 Common Operational Picture

Desktop Google Maps tracker for the current C:MO Day 1 planning baseline. It
reads `days/day-001/input.json` and `manifest.json` at runtime; campaign data is
not duplicated inside the app.

## Run

```powershell
cd tracker
npm install
npm start
```

The app first checks its own OS-encrypted settings, then the existing ignored
local campaign reports that already hold the demo key. Otherwise choose
**Google Maps key** and enter a key restricted to the Maps JavaScript API and
`http://127.0.0.1:43117/*`.

## Displayed layers

- seven airbase/island force concentrations with individual aircraft drill-down;
- six naval task groups and their planned courses;
- ten individually tracked submarines and patrol courses;
- BLUE and RED CAP, ASW, AEW, and tanker mission geometry;
- mainland escalation restriction overlay;
- force, route, mission, restriction, side, and text filters;
- readiness/loadout, DBID, and stable campaign-ID details.

Positions are the frozen Day 1 starting situation, not live telemetry from a
running C:MO session. Reloading reflects edits to the current manifest/input.
Surface routes, repaired submarine courses, mission geometry, and boundaries are
read from those generated artifacts; the tracker no longer maintains separate
route/mission coordinate constants. The map visualizes the navigation result,
while `days/day-001/route-audit.html` is the authoritative preflight report.
