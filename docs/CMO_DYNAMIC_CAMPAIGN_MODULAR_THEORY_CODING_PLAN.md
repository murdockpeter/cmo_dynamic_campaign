# CMO Dynamic Campaign — Modular Wargaming Theory Framework
## Guided Coding Plan for Codex

Repository: `https://github.com/murdockpeter/cmo_dynamic_campaign`

Status: Proposed architecture and implementation roadmap

Purpose: Refactor the existing CMO Dynamic Campaign framework so that outside contributors can add self-contained modules representing distinct wargaming theories, operational concepts, or analytical lenses without corrupting the baseline persistent campaign state.

---

# 1. Guiding Idea

The project should evolve from a dynamic campaign framework into a **modular operational-wargaming experimentation framework**.

The central design principle is:

> **CMO supplies the battlefield. Core supplies persistence. Modules supply theories of war.**

The repository should support a **Bring Your Own Theory (BYOT)** model in which contributors can PR new theory modules without needing to rewrite the campaign kernel.

Examples of future modules might include:

- Herman Entropy-Based Warfare
- Van Creveld command and uncertainty
- Boyd / OODA tempo
- Information-topology models
- Detailed logistics
- Maintenance and readiness
- Morale and cohesion
- ISR degradation
- Cyber effects
- Mission Command
- Operational reach
- Culmination
- Sea control
- Deterrence
- Political constraints

The baseline framework must remain usable with all optional theory modules disabled.

---

# 2. Intellectual Basis

The CNA / Naval War College paper *Transforming Naval Wargaming: A Framework for Operational-Level Wargaming* argues that operational-level wargames should condense reality through six dimensions:

- Time
- Space
- Forces
- Effects
- Information
- Command

It further organizes these into three linked wargame topologies:

- Operational topology
- Information topology
- Command topology

The paper also develops the ideas of:

- Clausewitzian friction
- Herman's Entropy-Based Warfare
- Van Creveld's command and uncertainty
- Network effects
- Timing and synchronization

This framework is particularly useful for the repository because it suggests that different theories should be represented as different **models layered over the same operational reality**, rather than as mutually entangled rewrites of the simulation.

Important implementation caution:

> The CNA paper discusses the conceptual relationships behind entropy, friction, disruption, lethality/destruction, command, information, and time, but it does **not** provide a complete mathematical implementation for Herman's entropy model.

Therefore any Entropy module in this repo should describe itself as:

> **An experimental implementation inspired by Herman's Entropy-Based Warfare as interpreted through the CNA operational-wargaming framework.**

It should not claim to reproduce an official or canonical Herman formula.

---

# 3. Architectural Law

The most important rule for the entire module system should be:

> **Modules may observe Core State.  
> Modules may own private State.  
> Modules may propose Effects.  
> Modules may NOT directly rewrite Core State.**

This is the main protection against accidental campaign corruption and theory overlap.

A theory module should not directly alter:

- damage
- fuel
- ammunition
- existence
- CMO GUIDs
- position
- platform inventories
- other modules' private state

Instead, it should return structured **effects** to the framework.

---

# 4. Three-Layer Architecture

The repository should conceptually separate three layers:

```text
┌─────────────────────────────────────────────────────┐
│              THEORY / EXPERIMENT MODULES           │
│                                                     │
│ Entropy | Logistics | Command | OODA | Morale     │
│ ISR | Cyber | Networks | Doctrine | etc.           │
└───────────────────────┬─────────────────────────────┘
                        │
                    Effects API
                        │
┌───────────────────────▼─────────────────────────────┐
│                CAMPAIGN FRAMEWORK CORE             │
│                                                     │
│ Identity | State | Events | Time | Transactions    │
│ Validation | Persistence | Effect Resolution       │
└───────────────────────┬─────────────────────────────┘
                        │
                    Adapter API
                        │
┌───────────────────────▼─────────────────────────────┐
│                        CMO                         │
│                                                     │
│ Platforms | Weapons | Sensors | Damage | Movement │
│ Detection | Fuel | Combat | Geography             │
└─────────────────────────────────────────────────────┘
```

Interpretation:

### CMO asks:
> What physically happened?

### Campaign Core asks:
> What persists?

### Theory modules ask:
> What does this mean under the theory being tested?

---

# 5. Core State Must Stay Small and Neutral

The Core should own only facts that are as theory-neutral as practical.

Examples:

```text
Campaign ID
Side
Element type
Formation relationship
CMO GUID
Position
Existence
Host/base
Physical damage
Fuel physically aboard
Weapons physically aboard
Current mission/status
Game time
Physical losses
```

