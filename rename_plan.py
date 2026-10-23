"""Inspect a literal prefix-removal plan. Never rename or write user files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_plan(names: list[str], prefix: str = "draft-") -> dict:
    if not isinstance(names, list) or any(type(n) is not str for n in names):
        raise TypeError("names must be a list of strings")
    if any(not n for n in names):
        raise ValueError("source names must not be empty")
    if len(set(names)) != len(names):
        raise ValueError("source names must be unique")
    if type(prefix) is not str or not prefix:
        raise ValueError("prefix must be a nonempty string")

    occupied = set(names)
    rows = []
    for source in names:
        target = source[len(prefix):] if source.startswith(prefix) else source
        if target == source:
            status, reason = "unchanged", "prefix absent at start"
        elif not target:
            status, reason = "blocked", "empty target"
        elif target in occupied:
            status, reason = "blocked", "target is an existing source name"
        else:
            status, reason = "ready", "literal target is not occupied"
        rows.append({"source": source, "target": target,
                     "status": status, "reason": reason})

    return {
        "policy": "Exact, case-sensitive strings; remove one leading prefix only",
        "scope": "Read-only synthetic name planning, not filesystem validation",
        "summary": {s: sum(r["status"] == s for r in rows)
                    for s in ("ready", "unchanged", "blocked")},
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names_json", type=Path)
    parser.add_argument("--prefix", default="draft-")
    args = parser.parse_args()
    try:
        names = json.loads(args.names_json.read_text(encoding="utf-8-sig"))
        result = build_plan(names, args.prefix)
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
