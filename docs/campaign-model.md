# Campaign persistence model

## Two layers of state

The campaign ledger is authoritative between game-days. A CMO scenario/save is
authoritative for what happened during one game-day.

Each record needs both:

- a stable campaign ID, assigned once and never recycled; and
- a CMO locator containing database filename, platform type, DBID, and the
  runtime/scenario GUID used for that game-day.

This prevents a destroyed unit, regenerated scenario, database update, or changed
CMO GUID from breaking campaign history.

## Hierarchy and accounting grain

`side -> command -> formation -> element`

- A land `formation` may be a brigade, regiment, or battalion. Every battalion is
  an explicit ledger record even if CMO represents it with several subordinate
  mobile facilities or with one aggregate unit.
- An `element` is the smallest persistent item: individual ship/submarine,
  aircraft tail, mobile ground component, fixed facility, or explicitly tracked
  stockpile.
- An airfield is a site formation whose elements include runways, access points,
  shelters/parking, fuel, magazines, sensors, and defenses. Hosted aircraft remain
  separate elements assigned to that site.
- A task group is an operational grouping. Ships keep their individual campaign
  identities when group membership changes.

## Element state at game-day boundary

At minimum:

- disposition: active, reserve, repairing, transiting, destroyed, captured, or
  withdrawn;
- latitude/longitude, base/site, and parent formation;
- CMO DB locator and last game-day GUID;
- damage points/percentage, fire/flood state, and damaged components;
- fuel by type;
- mounted weapons and magazine contents by weapon DBID;
- aircraft loadout, readiness/maintenance state, and accumulated fatigue where
  the API exposes it;
- repair estimate, replenishment eligibility, and administrative notes;
- provenance for every change: game result, scheduled arrival, logistics rule,
  or explicit adjudication.

## Daily artifacts

Every day directory should eventually contain:

- `input.json`: frozen pre-generation ledger slice and decisions;
- `build.lua`: generated, reviewable scenario construction script;
- `manifest.json`: stable campaign ID to generated CMO GUID mapping;
- `day-N.scen`: playable generated scenario;
- `day-N-final.save`: immutable player-returned final state;
- `snapshot/`: side exports and extracted loss/expenditure/unit state;
- `aar.json`: normalized observed outcome;
- `adjudication.json`: repairs, replenishment, arrivals, withdrawals, and manual
  rulings that produce the next ledger revision.

## Reconciliation order

1. Preserve the final save before running any extraction scripts.
2. Snapshot all surviving tracked units and their detailed state.
3. Read side loss and expenditure logs.
4. Match CMO GUIDs to the generated manifest; flag every unmatched record.
5. Classify elements as surviving, destroyed, missing/unconfirmed, captured, or
   excluded from the game-day.
6. Apply observed state to a new ledger revision.
7. Apply logistics/repair rules and explicit human adjudication as separate,
   attributed transactions.
8. Validate conservation rules before generating the next day.

No generator pass should silently repair damage, refill magazines, resurrect an
element, or change a DBID.

