"""Reflection: the same model revises its inventory from training games (Eq. 1).

Each attempt starts a fresh workspace with a copy of the parent inventory, the
training feedback, and the protocol files. The model has only Bash. After its
last call the candidate is validated; a rejected attempt is logged, and the next
attempt starts again from the parent with the logs available. When every attempt
is rejected the parent inventory is kept. Held-out games never reach this folder.
"""

import json
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

from envs.hex_feedback import diagnose_game
from harness import prompts
from harness.episode import GameResult
from harness.inventory import validate
from harness.ledger import Ledger
from harness.model import BASH, Model
from harness.sandbox import run_bash

_VALIDATOR = Path(__file__).with_name("validate_tracking.py")
_BASE_PYTHON = Path(sys.base_prefix) / "bin" / "python3"


@dataclass
class ReflectionConfig:
    max_calls: int = 50
    bash_timeout: float = 300.0  # Go and Hex in the paper (chess: 1800)
    max_attempts: int = 3  # Go and Hex in the paper (chess: 6)


@dataclass
class ReflectionOutcome:
    accepted: bool
    inventory: Path  # the accepted candidate, or the parent when every attempt failed
    attempts: list = field(default_factory=list)  # [{"attempt", "calls", "error"}]


def write_feedback(feedback: Path, games: list[tuple[GameResult, Path | None, Path | None]]) -> None:
    """Training games only: moves, diagnostics, result, transcript, session files."""
    games_dir = feedback / "games"
    games_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    for result, transcript, session in games:
        record = {
            "game_id": result.game_id,
            "actor": result.actor,
            "winner": result.winner,
            "score": result.score,
            "end_reason": result.end_reason,
            "model_calls": result.model_calls,
            "invalid_submissions": result.invalid_submissions,
            "moves": result.moves,
            "diagnostics": diagnose_game([(m["before"], m["action"]) for m in result.moves]),
        }
        if transcript and transcript.exists():
            record["transcript"] = json.loads(transcript.read_text())["messages"]
        (games_dir / f"{result.game_id}.json").write_text(json.dumps(record, indent=1))
        if session and session.exists():
            shutil.copytree(session, games_dir / f"{result.game_id}_session", dirs_exist_ok=True)
        blunders = sum(d["severity"] == "blunder" for d in record["diagnostics"])
        summary.append({"game_id": result.game_id, "score": result.score, "end_reason": result.end_reason,
                        "blunders": blunders})
    mean = 100 * sum(s["score"] for s in summary) / max(1, len(summary))
    (feedback / "summary.json").write_text(json.dumps({"mean_score": mean, "games": summary}, indent=1))


def _prepare(workspace: Path, parent: Path, feedback_src: Path, history: list) -> None:
    shutil.copytree(parent, workspace / "inventory", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(feedback_src, workspace / "feedback")
    protocol = workspace / "feedback" / "protocol"
    protocol.mkdir()
    (protocol / "SCHEMA.md").write_text(prompts.SCHEMA_MD)
    shutil.copy(_VALIDATOR, protocol / "validate_tracking.py")
    shutil.copytree(parent, protocol / "parent_inventory", ignore=shutil.ignore_patterns("__pycache__"))
    if history:
        attempts = workspace / "feedback" / "reflection_attempts"
        attempts.mkdir()
        for h in history:
            shutil.copy(h["log"], attempts / Path(h["log"]).name)
        (workspace / "feedback" / "reflection_retry_history.json").write_text(
            json.dumps([{k: v for k, v in h.items() if k != "log"} for h in history], indent=1)
        )


def reflect(
    model: Model,
    parent: Path,
    feedback_src: Path,
    attempt_root: Path,
    hidden,
    ledger: Ledger,
    checkpoint: int,
    cfg: ReflectionConfig = ReflectionConfig(),
) -> ReflectionOutcome:
    history: list[dict] = []
    for attempt in range(1, cfg.max_attempts + 1):
        attempt_dir = attempt_root / f"attempt_{attempt}"
        workspace = attempt_dir / "workspace"
        _prepare(workspace, parent, feedback_src, history)
        ws = workspace.resolve()
        validate_cmd = (
            f"{_BASE_PYTHON} -I {ws}/feedback/protocol/validate_tracking.py "
            f"{ws}/inventory {ws}/feedback/protocol/parent_inventory"
        )
        intro = prompts.REFLECTION.format(
            workspace=ws, bash_timeout=cfg.bash_timeout, max_calls=cfg.max_calls, validate_command=validate_cmd
        )
        if history:
            intro += "\n\n" + prompts.REFLECTION_RETRY.format(workspace=ws, latest_error=history[-1]["error"])
        messages: list[dict] = [{"role": "user", "content": intro}]
        calls = 0
        while calls < cfg.max_calls:
            remaining = cfg.max_calls - calls
            if remaining == 1:
                note = prompts.REFLECTION_FINAL.format(
                    used=calls, maximum=cfg.max_calls, remaining=remaining, turn=calls + 1, workspace=ws
                )
            else:
                note = prompts.REFLECTION_BUDGET.format(used=calls, maximum=cfg.max_calls, remaining=remaining)
            messages.append({"role": "user", "content": note})
            turn = model.step(prompts.SYSTEM, messages, [BASH])
            calls += 1
            ledger.add(checkpoint, "reflect", f"checkpoint_{checkpoint:03d}_attempt_{attempt}", turn.usage)
            messages.append({"role": "assistant", "content": turn.text, "tool_calls": list(turn.tool_calls)})
            if not turn.tool_calls:
                break
            for call in turn.tool_calls:
                if call.name != "bash":
                    out = f"unknown tool {call.name}; only bash is available"
                else:
                    res = run_bash(
                        str(call.args.get("command", "")), ws, readable=[ws], writable=[ws],
                        timeout=cfg.bash_timeout, hidden=hidden,
                    )
                    out = res.output + ("" if res.exit_code == 0 else f"\n[exit code {res.exit_code}]")
                messages.append({"role": "tool", "tool_call_id": call.id, "content": out})

        result = validate(workspace / "inventory", parent=parent, scratch=attempt_dir / "_smoke")
        log = attempt_dir / f"attempt_{attempt}.json"
        log.write_text(json.dumps({
            "attempt": attempt,
            "calls": calls,
            "accepted": result.ok,
            "errors": list(result.errors),
            "messages": [
                {**m, "tool_calls": [{"id": c.id, "name": c.name, "args": c.args} for c in m["tool_calls"]]}
                if "tool_calls" in m else m
                for m in messages
            ],
        }, indent=1))
        record = {"attempt": attempt, "calls": calls, "error": result.message or None, "log": str(log)}
        history.append(record)
        if result.ok:
            return ReflectionOutcome(True, workspace / "inventory", [{k: v for k, v in h.items() if k != "log"} for h in history])
    return ReflectionOutcome(False, parent, [{k: v for k, v in h.items() if k != "log"} for h in history])
