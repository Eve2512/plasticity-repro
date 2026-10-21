import json
import shutil
import subprocess
import sys

import pytest

from harness.inventory import commit, empty_inventory, validate
from harness.validate_tracking import check


def write_tracking(inv, modes, arts):
    (inv / "tracking" / "failure_modes.json").write_text(
        json.dumps({"schema_version": "failure_modes.v1", "failure_modes": modes})
    )
    (inv / "tracking" / "artifacts.json").write_text(
        json.dumps({"schema_version": "artifacts.v1", "artifacts": arts})
    )


FM = {"id": "FM-0001", "description": "missed win", "status": "active", "trajectory_ids": ["g1"]}
TOOL = {
    "id": "AR-0001",
    "description": "win finder",
    "kind": "tool",
    "paths": ["tools/wins.py"],
    "entrypoints": ["tools/wins.py:find_win"],
    "failure_mode_ids": ["FM-0001"],
    "status": "active",
}


@pytest.fixture
def inv(tmp_path):
    inv = empty_inventory(tmp_path / "inv")
    (inv / "tools").mkdir()
    (inv / "tools" / "wins.py").write_text("def find_win(moves):\n    return moves[0]\n")
    write_tracking(inv, [FM], [TOOL])
    return inv


def test_empty_inventory_is_valid(tmp_path):
    assert validate(empty_inventory(tmp_path / "i0")).ok


def test_valid_tool_inventory(inv):
    res = validate(inv)
    assert res.ok, res.message


def test_unlisted_file_is_rejected(inv):
    (inv / "notes.md").write_text("x")
    assert any("not listed" in e for e in check(inv))


def test_unknown_failure_mode_and_bad_entrypoint(inv):
    bad = dict(TOOL, failure_mode_ids=["FM-0009"], entrypoints=["tools/wins.py:nope"])
    write_tracking(inv, [FM], [bad])
    errors = check(inv)
    assert any("unknown failure mode" in e for e in errors)
    assert any("not defined" in e for e in errors)


def test_merged_needs_merged_into(inv):
    write_tracking(inv, [dict(FM, status="merged")], [TOOL])
    assert any("merged_into" in e for e in check(inv))


def test_retired_files_must_leave(inv):
    write_tracking(inv, [FM], [dict(TOOL, status="retired")])
    assert any("retired" in e for e in check(inv))


def test_parent_ids_must_be_preserved(inv, tmp_path):
    parent = tmp_path / "parent"
    shutil.copytree(inv, parent)
    shutil.rmtree(inv / "tools")
    write_tracking(inv, [], [])
    errors = check(inv, parent)
    assert any("preserved" in e for e in errors) and any("retire instead" in e for e in errors)


def test_tool_that_fails_to_load_is_rejected(inv):
    (inv / "tools" / "wins.py").write_text("import os\ndef find_win(m):\n    return m\n")
    res = validate(inv)
    assert not res.ok and "persistent tool load failed" in res.message


def test_cli(inv):
    script = "harness/validate_tracking.py"
    out = subprocess.run([sys.executable, script, str(inv)], capture_output=True, text=True)
    assert out.returncode == 0 and out.stdout.strip() == "OK"


def test_commit_copies_and_refuses_overwrite(inv, tmp_path):
    target = commit(inv, tmp_path / "checkpoint_001")
    assert (target / "tools" / "wins.py").exists()
    with pytest.raises(FileExistsError):
        commit(inv, target)
