"""Run one agent lineage (M, I_0) ... (M, I_T) on Hex (Section 2.1, 3.1).

At each checkpoint the current inventory plays train, held-out ID and held-out
OOD games, each in a fresh episode. Reflection on the training games produces
the next inventory. Held-out games are stored where neither the actor nor the
reflector can read them.

Run directory:
    inventories/checkpoint_NNN/     committed inventories (read-only to agents)
    games/checkpoint_NNN/<split>/   transcripts and per-game session folders
    feedback/checkpoint_NNN/        what reflection sees (training games only)
    reflect/checkpoint_NNN/         reflection attempts
    ledger.jsonl, results.json
"""

import json
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from envs.hex_engine import AlphaBetaEngine
from envs.hex_openings import OOD_LEVELS, TRAIN_ID_LEVELS, split_banks
from harness.episode import EpisodeConfig, GameResult, play_game
from harness.inventory import commit, empty_inventory
from harness.ledger import BudgetExceeded, Ledger
from harness.model import Model
from harness.reflection import ReflectionConfig, reflect, write_feedback
from plasticity.fit import fit_saturation
from plasticity.metrics import average_plasticity
from plasticity.pricing import PriceTable
from plasticity.psat import plasticity_to_saturation
from plasticity.significance import rise_p_value

SPLITS = ("train", "id", "ood")


@dataclass
class RunConfig:
    rounds: int = 5  # learning rounds T: checkpoints 0..T
    games: dict = field(default_factory=lambda: {"train": 40, "id": 40, "ood": 32})  # the paper's Hex counts
    train_id_levels: tuple = TRAIN_ID_LEVELS
    ood_levels: tuple = OOD_LEVELS
    episode: EpisodeConfig = field(default_factory=EpisodeConfig)
    reflection: ReflectionConfig = field(default_factory=ReflectionConfig)
    prices: PriceTable = field(default_factory=lambda: PriceTable(1.0, 5.0))  # learning cost, undiscounted
    billing: PriceTable | None = None  # what the provider charges; defaults to `prices`
    cap: float | None = None  # stop before any call once billed spend reaches this (USD)


def _opponent(levels, i):
    return AlphaBetaEngine(levels[i % len(levels)]).choose


def _play_split(model, split, openings, inventory, run_dir, t, ledger, cfg) -> list[tuple[GameResult, Path, Path]]:
    levels = cfg.ood_levels if split == "ood" else cfg.train_id_levels
    out = []
    for i, opening in enumerate(openings):
        colour = "red" if opening.actor == "X" else "blue"
        game_id = f"checkpoint_{t:03d}_{split}_g{i + 1:02d}_{colour}"
        base = run_dir / "games" / f"checkpoint_{t:03d}" / split
        session = base / "sessions" / game_id
        transcript = base / f"{game_id}.json"
        result = play_game(
            model, game_id, opening, _opponent(levels, i), inventory, session,
            hidden=[run_dir], ledger=ledger, checkpoint=t,
            phase="train" if split == "train" else "eval",
            cfg=cfg.episode, transcript_path=transcript,
        )
        out.append((result, transcript, session))
        print(f"  {game_id}: {result.end_reason}, score {result.score:g}")
    return out


def run_lineage(model: Model, run_dir: Path, cfg: RunConfig = RunConfig()) -> dict:
    run_dir.mkdir(parents=True, exist_ok=True)
    ledger = Ledger(cfg.prices, run_dir / "ledger.jsonl", billing=cfg.billing, cap=cfg.cap)
    banks = split_banks(cfg.games)
    inventory = empty_inventory(run_dir / "inventories" / "checkpoint_000")
    checkpoints: list[dict] = []
    try:
        _checkpoints(model, run_dir, cfg, ledger, banks, inventory, checkpoints)
    except BudgetExceeded as exc:
        print(f"stopped: {exc}")
        return _write(run_dir, model, cfg, checkpoints, ledger, stopped=str(exc))
    return _write(run_dir, model, cfg, checkpoints, ledger)


def _checkpoints(model, run_dir, cfg, ledger, banks, inventory, checkpoints) -> None:
    """Append one row per completed checkpoint; a row is added only when complete."""
    cumulative = 0.0
    for t in range(cfg.rounds + 1):
        print(f"checkpoint {t}")
        row = {"t": t, "cost_cumulative": cumulative}
        played = {}
        for split in SPLITS:
            played[split] = _play_split(model, split, banks[split], inventory, run_dir, t, ledger, cfg)
            row[split] = {"points": sum(r.score for r, _, _ in played[split]), "games": len(played[split]),
                          "unfinished": sum(r.end_reason != "finished" for r, _, _ in played[split])}
        if t < cfg.rounds:
            feedback = run_dir / "feedback" / f"checkpoint_{t:03d}"
            write_feedback(feedback, played["train"])
            outcome = reflect(model, inventory, feedback, run_dir / "reflect" / f"checkpoint_{t:03d}",
                              hidden=[run_dir], ledger=ledger, checkpoint=t, cfg=cfg.reflection)
            row["reflection"] = {"accepted": outcome.accepted, "attempts": outcome.attempts}
            inventory = commit(outcome.inventory, run_dir / "inventories" / f"checkpoint_{t + 1:03d}")
            cumulative += ledger.round_cost(t, "train") + ledger.round_cost(t, "reflect")
        checkpoints.append(row)
        _write(run_dir, model, cfg, checkpoints, ledger)


def plasticity_summary(checkpoints: list[dict], split: str = "id") -> dict:
    costs = np.array([c["cost_cumulative"] for c in checkpoints])
    points = np.array([c[split]["points"] for c in checkpoints])
    games = np.array([c[split]["games"] for c in checkpoints])
    scores = 100 * points / games
    summary = {"split": split, "scores": scores.tolist(), "costs": costs.tolist()}
    if len(costs) >= 2 and costs[-1] > 0:
        summary["average_plasticity"] = average_plasticity(scores, costs)
    if (costs > 0).sum() >= 2:
        fit = fit_saturation(costs, points, games)
        res = plasticity_to_saturation(fit, costs)
        summary.update({
            "fit": {"s0": fit.s0, "rise": fit.rise, "c50": fit.c50, "h": fit.h},
            "p_sat": res.value, "p_sat_kind": res.kind,
            "rise_p_value": rise_p_value(fit, points, games),
        })
    return summary


def _write(run_dir, model, cfg, checkpoints, ledger, stopped: str | None = None) -> dict:
    config = asdict(cfg)
    results = {
        "model": model.name,
        "config": config,
        "checkpoints": checkpoints,
        "stopped": stopped,
        "total_cost": ledger.total_cost(),
        "learning_cost": ledger.learning_cost(),
        "billed": ledger.billed(),
        "plasticity": plasticity_summary(checkpoints) if len(checkpoints) > 1 else None,
    }
    (run_dir / "results.json").write_text(json.dumps(results, indent=1, default=str))
    return results


def reset(run_dir: Path) -> None:
    """Remove a previous run with the same name."""
    if run_dir.exists():
        shutil.rmtree(run_dir)
