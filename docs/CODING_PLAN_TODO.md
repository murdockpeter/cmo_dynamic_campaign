# CMO Dynamic Campaign — TODO Coding Plan (Next Steps)

Status: Active working plan, superseding session-order in
[CMO_DYNAMIC_CAMPAIGN_MODULAR_THEORY_CODING_PLAN.md](CMO_DYNAMIC_CAMPAIGN_MODULAR_THEORY_CODING_PLAN.md)
for what to build *right now*.

## Why this document exists

The modular theory plan describes a full plug-in architecture (Core / Effects
API / theory modules like Herman Entropy and Detailed Logistics). It's sound,
but it's written to be built on top of a working persistent campaign loop —
and that loop doesn't exist yet. Repo inspection (2026-09-07) confirms:

- `days/day-001/` has a validated, navigation-safe `Day1.scen`
  (SHA-256 recorded in `cmo-validation-20260818.txt`), but no
  `day-001-final.save`, no `aar.json`, no `adjudication.json`.
- `Day1_playthru1.scen` (2026-08-15) predates the navigation-safety rebuild
  (2026-08-18) — it's a stale playtest, not the authoritative save chain.
- **Correction (2026-09-07):** the "Finalize Game-Day" special action
  *does* exist — `finalizer_lua()` in `tools/generate_day1.py` embeds it into
  `build.lua`. It was missed on first pass because it's generated Lua inside
  a Python f-string, not a standalone file. It had a real bug, since fixed
  (see Priority 1, item 1 below).
- There is no `campaign/campaign.json`, `campaign/ledger.json`, or
  `campaign/transactions.jsonl` — the persistence layer
  [campaign-model.md](campaign-model.md) specifies is undocumented-but-real
  design, not yet code.
- There is no reconciliation, adjudication, or day-002 transition tooling.
- None of the modular theory plan's Phase 1 SDK (`core/`, `schemas/`,
  `modules/`, event bus, effect resolver) has been started.

**Conclusion:** the modular theory plan's own Step 1 ("inspect current
persistent campaign state") has nothing concrete to inspect yet, because Day 1
has never been played through to a reconciled Day 2. Building the real ledger
first will produce a Core State Contract grounded in actual fields instead of
a speculative one — and it unblocks the campaign this repo exists for.

---

## Priority 1 — Close the Day 1 → Day 2 loop

This is the critical path. Nothing downstream (modular SDK or otherwise)
should start before this works end to end at least once.