Example:

```json
{
  "id": "BLU-USN-DDG-004",
  "exists": true,
  "position": {
    "lat": 14.233,
    "lon": 118.774
  },
  "damage_pct": 12,
  "fuel": {
    "naval_fuel_kg": 681000
  },
  "stores": {
    "SM6": 19,
    "SM2": 31
  }
}
```

These are campaign observations.

No optional theory module should own them.

---

# 6. Namespaced Module State

Each module should own only its own namespace.

Recommended structure:

```text
state/
  core/
    elements.json
    timeline.json
    events.json
    transactions.json

  modules/
    herman_entropy/
      state.json

    detailed_logistics/
      state.json

    van_creveld_command/
      state.json

    boyd_ooda/
      state.json
```

Example Entropy state:

```json
{
  "module": "herman_entropy",
  "schema_version": "1.0",
  "entities": {
    "BLU-USN-CSG-01": {
      "entropy": 27,
      "friction_pressure": 11,
      "disruption_pressure": 9,
      "destruction_pressure": 7
    }
  }
}
```

Critical rule:

> A module must never edit another module's state file.

---

# 7. Event Bus

Modules should communicate through a common event system instead of importing one another's private code.

Example events:

```text
UNIT_DAMAGED
UNIT_DESTROYED
UNIT_ACTIVITY_RECORDED
MISSION_COMPLETED
MISSION_ABORTED
LOGISTICS_DELIVERY_DELAYED
LOGISTICS_DELIVERY_COMPLETED
C2_DISRUPTED
C2_RESTORED
NETWORK_DEGRADED
NETWORK_RESTORED
BASE_DAMAGED
AIRFIELD_CLOSED
GAME_DAY_STARTED
GAME_DAY_ENDED
```

Example event:

```json
{
  "event": "LOGISTICS_DELIVERY_DELAYED",
  "timestamp": "D004T1830",
  "target": "BLU-USN-CSG-01",
  "severity": 0.62,
  "duration_hours": 9,
  "source": "detailed_logistics"
}
```

The Entropy module may interpret this event.

A Command module may interpret it differently.

Another module may ignore it.

This is preferable to direct module-to-module calls.

---

# 8. Typed Effects API

Modules should not directly mutate CMO or Core.

They should submit effects.

Initial effect vocabulary:

```text
OPERATIONAL_EFFECTIVENESS
ACTION_DELAY
ACTION_DENIAL
DETECTION_CONFIDENCE
INFORMATION_DELAY
COORDINATION
READINESS_PRESSURE
RECOVERY_RATE
RESOURCE_DEMAND
MOVEMENT_DELAY
MISSION_AVAILABILITY
```

Example:

```json
{
  "effect": "OPERATIONAL_EFFECTIVENESS",
  "target": "BLU-USN-CSG-01",
  "operation": "multiply",
  "value": 0.86,
  "source": "herman_entropy",
  "reason": "Entropy state 31"
}
```

The Core Effect Resolver decides how effects combine.

---

# 9. Preventing Module Math Explosion

One of the main risks of a modular theory system is accidental double-counting.

Bad example:

```text
Maintenance = 0.82
Entropy     = 0.76
Command     = 0.81

0.82 × 0.76 × 0.81 = 0.505
```

A force might become arbitrarily crippled because three modules modeled overlapping phenomena.

To prevent this, define effect domains.

Recommended initial domains:

| Domain | Meaning |
|---|---|
| Physical | Does the platform physically exist and work? |
| Resource | Does it have what it needs? |
| Organizational | Can the organization employ it coherently? |
| Information | Does it know what it needs to know? |
| Command | Can intent become coordinated action? |

Example ownership:

```text
CMO damage             -> Physical
Detailed Logistics     -> Resource
Herman Entropy         -> Organizational
Information topology   -> Information
Van Creveld Command    -> Command
```

The resolver should understand which stage of the operational pipeline each effect belongs to.

Do not blindly multiply all modifiers together.

---

# 10. Module Manifest

Every module should include a machine-readable manifest.

Recommended example:

```yaml
id: herman_entropy
name: Herman Entropy-Based Warfare
version: 0.1.0

author: Peter Robbins

theory:
  concept: "Entropy-Based Warfare"
  source: "Herman / CNA Transforming Naval Wargaming"

requires:
  core_api: ">=1.0"
  events:
    - UNIT_ACTIVITY_RECORDED
    - UNIT_DAMAGED
    - UNIT_DESTROYED
    - C2_DISRUPTED
    - LOGISTICS_DELIVERY_DELAYED
    - GAME_DAY_ENDED

provides:
  - entropy_state
  - effectiveness_modifier
  - execution_delay
  - cohesion_state

writes:
  namespace: herman_entropy

effects:
  - OPERATIONAL_EFFECTIVENESS
  - ACTION_DELAY
  - COORDINATION
  - ACTION_DENIAL

conflicts: []
```

