"""Sandboxed Bash and persistent Python for agents (macOS sandbox-exec).

The paper runs each actor in an isolated container with no network, no access to
the opponent process, credentials, held-out evaluations or other runs (Section 3.1).
Here the boundary is a sandbox-exec profile: no network, no reads under /Users
or the run directory except the paths given, and writes only to the writable
paths. The environment is emptied, so API keys never reach agent code.

The restricted builtins in the Python child mirror the paper's "Python imports
and direct filesystem access are unavailable"; they are a convention for the
agent, not the security boundary.
"""

import json
import os
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

MAX_OUTPUT = 20_000  # characters of stdout/stderr returned to the model
_BASE_PYTHON = Path(sys.base_prefix) / "bin" / "python3"
_CHILD = Path(__file__).with_name("_python_child.py").read_text()


def _real(path) -> str:
    return str(Path(path).resolve())


def sandbox_profile(readable, writable, hidden=()) -> str:
    """SBPL profile. Later rules override earlier ones.

    Parent folders of allowed paths get metadata access only (stat, not listing
    or reading), which `mkdir -p` and `cd` need for absolute paths.
    """
    hidden = ["/Users", *map(_real, hidden)]
    allowed = [_real(p) for p in [*readable, *writable, sys.base_prefix]]
    parents = sorted({str(a) for p in allowed for a in Path(p).parents if str(a) != "/"})
    deny_read = " ".join(f'(subpath "{p}")' for p in hidden)
    allow_read = " ".join(f'(subpath "{p}")' for p in allowed)
    allow_meta = " ".join(f'(literal "{p}")' for p in parents)
    allow_write = " ".join(f'(subpath "{_real(p)}")' for p in writable)
    return (
        "(version 1)(allow default)(deny network*)"
        "(deny file-write*)"
        f'(allow file-write* (literal "/dev/null") {allow_write})'
        f"(deny file-read* {deny_read})"
        f"(allow file-read* {allow_read})"
        + (f"(allow file-read-metadata {allow_meta})" if parents else "")
    )


def _clip(text: str) -> str:
    if len(text) <= MAX_OUTPUT:
        return text
    return text[:MAX_OUTPUT] + f"\n[... {len(text) - MAX_OUTPUT} characters cut]"


def _env(home: Path) -> dict:
    return {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "HOME": _real(home), "PWD": _real(home), "LANG": "en_US.UTF-8"}


@dataclass(frozen=True)
class ToolResult:
    output: str
    exit_code: int
    timed_out: bool = False


def run_bash(command: str, cwd, readable, writable, timeout: float, hidden=()) -> ToolResult:
    profile = sandbox_profile(readable, writable, hidden)
    proc = subprocess.Popen(
        ["/usr/bin/sandbox-exec", "-p", profile, "/bin/bash", "-c", command],
        cwd=_real(cwd),
        env=_env(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, _ = proc.communicate()
        return ToolResult(_clip(out or ""), -9, timed_out=True)
    return ToolResult(_clip(out), proc.returncode)


class PythonTimeout(Exception):
    pass


class PythonSession:
    """A persistent sandboxed interpreter whose game_api calls reach `api`.

    `api(method, args)` runs in this (trusted) process. `loadable` are the
    directories load_python(path) may read from.
    """

    def __init__(self, api, cwd, readable, writable, loadable, hidden=()):
        self.api = api
        profile = sandbox_profile(readable, writable, hidden)
        self.proc = subprocess.Popen(
            ["/usr/bin/sandbox-exec", "-p", profile, str(_BASE_PYTHON), "-I", "-S", "-c", _CHILD],
            cwd=_real(cwd),
            env=_env(cwd),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            start_new_session=True,
        )
        self._send({"op": "init", "loadable": [_real(p) for p in loadable]})
        self._read()

    def _send(self, message):
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()

    def _read(self):
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("python sandbox exited")
        return json.loads(line)

    def run(self, code: str, timeout: float) -> ToolResult:
        """Execute `code`; serve game_api calls until the child reports done."""
        import threading

        expired = threading.Event()

        def on_timeout():
            expired.set()
            self._kill()

        timer = threading.Timer(timeout, on_timeout)
        timer.start()
        try:
            self._send({"op": "exec", "code": code})
            while True:
                try:
                    msg = self._read()
                except (RuntimeError, ValueError):
                    if expired.is_set():
                        raise PythonTimeout(f"python call exceeded {timeout:g} s") from None
                    raise
                if msg["op"] == "api":
                    try:
                        reply = {"ok": True, "value": self.api(msg["method"], msg["args"])}
                    except Exception as exc:  # reported to the agent, not raised here
                        reply = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
                    self._send(reply)
                elif msg["op"] == "done":
                    return ToolResult(_clip(msg["output"]), 0 if msg["ok"] else 1)
        finally:
            timer.cancel()

    @property
    def alive(self) -> bool:
        return self.proc.poll() is None

    def _kill(self):
        if self.alive:
            os.killpg(self.proc.pid, signal.SIGKILL)

    def close(self):
        self._kill()
        self.proc.wait()
