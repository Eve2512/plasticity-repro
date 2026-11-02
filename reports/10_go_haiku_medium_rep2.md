# 10 Lineage `go_haiku_medium_rep2`: anthropic/claude-haiku-5.5 on 5x5 Go

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 20, 'ood': 4}; openings: pooled.
Billed $2.14 (cap $4.00); learning cost priced the paper's way $1.59.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 25 % | 55 % | 25 % | 1 | 0 | 0 / 0 / 0 of 32 | accepted (1) |
| 1 | $0.13 | 38 % | 55 % | 75 % | 2 | 3 | 18 / 0 / 0 of 32 | accepted (1) |
| 2 | $0.28 | 75 % | 50 % | 50 % | 0 | 3 | 23 / 0 / 0 of 32 | accepted (1) |
| 3 | $0.38 | 50 % | 60 % | 25 % | 0 | 3 | 23 / 0 / 0 of 32 | accepted (1) |
| 4 | $0.48 | 25 % | 30 % | 50 % | 2 | 3 | 22 / 0 / 0 of 32 | accepted (1) |
| 5 | $0.66 | 62 % | 50 % | 50 % | 0 | 4 | 22 / 0 / 0 of 32 | accepted (1) |
| 6 | $0.75 | 38 % | 50 % | 75 % | 0 | 5 | 21 / 0 / 0 of 32 | accepted (1) |
| 7 | $0.88 | 50 % | 50 % | 100 % | 0 | 5 | 21 / 0 / 0 of 32 | accepted (1) |
| 8 | $1.16 | 50 % | 50 % | 25 % | 0 | 7 | 12 / 0 / 0 of 32 | accepted (1) |
| 9 | $1.33 | 50 % | 60 % | 75 % | 1 | 7 | 15 / 0 / 0 of 32 | accepted (1) |
| 10 | $1.44 | 50 % | 60 % | 50 % | 1 | 7 | 18 / 0 / 0 of 32 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 3481.8 points per $1,000.
- Saturation fit (Eq. 4): S0 = 49.8 %, rise = 17.8 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 9416.0 points per $1,000 (extrapolated).
- Rise against a flat curve: p = 0.752; it does not pass the p < 0.05 gate from report 03.
