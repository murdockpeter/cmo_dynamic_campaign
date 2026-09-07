# CMO Dynamic Campaign — Master Coding TODO

Status: Active master checklist  
Created: 2026-09-07  
Last updated: 2026-09-07

This checklist consolidates and expands:

- [CODING_PLAN_TODO.md](CODING_PLAN_TODO.md), the near-term working plan; and
- [CMO_DYNAMIC_CAMPAIGN_MODULAR_THEORY_CODING_PLAN.md](CMO_DYNAMIC_CAMPAIGN_MODULAR_THEORY_CODING_PLAN.md), the long-term modular-theory architecture.

Use this document as the primary progress checklist. The earlier documents remain
useful as design rationale and historical context.

## Status conventions

- `[ ]` Not started
- `[~]` In progress or waiting on an external step
- `[x]` Complete and verified
- `[!]` Blocked or requires a decision

A phase is complete only when its exit gate is satisfied. Completing individual
implementation tasks is not sufficient if the resulting workflow has not been
verified end to end.

## Architectural decisions to preserve

- [x] Give every persistent element a stable campaign ID independent of CMO GUIDs.
- [x] Pin every DBID to an identified CMO database revision.
- [x] Treat the CMO final save as primary evidence of what happened during a game-day.
- [x] Keep administrative changes explicit, attributed, and human-approved.
- [x] Preserve navigation safety checks in both Python and CMO.
- [x] Defer the general modular-theory SDK until the persistent campaign loop works.
- [ ] Keep raw evidence, observed outcomes, accepted campaign state, and planned
      next-day state as distinct concepts and artifacts.
- [ ] Keep theory modules from directly mutating canonical campaign state or CMO.

---

## Phase 0 — Finish and preserve Day 1

Goal: obtain a complete, independently verifiable Day 1 evidence package.

### Existing groundwork

- [x] Generate the Day 1 scenario package.
- [x] Validate 336 tracked mobile elements and 16 navigation routes in CMO.
- [x] Record the 2026-09-07 validation receipt.
- [x] Make the finalization marker retry-safe: set it only after the protected
      finalization block succeeds and allow the special action to be retried.

### Complete the game-day

- [~] Play Day 1 to the agreed 24-hour boundary.
- [ ] Pause at the boundary and invoke **Finalize Game-Day 1**.
- [ ] Confirm that `day-001-final.save` was created.
- [ ] Confirm that BLUE and RED `.inst` exports were created.
- [ ] Confirm that the Lua history contains one identifiable completed finalization.
- [ ] Preserve the original final save before performing any transition or
      experimental extraction operation.
- [ ] Copy the relevant Lua history and exports into `days/day-001/`.

### Create an external artifact receipt

- [ ] Create `days/day-001/artifact-receipt.json`.
- [ ] Record campaign ID, day, finalization run ID, and finalization time.
- [ ] Record every artifact's relative path, byte size, and SHA-256 hash.
- [ ] Record the CMO build and database revision.
- [ ] Record the generator Git commit and hashes of `input.json`, `manifest.json`,
      generated Lua, and the starting scenario.
- [ ] Verify that all expected files exist and are readable before declaring the
      finalization complete.
- [ ] Retain failed or partial finalization attempts under unique run identifiers.

### Resolve Day 1 loose ends

- [ ] Investigate rejected underwater facility placements from the Woody Island
      and Fiery Cross `.inst` imports.
- [ ] Either fix those imports or record an explicit, reviewed acceptance of the
      resulting template composition.
- [ ] Move, archive, or unmistakably relabel `Day1_playthru1.scen` so it cannot be
      confused with the authoritative baseline.
- [ ] Decide whether 6-, 12-, and 18-hour checkpoint saves are required before Day 2.

### Phase 0 exit gate

- [ ] A complete Day 1 evidence package exists, its artifacts have been externally
      verified and hashed, and no file from an earlier playthrough can be mistaken
      for the authoritative final state.

---

## Phase 1 — Define the minimum campaign data contracts

