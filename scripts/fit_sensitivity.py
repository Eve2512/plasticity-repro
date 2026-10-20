"""Limitation tests for P_sat: rule choices, false rises, and ranking stability.

The paper runs one lineage per model and environment. These tests ask how much a
single lineage's P_sat moves under checkpoint noise and under the rule choices of
Section 2.2. Writes reports/03_fit_sensitivity.md.
"""

from pathlib import Path

import numpy as np

from plasticity.fit import SaturationFit, fit_saturation
from plasticity.psat import NO_RISE, plasticity_to_saturation
from plasticity.significance import rise_p_value
from plasticity.synthetic import cost_schedule, simulate_lineage

REPORT = Path(__file__).resolve().parent.parent / "reports" / "03_fit_sensitivity.md"
SEEDS = 200
ROUNDS = 20
COSTS = cost_schedule(ROUNDS, 50.0, rng=np.random.default_rng(99))

FAST = SaturationFit(0.20, 0.55, 150.0, 2.0, 0.0)
SLOW = SaturationFit(0.30, 0.40, 600.0, 1.5, 0.0)
FLAT = SaturationFit(0.35, 0.00, 300.0, 1.0, 0.0)
# Two learners whose true P_sat differ by about 25 %.
MODEL_A = SaturationFit(0.20, 0.50, 200.0, 2.0, 0.0)
MODEL_B = SaturationFit(0.20, 0.50, 250.0, 2.0, 0.0)

VARIANTS = {
    "paper (q 0.9, 10 pp, 3×)": {},
    "q = 0.8": {"q": 0.8},
    "q = 0.95": {"q": 0.95},
    "min rise 5 pp": {"min_rise_pp": 5.0},
    "min rise 15 pp": {"min_rise_pp": 15.0},
    "extrapolate 2×": {"extrapolate": 2.0},
    "extrapolate 5×": {"extrapolate": 5.0},
}


def fits(truth, games, seed):
    rng = np.random.default_rng(seed)
    return [
        fit_saturation(COSTS, simulate_lineage(truth, COSTS, games, rng).points, games)
        for _ in range(SEEDS)
    ]


def rule_table(lines):
    lines += [
        "## A. Rule choices",
        "",
        "Same fitted lineages, different Eq. 5 rules. Cells: median P_sat (5th – 95th percentile).",
        "",
        "| Rule | Fast, 12 games | Fast, 40 games | Slow, 12 games | Slow, 40 games |",
        "|---|---|---|---|---|",
    ]
    columns = [fits(t, g, seed=g) for t in (FAST, SLOW) for g in (12, 40)]
    truths = [FAST, FAST, SLOW, SLOW]
    true_row = [f"{plasticity_to_saturation(t, COSTS).value:.0f}" for t in truths]
    lines.append("| true value (paper rules) | " + " | ".join(true_row) + " |")
    for name, kwargs in VARIANTS.items():
        cells = []
        for col in columns:
            vals = [plasticity_to_saturation(f, COSTS, **kwargs).value for f in col]
            lo, med, hi = np.percentile(vals, [5, 50, 95])
            cells.append(f"{med:.0f} ({lo:.0f} – {hi:.0f})")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
        print(f"rules: {name}")
    lines.append("")


def false_rise_table(lines):
    lines += [
        "## B. False rises",
        "",
        "True curve is flat (no learning, score 35 %). Share of lineages that still get P_sat > 0,",
        "and the median P_sat among those. The last two columns add a likelihood-ratio test",
        "against a flat curve (plasticity/significance.py); a gate that works should let",
        "about 5 % through at p < 0.05.",
        "",
        "| Games per checkpoint | min rise 5 pp | min rise 10 pp (paper) | min rise 20 pp "
        "| 10 pp + p < 0.05 | 10 pp + p < 0.01 | Median fitted h of false rises |",
        "|---|---|---|---|---|---|---|",
    ]
    for games in (12, 20, 40):
        rng = np.random.default_rng(100 + games)
        lineages = [simulate_lineage(FLAT, COSTS, games, rng).points for _ in range(SEEDS)]
        col = [fit_saturation(COSTS, pts, games) for pts in lineages]
        pvals = [rise_p_value(f, pts, games) for f, pts in zip(col, lineages)]
        cells = []
        for min_rise in (5.0, 10.0, 20.0):
            res = [plasticity_to_saturation(f, COSTS, min_rise_pp=min_rise) for f in col]
            positive = [r.value for r in res if r.kind != NO_RISE]
            med = f", median {np.median(positive):.0f}" if positive else ""
            cells.append(f"{100 * len(positive) / SEEDS:.0f} %{med}")
        paper_rule = [plasticity_to_saturation(f, COSTS).kind != NO_RISE for f in col]
        for alpha in (0.05, 0.01):
            gated = sum(r and p < alpha for r, p in zip(paper_rule, pvals))
            cells.append(f"{100 * gated / SEEDS:.0f} %")
        false_h = [f.h for f, r in zip(col, paper_rule) if r]
        cells.append(f"{np.median(false_h):.1f}" if false_h else "–")
        lines.append(f"| {games} | " + " | ".join(cells) + " |")
        print(f"false rises: {games} games")
    lines += [
        "",
        "A large fitted h means a near-step curve: the fit explains a few noisy late",
        "checkpoints as a sudden rise.",
        "",
    ]


def ranking_table(lines):
    true_a = plasticity_to_saturation(MODEL_A, COSTS).value
    true_b = plasticity_to_saturation(MODEL_B, COSTS).value
    lines += [
        "## C. Ranking stability with one lineage per model",
        "",
        f"Model A has true P_sat {true_a:.0f}, model B {true_b:.0f} (same start, same rise, B is",
        "25 % slower). Each pair of lineages is one replay of the paper's comparison.",
        "",
        "| Games per checkpoint | B ranked above A | A or B gets P_sat = 0 |",
        "|---|---|---|",
    ]
    for games in (12, 20, 40):
        a = [plasticity_to_saturation(f, COSTS).value for f in fits(MODEL_A, games, seed=200 + games)]
        b = [plasticity_to_saturation(f, COSTS).value for f in fits(MODEL_B, games, seed=300 + games)]
        flips = np.mean(np.array(b) > np.array(a)) * 100
        zero = np.mean((np.array(a) == 0) | (np.array(b) == 0)) * 100
        lines.append(f"| {games} | {flips:.0f} % | {zero:.0f} % |")
        print(f"ranking: {games} games")
    lines.append("")


def main():
    lines = [
        "# 03 Sensitivity of P_sat to rules and checkpoint noise",
        "",
        f"Synthetic lineages: {ROUNDS} learning rounds of about $50 each, {SEEDS} lineages per cell.",
        "P_sat is in score points per $1,000. Game counts: 12 = Hard chess held-out ID,",
        "20 = Go, 40 = Hex.",
        "",
    ]
    rule_table(lines)
    false_rise_table(lines)
    ranking_table(lines)
    REPORT.write_text("\n".join(lines))
    print(f"wrote {REPORT.relative_to(REPORT.parent.parent)}")


if __name__ == "__main__":
    main()
