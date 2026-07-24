# Initial CMO reconnaissance

Survey date: 2026-07-22

Installation inspected:
`C:\Program Files (x86)\Steam\steamapps\common\Command - Modern Operations`

## Scenario and campaign formats

- The installation has 315 `.scen` files and 11 `.campaign` files.
- A `.scen` is an XML `ScenContainer`. Its useful metadata is readable, but the
  scenario body is held in a large `Scenario_Compressed` field. We should not
  reverse-engineer or directly write this payload.
- A `.campaign` is ordinary XML listing scenario filenames, scenario GUIDs, and
  pass scores. That built-in linear campaign format is not sufficient by itself
  for the desired operational persistence and adjudication.
- CMO Lua exposes `Tool_BuildBlankScenario`, so the supported construction route
  is: create a blank scenario for a pinned database, populate it through Lua,
  then save it through CMO.

## Databases and IDs

- Installed modern databases currently extend through `DB3K_515.db3`; Cold War
  databases extend through `CWDB_514.db3` in this installation.
- The `.db3` files are readable SQLite databases. `DB3K_515` has 176 tables,
  including platform, component, loadout, mount, sensor, weapon, and relationship
  tables.
- Representative DB3K_515 row counts observed: 7,630 aircraft; 5,050 ships;
  791 submarines; 4,639 facilities; 467 ground-unit records; 4,472 weapons; and
  34,258 loadouts.
- A DBID must always be stored with its database family and revision. A bare
  integer is not a durable campaign identifier.
- The bundled component-number text lists are revision 442 and are useful for
  the Scenario Batch Rebuilder, but the installed SQLite DB and in-game Database
  Viewer are the more current sources for platform selection.
- `ScenEdit_QueryDB` only supports weapon, mount, and sensor lookups. Offline
  cataloging is therefore useful for finding platform and loadout IDs, but all
  selected records should still be verified in CMO's Database Viewer.

## Import/export templates

- `ImportExport` contains 3,887 `.inst` files, organized mostly by country and
  including airfields, fixed installations, missile sites, and ship groups.
- Despite the Lua documentation describing XML, current bundled `.inst` files
  are JSON. They record member DBIDs, CMO GUIDs, coordinates, grouping, hosted
  aircraft/boats, magazines, and deltas from the database baseline.
- Example: `Spain/Air Base Albacete.inst` contains 40 facility members. This is
  exactly the kind of detailed airfield construction we should reuse rather than
  recreating runway access points, taxiways, parking, fuel, and magazines one at
  a time.
- `ScenEdit_ImportInst(side, relative_filename)` imports templates into a side.
  `ScenEdit_ExportInst` can export a group or unit set and includes deltas from
  the vanilla DB entry. This is promising for end-of-day survivor state, but it
  must be validated experimentally for damage, depleted magazines, hosted units,
  and GUID behavior before it becomes the only reconciliation mechanism.

## Lua capabilities relevant to this campaign

The current online guide identifies the following supported building blocks:

- blank scenario creation and scenario saving;
- side, unit, group, reference-point, zone, event, and mission creation;
- aircraft basing and loadout assignment;
- facility/task-group import and export through `.inst` files;
- access to each side's units, losses, expenditures, and missions;
- unit damage, components, fuel, magazines, mounts, loadout, base, course, and
  group/formation data;
- persistent key/value storage, including values passed to a following built-in
  campaign scenario.

Lua's key/value store is useful for small in-scenario flags. It should not replace
the external campaign ledger: the ledger needs auditable history, stable IDs,
manual adjudication, and data that can survive scenario rebuilding.

## Construction strategy

1. Pin the game-day to one installed DB filename.
2. Start from `Tool_BuildBlankScenario(pinned_db)` or a deliberately maintained
   seed scenario.
3. Add sides, postures, date/time, weather, doctrine, and campaign boundary.
4. Import complex static sites and reusable naval groups from reviewed `.inst`
   templates.
5. Add or update uniquely tracked platforms through `ScenEdit_AddUnit`; supply
   stable custom GUIDs where practical, while retaining an external ID mapping.
6. Base aircraft by individual tail/airframe and assign exact loadout IDs.
7. Create support missions (AEW, tanker, CAP, ASW, patrol, ferry, SAR where
   represented) from declarative mission records.
8. Add scheduled snapshot/checkpoint events and save the playable game-day.

## Risks to test before the first large build

- Whether custom GUIDs remain stable across `.inst` export/import cycles.
- Which damage, repair state, fuel, loadout readiness, magazine, and hosted-unit
  fields survive `.inst` export/import.
- Whether a large generated scenario performs acceptably at the desired unit
  density and event cadence.
- How destroyed units are exposed before they are purged, and whether side loss
  logs provide enough identity to map them unambiguously to campaign elements.
- Whether some airfield templates need DB migration or replacement for the chosen
  game date and pinned DB revision.
- Whether ground formations should be represented at vehicle/platoon granularity
  or as fewer aggregate CMO units. Campaign accounting remains battalion-level
  either way, but simulation density must be a conscious choice.

## Sources

- Command Lua API: https://commandlua.github.io/
- Blank scenario: https://commandlua.github.io/assets/Function_Tool_BuildBlankScenario.html
- Add unit: https://commandlua.github.io/assets/Function_ScenEdit_AddUnit.html
- Import INST: https://commandlua.github.io/assets/Function_ScenEdit_ImportInst.html
- Export INST: https://commandlua.github.io/assets/Function_ScenEdit_ExportInst.html
- Save scenario: https://commandlua.github.io/assets/Function_Command_SaveScen.html
- Lua wrappers: https://commandlua.github.io/assets/Wrappers.html

