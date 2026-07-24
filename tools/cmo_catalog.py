"""Read-only catalog for installed CMO databases and INST templates."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path


DEFAULT_CMO_ROOT = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Command - Modern Operations"
)

TABLES = {
    "aircraft": "DataAircraft",
    "ship": "DataShip",
    "submarine": "DataSubmarine",
    "facility": "DataFacility",
    "ground_unit": "DataGroundUnit",
    "weapon": "DataWeapon",
    "loadout": "DataLoadout",
}


def version_key(path: Path) -> tuple[int, str]:
    match = re.search(r"_(\d+)([a-z]?)\.db3$", path.name, re.IGNORECASE)
    return (int(match.group(1)), match.group(2).lower()) if match else (-1, path.name)


def cmo_root(value: str | None) -> Path:
    root = Path(value or os.environ.get("CMO_ROOT", DEFAULT_CMO_ROOT))
    if not (root / "DB").is_dir():
        raise SystemExit(f"CMO DB directory not found below: {root}")
    return root


def choose_db(root: Path, requested: str | None) -> Path:
    if requested:
        path = root / "DB" / requested
        if not path.is_file():
            raise SystemExit(f"Database not found: {path}")
        return path
    candidates = sorted(root.joinpath("DB").glob("DB3K_*.db3"), key=version_key)
    if not candidates:
        raise SystemExit("No DB3K database found")
    return candidates[-1]


def connect_read_only(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)


def command_info(args: argparse.Namespace) -> None:
    root = cmo_root(args.root)
    dbs = list(root.joinpath("DB").glob("*.db3"))
    latest: dict[str, Path] = {}
    for db in dbs:
        family = db.name.split("_")[0].upper()
        if family not in latest or version_key(db) > version_key(latest[family]):
            latest[family] = db
    print(f"CMO root: {root}")
    print(f"Database files: {len(dbs)}")
    for family, db in sorted(latest.items()):
        with connect_read_only(db) as con:
            count = con.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table'"
            ).fetchone()[0]
        print(f"Latest {family}: {db.name} ({count} tables)")
    templates = list(root.joinpath("ImportExport").rglob("*.inst"))
    print(f"INST templates: {len(templates)}")


def command_search(args: argparse.Namespace) -> None:
    root = cmo_root(args.root)
    db = choose_db(root, args.db)
    table = TABLES[args.kind]
    with connect_read_only(db) as con:
        columns = {row[1] for row in con.execute(f"PRAGMA table_info([{table}])")}
    selected = ["ID", "Name"]
    for optional in ("YearCommissioned", "YearDecommissioned", "Deprecated"):
        if optional in columns:
            selected.append(optional)
    conditions = ["Name LIKE ?"]
    values: list[object] = [f"%{args.query}%"]
    if args.year is not None and {"YearCommissioned", "YearDecommissioned"} <= columns:
        conditions.append("YearCommissioned <= ?")
        conditions.append("(YearDecommissioned = 0 OR YearDecommissioned >= ?)")
        values.extend((args.year, args.year))
    sql = (
        f"SELECT {', '.join(selected)} FROM [{table}] "
        f"WHERE {' AND '.join(conditions)} ORDER BY Name, ID LIMIT ?"
    )
    values.append(args.limit)
    with connect_read_only(db) as con:
        rows = con.execute(sql, values).fetchall()
    print(f"Database: {db.name}\nKind: {args.kind}\nMatches: {len(rows)}")
    print(" | ".join(selected))
    for row in rows:
        print(" | ".join(str(value) for value in row))


def template_summary(path: Path, root: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        records = data.get("MemberRecords", [])
        lats = [r.get("Latitude") for r in records if isinstance(r.get("Latitude"), (int, float))]
        lons = [r.get("Longitude") for r in records if isinstance(r.get("Longitude"), (int, float))]
        center = ""
        if lats and lons:
            center = f" | center={sum(lats)/len(lats):.4f},{sum(lons)/len(lons):.4f}"
        return (
            f"{path.relative_to(root / 'ImportExport')} | members={len(records)}"
            f" | db_family_id={data.get('DB_ID')}{center}"
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return f"{path.relative_to(root / 'ImportExport')} | unreadable: {exc}"


def command_templates(args: argparse.Namespace) -> None:
    root = cmo_root(args.root)
    query = args.query.casefold()
    matches = [
        path
        for path in root.joinpath("ImportExport").rglob("*.inst")
        if query in str(path.relative_to(root / "ImportExport")).casefold()
    ][: args.limit]
    print(f"Matches: {len(matches)}")
    for path in matches:
        print(template_summary(path, root))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", help="CMO installation root (or set CMO_ROOT)")
    result.add_argument("--db", help="database filename; defaults to latest DB3K")
    subs = result.add_subparsers(dest="command", required=True)

    info = subs.add_parser("info", help="show installed database/template summary")
    info.set_defaults(func=command_info)

    search = subs.add_parser("search", help="search platform/component names")
    search.add_argument("query")
    search.add_argument("--kind", choices=sorted(TABLES), default="aircraft")
    search.add_argument("--year", type=int, help="filter platforms active in this year")
    search.add_argument("--limit", type=int, default=50)
    search.set_defaults(func=command_search)

    templates = subs.add_parser("templates", help="search relative INST template paths")
    templates.add_argument("query")
    templates.add_argument("--limit", type=int, default=50)
    templates.set_defaults(func=command_templates)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        args.func(args)
    except sqlite3.Error as exc:
        print(f"Database error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