Goal: define the first real vertical slice without designing the entire future
module system speculatively.

The required flow is:

```text
raw evidence
  -> normalized outcome
  -> proposed transactions
  -> approved transactions
  -> ledger revision
  -> next-day transition plan
```

### Source-of-truth model

- [ ] Write an architecture decision record defining these layers:
  - [ ] Raw CMO evidence
  - [ ] Normalized observed outcome
  - [ ] Accepted canonical campaign state
  - [ ] Administrative adjudication
  - [ ] Planned next-day state
- [ ] Specify which artifact is authoritative at each stage.
- [ ] Specify when an artifact becomes immutable.
- [ ] Specify how a correction is represented without silently rewriting history.
- [ ] Decide whether `transactions.jsonl` or the materialized ledger is canonical.
      Recommended: append-only transactions with reproducible ledger snapshots.

### Initial schemas

- [ ] Add an artifact-receipt schema.
- [ ] Add a raw finalizer-record schema.
- [ ] Add a normalized outcome schema.
- [ ] Add a campaign-ledger schema.
- [ ] Add a transaction schema.
- [ ] Add an adjudication-decision schema.
- [ ] Add a transition-plan schema.
- [ ] Require `schema_version`, campaign ID, campaign day, provenance, and run or
      revision identity where applicable.
- [ ] Define schema migration and backward-compatibility expectations.

### Identity and classification

- [ ] Define identity rules for campaign IDs, CMO GUIDs, DBIDs, groups, formations,
      imported facilities, and day-specific locators.
- [ ] Define the allowed outcome classifications:
  - [ ] Surviving
  - [ ] Destroyed
  - [ ] Missing
  - [ ] Unconfirmed
  - [ ] Excluded from the game-day
  - [ ] Imported but untracked
  - [ ] Withdrawn
  - [ ] Captured
- [ ] Define how identity ambiguity is recorded and resolved.
- [ ] Define duplicate-detection and idempotency rules.

### Core invariants

- [ ] Create `docs/core-state-contract.md` from fields actually needed by the
      first reconciliation pipeline.
- [ ] Create `docs/core-invariants.md`.
- [ ] Include the seven modular-plan invariants, revised against actual code.
- [ ] Add invariants preventing silent repair, refueling, magazine refill,
      resurrection, DBID changes, or unexplained disappearance.
- [ ] Define conservation rules for platforms, fuel, weapons, reinforcements,
      withdrawals, and administrative transfers.

### Imported infrastructure decision

- [ ] Inventory members imported by all seven Day 1 templates.
- [ ] Decide which imported members need stable campaign identities.
- [ ] Assign identities to persistently tracked template members, or explicitly
      classify them as untracked infrastructure.
- [ ] Document the reconciliation limitations for anything left untracked.

### Phase 1 exit gate

- [ ] Schemas and invariants cover one complete Day 1-to-Day 2 vertical slice,
      distinguish evidence from decisions, and explicitly address imported
      infrastructure.

---

## Phase 2 — Harden generation, deployment, and finalization

Goal: make scenario tooling reproducible, portable, and independently verifiable.

### Separate generation from deployment

- [ ] Split generation, deployment, and validation into distinct commands.
- [ ] Remove personal absolute paths from generated Lua.
- [ ] Make workspace, CMO installation, export directory, campaign, day, and
      database revision configurable through documented CLI arguments or config.
- [ ] Ensure ordinary generation writes only inside the repository.
- [ ] Require an explicit deployment command before copying files into CMO.
- [ ] Add clear failures for missing or incompatible CMO paths.

### Make inputs authoritative

- [ ] Move Day 1 OOB, identities, loadouts, starts, routes, missions, and templates
      into reviewed declarative source data.
- [ ] Generate Lua and manifests from that source data.
- [ ] Stop treating a Python source table and generated `input.json` as two
      potentially divergent representations of the same plan.
- [ ] Record source hashes in every generated artifact receipt.

### Improve finalizer records

