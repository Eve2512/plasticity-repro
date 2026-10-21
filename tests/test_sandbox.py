import os

import pytest

from harness.sandbox import PythonSession, PythonTimeout, run_bash


@pytest.fixture
def dirs(tmp_path):
    inv = tmp_path / "inventory"
    ses = tmp_path / "session"
    secret = tmp_path / "heldout"
    for d in (inv, ses, secret):
        d.mkdir()
    (inv / "tool.py").write_text("def double(x):\n    return 2 * x\n")
    (secret / "scores.json").write_text("{}")
    return inv, ses, secret


def bash(cmd, dirs, timeout=10):
    inv, ses, secret = dirs
    return run_bash(cmd, ses, readable=[inv], writable=[ses], timeout=timeout, hidden=[secret.parent])


def test_bash_reads_inventory_and_writes_session(dirs):
    res = bash("cat ../inventory/tool.py | head -1 && echo ok > note.txt && cat note.txt", dirs)
    assert res.exit_code == 0 and "def double" in res.output and "ok" in res.output


def test_bash_cannot_write_inventory(dirs):
    assert bash("echo x > ../inventory/new.py", dirs).exit_code != 0
    assert not (dirs[0] / "new.py").exists()


def test_bash_cannot_read_hidden_dirs_or_home(dirs):
    assert bash("cat ../heldout/scores.json", dirs).exit_code != 0
    assert bash(f"ls {os.path.expanduser('~')}", dirs).exit_code != 0


def test_bash_has_no_network_or_secrets(dirs, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "should-not-leak")
    assert "should-not-leak" not in bash("env", dirs).output
    res = bash("curl -s -m 3 https://example.com >/dev/null && echo open || echo blocked", dirs)
    assert "blocked" in res.output


def test_bash_timeout(dirs):
    res = bash("sleep 5", dirs, timeout=0.5)
    assert res.timed_out


def test_absolute_paths_under_users():
    """Regression: mkdir -p on an absolute path under /Users needs parent metadata."""
    import shutil
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent / "runs" / "_sandbox_test"
    shutil.rmtree(root, ignore_errors=True)
    ses = root / "session"
    ses.mkdir(parents=True)
    (root / "secret.txt").write_text("x")
    try:
        res = run_bash(f"mkdir -p {ses}/a/b && cd {ses}/a && pwd", ses, readable=[], writable=[ses],
                       timeout=10, hidden=[root])
        assert res.exit_code == 0 and res.output.strip() == f"{ses}/a", res.output
        assert "getcwd" not in res.output
        res = run_bash(f"cat {root}/secret.txt; ls {root}", ses, readable=[], writable=[ses], timeout=10,
                       hidden=[root])
        assert res.output.count("Operation not permitted") == 2
    finally:
        shutil.rmtree(root, ignore_errors=True)


def make_python(dirs, api=lambda m, a: f"{m}{a}"):
    inv, ses, secret = dirs
    return PythonSession(api, ses, readable=[inv], writable=[ses], loadable=[inv, ses], hidden=[secret.parent])


def test_python_persists_state_and_calls_api(dirs):
    py = make_python(dirs)
    try:
        assert py.run("x = 21", 10).exit_code == 0
        assert py.run("x * 2", 10).output.strip() == "42"
        assert "get_state[]" in py.run("game_api['get_state']()", 10).output
    finally:
        py.close()


def test_python_load_python_only_from_permitted_dirs(dirs):
    inv, ses, secret = dirs
    py = make_python(dirs)
    try:
        assert py.run(f"load_python('{inv / 'tool.py'}'); double(4)", 10).output.strip().endswith("8")
        res = py.run(f"load_python('{secret / 'scores.json'}')", 10)
        assert res.exit_code == 1 and "PermissionError" in res.output
    finally:
        py.close()


def test_python_imports_and_open_unavailable(dirs):
    py = make_python(dirs)
    try:
        assert "ImportError" in py.run("import os", 10).output
        assert "NameError" in py.run("open('x')", 10).output
        assert py.run("class A(object):\n    pass\nA()", 10).exit_code == 0
    finally:
        py.close()


def test_python_api_errors_are_reported(dirs):
    def api(method, args):
        raise ValueError("bad move")

    py = make_python(dirs, api)
    try:
        res = py.run("game_api['submit_action']('z9')", 10)
        assert res.exit_code == 1 and "bad move" in res.output
    finally:
        py.close()


def test_python_timeout_kills_session(dirs):
    py = make_python(dirs)
    with pytest.raises(PythonTimeout):
        py.run("while True:\n    pass", 0.5)
    assert not py.alive
