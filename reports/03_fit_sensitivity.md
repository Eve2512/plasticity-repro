# 03 Sensitivity of P_sat to rules and checkpoint noise

Synthetic lineages: 20 learning rounds of about $50 each, 200 lineages per cell.
P_sat is in score points per $1,000. Game counts: 12 = Hard chess held-out ID,
20 = Go, 40 = Hex.

## A. Rule choices

Same fitted lineages, different Eq. 5 rules. Cells: median P_sat (5th – 95th percentile).

| Rule | Fast, 12 games | Fast, 40 games | Slow, 12 games | Slow, 40 games |
|---|---|---|---|---|
| true value (paper rules) | 108 | 108 | 14 | 14 |
| paper (q 0.9, 10 pp, 3×) | 114 (41 – 311) | 105 (46 – 180) | 38 (20 – 129) | 30 (16 – 53) |
| q = 0.8 | 136 (48 – 362) | 139 (65 – 215) | 40 (18 – 130) | 30 (17 – 61) |
| q = 0.95 | 87 (31 – 291) | 83 (33 – 154) | 37 (18 – 129) | 29 (16 – 50) |
| min rise 5 pp | 114 (41 – 311) | 105 (46 – 180) | 38 (20 – 129) | 30 (16 – 53) |
| min rise 15 pp | 114 (41 – 311) | 105 (46 – 180) | 37 (0 – 129) | 30 (14 – 53) |
| extrapolate 2× | 114 (45 – 311) | 105 (51 – 180) | 39 (20 – 129) | 30 (20 – 53) |
| extrapolate 5× | 114 (24 – 311) | 105 (38 – 180) | 38 (17 – 129) | 29 (13 – 53) |

## B. False rises

True curve is flat (no learning, score 35 %). Share of lineages that still get P_sat > 0,
and the median P_sat among those. The last two columns add a likelihood-ratio test
against a flat curve (plasticity/significance.py); a gate that works should let
about 5 % through at p < 0.05.

| Games per checkpoint | min rise 5 pp | min rise 10 pp (paper) | min rise 20 pp | 10 pp + p < 0.05 | 10 pp + p < 0.01 | Median fitted h of false rises |
|---|---|---|---|---|---|---|
| 12 | 72 %, median 37 | 43 %, median 41 | 18 %, median 40 | 2 % | 0 % | 10.0 |
| 20 | 64 %, median 33 | 32 %, median 43 | 14 %, median 41 | 2 % | 0 % | 10.0 |
| 40 | 56 %, median 34 | 26 %, median 37 | 16 %, median 35 | 2 % | 0 % | 10.0 |

A large fitted h means a near-step curve: the fit explains a few noisy late
checkpoints as a sudden rise.

## C. Ranking stability with one lineage per model

Model A has true P_sat 73, model B 60 (same start, same rise, B is
25 % slower). Each pair of lineages is one replay of the paper's comparison.

| Games per checkpoint | B ranked above A | A or B gets P_sat = 0 |
|---|---|---|
| 12 | 46 % | 0 % |
| 20 | 46 % | 0 % |
| 40 | 37 % | 0 % |