- [ ] Add a schema version and unique finalization run ID.
- [ ] Add unambiguous `BEGIN`, per-section, and `END` records.
- [ ] Add expected and actual record counts.
- [ ] Use unique export paths per finalization attempt.
- [ ] Check CMO API return values as well as caught Lua exceptions.
- [ ] Record campaign ID, day, database, scenario time, scores, and persistent
      escalation/objective flags.
- [ ] Ensure retries cannot overwrite the only copy of prior evidence.

### Verify richer CMO fields experimentally

- [ ] Verify the live Lua representation of unit base or host.
- [ ] Verify group membership.
- [ ] Verify mission assignment and operating state.
- [ ] Verify aircraft loadout and readiness.
- [ ] Verify detailed fuel values.
- [ ] Verify mounts and mounted weapons.
- [ ] Verify magazines and magazine contents.
- [ ] Verify components and component damage.
- [ ] Verify hosted aircraft and boats.
- [ ] Add only verified fields to the finalizer.
- [ ] Document unavailable or unreliable fields instead of guessing them.

### Generator and artifact tests

- [ ] Test deterministic GUID generation.
- [ ] Test manifest completeness and uniqueness.
- [ ] Test that all mission-assigned campaign IDs exist.
- [ ] Test declared bases, groups, DBIDs, and loadout IDs.
- [ ] Test regeneration and fail on unexplained generated-artifact drift.
- [ ] Preserve existing navigation tests and CMO validation gates.

### Phase 2 exit gate

- [ ] A clean checkout can generate identical repository artifacts without writing
      outside the repository, and an explicit deployment step can install them
      using documented configuration.

---

## Phase 3 — Extract and reconcile game-day outcomes

Goal: turn raw CMO evidence into a normalized, reviewable Day 1 outcome without
silently inventing state.

### Evidence ingestion

- [ ] Preserve an unmodified copy of every raw input artifact.
- [ ] Select one finalization run explicitly.
- [ ] Parse only records inside that run's boundaries.
- [ ] Reject incomplete runs unless the operator explicitly invokes a recovery mode.
- [ ] Detect duplicate, malformed, truncated, and out-of-order records.
- [ ] Parse side losses and expenditures.
- [ ] Parse surviving unit state.
- [ ] Parse persistent campaign flags.
- [ ] Parse `.inst` exports experimentally.
- [ ] Document exactly which state survives `.inst` export.

### Identity reconciliation

- [ ] Match every tracked CMO GUID to its stable campaign ID.
- [ ] Detect GUID, name, side, and DBID conflicts.
- [ ] Distinguish expected imported infrastructure from unexpected units.
- [ ] Do not automatically classify an absent unit as destroyed.
- [ ] Reconcile absences against loss records and other evidence.
- [ ] Create explicit ambiguity records for missing or non-unique evidence.
- [ ] Require human disposition for unresolved identities or outcomes.

### Outputs

- [ ] Generate `days/day-001/outcome.json`.
- [ ] Generate machine-readable reconciliation findings.
- [ ] Generate a human-readable `aar.md`.
- [ ] Generate proposed observed-state transactions.
- [ ] Include source-artifact hashes in every derived artifact's provenance.
- [ ] Make extraction reproducible from preserved evidence alone.

### Parser and reconciliation tests

- [ ] Add a complete finalization fixture.
- [ ] Add a partial finalization fixture.
- [ ] Add a duplicate-run fixture.
- [ ] Add malformed and truncated record fixtures.
- [ ] Add an unknown imported-infrastructure fixture.
- [ ] Add an individual-aircraft loss ambiguity fixture.
- [ ] Add missing or purged unit fixtures.
- [ ] Add golden-file tests for normalized outcomes and findings.

### Phase 3 exit gate

- [ ] Re-running extraction from the preserved Day 1 evidence produces an equivalent
      normalized outcome, and every unmatched or ambiguous record is explained or
      explicitly awaiting human adjudication.

---

## Phase 4 — Implement the campaign ledger and adjudication

