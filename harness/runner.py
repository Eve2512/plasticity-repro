"""Run one agent lineage (M, I_0) ... (M, I_T) on Hex or Go (Section 2.1, 3.1).

At each checkpoint the current inventory plays train, held-out ID and held-out
OOD games, each in a fresh episode. Go draws new training openings and seeds at
every checkpoint; held-out openings stay fixed. Reflection on the training games produces
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
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

import numpy as np

from envs.games import GAMES
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
RESUME_DEFAULTS = {"game": "hex", "reflection_feedback": "full"}  # for runs written before these keys existed
NO_FEEDBACK_NOTE = """\
No records of the training games are available in this round: no transcripts, \
moves, results or diagnostics. Your current inventory and the protocol files are \
here as usual. Improve the infrastructure for future games using your own reasoning.
"""


@dataclass
class RunConfig:
    rounds: int = 5  # learning rounds T: checkpoints 0..T
    games: dict = field(default_factory=lambda: {"train": 40, "id": 40, "ood": 32})  # the paper's Hex counts
    game: str = "hex"  # or "go"
    train_id_levels: tuple | None = None  # None: the game's levels (envs/games.py)
    ood_levels: tuple | None = None
    openings: str = "pooled"  # Hex also: "contested" (lineage A) or "legacy" (smoke run)
    episode: EpisodeConfig = field(default_factory=EpisodeConfig)
    reflection: ReflectionConfig = field(default_factory=ReflectionConfig)
    prices: PriceTable = field(default_factory=lambda: PriceTable(1.0, 5.0))  # learning cost, undiscounted
    billing: PriceTable | None = None  # what the provider charges; defaults to `prices`
    cap: float | None = None  # stop before any call once billed spend reaches this (USD)
    workers: int = 1  # games played at once (separate processes); needs a model factory
    reflection_feedback: str = "full"  # "none": reflection sees no game records (experience-vs-compute control)


@dataclass(frozen=True)
class _Job:
    split: str
    index: int
    game_id: str
    opening: object  # Opening
    opponent_level: int  # Hex: nodes per move; Go: GNU Go level
    session: Path
    transcript: Path


def _jobs(banks, t, run_dir, cfg) -> list[_Job]:
    jobs = []
    for split in SPLITS:
        levels = cfg.ood_levels if split == "ood" else cfg.train_id_levels
        base = run_dir / "games" / f"checkpoint_{t:03d}" / split
        for i, opening in enumerate(banks[split]):
            colour = GAMES[cfg.game].colours[opening.actor]
            game_id = f"checkpoint_{t:03d}_{split}_g{i + 1:02d}_{colour}"
            jobs.append(_Job(split, i, game_id, opening, levels[i % len(levels)],
                             base / "sessions" / game_id, base / f"{game_id}.json"))
    return jobs


def _play(model, job: _Job, inventory, run_dir, t, ledger, episode_cfg, game: str) -> GameResult:
    spec = GAMES[game]
    return play_game(
        model, job.game_id, job.opening, spec.opponent(job.opponent_level, job.opening), inventory, job.session,
        hidden=[run_dir], ledger=ledger, checkpoint=t,
        phase="train" if job.split == "train" else "eval",
        cfg=episode_cfg, transcript_path=job.transcript, spec=spec,
    )


def _worker(model_factory, job, inventory, run_dir, t, episode_cfg, game, prices, billing, remaining):
    """One game in a separate process; returns (result or None, ledger entries)."""
    ledger = Ledger(prices, billing=billing, cap=remaining)
    try:
        return _play(model_factory(), job, inventory, run_dir, t, ledger, episode_cfg, game), ledger.entries
    except BudgetExceeded:
        return None, ledger.entries


def _play_checkpoint(model, model_factory, jobs, inventory, run_dir, t, ledger, cfg) -> dict[str, list]:
    """Play every game of a checkpoint; results come back in job order per split."""
    results: dict[str, dict[int, GameResult]] = {s: {} for s in SPLITS}

    def record(job, result):
        results[job.split][job.index] = result
        print(f"  {job.game_id}: {result.end_reason}, score {result.score:g}", flush=True)

    if cfg.workers <= 1 or model_factory is None:
        for job in jobs:
            record(job, _play(model, job, inventory, run_dir, t, ledger, cfg.episode, cfg.game))
    else:
        from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
        from multiprocessing import get_context

        queue, pending, stop = list(jobs), {}, None
        with ProcessPoolExecutor(cfg.workers, mp_context=get_context("spawn")) as pool:
            while queue or pending:
                while queue and len(pending) < cfg.workers and stop is None:
                    try:
                        ledger.check_budget()
                    except BudgetExceeded as exc:
                        stop = exc
                        break
                    job = queue.pop(0)
                    remaining = None if ledger.cap is None else ledger.cap - ledger.billed()
                    fut = pool.submit(_worker, model_factory, job, inventory, run_dir, t,
                                      cfg.episode, cfg.game, ledger.prices, ledger.billing, remaining)
                    pending[fut] = job
                if not pending:
                    break
                done, _ = wait(pending, return_when=FIRST_COMPLETED)
                for fut in done:
                    job = pending.pop(fut)
                    result, entries = fut.result()
                    for e in entries:  # money spent in a worker always reaches the ledger
                        ledger.add_entry(e)
                    if result is None:
                        stop = stop or BudgetExceeded(f"spent ${ledger.billed():.2f} of the ${ledger.cap:.2f} cap")
                    else:
                        record(job, result)
        if stop is not None:
            raise stop
    by_job = {(j.split, j.index): j for j in jobs}
    return {
        s: [(results[s][i], by_job[(s, i)].transcript, by_job[(s, i)].session) for i in sorted(results[s])]
        for s in SPLITS
    }


def run_lineage(model: Model, run_dir: Path, cfg: RunConfig = RunConfig(), model_factory=None,
                resume: bool = False) -> dict:
    """Run (or, with `resume`, continue) a lineage.

    `model` plays and reflects; with cfg.workers > 1, games run in separate processes,
    each building its own model from the picklable `model_factory()`.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    spec = GAMES[cfg.game]
    cfg = replace(cfg, train_id_levels=tuple(cfg.train_id_levels or spec.train_id_levels),
                  ood_levels=tuple(cfg.ood_levels or spec.ood_levels))
    spec.banks(cfg.games, cfg.openings, 0)  # fail early when a bank file is missing
    checkpoints: list[dict] = []
    prior_billed = 0.0
    if resume and (run_dir / "results.json").exists():
        checkpoints, prior_billed = _prepare_resume(run_dir, cfg)
    elif resume:
        print("nothing to resume; starting a new run")
    ledger = Ledger(cfg.prices, run_dir / "ledger.jsonl", billing=cfg.billing, cap=cfg.cap, prior_billed=prior_billed)
    for e in Ledger.read(run_dir / "ledger.jsonl"):
        ledger.add_entry(e, write=False)
    start = len(checkpoints)
    if start > cfg.rounds:
        print("run already complete")
        return _write(run_dir, model, cfg, checkpoints, ledger)
    inventory = (run_dir / "inventories" / f"checkpoint_{start:03d}") if start else \
        empty_inventory(run_dir / "inventories" / "checkpoint_000")
    try:
        _checkpoints(model, model_factory, run_dir, cfg, ledger, inventory, checkpoints, start)
    except BudgetExceeded as exc:
        print(f"stopped: {exc}")
        return _write(run_dir, model, cfg, checkpoints, ledger, stopped=str(exc))
    return _write(run_dir, model, cfg, checkpoints, ledger)


