"""Run named checks against original synthetic personal-portfolio mechanisms."""
import copy
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from config_diff import review_changes
from rename_plan import build_plan

base = Path(__file__).parent
checks = []
input_paths = [base / n for n in ("names.synthetic.json", "before.synthetic.json", "after.synthetic.json")]
input_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths}


def check(name, actual, expected):
    checks.append({"id": name, "actual": actual, "expected": expected,
                   "passed": actual == expected})


def raises(name, function, expected):
    try:
        function()
        actual = "no exception"
    except Exception as exc:
        actual = type(exc).__name__
    check(name, actual, expected)


names = json.loads((base / "names.synthetic.json").read_text(encoding="utf-8"))
original_names = names.copy()
plan = build_plan(names)
rename_rows = {r["source"]: r for r in plan["rows"]}
check("rename-nine-row-buckets", plan["summary"],
      {"ready": 4, "unchanged": 2, "blocked": 3})
check("rename-existing-target-blocked", rename_rows["draft-report.txt"]["status"], "blocked")
check("rename-moving-target-still-blocked", rename_rows["draft-draft-note.txt"]["status"], "blocked")
check("rename-one-prefix-only", rename_rows["draft-draft-note.txt"]["target"], "draft-note.txt")
check("rename-empty-target-blocked", rename_rows["draft-"]["reason"], "empty target")
check("rename-unicode-name-retained", rename_rows["draft-茶.txt"]["target"], "茶.txt")
check("rename-input-not-mutated", names, original_names)
check("rename-prefix-in-middle-unchanged", build_plan(["my-draft-file.txt"])["summary"],
      {"ready": 0, "unchanged": 1, "blocked": 0})
ready = [r["target"] for r in plan["rows"] if r["status"] == "ready"]
check("rename-ready-targets-unique-and-unoccupied",
      len(ready) == len(set(ready)) and not (set(ready) & set(names)), True)
check("rename-exact-case-policy", build_plan(["draft-Report.txt", "report.txt"])["summary"],
      {"ready": 1, "unchanged": 1, "blocked": 0})
raises("rename-duplicate-source-rejected", lambda: build_plan(["x", "x"]), "ValueError")
raises("rename-nonstring-rejected", lambda: build_plan([None]), "TypeError")
raises("rename-empty-prefix-rejected", lambda: build_plan(["x"], ""), "ValueError")

before = json.loads((base / "before.synthetic.json").read_text(encoding="utf-8"))
after = json.loads((base / "after.synthetic.json").read_text(encoding="utf-8"))
original_configs = copy.deepcopy((before, after))
diff = review_changes(before, after)
diff_rows = {r["key"]: r for r in diff["rows"]}
check("config-six-key-buckets", diff["summary"],
      {"added": 1, "removed": 2, "changed": 2, "unchanged": 1})
check("config-boolean-number-change-detected", diff_rows["include_archived"]["status"], "changed")
check("config-same-json-number-unchanged", diff_rows["max_retries"]["status"], "unchanged")
check("config-added-null-is-present", diff_rows["new_hint"]["after"],
      {"present": True, "value": None, "kind": "null"})
check("config-removed-null-was-present", diff_rows["support_note"]["before"],
      {"present": True, "value": None, "kind": "null"})
check("config-absent-side-has-no-invented-null", diff_rows["support_note"]["after"],
      {"present": False})
check("config-inputs-not-mutated", json.dumps([before, after], sort_keys=True),
      json.dumps(original_configs, sort_keys=True))
check("config-stable-key-order", [r["key"] for r in diff["rows"]],
      ["include_archived", "legacy_mode", "max_retries", "new_hint", "support_note", "theme"])
raises("config-nested-object-rejected", lambda: review_changes({"a": {}}, {}), "TypeError")
raises("config-array-rejected", lambda: review_changes([], {}), "TypeError")
raises("config-nonfinite-number-rejected", lambda: review_changes({"a": float("nan")}, {}), "ValueError")
check("config-original-equality-trap-reproduced", False == 0, True)

cli_runs = []
for name, arguments, expected in [
    ("rename", ["rename_plan.py", "names.synthetic.json"],
     {"ready": 4, "unchanged": 2, "blocked": 3}),
    ("config", ["config_diff.py", "before.synthetic.json", "after.synthetic.json"],
     {"added": 1, "removed": 2, "changed": 2, "unchanged": 1}),
]:
    result = subprocess.run([sys.executable, "-X", "utf8", *arguments], cwd=base,
                            capture_output=True, text=True, encoding="utf-8", timeout=10)
    check(name + "-cli-exit", result.returncode, 0)
    try:
        actual_summary = json.loads(result.stdout)["summary"]
    except (ValueError, KeyError):
        actual_summary = None
    check(name + "-cli-summary", actual_summary, expected)
    cli_runs.append({"command": "python -X utf8 " + " ".join(arguments),
                     "exitCode": result.returncode, "summary": actual_summary})
check("cli-input-file-hashes-unchanged",
      {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths}, input_hashes)

report = {
    "executedAt": datetime.now(timezone.utc).isoformat(),
    "runtime": platform.python_implementation() + " " + platform.python_version(),
    "system": platform.system(),
    "scope": "Pure Python offline checks; no rename, restart, browser, client data, or production tests",
    "syntheticInputs": True,
    "codexAssistanceDisclosed": True,
    "cliRuns": cli_runs,
    "summary": {"passed": sum(c["passed"] for c in checks),
                "failed": sum(not c["passed"] for c in checks), "total": len(checks)},
    "checks": checks,
}
(base / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(base / "rename-plan-result.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(base / "config-diff-result.json").write_text(json.dumps(diff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"executedAt": report["executedAt"], "runtime": report["runtime"],
                  "summary": report["summary"], "rename": plan["summary"],
                  "config": diff["summary"]}))
raise SystemExit(0 if report["summary"]["failed"] == 0 else 1)
