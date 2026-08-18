# Dynamic campaign daily workflow

## Core decision

We will create one initial playable `.scen` through CMO's Scenario Editor and
supported Lua API. After Day 1, the normal campaign path is a continuous chain of
CMO `.save` checkpoints:

`Day 1 start.scen -> Day 1 final.save -> Day 2 start.save -> Day 2 final.save`

We will not rebuild the entire theater between ordinary game-days. Continuing
from the final save preserves detailed state that would otherwise be difficult or
impossible to recreate perfectly:

- surviving units, positions, courses, and group formations;
- aircraft basing, loadouts, readiness, and hosted-unit state;
- damage points, fires, flooding, and damaged components;
- fuel, mount weapons, magazine contents, and expenditures;
- contacts, uncertainty areas, emissions knowledge, and side awareness;
- mission, event, message, score, and escalation state.

The external campaign ledger remains authoritative for administrative decisions
between game-days. The CMO save remains authoritative for what physically occurred
during a played game-day.

## Initial scenario construction

Codex will generate a deterministic Day 1 package:

- frozen `input.json` containing the approved OOB and situation;
- `preflight.lua` to create the blank scenario and run C:MO terrain/depth checks;
- `build.lua` to create/import units, airfields, sides, postures, missions, zones,
  events, and initial state;
- `manifest.json` mapping stable campaign IDs to DBIDs and predetermined/generated
  CMO GUIDs;
- runtime event actions embedded by the build script;
- a validation script and expected unit/mission counts.

The generated build will use:

1. `Tool_BuildBlankScenario('DB3K_515.db3')`;
2. reviewed `.inst` airfield templates;
3. `ScenEdit_AddUnit` for individually tracked platforms;
4. exact aircraft loadouts and bases;
5. support, patrol, strike-ready, and logistics missions;
6. scheduled checkpoint and end-of-day events;
7. stable campaign identifiers recorded in the manifest and CMO key store.

Before Lua is emitted, every generated ship/submarine start and complete route is
checked against the offline South China Sea coastline/hazard index. Unsafe legs
are repaired with additional waypoints and revalidated; unresolved errors stop
generation. `route-audit.json` and `route-audit.html` record all original and
resolved courses. During the C:MO build, `World_GetElevation()` samples the
resolved routes against the engine's terrain and bathymetry. Any land hit or
submarine water-depth violation prevents the preflight key from being set, and
the build refuses to start without that key.

The user will open the CMO Scenario Editor and run the generated build script.
CMO itself must perform the final **Save As Scenario** operation because it owns
the compressed scenario payload. Codex will inspect the CMO Lua history/error logs
and generated artifacts after the build.

The initial CMO scenario can have a long overall duration. We will treat each
24-hour boundary as an operational pause rather than relying on the scenario to
terminate permanently after Day 1.

## What runs inside the scenario

Embedded Lua will be deliberately conservative. It may:

- manage escalation flags and scenario objectives;
- activate/deactivate preplanned missions;
- record important event outcomes in persistent key/value fields;
- issue six-hour checkpoint saves if enabled;
- present a clear 24-hour “End Game-Day” notification;
- expose a repeatable **Finalize Game-Day** special action;
- print a structured final report to CMO's `LuaHistory_YYYY-MM-DD.txt`;
- export surviving BLUE and RED unit sets using `ScenEdit_ExportInst`;
- save the final checkpoint to the campaign workspace with `Command_SaveScen`.

Embedded Lua will not automatically:

- spawn unapproved reinforcements;
- repair damage;
- refill fuel or magazines;
- resurrect destroyed units;
- change platform DBIDs;
- escalate attacks against protected geographic areas without a defined trigger.

CMO's persistent key/value store is appropriate for compact flags such as
`mainland_strikes_authorized=false` or `objective_alpha_status=damaged`. It is not
the master campaign database.

## End-of-day package

At the 24-hour boundary the user pauses the simulation and invokes the
**Finalize Game-Day** special action. The finalizer will create or expose:

- `day-001-final.save`, written directly into the workspace;
- side `.inst` survivor exports under a unique campaign/day export path;
- a structured report in the Lua history log containing:
  - scenario time and scores;
  - side losses and expenditures;
  - surviving tracked GUIDs;
  - unit position, base, group, mission, and operating state;
  - damage, fuel, loadout, mount, and magazine summaries;
  - persistent escalation/objective flags;