The module loader should validate this manifest before activation.

---

# 11. Module Permission Levels

To keep community contributions safe, assign modules permission levels.

## Level 0 — Observer

May read Core State and events.

May generate:

- reports
- analytics
- visualizations
- measures of effectiveness

Cannot affect campaign execution.

---

## Level 1 — Interpretive

May:

- read Core State
- read events
- maintain private module state
- compute theory-specific metrics

Examples:

- Entropy meter
- C2 health
- morale
- operational tempo

Still cannot change gameplay.

---

## Level 2 — Effect Provider

May submit approved Effects through the resolver.

Examples:

- Entropy increases execution delay
- Logistics constrains mission availability
- Command disruption reduces coordination

Cannot directly mutate CMO.

---

## Level 3 — Scenario Adapter

May perform approved CMO mutations.

This should normally be restricted to carefully reviewed framework/adaptor modules.

Examples:

- CMO logistics adapter
- CMO mission adapter
- CMO scenario generator
- CMO reconciliation writer

Theory modules should normally stay at Level 0–2.

---

# 12. Universal Module Modes

Every theory module should support:

```text
OFF
OBSERVE
ADVISORY
ACTIVE
```

## OFF

No execution.

## OBSERVE

Tracks theory state but applies no campaign effects.

## ADVISORY

Shows what effects would have been applied.

## ACTIVE

Submits actual effects through the resolver.

Example config:

```yaml
modules:

  detailed_logistics:
    enabled: true
    mode: active

  herman_entropy:
    enabled: true
    mode: advisory

  van_creveld_command:
    enabled: false

  boyd_ooda:
    enabled: true
    mode: observe
```

This is important for theory testing and A/B comparisons.

---

# 13. Shadow-Mode Experimentation

The framework should make it easy to compare:

```text
Campaign A
Baseline only

Campaign B
+ Entropy

Campaign C
+ Entropy
+ Detailed Logistics

Campaign D
+ Entropy
+ Logistics
+ Command topology
```

Because the Core campaign record remains stable, contributors can compare outputs without contaminating the underlying physical record.

A module in OBSERVE mode might produce:

```text
BOYD MODULE

Predicted BLUE decision cycle:
47 min

Predicted RED decision cycle:
91 min

Predicted BLUE tempo advantage:
+31%

No effects applied.
```

---

# 14. Required THEORY.md

Every theory module should include:

```text
THEORY.md
```

Suggested template:

```markdown
# Theory

## Claim

What is the theory claiming?

## Source

What published theory, paper, book, doctrine, article, or design concept is being represented?

## Model Interpretation

How does this implementation translate the theory into game mechanics?

## Observable Inputs

What campaign observations feed this model?

## Private State

What state does this module own?

## Effects Emitted

What typed effects may the module produce?

## Phenomena Explicitly Not Modeled

What is outside this module's scope?

## Assumptions

What simplifying assumptions were made?

## Calibration

How were values selected?

## Falsifiable Expectations

What observable differences should appear if the theory is useful?
```

The PR should be judged on both code and theoretical transparency.

---

# 15. Required Overlap Documentation

Every module PR should answer:

```text
## Phenomena modeled

## Phenomena explicitly NOT modeled

## Existing modules with potential overlap

## Core State read

## Core State written
NONE

## Effects emitted

## Calibration evidence

## Expected interaction with:
- logistics
- command
- information
- damage
- readiness
```

This is critical to prevent multiple modules from claiming ownership of the same concept.

---

# 16. Core Invariants

Create a document such as:

```text
docs/core-invariants.md
```

Recommended invariants:

1. **Physical truth belongs to CMO.**
2. **Persistent campaign identity belongs to Core.**
3. **Modules cannot alter another module's state.**
4. **Theory modules cannot directly mutate CMO.**
5. **All gameplay influence passes through typed Effects.**
6. **Every state change has provenance.**
7. **Disabling a module must never invalidate Core campaign state.**

The seventh rule is particularly important.

A campaign should be able to disable Entropy on Day 17 without breaking campaign continuity.

The theory disappears.

The war does not.

---

# 17. Provenance

Every meaningful effect should be traceable.

Example:

```text
VFA-115
Operational Capability: 63%
```

Expanded:

```text
PHYSICAL
Aircraft available          10/12

RESOURCE
Fuel                         GREEN
AAM                          AMBER

ORGANIZATIONAL
Entropy                       47
Effect                       -12%

COMMAND
C2 effectiveness             0.91
Effect                        -4%

FINAL RESOLVED
Operational capability       63%
```

Entropy detail:

```text
ENTROPY 47

Friction pressure            18
Disruption pressure          16
Destruction pressure         13

Major contributors:

High sortie tempo            +6
Loss of 2 aircraft           +5
Data-link disruption         +7
Delayed resupply             +3

Recovery:

12 hours low-tempo           -4
Command intervention         -3
```

This avoids black-box adjudication.

---

# 18. Reference Module #1 — Herman Entropy

The first real theory module should be:

```text
modules/theories/herman_entropy/
```

Its purpose is not to replace CMO damage or logistics.

Its purpose is to interpret how much of a formation's physical capability is effectively available for coherent operational action.

## Entropy owns

```text
friction_pressure
disruption_pressure
destruction_pressure
entropy_state
organizational_cohesion
recovery_burden
```

## Entropy reads

```text
activity
combat intensity
damage events
losses
C2 events
information events
logistics disruption
tempo
rest
```

## Entropy may emit

```text
OPERATIONAL_EFFECTIVENESS
ACTION_DELAY
COORDINATION
ACTION_DENIAL
RECOVERY_RATE
```

## Entropy does NOT own

```text
physical damage
fuel
ammunition
maintenance spares
sensor detection physics
weapon probability of kill
aircraft existence
ship existence
```

---

# 19. Entropy Pressure vs Entropy State

Do not treat Entropy as another hit-point track.

Separate:

- current state
- incoming pressure
- recovery

Example:

```text
Inputs this cycle:

Friction pressure       +8
Disruption pressure    +11
Destruction pressure    +5
Command recovery        -7
Rest/reorganization     -4

Resulting entropy state = 32
```

This makes the model more interpretable.

---

# 20. Entropy Convergence

The CNA discussion emphasizes that the combination of friction, disruption, and destruction can produce disproportionately severe effects.

Do not begin with a purely additive system.

Possible initial model:

```text
Entropy Pressure =
    F
  + D
  + L
  + pairwise convergence
  + three-way convergence
```

Example:

```text
F = 7
D = 4
L = 3

Base                  = 14

F + D convergence     = +2
F + L convergence     = +1
D + L convergence     = +1
Three-way convergence = +3

Total pressure        = 21
```

Keep coefficients configurable.

Do not claim these coefficients are canonical Herman values.

---

# 21. Initial Entropy Scale

Start coarse.

| Entropy | State | Interpretation |
|---:|---|---|
| 0–19 | Coherent | Near normal potential |
| 20–39 | Stressed | Noticeable organizational friction |
| 40–59 | Disordered | Degraded synchronization and execution |
| 60–79 | Severely Disrupted | Major capability inaccessible |
| 80–94 | Fragmenting | Only limited coherent action |
| 95–100 | Collapsed | Formation temporarily ineffective |

Avoid initially mapping this directly to huge combat-strength penalties.

Prefer modest operational effects first.

Example:

```text
0–19
No added effect.

20–39
Small execution-delay risk.

40–59
Moderate delay and coordination uncertainty.

60–79
Larger delay plus some complex actions unavailable.

80+
Major command intervention or recovery required.
```

Calibrate through test campaigns.

---

# 22. Entropy Recovery

Entropy should be recoverable.

Possible recovery sources:

```text
rest
reorganization
resupply
restored communications
stable operational tempo
successful command intervention
reserve integration
time without disruption
improved situational understanding
```

This makes entropy a dynamic organizational state rather than permanent attrition.

---

# 23. Command Effort Should Have a Cost

The Clausewitz-derived design concepts in the CNA paper suggest that command can overcome friction, but that doing so should impose costs.

Possible future mechanism:

```text
COMMAND EFFORT:
Reassert control over CSG operations
```

Immediate benefit:

```text
Entropy recovery        -8
```

Potential cost:

```text
Staff capacity          -2
Planning bandwidth      -1
Command fatigue         +3
```

Do not implement this until the basic Entropy module is stable.

This is likely better handled when a future Van Creveld Command module exists.

---

# 24. Reference Module #2 — Detailed Logistics

Detailed Logistics should be the reference **resource-system module**, complementing Entropy.

The Logistics module should track things such as:

```text
fuel
munitions
spares
maintenance resources
transport
in-transit cargo
base throughput
port throughput
airfield throughput
replenishment
stock reservations
days of supply
```