Goal: produce a reproducible next-state ledger using attributed, approved
transactions.

### Ledger bootstrap

- [ ] Create `campaign/campaign.json`.
- [ ] Create `campaign/transactions.jsonl`.
- [ ] Create the first materialized `campaign/ledger.json`.
- [ ] Bootstrap ledger revision 0 from authoritative Day 1 source data and the
      manifest.
- [ ] Include template-member identities or explicit untracked classifications.
- [ ] Record the database revision and identity namespace.

### Observed-state transactions

- [ ] Convert the normalized Day 1 outcome into proposed observed transactions.
- [ ] Review and resolve all ambiguities.
- [ ] Append accepted observed transactions to produce the post-Day-1 revision.
- [ ] Preserve rejected and superseded proposals with status and rationale.

### Administrative adjudication

- [ ] Define transaction types for repair, replenishment, reinforcement, transfer,
      withdrawal, capture, escalation, and manual correction.
- [ ] Build a human-readable review workflow.
- [ ] Require explicit approval status and approver provenance.
- [ ] Keep administrative decisions separate from observed game results.
- [ ] Generate `days/day-001/adjudication.json`.
- [ ] Apply only approved adjudication transactions.

### Transaction integrity

- [ ] Give every transaction a stable unique ID and idempotency key.
- [ ] Require the expected parent revision or hash.
- [ ] Reject duplicate or stale transaction batches.
- [ ] Validate conservation rules before committing a revision.
- [ ] Make ledger snapshots reproducible from the transaction history.
- [ ] Test that transaction replay produces equivalent normalized ledger state.
- [ ] Represent corrections as new transactions rather than editing history.

### Tracker integration

- [ ] Make the tracker select the current campaign day dynamically.
- [ ] Read current accepted ledger state rather than hard-coded Day 1 planning files.
- [ ] Show observation time, ledger revision, and provenance.
- [ ] Display ambiguous or unconfirmed state distinctly.
- [ ] Remove the unrelated-project Google Maps key fallback.
- [ ] Add data-loading and rendering tests.

### Phase 4 exit gate

- [ ] Day 1 evidence plus approved decisions can recreate the accepted next-day
      ledger from scratch, with every change attributed and no silent state reset.

---

## Phase 5 — Generate and verify the Day 2 transition

Goal: safely apply the approved next-day state to a copy of the Day 1 final save,
then establish the real Day 2 start artifact.

### Transition plan

- [ ] Generate a declarative Day 2 transition plan from approved transactions.
- [ ] Produce a human-readable before/after diff.
- [ ] Associate every proposed CMO mutation with approved transaction IDs.
- [ ] List state that must remain unchanged.
- [ ] Require human approval of the transition plan before Lua generation.

### Source-save verification

- [ ] Externally verify the selected Day 1 final-save SHA-256 before generating the
      transition.
- [ ] Record the expected source artifact receipt and ledger revision.
- [ ] Generate a unique logical transition token.
- [ ] Do not claim Lua verifies an external file hash unless that capability is
      experimentally demonstrated.

### Transition Lua

- [ ] Generate `days/day-002/transition-day-002.lua`.
- [ ] Verify campaign ID, current day, database revision, and transition token.
- [ ] Refuse a stale, mismatched, or repeated transition.
- [ ] Remove or deactivate expired Day 1 missions and events.
- [ ] Apply approved repairs and replenishment explicitly.
- [ ] Add approved reinforcements and scheduled arrivals.
- [ ] Withdraw approved elements.
- [ ] Apply escalation and objective changes explicitly.
- [ ] Create Day 2 missions, events, objectives, and weather.
- [ ] Reset only logs and scores authorized by the campaign rules.
- [ ] Install the Day 2 finalizer and any approved checkpoints.
- [ ] Validate intended changes and prohibited non-changes.
- [ ] Save `day-002-start.save`.

### Safe test sequence

