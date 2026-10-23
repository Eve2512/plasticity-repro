# 11 Pooled opening banks: is held-out ID the same kind of game as train?

Difficulty: how many of the 3k, 10k and 30k opponents the 30k reference engine beats
from the opening (1–3, higher is easier; engines only, no model results used).
Mid engine: 10,000 nodes, not used to build the banks, against the runner's opponent per slot.

## Games option A uses (8 train, 12 ID, 4 OOD)

| Split | Games | Mean difficulty (red / blue) | Mid engine wins (red / blue) | Total |
|---|---|---|---|---|
| train | 8 | 2.00 / 2.00 | 2/4 / 2/4 | 4/8 |
| id | 12 | 2.17 / 2.00 | 5/6 / 2/6 | 7/12 |
| ood | 4 | 2.00 / 2.00 | 1/2 / 0/2 | 1/4 |

Train vs ID, mid engine: z = -0.37 (|z| < 2: no detectable difference).

## Full train and ID banks (40 each)

| Split | Games | Mean difficulty (red / blue) | Mid engine wins (red / blue) | Total |
|---|---|---|---|---|
| train | 40 | 2.35 / 2.30 | 13/20 / 13/20 | 26/40 |
| id | 40 | 2.45 / 2.30 | 17/20 / 12/20 | 29/40 |

Train vs ID, mid engine: z = -0.72 (|z| < 2: no detectable difference).

For comparison, lineage A's per-seed banks gave Sonnet 5.5 train 8/8 and ID 2/12 (z ≈ 3.7),
and the mid engine 29/40 train vs 22/40 ID on the full banks (report 09).
