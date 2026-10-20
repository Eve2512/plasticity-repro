# 02 Consistency of reported numbers

Every check uses only numbers printed in the paper (v1) and the game counts in Table 2.

## Score values versus game counts

A score over N games (draws count half in chess) can only take a fixed set of values.

| Claim | Section | Reported | Games × checkpoints | Step | Nearest possible values | Consistent |
|---|---|---|---|---|---|---|
| Hard chess, Fable 5, held-out ID, checkpoint 0 | 3.2 | 37.5 | 12 × 1 | 4.167 | 33.333, 37.5, 41.667 | yes |
| Hard chess, Opus 5, held-out ID, checkpoint 0 | 3.2 | 25.0 | 12 × 1 | 4.167 | 20.833, 25, 29.167 | yes |
| Hard chess, Fable 5, held-out ID, mean of checkpoints 16–20 | 3.2 | 73.3 | 12 × 5 | 0.8333 | 72.5, 73.333, 74.167 | yes |
| Hard chess, Opus 5, held-out ID, mean of checkpoints 16–20 | 3.2 | 66.4 | 12 × 5 | 0.8333 | 65.833, 66.667, 67.5 | **no** |
| Hard chess, GPT-5.6 Sol, held-out ID, mean of checkpoints 16–20 | 3.2 | 36.9 | 12 × 5 | 0.8333 | 35.833, 36.667, 37.5 | **no** |
| Easy chess, Opus 4.8, held-out ID, late value | 3.2 | 19.0 | 16 × 5 | 0.625 | 18.125, 18.75, 19.375 | **no** |
| Go, Fable 5, held-out ID, checkpoint 0 | 3.3 | 20.0 | 20 × 1 | 5 | 15, 20, 25 | yes |
| Go, Fable 5, held-out ID, checkpoint 20 | 3.3 | 80.0 | 20 × 1 | 5 | 75, 80, 85 | yes |
| Go, Fable 5, held-out OOD, checkpoint 20 | 3.3 | 50.0 | 12 × 1 | 8.333 | 41.667, 50, 58.333 | yes |
| Hex, GPT-5.6 Sol, held-out ID, checkpoint 0 | 3.3 | 40.0 | 40 × 1 | 2.5 | 37.5, 40, 42.5 | yes |
| Hex, GPT-5.6 Sol, held-out ID, checkpoint 20 | 3.3 | 77.5 | 40 × 1 | 2.5 | 75, 77.5, 80 | yes |
| Hex, GPT-5.6 Sol, held-out OOD, checkpoint 0 | 3.3 | 28.1 | 32 × 1 | 3.125 | 25, 28.125, 31.25 | yes |
| Hex, GPT-5.6 Sol, held-out OOD, checkpoint 20 | 3.3 | 78.1 | 32 × 1 | 3.125 | 75, 78.125, 81.25 | yes |
| Go, Opus 4.8, held-out ID, checkpoint 0 | 3.5 | 40.0 | 20 × 1 | 5 | 35, 40, 45 | yes |

## NetHack P_sat arithmetic (Appendix C)

| Check | Arithmetic | Holds |
|---|---|---|
| P_sat = 1000 x fitted gain / cost | 1000 x 66.25 / 1072.73 = 61.758; reported 61.75 | yes |
| Fitted gain at C* is at least 90 % of the fitted rise | 66.25 >= 0.9 x 68.95 = 62.06 | yes |
| Raw early/late means fit the fitted gain | normalised means: checkpoints 0–2 = 28.6, 36–40 = 89.0, difference 60.4 vs fitted gain 66.25 | yes |

## Reading

11 of 14 score values match the stated game counts.
The values that do not match are window averages or late values:

- Hard chess, Opus 5, held-out ID, mean of checkpoints 16–20
- Hard chess, GPT-5.6 Sol, held-out ID, mean of checkpoints 16–20
- Easy chess, Opus 4.8, held-out ID, late value

Possible causes, none confirmed: some checkpoints had a different number of games
(for example games dropped after an infrastructure error), or the window differs
from checkpoints 16–20. The Easy chess value has no stated window, so that row tests
the most likely reading only. A mean of per-colour or per-opponent scores cannot
explain the gap, because every colour and opponent has the same number of games.
A mismatch of this size does not change the paper's conclusions, but it means the
curves cannot be rebuilt exactly from the text alone.