- [x] **Finalizer Lua atomicity fix** (done 2026-09-07): the finalizer
      already existed (`finalizer_lua()` in `tools/generate_day1.py`,
      embedded into `build.lua`'s `Finalize Game-Day 1` special action) but
      had a real bug, flagged by a prior session's own audit in
      [code-deep-dive.html](code-deep-dive.html): the `dc.day001.finalized`
      marker was set *before* the export/save ran, and the action was
      `IsRepeatable=false`. A failed export or save still got recorded as
      complete, with no way to retry. Fixed: the export/save now runs inside
      `pcall`, the marker is only set on success, failure prints
      `DCREPORT|ERROR|...` and shows a clear "not marked complete" message,
      and the action is now `IsRepeatable=true` so a failed run can be
      retried safely. Regenerated `build.lua`/`preflight.lua`/`validate.lua`
      and redeployed to the CMO Lua directory.
      - **Side finding**: regenerating also picked up a legitimate,
        deterministic navigation update — `build.lua` had never been
        recommitted since the "Updated land collision detection methods"
        commit (`1500ca2`, 2026-08-18), so the `TG B-3 America ARG` route in
        the committed artifacts predated that fix. The regenerated route
        adds one waypoint and is presumably safer; scope was verified
        limited to that single route (manifest/unit identities unchanged).
        **This means the SHA-256 receipt in `cmo-validation-20260818.txt` is
        now stale** — a fresh build + validate + save pass through CMO's
        Editor is needed before this is trusted as the Day 1 baseline.
      - **Still open** (documented gap, not yet done): the finalizer's
        per-unit report only prints GUID/name/DBID/position/damage/fuel/
        weapon-state. `daily-workflow.md` and this plan call for base,
        group, mission, loadout, and magazine contents too. Adding those
        needs the exact CMO Lua unit-table field names verified against a
        live CMO session (not guessed) before shipping, since a wrong field
        name only fails at runtime inside the Editor.
      - **Still open**: optional 6/12/18-hour checkpoint saves — not
        implemented; `daily-workflow.md` describes these but no code exists
        for them yet.
- [ ] **Rebuild and re-validate `Day1.scen`** through CMO's Editor
      (`preflight.lua` → `build.lua` → `validate.lua`, per `RUNME.txt`) to
      pick up the finalizer fix and the corrected `TG B-3 America ARG`
      route, then record a fresh validation receipt (replacing
      `cmo-validation-20260818.txt`, whose hash is now stale).
- [ ] **Play Day 1 to completion** using the freshly rebuilt `Day1.scen`
      (not the stale `Day1_playthru1.scen`), invoke the finalizer, and
      confirm `day-001-final.save` plus exports/logs land correctly. Also
      confirm the finalizer is safely re-runnable if a first attempt fails
      partway (the fix above).
- [ ] **Extraction tooling** (Python, alongside `tools/generate_day1.py`):
      parse the Lua history log + `.inst` exports into a normalized
      `outcome.json` / `aar.json` per the "Daily artifacts" section of
      [campaign-model.md](campaign-model.md). Match every CMO GUID back to
      `manifest.json` campaign IDs; flag unmatched records instead of
      guessing.
- [ ] **Ledger bootstrap**: create `campaign/campaign.json`,
      `campaign/ledger.json`, `campaign/transactions.jsonl` per the
      "Proposed artifact layout" in [daily-workflow.md](daily-workflow.md).
      Seed the ledger from `days/day-001/input.json` +
      `days/day-001/manifest.json`.
- [ ] **Adjudication workflow**: a script/checklist that turns approved
      repairs, replenishment, reinforcements, withdrawals, and escalation
      decisions into `days/day-001/adjudication.json` transactions applied to
      the ledger. Keep it human-in-the-loop (flag ambiguities, don't
      auto-resolve).
- [ ] **`transition-day-002.lua` generator**: verify campaign/day ID and
      source-save fingerprint, refuse double-run, apply approved changes,
      install next finalizer/checkpoint events, write `day-002-start.save`
      — mirroring the existing `preflight.lua` → `build.lua` → `validate.lua`
      pattern already proven for Day 1.
- [ ] **Play Day 2** to prove the full loop (`Day 1 final.save` →
      `Day 2 start.save` → `Day 2 final.save`) works without silently
      resetting either side.

## Priority 2 — Known loose ends from the Day 1 build

- [ ] Audit the "known non-navigation warning" in
      `days/day-001/cmo-validation-20260818.txt`: rejected underwater
      facility placements when importing the Woody Island / Fiery Cross
      `.inst` templates. Navigation/route validation passed, but fixed-
      facility template composition at those sites is unverified —
      `validate.lua` doesn't cover it. Decide whether this needs a fix or
      just documented acceptance.
- [ ] Decide the fate of `Day1_playthru1.scen` — archive it out of the repo
      (like the pre-navigation backups already moved to a temp dir) once its
      history is no longer needed, so it doesn't get mistaken for the current
      baseline.

## Priority 3 — Formalize Core State Contract (grounded, not speculative)

Only after Priority 1 produces a real ledger with real fields:

- [ ] Write `docs/core-state-contract.md` describing the *actual* fields now
      living in `campaign/ledger.json` / `manifest.json` / `outcome.json` —
      required fields, ownership, schema versioning. This directly satisfies
      Modular Theory Plan §27 Step 1, but based on working code instead of
      the plan's illustrative JSON.
- [ ] Write `docs/core-invariants.md` using the seven invariants from
      Modular Theory Plan §16, checked against what the Priority 1 loop
      actually guarantees (e.g. "no generator pass silently repairs damage"
      is already a stated rule in campaign-model.md — verify the code
      upholds it).

## Priority 4 — Deferred: Modular Theory SDK

Backlog, not scheduled. Revisit once the campaign has run several real
game-days and there's a concrete theory (entropy, logistics) worth testing
against real data. When it's time, resume at Modular Theory Plan §45's
sequence starting from Event API (Core State Contract and Invariants will
already be done via Priority 3 above):

```text
Event API → Module Manifest → Module Loader → Namespaced State →
Modes + Permissions → Effect API → Effect Resolver → Hello Theory →
Herman Entropy (OBSERVE) → Herman Entropy (ADVISORY) →
LOG-SNAPSHOT → Detailed Logistics → Entropy + Logistics integration
```

Do not start this priority while Priority 1 is incomplete — the modular
plan's own §45 explicitly warns against building interesting modules on top
of an architecture (or in this case, a campaign loop) that can't yet safely
compose them.

---

## Immediate next action

Start Priority 1, item 1: implement the Finalize Game-Day Lua in
`days/day-001/build.lua`. Everything else in this document depends on having
a real finalized game-day to reconcile from.