- [ ] Run the transition against a disposable copy of the Day 1 final save.
- [ ] Confirm the transition refuses a second application.
- [ ] Test recovery from a partially failed transition.
- [ ] Compare actual post-transition state with the approved transition plan.
- [ ] Inspect missions, groups, hosted units, loadouts, damage, fuel, and stores.
- [ ] Create and verify the Day 2 start artifact receipt.
- [ ] Perform a short Day 2 smoke run.
- [ ] Begin the authoritative Day 2 only after the smoke test passes.

### Prove that it is a loop

- [ ] Play and finalize Day 2.
- [ ] Extract and reconcile Day 2 through the same pipeline.
- [ ] Generate and validate the Day 3 transition.
- [ ] Confirm no cumulative identity, provenance, or conservation errors.

### Phase 5 exit gate

- [ ] The campaign has completed at least two reproducible, verified day transitions
      without silently resetting either side.

---

## Phase 6 — Engineering and operational reliability

Goal: make the campaign maintainable and recoverable rather than dependent on a
single workstation session.

### Automated tests and CI

- [ ] Add tests for schemas, parser behavior, identity mapping, ledger replay,
      idempotency, conservation rules, and transition generation.
- [ ] Add integration tests using sanitized fixture logs and exports.
- [ ] Add tracker tests beyond JavaScript syntax checks.
- [ ] Add CI for Python tests, JavaScript checks, schema validation, and generated
      artifact drift.
- [ ] Document tests that require a live licensed CMO installation.
- [ ] Keep live-CMO validation separate from portable offline CI.

### CLI and diagnostics

- [ ] Provide one documented command entry point for each workflow stage.
- [ ] Add structured logs and actionable exit codes.
- [ ] Fail closed on missing inputs, hash mismatches, schema errors, and stale
      revisions.
- [ ] Provide dry-run modes for reconciliation, adjudication, and transition.
- [ ] Add concise summaries of files read, files written, and unresolved findings.

### Retention and recovery

- [ ] Define backup and retention policy for ignored `.save` files.
- [ ] Decide which curated `.scen` files belong in Git and document the distinction.
- [ ] Add a recovery runbook for failed finalization.
- [ ] Add a recovery runbook for corrupt or incomplete artifact receipts.
- [ ] Add a recovery runbook for partial adjudication.
- [ ] Add a recovery runbook for failed transitions.
- [ ] Verify restoration from backed-up evidence and transaction history.

### Living project status

- [ ] Add a concise machine-readable project status file.
- [ ] Record current authoritative campaign/day/revision and the next unblocked task.
- [ ] Update this checklist and the status file together after each milestone.
- [ ] Periodically remove or label superseded instructions in older planning docs.

### Phase 6 exit gate

- [ ] A new contributor can reproduce offline artifacts, understand live-CMO steps,
      run automated checks, and recover the campaign from preserved evidence using
      repository documentation.

---

## Phase 7 — Modular theory framework

Entry gate: do not begin the general SDK until Phase 5 has completed two verified
transitions and the outcome/ledger contracts are stable enough to consume.

Goal: add optional, testable analytical theories without contaminating canonical
campaign history.

### Runtime and trust model

- [ ] Write an architecture decision for the module host language and trust model.
- [ ] Prefer Python for the campaign core and theory modules.
- [ ] Keep CMO Lua as a thin capture/application adapter.
- [ ] Define whether third-party modules are trusted code or require process-level
      isolation.
- [ ] Treat declared module permission levels as policy unless technically enforced.
- [ ] Define filesystem, network, runtime, and resource limits for contributed code.

### Event substrate

- [ ] Derive the initial event vocabulary from real campaign outcomes.
- [ ] Add an immutable event-envelope schema.
- [ ] Include event identity, type, campaign time, source, target, payload,
      provenance, schema version, and causal references.
- [ ] Implement validation, recording, querying, and replay.
- [ ] Ensure one consumer cannot mutate the event seen by another.
- [ ] Test deterministic replay.

### Module substrate

