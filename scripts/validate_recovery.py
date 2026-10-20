"""Check that the fit and P_sat recover known curves from noisy synthetic lineages.

Writes reports/01_parameter_recovery.md.
"""

from pathlib import Path

import numpy as np

from plasticity.fit import SaturationFit, fit_saturation
from plasticity.psat import plasticity_to_saturation
from plasticity.synthetic import cost_schedule, simulate_lineage

REPORT = Path(__file__).resolve().parent.parent / "reports" / "01_parameter_recovery.md"
SEEDS = 200
ROUNDS = 20

# (name, truth, cost per round in USD)
CASES = [
    ("fast learner", SaturationFit(0.20, 0.55, 150.0, 2.0, 0.0), 50.0),
    ("slow learner", SaturationFit(0.30, 0.40, 600.0, 1.5, 0.0), 50.0),
    ("no learning", SaturationFit(0.35, 0.00, 300.0, 1.0, 0.0), 50.0),
    ("late riser", SaturationFit(0.05, 0.60, 2500.0, 3.0, 0.0), 100.0),
]
GAME_COUNTS = (12, 20, 40)  # chess ID, Go ID, Hex ID games per checkpoint


def true_psat(truth, costs):
    return plasticity_to_saturation(truth, costs)


def main():
    lines = [
        "# 01 Parameter recovery on synthetic lineages",
        "",
        f"Each case draws {SEEDS} lineages of {ROUNDS} learning rounds from a known curve",
        "(Eq. 4), fits Eq. 4 by binomial maximum likelihood, and computes P_sat (Eq. 5).",
        "Game counts match held-out ID sets in the paper: 12 (Hard chess), 20 (Go), 40 (Hex).",
        "",
        "| Case | Games | True P_sat (kind) | Median estimate | 90 % of estimates | Same kind | Rise error (pp, median abs) |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, truth, per_round in CASES:
        costs = cost_schedule(ROUNDS, per_round, rng=np.random.default_rng(99))
        target = true_psat(truth, costs)
        for games in GAME_COUNTS:
            rng = np.random.default_rng(games)
            estimates, same_kind, rise_err = [], 0, []
            for _ in range(SEEDS):
                lin = simulate_lineage(truth, costs, games, rng)
                fit = fit_saturation(lin.costs, lin.points, games)
                res = plasticity_to_saturation(fit, costs)
                estimates.append(res.value)
                same_kind += res.kind == target.kind
                rise_err.append(abs(fit.rise - truth.rise) * 100)
            lo, med, hi = np.percentile(estimates, [5, 50, 95])
            lines.append(
                f"| {name} | {games} | {target.value:.1f} ({target.kind}) | {med:.1f} | "
                f"{lo:.1f} – {hi:.1f} | {100 * same_kind / SEEDS:.0f} % | {np.median(rise_err):.1f} |"
            )
        print(f"done: {name}")

    lines += [
        "",
        "P_sat is in score points per $1,000. \"Same kind\" is the share of lineages where the",
        "estimate used the same Eq. 5 rule as the truth (saturated, extrapolated, to date, no rise).",
        "",
    ]
    REPORT.write_text("\n".join(lines))
    print(f"wrote {REPORT.relative_to(REPORT.parent.parent)}")


if __name__ == "__main__":
    main()