It should emit events and effects rather than directly manipulate theory modules.

Example event:

```text
LOGISTICS_DELIVERY_DELAYED
```

Entropy may interpret that as disruption/friction pressure.

Command may interpret it differently.

This proves that two major modules can interoperate without importing each other's internals.

---

# 25. Recommended Repository Layout

Target layout:

```text
cmo_dynamic_campaign/

  core/
    identity/
    state/
    events/
    timeline/
    effects/
    transactions/
    validation/

  adapters/
    cmo/
      reader/
      writer/
      scenario/
      reconciliation/

  modules/

    resources/
      detailed_logistics/

    theories/
      herman_entropy/
        module.lua
        manifest.yaml
        defaults.yaml
        THEORY.md
        README.md
        tests/

      van_creveld_command/
        ...

      boyd_ooda/
        ...

      information_topology/
        ...

  campaigns/
    <campaign-name>/
      campaign.yaml
      modules.yaml

  schemas/

  tests/

  docs/
    module-authoring.md
    core-invariants.md
    effects-api.md
    event-api.md
    theory-module-standard.md
```

---

# 26. Generic Lua Module Interface

Initial target interface:

```lua
return {

    manifest = {
        id = "example_module",
        version = "0.1.0"
    },

    initialize = function(context)
        -- initialize private state
    end,

    observe = function(event, context)
        -- process event
    end,

    evaluate = function(context)
        -- return proposed effects
        return {}
    end,

    transition = function(context)
        -- return updated private state
        return {}
    end,

    report = function(context)
        -- return human-readable / structured report data
        return {}
    end
}
```

Important:

Theory modules should generally **not** call:

```lua
ScenEdit_SetUnit()
```

or equivalent CMO mutation APIs directly.

CMO writes should pass through framework adapters.

---

# 27. Phase 1 — Build the Module SDK First

Do this before implementing deep Logistics or Entropy mechanics.

## Step 1 — Document Core State Contract

Create:

```text
docs/core-state-contract.md
```

Define:

- required fields
- immutable identity rules
- who owns each field
- what may be written during reconciliation
- serialization format
- schema versioning

Acceptance criteria:

- Core state can be understood without any optional module.
- No theory-specific fields exist in Core state.

---

## Step 2 — Document Core Invariants

Create:

```text
docs/core-invariants.md
```

Add the seven invariants from this plan.

Acceptance criteria:

- Every future module PR can be evaluated against these rules.

---

## Step 3 — Create Event Schema

Create:

```text
schemas/event.schema.json
docs/event-api.md
```

Minimum fields:

```text
event_id
event_type
timestamp
source
target
campaign_day
payload
provenance
```

Acceptance criteria:

- Events can be logged and replayed.
- Event consumers do not need to know emitter internals.

---

## Step 4 — Implement Event Bus

Responsibilities:

```text
publish
subscribe
validate
record
replay
```

Acceptance criteria:

- Two dummy modules can independently subscribe to the same event.
- One module cannot mutate the event seen by another.

---

## Step 5 — Create Effect Schema

Create:

```text
schemas/effect.schema.json
docs/effects-api.md
```

Minimum fields:

```text
effect_id
effect_type
target
domain
operation
value
source_module
reason
duration
priority
provenance
```

Acceptance criteria:

- Effects are validated before entering resolver.

---

## Step 6 — Build Effect Resolver

Responsibilities:

- validate effects
- group by domain
- detect conflicts
- apply composition rules
- generate provenance
- produce final resolved state/effects

Acceptance criteria:

- Resolver rejects unknown effect types.
- Resolver can explain why a final value was produced.
- Resolver detects obvious overlapping effects.

---

## Step 7 — Create Module Manifest Schema

Create:

```text
schemas/module-manifest.schema.json
```

Acceptance criteria:

- Invalid module manifests fail fast.
- Required API version is checked.
- Declared events/effects are validated.
- Permission level is validated.

---

## Step 8 — Implement Module Loader

Responsibilities:

```text
discover modules
validate manifest
load configuration
load private state
enforce mode
enforce permissions
initialize lifecycle
```

Acceptance criteria:

- Disabled modules load no runtime code.
- Missing optional modules do not break campaign state.
- Invalid modules produce readable errors.

---

## Step 9 — Namespaced Module State

Implement:

```text
state/modules/<module-id>/
```

Acceptance criteria:

- Module can read/write only its namespace.
- Core state remains valid if module directory is deleted.
- Module version/schema recorded with state.

---

## Step 10 — Implement Universal Modes

Support:

