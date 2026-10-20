# 01 Parameter recovery on synthetic lineages

Each case draws 200 lineages of 20 learning rounds from a known curve
(Eq. 4), fits Eq. 4 by binomial maximum likelihood, and computes P_sat (Eq. 5).
Game counts match held-out ID sets in the paper: 12 (Hard chess), 20 (Go), 40 (Hex).

| Case | Games | True P_sat (kind) | Median estimate | 90 % of estimates | Same kind | Rise error (pp, median abs) |
|---|---|---|---|---|---|---|
| fast learner | 12 | 107.9 (saturated) | 113.9 | 41.2 – 310.8 | 78 % | 11.9 |
| fast learner | 20 | 107.9 (saturated) | 113.7 | 44.5 – 233.0 | 82 % | 7.6 |
| fast learner | 40 | 107.9 (saturated) | 105.3 | 46.0 – 180.2 | 89 % | 5.2 |
| slow learner | 12 | 13.9 (extrapolated) | 37.9 | 19.7 – 129.4 | 16 % | 19.9 |
| slow learner | 20 | 13.9 (extrapolated) | 32.2 | 18.4 – 74.6 | 20 % | 17.2 |
| slow learner | 40 | 13.9 (extrapolated) | 29.8 | 16.3 – 52.7 | 22 % | 17.2 |
| no learning | 12 | 0.0 (no_rise) | 0.0 | 0.0 – 280.2 | 49 % | 11.6 |
| no learning | 20 | 0.0 (no_rise) | 0.0 | 0.0 – 114.2 | 66 % | 7.5 |
| no learning | 40 | 0.0 (no_rise) | 0.0 | 0.0 – 41.8 | 77 % | 6.0 |
| late riser | 12 | 10.4 (extrapolated) | 10.9 | 0.0 – 28.6 | 30 % | 37.9 |
| late riser | 20 | 10.4 (extrapolated) | 10.5 | 3.9 – 27.8 | 45 % | 36.8 |
| late riser | 40 | 10.4 (extrapolated) | 9.9 | 6.0 – 21.8 | 48 % | 35.9 |

P_sat is in score points per $1,000. "Same kind" is the share of lineages where the
estimate used the same Eq. 5 rule as the truth (saturated, extrapolated, to date, no rise).