def _prepare_resume(run_dir: Path, cfg: RunConfig) -> tuple[list[dict], float]:
    """Keep completed checkpoints; clear the unfinished one and set its spend aside."""
    prev = json.loads((run_dir / "results.json").read_text())
    for key in ("game", "rounds", "games", "openings", "train_id_levels", "ood_levels", "reflection_feedback"):
        old, new = prev["config"].get(key, RESUME_DEFAULTS.get(key)), asdict(cfg)[key]
        if json.loads(json.dumps(old)) != json.loads(json.dumps(new)):
            raise ValueError(f"cannot resume: {key} was {old}, now {new}")
    checkpoints = prev["checkpoints"]
    k = len(checkpoints)
    entries = Ledger.read(run_dir / "ledger.jsonl")
    keep = [e for e in entries if e.checkpoint < k]
    drop = [e for e in entries if e.checkpoint >= k]
    with (run_dir / "ledger_discarded.jsonl").open("a") as fh:
        for e in drop:
            fh.write(json.dumps(asdict(e)) + "\n")
    (run_dir / "ledger.jsonl").write_text("".join(json.dumps(asdict(e)) + "\n" for e in keep))
    for path in (run_dir / "games" / f"checkpoint_{k:03d}", run_dir / "feedback" / f"checkpoint_{k:03d}",
                 run_dir / "reflect" / f"checkpoint_{k:03d}", run_dir / "inventories" / f"checkpoint_{k + 1:03d}"):
        if path.exists():
            shutil.rmtree(path)
    if k and not (run_dir / "inventories" / f"checkpoint_{k:03d}").exists():
        raise ValueError(f"cannot resume: inventory for checkpoint {k} is missing")
    discarded = Ledger(cfg.prices, billing=cfg.billing)
    prior = sum(discarded.entry_cost(e) for e in Ledger.read(run_dir / "ledger_discarded.jsonl"))
    print(f"resuming at checkpoint {k}; ${prior:.2f} of discarded work counts toward the cap")
    return checkpoints, prior


def _checkpoints(model, model_factory, run_dir, cfg, ledger, inventory, checkpoints, start=0) -> None:
    """Append one row per completed checkpoint; a row is added only when complete."""
    cumulative = sum(ledger.round_cost(u, "train") + ledger.round_cost(u, "reflect") for u in range(start))
    for t in range(start, cfg.rounds + 1):
        print(f"checkpoint {t}", flush=True)
        row = {"t": t, "cost_cumulative": cumulative}
        banks = GAMES[cfg.game].banks(cfg.games, cfg.openings, t)
        played = _play_checkpoint(model, model_factory, _jobs(banks, t, run_dir, cfg), inventory, run_dir, t,
                                  ledger, cfg)
        for split in SPLITS:
            row[split] = {"points": sum(r.score for r, _, _ in played[split]), "games": len(played[split]),
                          "unfinished": sum(r.end_reason != "finished" for r, _, _ in played[split])}
        if t < cfg.rounds:
            feedback = run_dir / "feedback" / f"checkpoint_{t:03d}"
            if cfg.reflection_feedback == "none":  # training games still played and paid for
                feedback.mkdir(parents=True, exist_ok=True)
                (feedback / "README.md").write_text(NO_FEEDBACK_NOTE)
            else:
                write_feedback(feedback, played["train"], GAMES[cfg.game])
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