```text
off
observe
advisory
active
```

Acceptance criteria:

- OBSERVE generates state but no effects.
- ADVISORY generates proposed effects but does not apply them.
- ACTIVE sends effects to resolver.

---

## Step 11 — Add Permission Enforcement

Implement Levels 0–3.

Acceptance criteria:

- Level 0 module cannot submit effects.
- Level 1 module cannot mutate CMO.
- Level 2 can submit typed effects only.
- Level 3 access is explicit and auditable.

---

## Step 12 — Add THEORY.md Template

Create:

```text
docs/templates/THEORY.md
```

Acceptance criteria:

- Every module under `modules/theories/` must contain THEORY.md.

---

## Step 13 — Add Module PR Template

Update repository PR template.

Require:

```text
Theory claim
Source
Inputs
Private state
Effects
Non-goals
Overlap
Calibration
Tests
Expected interactions
```

---

## Step 14 — Build "Hello Theory"

Create the simplest possible example module:

```text
modules/theories/hello_theory/
```

It should:

- subscribe to GAME_DAY_ENDED
- increment a private counter
- produce one harmless advisory metric
- demonstrate all four modes
- demonstrate manifest validation
- demonstrate state persistence

Acceptance criteria:

- A contributor can copy this directory to begin a new module.

---

# 28. Phase 2 — Herman Entropy v0.1

Once the SDK works, implement Entropy first.

## Step 1 — Create Module Skeleton

```text
modules/theories/herman_entropy/
```

Files:

```text
module.lua
manifest.yaml
defaults.yaml
THEORY.md
README.md
tests/
```

---

## Step 2 — Observer-Only First

Start in OBSERVE mode.

Track:

```text
friction_pressure
disruption_pressure
destruction_pressure
entropy_state
```

Do not apply gameplay effects yet.

---

## Step 3 — Map Events to Pressures

Initial experimental mappings:

```text
UNIT_ACTIVITY_RECORDED
  -> friction

MISSION_ABORTED
  -> friction

LOGISTICS_DELIVERY_DELAYED
  -> friction/disruption

C2_DISRUPTED
  -> disruption

NETWORK_DEGRADED
  -> disruption

UNIT_DAMAGED
  -> destruction pressure

UNIT_DESTROYED
  -> destruction pressure

REST_PERIOD_COMPLETED
  -> recovery

C2_RESTORED
  -> recovery
```

Keep mappings configurable.

---

## Step 4 — Add Convergence

Implement:

- F + D interaction
- F + L interaction
- D + L interaction
- F + D + L interaction

Keep all weights in `defaults.yaml`.

---

## Step 5 — Add Recovery

Implement:

```text
time recovery
rest recovery
reorganization recovery
command recovery input
logistics restoration input
network restoration input
```

---

## Step 6 — Reporting

Generate:

```text
Entropy state
Current band
Pressure by source
Top contributing events
Recovery this cycle
Trend
```

---

## Step 7 — Advisory Effects

Switch to ADVISORY mode.

Propose only mild effects:

```text
ACTION_DELAY
COORDINATION
OPERATIONAL_EFFECTIVENESS
```

Do not apply them yet.

---

## Step 8 — Run Calibration Campaigns

Compare:

```text
Baseline
Entropy Observe
Entropy Advisory
```

Questions:

- Does entropy move when expected?
- Does it recover?
- Does high tempo create pressure?
- Does disruption matter?
- Are physical losses double-counted?
- Are effect magnitudes reasonable?
- Are there runaway feedback loops?

---

## Step 9 — Activate Carefully

Only after calibration:

```text
mode: active
```

Start with modest consequences.

Do not immediately make high entropy equivalent to huge combat penalties.

---

# 29. Phase 3 — Detailed Logistics v0.1

After Entropy proves the plug-in architecture, build Logistics as the next major reference module.

Recommended sequence:

```text
LOG-CORE
LOG-SNAPSHOT
LOG-INVENTORY
LOG-MUNITIONS
LOG-FUEL
LOG-LOADOUT
LOG-MAINT
LOG-FACILITY
LOG-TRANSPORT
LOG-UNREP
LOG-CAPACITY
LOG-DEMAND
LOG-PRIORITIES
LOG-INTERDICTION
LOG-REPORT
```

The first concrete implementation should still be:

> **LOG-SNAPSHOT**

Its purpose is to prove exactly what physical logistics state CMO exposes reliably.

Capture as much as practical:

```text
unit
fuel
magazines
magazine weapons
mounts
mount weapons
aircraft loadout
hosted aircraft
components
damage
readiness-related physical state
```

