"""Structural checks for an agent inventory (the schemas in Appendix I.3).

Standalone and stdlib-only: the reflecting agent runs it inside the sandbox as
    python3 validate_tracking.py <inventory> [<parent inventory>]
and the harness imports `check` for the same rules.
"""

import ast
import json
import re
import sys
from pathlib import Path

FM_ID = re.compile(r"^FM-\d{4}$")
AR_ID = re.compile(r"^AR-\d{4}$")
FM_STATUS = {"active", "mitigated", "merged"}
AR_STATUS = {"active", "retired"}
AR_KIND = {"tool", "memory", "strategy", "instruction", "other"}
TRACKING = "tracking"


def _load(path: Path, schema: str, key: str, errors: list) -> list:
    if not path.exists():
        errors.append(f"missing {path.name}")
        return []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name}: invalid JSON ({exc})")
        return []
    if not isinstance(data, dict) or data.get("schema_version") != schema:
        errors.append(f"{path.name}: schema_version must be {schema!r}")
        return []
    items = data.get(key)
    if not isinstance(items, list):
        errors.append(f"{path.name}: {key!r} must be a list")
        return []
    return items


def _functions(path: Path) -> set:
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError:
        return set()
    return {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


def check(inventory, parent=None) -> list:
    inv = Path(inventory)
    errors = []
    modes = _load(inv / TRACKING / "failure_modes.json", "failure_modes.v1", "failure_modes", errors)
    arts = _load(inv / TRACKING / "artifacts.json", "artifacts.v1", "artifacts", errors)

    fm_ids = set()
    for fm in modes:
        fid = fm.get("id") if isinstance(fm, dict) else None
        if not isinstance(fid, str) or not FM_ID.match(fid):
            errors.append(f"failure mode with bad id: {fid!r}")
            continue
        if fid in fm_ids:
            errors.append(f"duplicate failure mode id {fid}")
        fm_ids.add(fid)
        if not isinstance(fm.get("description"), str) or not fm["description"].strip():
            errors.append(f"{fid}: description must be a non-empty string")
        if fm.get("status") not in FM_STATUS:
            errors.append(f"{fid}: status must be one of {sorted(FM_STATUS)}")
        if not isinstance(fm.get("trajectory_ids"), list):
            errors.append(f"{fid}: trajectory_ids must be a list")
        if (fm.get("status") == "merged") != ("merged_into" in fm):
            errors.append(f"{fid}: merged_into is required for merged modes and only for them")
    for fm in modes:
        if isinstance(fm, dict) and "merged_into" in fm and fm["merged_into"] not in fm_ids:
            errors.append(f"{fm.get('id')}: merged_into {fm['merged_into']!r} does not exist")

    ar_ids, active_paths, retired_paths = set(), set(), set()
    for ar in arts:
        aid = ar.get("id") if isinstance(ar, dict) else None
        if not isinstance(aid, str) or not AR_ID.match(aid):
            errors.append(f"artifact with bad id: {aid!r}")
            continue
        if aid in ar_ids:
            errors.append(f"duplicate artifact id {aid}")
        ar_ids.add(aid)
        if ar.get("kind") not in AR_KIND:
            errors.append(f"{aid}: kind must be one of {sorted(AR_KIND)}")
        if ar.get("status") not in AR_STATUS:
            errors.append(f"{aid}: status must be one of {sorted(AR_STATUS)}")
        paths, entries, fms = ar.get("paths"), ar.get("entrypoints"), ar.get("failure_mode_ids")
        if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
            errors.append(f"{aid}: paths must be a list of strings")
            continue
        if not isinstance(entries, list):
            errors.append(f"{aid}: entrypoints must be a list")
            entries = []
        if not isinstance(fms, list) or not fms:
            errors.append(f"{aid}: failure_mode_ids must be a non-empty list")
        else:
            for f in fms:
                if f not in fm_ids:
                    errors.append(f"{aid}: unknown failure mode {f}")
        if ar.get("kind") != "tool" and entries:
            errors.append(f"{aid}: non-executable artifacts use an empty entrypoints list")
        (active_paths if ar.get("status") == "active" else retired_paths).update(paths)
        for p in paths:
            if p.startswith("/") or ".." in Path(p).parts or p.startswith(TRACKING + "/"):
                errors.append(f"{aid}: path {p!r} must be relative to the inventory and outside tracking/")
            elif ar.get("status") == "active" and not (inv / p).is_file():
                errors.append(f"{aid}: path {p} does not exist")
        for e in entries:
            file, _, func = str(e).partition(":")
            if file not in paths or not func:
                errors.append(f"{aid}: entrypoint {e!r} must be '<one of paths>:<function>'")
            elif (inv / file).is_file() and func not in _functions(inv / file):
                errors.append(f"{aid}: entrypoint {e!r} is not defined in {file}")

    for f in sorted(p.relative_to(inv).as_posix() for p in inv.rglob("*") if p.is_file()):
        if f.startswith(TRACKING + "/") or "__pycache__" in f:
            continue
        if f in retired_paths and f not in active_paths:
            errors.append(f"{f}: belongs to a retired artifact but is still in the inventory")
        elif f not in active_paths:
            errors.append(f"{f}: not listed in any active artifact")

    if parent is not None:
        p_errors = []
        p_modes = _load(Path(parent) / TRACKING / "failure_modes.json", "failure_modes.v1", "failure_modes", p_errors)
        p_arts = _load(Path(parent) / TRACKING / "artifacts.json", "artifacts.v1", "artifacts", p_errors)
        for fm in p_modes:
            if fm.get("id") not in fm_ids:
                errors.append(f"{fm.get('id')}: failure modes must be preserved, not deleted")
        for ar in p_arts:
            if ar.get("id") not in ar_ids:
                errors.append(f"{ar.get('id')}: artifact ids must be kept (retire instead of deleting)")
    return errors


def main(argv):
    if len(argv) not in (2, 3):
        print("usage: validate_tracking.py <inventory> [<parent inventory>]")
        return 2
    errors = check(argv[1], argv[2] if len(argv) == 3 else None)
    if errors:
        print("INVALID")
        for e in errors:
            print(f"- {e}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
