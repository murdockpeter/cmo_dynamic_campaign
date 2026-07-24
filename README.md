# CMO Dynamic Campaign

Local tooling and campaign records for a persistent, day-by-day Command: Modern
Operations campaign.

The intended loop is:

1. Define a campaign situation and order of battle outside CMO.
2. Generate a 24-hour CMO game-day from that state through supported Lua APIs.
3. Play the game-day and retain the final `.save` as the immutable source artifact.
4. Reconcile surviving elements, losses, expenditure, damage, fuel, and stores.
5. Adjudicate repair, replenishment, reinforcement, and movement between days.
6. Generate the next game-day without silently resetting either side.

See [docs/reconnaissance.md](docs/reconnaissance.md) for findings from the local
CMO installation and Lua API, and [docs/campaign-model.md](docs/campaign-model.md)
for the proposed persistence model.

The current fictional South China Sea force proposal is in
[docs/day-1-oob-proposal.md](docs/day-1-oob-proposal.md).

The human/CMO handoff and 24-hour campaign loop are defined in
[docs/daily-workflow.md](docs/daily-workflow.md).

## Database and template catalog

`tools/cmo_catalog.py` reads the installed CMO databases in read-only mode. It
does not alter the game installation.

```powershell
python tools/cmo_catalog.py info
python tools/cmo_catalog.py search "F-15E" --kind aircraft --year 2026
python tools/cmo_catalog.py search "Arleigh Burke" --kind ship
python tools/cmo_catalog.py search "Patriot" --kind facility --year 2026
python tools/cmo_catalog.py templates "Albacete"
```

Use `--db DB3K_515.db3` (or a CWDB file) to pin a database explicitly. Generated
game-days must always record the exact database filename because DBIDs are only
meaningful in the context of that database revision.

## Guardrails

- Treat the installed `DB/*.db3` files as read-only reference data.
- Never edit bundled scenarios or templates in place.
- Keep generated Lua, scenario saves, AAR snapshots, and campaign ledgers here.
- Preserve every end-of-day `.save`; reconciliation should be repeatable.
- Give every tracked element a stable campaign ID independent of CMO's runtime
  GUID. Runtime GUIDs are mappings, not campaign identity.
