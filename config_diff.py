"""Review two flat JSON objects without changing configuration or services."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def json_kind(value) -> str:
    if value is None:
        return "null"
    if type(value) is bool:
        return "boolean"
    if type(value) in (int, float):
        if type(value) is float and not math.isfinite(value):
            raise ValueError("numbers must be finite")
        return "number"
    if type(value) is str:
        return "string"
    raise TypeError("only flat JSON objects with scalar values are supported")


def validate_config(config: dict) -> None:
    if type(config) is not dict or any(type(k) is not str for k in config):
        raise TypeError("configuration must be an object with string keys")
    for value in config.values():
        json_kind(value)


def review_changes(before: dict, after: dict) -> dict:
    validate_config(before)
    validate_config(after)
    rows = []
    for key in sorted(before.keys() | after.keys()):
        was, now = key in before, key in after
        old = {"present": was}
        new = {"present": now}
        if was:
            old.update(value=before[key], kind=json_kind(before[key]))
        if now:
            new.update(value=after[key], kind=json_kind(after[key]))
        if not was:
            status = "added"
        elif not now:
            status = "removed"
        elif old["kind"] == new["kind"] and old["value"] == new["value"]:
            status = "unchanged"
        else:
            status = "changed"
        rows.append({"key": key, "status": status, "before": old, "after": new})
    return {
        "scope": "Read-only, flat JSON scalar review; not application validation",
        "summary": {s: sum(r["status"] == s for r in rows)
                    for s in ("added", "removed", "changed", "unchanged")},
        "rows": rows,
    }


def reject_constant(token: str):
    raise ValueError("nonfinite JSON constants are not supported")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before_json", type=Path)
    parser.add_argument("after_json", type=Path)
    args = parser.parse_args()
    try:
        before, after = [json.loads(p.read_text(encoding="utf-8-sig"),
                                   parse_constant=reject_constant)
                         for p in (args.before_json, args.after_json)]
        result = review_changes(before, after)
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
