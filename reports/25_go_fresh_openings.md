# 25 Go model gaps on fresh held-out openings

Each Go lineage at reflection effort high plays 40 held-out openings no run has played (20 per colour),
with its final inventory (checkpoint 10) and the run's settings. The 40 come from the same contested
pool as the original bank, with the same median difficulty per colour; none is in the symmetry class
(rotations and reflections of the 5×5 board) of an original held-out opening, and no two share one.
5×5 Go has few distinct 2-move openings for Black, so 10 of the 20 Black openings are rotations or
reflections of training openings; the last table leaves them out.

## Per lineage

| Lineage | Model | Fresh openings | Lost to limits | Original 20 openings, checkpoint 10 |
|---|---|---|---|---|
| `go_sonnet_reflect_high` | Sonnet 5.5 | 20/40 = 50 % | 0 | 10/20 = 50 % |
| `go_sonnet_reflect_high_rep2` | Sonnet 5.5 | 38/40 = 95 % | 0 | 18/20 = 90 % |
| `go_haiku_reflect_high` | Haiku 5.5 | 27/40 = 68 % | 3 | 9/20 = 45 % |
| `go_haiku_reflect_high_rep2` | Haiku 5.5 | 23/40 = 58 % | 0 | 11/20 = 55 % |
| `go_glm_reflect_high` | GLM 5.3 | 7/40 = 18 % | 5 | 5/20 = 25 % |
| `go_glm_reflect_high_rep2` | GLM 5.3 | 21/40 = 52 % | 2 | 12/20 = 60 % |

## All 40 fresh openings

| Comparison (A vs B) | Openings | A | B | B better / worse | Sign test p | Permutation p |
|---|---|---|---|---|---|---|
| Sonnet 5.5 vs Haiku 5.5 | 40 | 62 % | 72 % | 13 / 8 | 0.38 | 0.25 |
| Sonnet 5.5 vs GLM 5.3 | 40 | 35 % | 72 % | 24 / 1 | 1.5e-06 | 1e-05 |
| Haiku 5.5 vs GLM 5.3 | 40 | 35 % | 62 % | 18 / 3 | 0.0015 | 0.00062 |

## Leaving out the 10 Black openings symmetric to training openings

| Comparison (A vs B) | Openings | A | B | B better / worse | Sign test p | Permutation p |
|---|---|---|---|---|---|---|
| Sonnet 5.5 vs Haiku 5.5 | 30 | 63 % | 75 % | 9 / 4 | 0.27 | 0.17 |
| Sonnet 5.5 vs GLM 5.3 | 30 | 38 % | 75 % | 18 / 1 | 7.6e-05 | 0.0001 |
| Haiku 5.5 vs GLM 5.3 | 30 | 38 % | 63 % | 13 / 3 | 0.021 | 0.0084 |

## Reading

- Both gaps to GLM hold on new openings. Sonnet beats GLM on 24 of 40 openings and loses on 1
  (sign test p = 1.5e-06); Haiku beats GLM on 18 and loses on 3 (p = 0.0015). With the original
  20 openings, replayed across checkpoints 3–10, Sonnet against GLM was 11 better and 6 worse
  (p = 0.33) and Haiku against GLM was not tested on Go (report 23). Both gaps stay below 0.05
  without the 10 Black openings that are rotations or reflections of training openings.
- Sonnet against Haiku is not established: 72 % against 62 %, 13 openings better and 8 worse
  (p = 0.38). The two Sonnet lineages are far apart, as on the original openings: 95 % for
  `go_sonnet_reflect_high_rep2` and 50 % for `go_sonnet_reflect_high`, below both Haiku lineages
  (68 % and 58 %). Which Sonnet lineage one ran decides the comparison; two lineages per model
  cannot say what Sonnet does on average.
- The fresh openings reproduce each final inventory's level on the original openings within
  about 10 points, except `go_haiku_reflect_high` (68 % against 45 %). A checkpoint-10 score on 20
  openings carries about ±11 points of sampling error on its own, so the original Go endpoints
  were not misleading; the problem in report 23 was too few openings for a test, not wrong levels.
- These are endpoints, not learning curves: the final inventories play once. On Go no model's
  pooled held-out ID rose from early to late checkpoints (reports 15, 21, 22), so there was no Go
  learning curve to re-test.
- GLM lost 7 of its 80 games to the time and call limits, Haiku 3 of 80, Sonnet none.
