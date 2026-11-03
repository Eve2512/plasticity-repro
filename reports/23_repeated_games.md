# 23 Repeated held-out games

Several lineages hold one held-out ID score for many checkpoints (e.g. `sonnet_reflect_high_rep2`
at 92 % for checkpoints 2–10). This report checks whether those are new games with the same result
or the same games played again, and what that means for the tests in earlier reports.

## Why games repeat

- Held-out ID openings are fixed: every checkpoint plays the same 12 (Hex) or 20 (Go) openings with
  the same colours, each against the same opponent level, and all Hex lineages on the pooled bank
  (except `haiku_r20`, 24 openings) and all Go lineages share one set. So two conditions can be
  compared opening by opening.
- The opponents are deterministic. Over all held-out games, 17,048 times the opponent met a
  position it had already answered (same game, level, position and actor move); it replied
  differently 0 times. (In training games: 6,734 repeated positions,
  6 different replies, all from GNU Go at level 5.)
- So when the actor plays the same moves, the whole game repeats.

## Repeats per lineage

"Exact repeats": held-out games whose full move record matches an earlier game of the same
lineage on the same opening. "Longest flat stretch": the longest run of checkpoints with one
held-out score; "same as previous checkpoint": games in that run, after its first checkpoint,
identical move for move to the same opening one checkpoint earlier.

| Lineage | Held-out games | Exact repeats | Longest flat stretch | Score | Tool code unchanged in it | Same as previous checkpoint |
|---|---|---|---|---|---|---|
| `lineage_a2` | 132 | 31 (23 %) | 2–4 | 8/12 = 67 % | yes | 2/24 |
| `sonnet_medium_rep2` | 132 | 39 (30 %) | 8–10 | 9/12 = 75 % | yes | 5/24 |
| `sonnet_reflect_high` | 132 | 85 (64 %) | 3–10 | 9/12 = 75 % | yes | 82/84 |
| `sonnet_reflect_high_rep2` | 132 | 92 (70 %) | 2–10 | 11/12 = 92 % | yes | 74/96 |
| `hex_haiku_medium_rep2` | 132 | 24 (18 %) | 2–3 | 7/12 = 58 % | no | 1/12 |
| `hex_haiku_reflect_high` | 132 | 75 (57 %) | 7–10 | 5/12 = 42 % | no | 21/36 |
| `hex_haiku_reflect_high_rep2` | 132 | 69 (52 %) | 3–4 | 6/12 = 50 % | no | 3/12 |
| `haiku_r20` | 504 | 132 (26 %) | 0–1 | 7/24 = 29 % | no | 4/24 |
| `hex_glm_reflect_high` | 132 | 56 (42 %) | 6–8 | 5/12 = 42 % | no | 23/24 |
| `hex_glm_reflect_high_rep2` | 132 | 20 (15 %) | 2–3 | 1/12 = 8 % | yes | 3/12 |
| `sonnet_nofeedback_high` | 96 | 31 (32 %) | 0–2 | 9/12 = 75 % | yes | 5/24 |
| `sonnet_nofeedback_high_rep2` | 96 | 25 (26 %) | 3–4 | 7/12 = 58 % | yes | 5/12 |
| `go_sonnet_medium` | 220 | 93 (42 %) | 6–8 | 11/20 = 55 % | yes | 16/40 |
| `go_sonnet_medium_rep2` | 220 | 93 (42 %) | 4–6 | 13/20 = 65 % | yes | 12/40 |
| `go_sonnet_reflect_high` | 220 | 49 (22 %) | 7–9 | 3/20 = 15 % | no | 37/40 |
| `go_sonnet_reflect_high_rep2` | 220 | 81 (37 %) | 5–10 | 18/20 = 90 % | no | 49/100 |
| `go_haiku_medium` | 220 | 52 (24 %) | 4–5 | 13/20 = 65 % | no | 4/20 |
| `go_haiku_medium_rep2` | 220 | 65 (30 %) | 5–8 | 10/20 = 50 % | no | 7/60 |
| `go_haiku_reflect_high` | 220 | 41 (19 %) | 0–1 | 11/20 = 55 % | no | 3/20 |
| `go_haiku_reflect_high_rep2` | 220 | 49 (22 %) | 2–3 | 10/20 = 50 % | no | 4/20 |
| `go_glm_reflect_high` | 220 | 63 (29 %) | 6–8 | 7/20 = 35 % | no | 18/40 |
| `go_glm_reflect_high_rep2` | 220 | 40 (18 %) | 1–4 | 11/20 = 55 % | no | 13/60 |

## Main tests, games against openings as the unit