Then normalize the output into a reusable logistics snapshot format.

---

# 30. Integration Test — Entropy + Logistics

This should become the first serious proof of modularity.

Scenario:

1. Logistics convoy is delayed.
2. Logistics emits:
   `LOGISTICS_DELIVERY_DELAYED`
3. Core records the event.
4. Entropy observes the event.
5. Entropy increases friction/disruption pressure.
6. Entropy proposes an `ACTION_DELAY`.
7. Resolver applies or reports the effect.
8. Core physical inventory remains untouched unless Logistics/CMO legitimately changes it.

Acceptance criteria:

- Entropy does not import Logistics internals.
- Logistics does not import Entropy internals.
- Disabling Entropy changes no Logistics state.
- Disabling Logistics does not corrupt Entropy state.
- Core remains valid with either or both disabled.

---

# 31. Testing Strategy

Create several layers of tests.

## Core tests

- State schema validation
- Event immutability
- Effect validation
- Resolver determinism
- Module namespace isolation
- Module mode enforcement
- Permission enforcement

## Module tests

Each module should test:

- input events
- state transitions
- emitted effects
- malformed config
- missing optional data
- recovery behavior
- save/load behavior

## Integration tests

Test pairs:

```text
Entropy + Logistics
Entropy + Command
Logistics + Command
Entropy + Information
```

## Regression tests

A baseline campaign with all modules OFF must behave like the framework did before modularization, except for intentional Core refactor changes.

---

# 32. Determinism

When possible, theory modules should support deterministic replay.

If chance is used:

- use a seeded PRNG
- record the seed
- record the roll
- record the result
- record the module/version

Example:

```json
{
  "module": "herman_entropy",
  "event": "ACTION_DELAY_CHECK",
  "seed": 447190,
  "roll": 0.63,
  "threshold": 0.41,
  "result": "delay_applied"
}
```

This is essential for scientific comparison and debugging.

---

# 33. Configuration Philosophy

Avoid hard-coded values.

Use:

```text
defaults.yaml
```

Example:

```yaml
entropy:
  min: 0
  max: 100

pressure:
  friction_weight: 1.0
  disruption_weight: 1.0
  destruction_weight: 1.0

convergence:
  friction_disruption: 0.15
  friction_destruction: 0.10
  disruption_destruction: 0.15
  all_three: 0.20

recovery:
  passive_per_hour: 0.15
  rest_multiplier: 2.0

bands:
  coherent: [0, 19]
  stressed: [20, 39]
  disordered: [40, 59]
  severely_disrupted: [60, 79]
  fragmenting: [80, 94]
  collapsed: [95, 100]
```

These are placeholders for experimentation, not authoritative theory values.

---

# 34. Versioning

Every module state must include:

```text
module_id
module_version
schema_version
```

The framework should support future migration functions:

```lua
migrate_state(old_version, new_version, state)
```

Do not assume module state files will remain stable forever.

---

# 35. Failure Isolation

A broken optional module should not destroy the campaign.

Recommended behavior:

```text
Module fails
   ↓
Framework records error
   ↓
Module disabled for current processing cycle
   ↓
Core campaign continues
   ↓
User receives explicit warning
```

Never silently swallow failures.

Never corrupt Core state because one module crashed.

---

# 36. Codex Working Style

When Codex work resumes, use this plan incrementally.

Recommended instruction pattern:

> Read the repository first. Do not refactor unrelated code. Implement only the current numbered step. Preserve current campaign behavior. Add tests. Explain every file changed. Do not begin the next step until the current step passes.

For each step:

1. Inspect current code.
2. Identify smallest compatible change.
3. Implement.
4. Add tests.
5. Run tests.
6. Show diff summary.
7. Commit locally if desired.
8. Move to next step only after review.

Avoid asking Codex to implement the entire architecture in one pass.

---

# 37. Suggested First Codex Session

Use this exact scope:

## Goal

Build only the **Core State Contract + Core Invariants documentation**.

Tasks:

```text
1. Inspect the current repo structure.
2. Identify all currently persistent campaign state fields.
3. Identify where CMO-derived physical truth is stored.
4. Identify theory-specific or policy-specific state currently mixed into Core, if any.
5. Draft docs/core-state-contract.md.
6. Draft docs/core-invariants.md.
7. Do not move files yet.
8. Do not change runtime behavior.
9. Propose any necessary future refactors separately.
```

This creates a safe first PR.

---

# 38. Suggested Second Codex Session

## Goal

Create the **Event API** without changing campaign behavior.

Tasks:

