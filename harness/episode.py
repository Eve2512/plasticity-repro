"""One actor game in a fresh context (Section 2.1, Appendix I.2).

The actor gets Bash (inventory read-only, session writable), a persistent Python
interpreter with game_api, and a native submit_action tool. A game the actor does
not finish (budget spent, no action returned, or a second tool timeout) is a loss.

On a tool timeout the actor gets one recovery call with only get_state,
get_legal_actions and submit_action. The paper does not say whether play goes on
after that call; here it does, with a fresh Python interpreter, and a second
timeout forfeits the game.
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from envs.games import HEX, Game
from harness import prompts
from harness.game_api import GameSession
from harness.ledger import Ledger
from harness.model import (
    BASH, GET_LEGAL_ACTIONS, GET_STATE, PYTHON, SUBMIT_ACTION, Model, ToolCall, serialise_messages,
)
from harness.sandbox import PythonSession, PythonTimeout, run_bash

@dataclass
class EpisodeConfig:
    max_calls: int = 32  # Go and Hex in the paper
    tool_timeout: float = 240.0


@dataclass
class GameResult:
    game_id: str
    actor: str
    winner: str | None
    score: float  # 1 for a win, 0 otherwise (Hex and Go with komi 9.5 have no draws)
    end_reason: str  # finished | budget | no_action | timeout
    model_calls: int
    moves: list = field(default_factory=list)  # [{"before": [...], "action", "opponent_action"}]
    invalid_submissions: int = 0


class _Actor:
    def __init__(self, game: GameSession, inventory: Path, session_dir: Path, hidden, cfg: EpisodeConfig):
        self.game, self.inventory, self.session_dir, self.hidden, self.cfg = game, inventory, session_dir, hidden, cfg
        self.python: PythonSession | None = None

    def _python(self) -> PythonSession:
        if self.python is None or not self.python.alive:
            self.python = PythonSession(
                self.game.dispatch,
                self.session_dir,
                readable=[self.inventory],
                writable=[self.session_dir],
                loadable=[self.inventory, self.session_dir],
                hidden=self.hidden,
            )
        return self.python

    def run(self, call: ToolCall) -> tuple[str, bool]:
        """Execute a tool call; returns (output, timed_out)."""
        name, args = call.name, call.args
        if name == "bash":
            res = run_bash(
                str(args.get("command", "")),
                self.session_dir,
                readable=[self.inventory],
                writable=[self.session_dir],
                timeout=self.cfg.tool_timeout,
                hidden=self.hidden,
            )
            out = res.output + ("" if res.exit_code == 0 else f"\n[exit code {res.exit_code}]")
            return out, res.timed_out
        if name == "python":
            try:
                return self._python().run(str(args.get("code", "")), self.cfg.tool_timeout).output, False
            except PythonTimeout as exc:
                return str(exc), True
        if name == "submit_action":
            return json.dumps(self.game.submit_action(str(args.get("action", "")))), False
        if name == "get_state":
            return json.dumps(self.game._describe(self.game.real)), False
        if name == "get_legal_actions":
            return json.dumps(self.game.real.legal_actions()), False
        return f"unknown tool {name}", False

    def close(self):
        if self.python is not None:
            self.python.close()


def play_game(
    model: Model,
    game_id: str,
    opening,
    opponent,
    inventory: Path,
    session_dir: Path,
    hidden,
    ledger: Ledger,
    checkpoint: int,
    phase: str,
    cfg: EpisodeConfig = EpisodeConfig(),
    transcript_path: Path | None = None,
    spec: Game = HEX,
) -> GameResult:
    session_dir.mkdir(parents=True, exist_ok=True)
    game = GameSession(opening, opponent)
    actor = _Actor(game, inventory, session_dir, hidden, cfg)
    intro = spec.prompt.format(
        actor_role=spec.roles[opening.actor],
        max_actions=getattr(game.real, "max_actions", None),
        komi=getattr(game.real, "komi", 0),
        inventory=inventory.resolve(),
        session=session_dir.resolve(),
        max_calls=cfg.max_calls,
        tool_timeout=cfg.tool_timeout,
    )
    messages: list[dict] = [{"role": "user", "content": intro}]
    calls, end_reason, recovered = 0, "budget", False
    tools = [BASH, PYTHON, SUBMIT_ACTION]
    try:
        while calls < cfg.max_calls and not game.done:
            budget = prompts.ACTOR_BUDGET.format(used=calls, maximum=cfg.max_calls, remaining=cfg.max_calls - calls)
            messages.append({"role": "user", "content": budget})
            ledger.check_budget()
            turn = model.step(prompts.SYSTEM, messages, tools)
            calls += 1
            ledger.add(checkpoint, phase, game_id, turn.usage)
            messages.append({"role": "assistant", "content": turn.text, "tool_calls": list(turn.tool_calls), "raw": turn.raw})
            if not turn.tool_calls:
                end_reason = "no_action"
                break
            timed_out = False
            for call in turn.tool_calls:
                if timed_out or game.done:
                    out = "not run: an earlier call in this turn timed out" if timed_out else "not run: game over"
                else:
                    out, timed_out = actor.run(call)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": out})
            if timed_out:
                if recovered or calls >= cfg.max_calls:
                    end_reason = "timeout"
                    break
                recovered = True
                messages.append({"role": "user", "content": prompts.ACTOR_TIMEOUT_RECOVERY})
                ledger.check_budget()
                turn = model.step(prompts.SYSTEM, messages, [GET_STATE, GET_LEGAL_ACTIONS, SUBMIT_ACTION])
                calls += 1
                ledger.add(checkpoint, phase, game_id, turn.usage)
                messages.append({"role": "assistant", "content": turn.text, "tool_calls": list(turn.tool_calls), "raw": turn.raw})
                for call in turn.tool_calls:
                    out, _ = actor.run(call) if call.name != "bash" and call.name != "python" else ("not available", False)
                    messages.append({"role": "tool", "tool_call_id": call.id, "content": out})
                if not any(c.name == "submit_action" for c in turn.tool_calls):
                    end_reason = "timeout"
                    break
    finally:
        actor.close()

    if game.done:
        end_reason = "finished"
    winner = game.real.winner()
    result = GameResult(
        game_id=game_id,
        actor=opening.actor,
        winner=winner,
        score=1.0 if winner == opening.actor else 0.0,
        end_reason=end_reason,
        model_calls=calls,
        moves=[{"before": list(m.before), "action": m.action, "opponent_action": m.opponent_action} for m in game.log],
        invalid_submissions=game.invalid_submissions,
    )
    if transcript_path:
        transcript_path.parent.mkdir(parents=True, exist_ok=True)
        transcript_path.write_text(
            json.dumps(
                {"result": asdict(result), "opening": list(opening.moves), "messages": serialise_messages(messages)},
                indent=1,
            )
        )
    return result
