"""Replay saved Hex tools without a model (report 20).

Plays each saved checkpoint's hex/hex_glue.py against the run's opponent on the run's own
held-out openings: turn() is called every move and its action submitted. No API calls.

  python scripts/replay_hex_glue.py runs/hex_glm_reflect_high 1,2,3 [id|ood]
"""
import contextlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from envs.games import GAMES
from envs.hex_openings import split_banks
from harness.game_api import GameSession

API = ("get_state", "get_legal_actions", "apply_action", "undo_action", "current_player", "submit_action")


def load(path, ns):
    exec(compile(Path(path).read_text(), str(path), "exec"), ns)


def replay(run, version, split="id", max_turns=40):
    cfg = json.loads((run / "results.json").read_text())["config"]
    banks = split_banks(cfg["games"], source=cfg.get("openings", "pooled"))
    levels = cfg["ood_levels"] if split == "ood" else cfg["train_id_levels"]
    glue = run / "inventories" / f"checkpoint_{version:03d}" / "hex" / "hex_glue.py"
    rows = []
    for i, opening in enumerate(banks[split]):
        s = GameSession(opening, GAMES["hex"].opponent(levels[i % len(levels)], opening))
        api = {m: getattr(s, m) for m in API}
        ns = {"__name__": "glue"}
        ns["load_python"] = lambda p, ns=ns: load(p, ns)
        err = None
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                load(glue, ns)
                n = 0
                while not s.done and n < max_turns:
                    a = ns["turn"](api)
                    n += 1
                    if s.real.to_move == s.actor and not s.done:
                        api["submit_action"](a)
        except Exception as e:
            err = type(e).__name__
        w = s.real.winner()
        rows.append((opening.actor, w == s.actor, err if w is None else None))
    return rows


def main():
    run = Path(sys.argv[1])
    split = sys.argv[3] if len(sys.argv) > 3 else "id"
    for v in (int(x) for x in sys.argv[2].split(",")):
        rows = replay(run, v, split)
        cells = " ".join(f"{a}{'W' if won else ('E:' + err if err else 'L')}" for a, won, err in rows)
        print(f"tool v{v}: {sum(won for _, won, _ in rows)}/{len(rows)} {split}  {cells}", flush=True)


if __name__ == "__main__":
    main()