- [ ] Add a module-manifest schema and compatibility checks.
- [ ] Add module discovery and explicit enablement.
- [ ] Add namespaced private state and state-version migration hooks.
- [ ] Implement `OFF`, `OBSERVE`, and `ADVISORY` modes.
- [ ] Ensure disabled or failed optional modules cannot invalidate Core state.
- [ ] Add `THEORY.md`, overlap-analysis, and module-PR templates.
- [ ] Build and document `hello_theory`.

### Physical logistics snapshot

- [ ] Treat reliable CMO physical-state capture as a Core adapter capability.
- [ ] Normalize unit, fuel, magazine, mount, loadout, hosted-unit, component,
      damage, and readiness-related state where CMO exposes it reliably.
- [ ] Version the physical snapshot schema.
- [ ] Let an optional detailed-logistics module consume the snapshot later.
- [ ] Do not make campaign reconciliation depend on an optional theory module.

### Herman Entropy experiment

- [ ] Add the Herman Entropy module and `THEORY.md`.
- [ ] State clearly that it is an experimental interpretation, not a canonical
      Herman formula.
- [ ] Begin in `OBSERVE` mode.
- [ ] Track friction, disruption, destruction pressure, recovery, and entropy state.
- [ ] Make mappings and weights configurable.
- [ ] Record the event provenance behind every state change.
- [ ] Define falsifiable expectations before calibration.
- [ ] Run sensitivity and boundary analysis.
- [ ] Check for double-counting and runaway feedback loops.
- [ ] Advance to `ADVISORY` only after observer results are interpretable.

### Effect model

- [ ] Derive effect requirements from actual advisory module outputs.
- [ ] Define effect type, target, domain, units, allowed range, aggregation scope,
      effective interval, expiry, priority, stacking, caps, and exclusivity.
- [ ] Include source module/version, evidence, confidence, causal references,
      reason, and idempotency key.
- [ ] Separate analytical metrics, administrative recommendations, and proposed
      CMO mutations.
- [ ] Implement conflict detection and fully explainable resolution.
- [ ] Add composition tests for overlapping modules.
- [ ] Require explicit approval before an effect becomes a CMO-facing transition.
- [ ] Add `ACTIVE` mode only after advisory calibration and safety tests pass.

### Experimental design

- [ ] Define baseline and treatment configurations before running comparisons.
- [ ] Record module versions, configuration, seeds, inputs, and outputs.
- [ ] Distinguish deterministic module replay from CMO simulation determinism.
- [ ] Use the same recorded event stream for observer/advisory comparisons.
- [ ] Use branched saves for active-treatment comparisons where practical.
- [ ] Document uncontrolled CMO variation and avoid unsupported causal claims.
- [ ] Add Entropy + Logistics as the first serious multi-module integration test.

### Phase 7 exit gate

- [ ] A contributor can add, replay, compare, disable, and remove an optional theory
      module without altering or invalidating canonical campaign history.

---

## Recommended work order from the current state

1. Finish and externally receipt Day 1.
2. Define the minimum evidence/outcome/transaction/ledger contracts.
3. Harden the finalizer and separate generation from deployment.
4. Build extraction and reconciliation from preserved Day 1 evidence.
5. Bootstrap and replay the ledger.
6. Review and approve Day 1 adjudication.
7. Dry-run, validate, and apply the Day 2 transition.
8. Repeat through the Day 3 start to prove the loop.
9. Improve reliability, CI, recovery, and tracker integration.
10. Begin the modular theory framework with events, `hello_theory`, and Entropy in
    observer mode.

## Current next actions

- [~] Operator: complete Day 1 and invoke the finalizer at the agreed boundary.
- [ ] Code: define the artifact receipt and minimum raw-finalizer schemas.
- [ ] Code: add an external finalization verifier and hasher.
- [ ] Research in live CMO: verify the richer unit fields required for reliable
      reconciliation.
- [x] Documentation: replace the stale immediate-next-action text in
      `CODING_PLAN_TODO.md` with a link to this master checklist.
