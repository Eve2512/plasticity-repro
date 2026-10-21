"""Persistent agent inventories: creation, validation, and committing checkpoints.

A candidate inventory becomes persistent only if the tracking files pass
validate_tracking.check and every Python file loads in the sandbox with its
entrypoints defined (the paper's "structural and executable checks").
"""

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from harness.sandbox import PythonSession
from harness.validate_tracking import TRACKING, check

SMOKE_TIMEOUT = 30.0


def empty_inventory(path) -> Path:
    """Checkpoint 0: the bare harness, with empty tracking files."""
    inv = Path(path)
    (inv / TRACKING).mkdir(parents=True, exist_ok=True)
    (inv / TRACKING / "failure_modes.json").write_text(
        json.dumps({"schema_version": "failure_modes.v1", "failure_modes": []}, indent=2)
    )
    (inv / TRACKING / "artifacts.json").write_text(
        json.dumps({"schema_version": "artifacts.v1", "artifacts": []}, indent=2)
    )
    return inv


@dataclass(frozen=True)
class Validation:
    ok: bool
    errors: tuple[str, ...]

    @property
    def message(self) -> str:
        return "; ".join(self.errors)


def _smoke_load(inv: Path, scratch: Path) -> list[str]:
    arts = json.loads((inv / TRACKING / "artifacts.json").read_text())["artifacts"]
    entrypoints = [e for a in arts if a.get("status") == "active" for e in a.get("entrypoints", [])]
    py_files = sorted(p for p in inv.rglob("*.py") if TRACKING not in p.relative_to(inv).parts)
    if not py_files:
        return []
    scratch.mkdir(parents=True, exist_ok=True)

    def no_api(method, args):
        raise RuntimeError("game_api is unavailable during validation")

    session = PythonSession(no_api, scratch, readable=[inv], writable=[scratch], loadable=[inv])
    errors = []
    try:
        for f in py_files:
            res = session.run(f"load_python({str(f.resolve())!r})", SMOKE_TIMEOUT)
            if res.exit_code:
                errors.append(f"persistent tool load failed: {f.relative_to(inv)}: {res.output.strip()}")
        for e in entrypoints:
            func = e.partition(":")[2]
            res = session.run(f"callable({func})", SMOKE_TIMEOUT)
            if res.output.strip() != "True":
                errors.append(f"entrypoint {e} is not callable after loading")
    except Exception as exc:
        errors.append(f"smoke validation failed: {type(exc).__name__}: {exc}")
    finally:
        session.close()
    return errors


def validate(candidate, parent=None, scratch=None) -> Validation:
    inv = Path(candidate)
    errors = check(inv, parent)
    if not errors:
        errors = _smoke_load(inv, Path(scratch) if scratch else inv.parent / "_smoke")
    return Validation(not errors, tuple(errors))


def commit(candidate, target) -> Path:
    """Copy an accepted candidate to its checkpoint directory (read-only from then on)."""
    target = Path(target)
    if target.exists():
        raise FileExistsError(target)
    shutil.copytree(candidate, target, ignore=shutil.ignore_patterns("__pycache__"))
    return target