Pooled: two-proportion z-test over all held-out games, as in the reports. Per opening: each
(opening, colour) scored by its mean over both lineages and the checkpoints compared; "better" /
"worse" count openings where B's mean is above / below A's; sign test (ties dropped) and exact
sign-flip permutation test on the per-opening differences, both two-sided.

| Comparison (A → B) | Report | Pooled A → B | Pooled p | Openings | Per opening A → B | Better / worse | Sign p | Permutation p |
|---|---|---|---|---|---|---|---|---|
| Hex Sonnet, high vs medium effort, checkpoints 4–10 | 12 | 65 % → 83 % | 0.00018 | 12 | 65 % → 83 % | 10 / 1 | 0.012 | 0.066 |
| Hex Sonnet high, checkpoints 0–3 → 4–10 | 12 | 73 % → 83 % | 0.044 | 12 | 73 % → 83 % | 9 / 1 | 0.021 | 0.051 |
| Hex Sonnet medium, checkpoints 0–3 → 4–10 | 12 | 59 % → 65 % | 0.32 | 12 | 59 % → 65 % | 4 / 5 | 1 | 0.38 |
| Hex, feedback vs no game records, checkpoints 3–7 | 18 | 56 % → 83 % | 3.7e-06 | 12 | 56 % → 83 % | 8 / 1 | 0.039 | 0.035 |
| Hex late, Sonnet vs Haiku | 15 | 40 % → 83 % | 2.9e-18 | 12 | 40 % → 83 % | 10 / 1 | 0.012 | 0.0029 |
| Hex late, Sonnet vs GLM | 21 | 24 % → 83 % | 1.9e-31 | 12 | 24 % → 83 % | 11 / 0 | 0.00098 | 0.00098 |
| Hex late, Haiku vs GLM | 21 | 24 % → 40 % | 0.0007 | 12 | 24 % → 40 % | 7 / 1 | 0.07 | 0.039 |
| Go late, Sonnet vs Haiku | 15 | 47 % → 60 % | 0.0012 | 20 | 47 % → 60 % | 13 / 5 | 0.096 | 0.089 |
| Go late, Sonnet vs GLM | 21 | 46 % → 60 % | 0.00049 | 20 | 46 % → 60 % | 11 / 6 | 0.33 | 0.059 |
| Go late, Sonnet high vs medium effort | 22 | 61 % → 60 % | 0.69 | 20 | 61 % → 60 % | 8 / 10 | 0.81 | 0.9 |

## Reading

- A flat held-out score in these runs is a replay, not a fresh measurement. The held-out openings are
  the same at every checkpoint and no held-out opponent ever answered the same position two ways, so
  once a lineage's tool code stops changing, each checkpoint plays the previous one's games again,
  most of them move for move. `sonnet_reflect_high` kept the same tool code from checkpoint 3 to 10
  and `sonnet_reflect_high_rep2` from checkpoint 2 to 10; at 75 % and 92 % their later checkpoints
  add almost no new information. In `go_sonnet_reflect_high_rep2` the tool code kept changing but
  every held-out result from checkpoint 6 on matched the checkpoint before.
- Repeats are not only a tool effect. Sonnet at medium effort on Go ran a saved tool in 1–6 % of
  games, yet 42 % of its held-out games repeat an earlier one move for move: on 5×5 the model itself
  often plays the same line from the same opening.
- The pooled z-tests of reports 12, 15, 21 and 22 count each game as independent, so repeats make
  them far too confident. With openings as the unit, the direction of every main result holds, but
  the evidence is much weaker. High against medium effort on Hex: better on 10 of 12 openings, worse
  on 1 (sign test p = 0.012, permutation p = 0.066), against p = 0.0002 pooled. High effort's
  early → late gain: 9 better, 1 worse (p = 0.021 / 0.051). Feedback against no game records
  (test 5): 8 better, 1 worse (p = 0.039 / 0.035); report 18's p = 2.5e-07 counted the same
  openings once per checkpoint. Sonnet against GLM on Hex survives (11 of 12, p = 0.001); Haiku
  against GLM on Hex is borderline (7 better, 1 worse, p = 0.07 / 0.039); the Go model gaps do not
  reach p < 0.05. These per-opening tests still pool the two lineages of a condition, so they do not
  account for lineage-to-lineage spread either.
- Twelve Hex openings cap what any test here can show: even 12 better and 0 worse gives a sign-test
  p of 0.0005. More openings per checkpoint, or new openings at each checkpoint, would add
  information; more checkpoints with a fixed tool would not.
- The same holds for the plasticity fits. A fit treats each checkpoint's score as a new noisy
  measurement; a replayed score is not one, so a long flat tail makes a curve look saturated with
  more certainty than the data have (`go_sonnet_reflect_high_rep2`, P_sat "saturated", p = 0.019).