```text
1. Add schemas/event.schema.json.
2. Add docs/event-api.md.
3. Add minimal event record helper.
4. Add tests.
5. Do not yet convert every existing workflow to events.
6. Demonstrate one non-invasive event, such as GAME_DAY_ENDED.
```

---

# 39. Suggested Third Codex Session

## Goal

Create the **Module Manifest + Loader**.

Tasks:

```text
1. Add module manifest schema.
2. Add module discovery.
3. Add enabled/disabled configuration.
4. Add private state namespace.
5. Add Hello Theory sample module.
6. Add tests proving disabled modules do not alter Core behavior.
```

---

# 40. Suggested Fourth Codex Session

## Goal

Create **Effect API + Advisory Mode**.

Tasks:

```text
1. Add effect schema.
2. Add effect collector.
3. Add ADVISORY mode.
4. Add provenance reporting.
5. Do not apply effects to CMO yet.
```

---

# 41. Suggested Fifth Codex Session

## Goal

Build **Herman Entropy v0.1 in OBSERVE mode**.

Tasks:

```text
1. Create module skeleton.
2. Add THEORY.md.
3. Subscribe to available campaign events.
4. Track pressure and entropy state.
5. Generate report.
6. Apply no effects.
```

---

# 42. Suggested Sixth Codex Session

## Goal

Start **LOG-SNAPSHOT**.

Tasks:

```text
1. Inspect existing Lua finalizer.
2. Enumerate reliable CMO-accessible logistics state.
3. Create normalized snapshot records.
4. Do not add replenishment mechanics yet.
5. Produce machine-readable output.
6. Add a validation/test workflow.
```

---

# 43. Definition of Success

The refactor is successful when all of the following are true:

- The campaign runs with all optional modules OFF.
- A contributor can copy `hello_theory` and create a new module.
- A module owns only its own private state.
- A module can subscribe to common events.
- A module can operate in OFF / OBSERVE / ADVISORY / ACTIVE modes.
- A theory module cannot directly mutate CMO.
- Effects are typed and traceable.
- Effect composition is centralized.
- Core state remains theory-neutral.
- One module can be removed without invalidating the campaign.
- Entropy and Logistics can coexist without importing one another's internals.
- Every significant module output has provenance.
- The framework can support A/B theory experiments.

---

# 44. End-State Vision

The long-term project should support this concept:

> **CMO Dynamic Campaign is a neutral persistent campaign kernel for operational wargaming. CMO resolves the physical battles. The campaign Core records what persists. Optional modules represent competing theories, models, constraints, and analytical lenses.**

This allows researchers, hobbyists, designers, professional wargamers, and contributors to test questions such as:

- What changes when organizational entropy is modeled?
- What changes when logistics is finite and explicit?
- What changes when command uncertainty is modeled?
- What changes when information networks become fragile?
- What changes when operational tempo is constrained?
- What changes when multiple theories interact?

The repository should make these theories:

```text
pluggable
observable
traceable
configurable
comparable
removable
```

without allowing them to redefine the physical history of the campaign.

That is the core architectural objective.

---

# 45. Immediate Next Action When Codex Tokens Reset

Start with:

> **Phase 1, Step 1: Core State Contract**

Do not begin with Entropy calculations.

Do not begin with deep Logistics code.

First create the stable plug-in substrate that makes both of those modules safe to add.

Then proceed in this order:

```text
Core State Contract
    ↓
Core Invariants
    ↓
Event API
    ↓
Module Manifest
    ↓
Module Loader
    ↓
Namespaced State
    ↓
Modes + Permissions
    ↓
Effect API
    ↓
Effect Resolver
    ↓
Hello Theory
    ↓
Herman Entropy OBSERVE
    ↓
Herman Entropy ADVISORY
    ↓
LOG-SNAPSHOT
    ↓
Detailed Logistics
    ↓
Entropy + Logistics integration
```

This sequence minimizes the risk of building interesting modules on top of an architecture that cannot safely compose them.

---

## Source Note

The theoretical framing for Entropy, friction, disruption/destruction, command, uncertainty, information, synchronization, and the operational/information/command topologies in this plan is derived from:

**Peter P. Perla, Michael C. Markowitz, Christopher A. Weuve, Stephen Downes-Martin, Michael Martin, and Paul V. Vebber, _Transforming Naval Wargaming: A Framework for Operational-Level Wargaming_, CNA / Naval War College, originally published 2004, reprinted 2024.**

The software architecture, module API, event/effect system, permission model, lifecycle, file layout, and implementation sequence proposed here are design recommendations for this repository rather than mechanisms prescribed by the CNA paper.
