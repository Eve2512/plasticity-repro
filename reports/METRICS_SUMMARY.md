# Phase 1 summary: the plasticity metric

Phase 1 rebuilds the paper's metric code (Eq. 2–5 and the parametric bootstrap)
and tests it on synthetic lineages whose true curve is known. No model API was
called. Details are in reports 01–04.

## Findings

| # | Finding | Evidence |
|---|---|---|
| 1 | The fit recovers a fast learner without bias, but one lineage gives a wide range. True P_sat 108; the middle 90 % of estimates is 41–311 with 12 games per checkpoint and 46–180 with 40. | [01](01_parameter_recovery.md) |
| 2 | Slow learners, whose 90 % point must be extrapolated, are overestimated about 2–3× (true 14, median estimate 30–38), and the estimate uses the right Eq. 5 rule only 16–22 % of the time. | [01](01_parameter_recovery.md) |
| 3 | With the paper's 10 pp rule alone, a model with **no learning** gets P_sat > 0 in 26–43 % of lineages (median about 40 points per $1,000). These fits are steps (h at its bound) that explain a few noisy checkpoints. A likelihood-ratio test against a flat curve lowers this to 2 %. The paper gives a p-value for NetHack but describes only the 10 pp rule for the board games. | [03 B](03_fit_sensitivity.md) |
| 4 | Two models whose true P_sat differs by 25 % swap ranks in 37–46 % of single-lineage replays. The paper's top two combined-curve values (298 and 233) differ by about 28 %; their curve averages three games, so its noise is lower than in this test, but a seed-replicated run would be needed to settle the ranking. | [03 C](03_fit_sensitivity.md) |
| 5 | The 90 % threshold moves P_sat by about ±25 % (q = 0.8 vs 0.95). The minimum-rise and extrapolation limits matter mostly near their edges. | [03 A](03_fit_sensitivity.md) |
| 6 | The price table alone can reverse a ranking: with identical learning per round, an input-heavy agent loses under undiscounted prices and wins by 2× under a cache discount. | [04](04_pricing_sensitivity.md) |
| 7 | 11 of 14 reported scores fit the stated game counts. Three window averages (Opus 5 66.4, GPT-5.6 Sol 36.9, Opus 4.8 Easy 19.0) cannot be produced by the stated counts. The NetHack P_sat arithmetic checks out. | [02](02_paper_number_checks.md) |

## What this means for the paper's claims

- The qualitative findings (models differ sharply; endpoint and efficiency diverge)
  are not challenged by phase 1. Large gaps, such as a rise from about 0 to 37 %
  against no rise, are well outside the noise shown here.
- Scalar P_sat values and close rankings need more than one lineage per model.
  The paper itself warns against reading small differences as rankings (Section 4);
  findings 3 and 4 give a size for that warning.
- A significance gate on the rise should be part of the definition of P_sat,
  not only of the NetHack analysis.

## Assumptions made where the paper is silent

- h is bounded to [0.2, 10] and C50 to [min cost / 100, max cost × 100].
- Bootstrap resamples are binomial; chess draws are not modelled separately.
- The likelihood-ratio test uses a chi-square reference with 3 degrees of freedom.

## Next: phase 2

Rebuild the 6×6 Hex harness from Appendix B and I, run a small smoke lineage
within a $5 API budget, and measure tokens per game before planning larger runs.