- optional six-, twelve-, and eighteen-hour checkpoint saves;
- a finalization marker so accidental double-finalization is visible.

We will rely on documented CMO outputs—scenario saves, `.inst` exports, persistent
key/value state, and Lua history logs—rather than assuming unrestricted Lua file
access.

If finalization is forgotten, the final save is still preserved. It can be
reopened and finalized before any transition script is applied.

## Reconciliation between user and Codex

### User

1. Play until the agreed 24-hour boundary.
2. Pause and use **Finalize Game-Day**.
3. Tell Codex that the game-day is complete.
4. Provide operational observations not fully expressed in machine state:
   intent, perceived intelligence, aborted plans, desired posture, and priorities.
5. Review and approve the proposed repairs, replenishment, reinforcements, and
   political/escalation decisions.

Because CMO and the workspace are on the same machine, normal campaign files do
not need to be manually uploaded. Codex can inspect the agreed workspace paths,
CMO export directory, and Lua history logs after the user confirms finalization.

### Codex

1. Preserve/hash the final save and copy the relevant export/log evidence into
   the game-day directory.
2. Match every CMO GUID to the stable campaign manifest.
3. Reconcile survivors, destroyed/missing units, expenditures, damage, fuel,
   stores, aircraft readiness, and geographic disposition.
4. Produce a draft AAR and a transaction-by-transaction next-day proposal.
5. Flag ambiguities rather than silently guessing.
6. Apply only user-approved repair, replacement, replenishment, reinforcement,
   withdrawal, and escalation decisions to a new ledger revision.
7. Generate and validate the next transition script.

## Creating the next game-day

The user loads `day-001-final.save` in the Scenario Editor and runs the generated
`transition-day-002.lua`. The transition script will:

- verify the expected campaign/day ID and source-save fingerprint marker;
- refuse to run twice;
- remove or deactivate expired Day 1 missions/events;
- apply approved repairs and replenishment explicitly;
- add approved reinforcements and scheduled arrivals;
- withdraw units that left the theater;
- create Day 2 missions, events, objectives, and weather;
- reset only the logs/scores that the campaign rules say should reset;
- install the next finalizer/checkpoint events;
- write `day-002-start.save`.

The user then plays the next 24 hours. This repeats for each game-day.

## Stable identity

Every persistent element gets a stable ID such as:

- `BLU-USN-CVN-0001`;
- `BLU-USAF-F35A-0007`;
- `RED-PLAN-SSN-0002`;
- `RED-PLAAF-J16-0019`;
- `BLU-PHL-2CD-BN`;
- `RED-FIERY-HQ9-BN`.

CMO runtime GUIDs and DBIDs are mapped to these IDs. They do not replace them.
Aircraft are tracked by individual tail-equivalent element. Ships and submarines
are individual elements. Land battalions are explicit parent formations whose
batteries/companies/CMO units are child elements.

## Recovery and periodic rebuilds

A fresh reconstruction from the external ledger is a fallback when:

- a save becomes unusable;
- cumulative events or purged wrecks make the scenario unstable;
- a database migration is deliberately approved;
- performance requires a theater cleanup;
- we want to branch an alternate campaign timeline.

Survivor `.inst` exports, the manifest, ledger, transaction history, and immutable
final saves make such a rebuild possible. We should consider a controlled cleanup
rebuild every five to ten game-days only if performance or accumulated state makes
it worthwhile.

## Proposed artifact layout

```text
campaign/
  campaign.json
  ledger.json
  transactions.jsonl
days/
  day-001/
    input.json
    manifest.json
    build.lua
    validate.lua
    day-001-start.scen
    checkpoints/
    day-001-final.save
    exports/
    lua-history.txt
    outcome.json
    aar.md
    adjudication.json
  day-002/
    input.json
    manifest.json
    transition-day-002.lua
    day-002-start.save
    ...
```

Large `.scen` and `.save` files stay local and are ignored by Git. Small manifests,
ledgers, scripts, AARs, and adjudication records are suitable for version control.
