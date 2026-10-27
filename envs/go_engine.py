"""GNU Go opponent and scorer over GTP (Table 2: levels 5-9 train/ID, 10 OOD).

Each call starts `gnugo --mode gtp`, replays the game so far and asks for one
move (or the final score), then quits. That keeps the opponent stateless and
picklable for worker processes; on 5×5 a call takes a few tens of milliseconds.
GNU Go runs with Chinese rules, positional superko, komi 9.5, never resigns,
and uses a fixed random seed per game, so the same position, level and seed
give the same move.

Install: `brew install gnu-go` (the formula is gnu-go, the binary gnugo).
"""

import shutil
import subprocess
from dataclasses import dataclass

from envs.go import BLACK, GoState

GNUGO = "gnugo"
SCORER_LEVEL = 10
TIMEOUT = 60.0


class GnuGoError(RuntimeError):
    pass


def available() -> bool:
    return shutil.which(GNUGO) is not None


def _gtp(state: GoState, commands: list[str], level: int, seed: int) -> list[str]:
    """Replay `state` in a fresh GNU Go and run `commands`; returns their responses."""
    if not available():
        raise GnuGoError("gnugo not found; install it with `brew install gnu-go`")
    setup = [f"boardsize {state.size}", "clear_board", f"komi {state.komi}"]
    colour = BLACK
    for i in state.history:
        setup.append(f"play {'black' if colour == BLACK else 'white'} {state.name(i)}")
        colour = "O" if colour == BLACK else BLACK
    script = "\n".join(setup + commands + ["quit"]) + "\n"
    proc = subprocess.run(
        [GNUGO, "--mode", "gtp", "--level", str(level), "--seed", str(seed), "--chinese-rules",
         "--positional-superko", "--never-resign"],
        input=script, capture_output=True, text=True, timeout=TIMEOUT,
    )
    # One response per command, each "= ..." or "? ..." followed by a blank line.
    replies = [r.strip() for r in proc.stdout.split("\n\n") if r.strip()]
    if len(replies) != len(setup) + len(commands) + 1:
        raise GnuGoError(f"unexpected GTP output: {proc.stdout!r} {proc.stderr!r}")
    for cmd, reply in zip(setup, replies):
        if not reply.startswith("="):
            raise GnuGoError(f"{cmd!r} failed: {reply}")
    return [r.lstrip("=?").strip() if r.startswith("=") else r for r in replies[len(setup):-1]]


@dataclass(frozen=True)
class GnuGoEngine:
    level: int
    seed: int = 0

    def choose(self, state: GoState) -> str:
        if state.is_over():
            raise ValueError("game is over")
        colour = "black" if state.to_move == BLACK else "white"
        (reply,) = _gtp(state, [f"genmove {colour}"], self.level, self.seed)
        if reply.startswith("?"):
            raise GnuGoError(f"genmove failed: {reply}")
        move = "pass" if reply.upper() in ("PASS", "RESIGN") else reply.upper()
        # GNU Go and this engine agree on the rules; fall back to a pass if they ever differ.
        return move if move == "pass" or move in state.legal_actions() else "pass"


def gnugo_final_margin(state: GoState) -> float:
    """Black's margin after komi from GNU Go's final_score (dead stones removed)."""
    (reply,) = _gtp(state, ["final_score"], SCORER_LEVEL, 0)
    if reply.startswith("?"):
        raise GnuGoError(f"final_score failed: {reply}")
    if reply == "0":
        return 0.0
    side, _, amount = reply.partition("+")
    return float(amount) if side == "B" else -float(amount)
