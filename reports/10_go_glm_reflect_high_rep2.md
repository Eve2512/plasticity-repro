# 10 Lineage `go_glm_reflect_high_rep2`: z-ai/glm-5.3 on 5x5 Go

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 20, 'ood': 4}; openings: pooled.
Billed $10.71 (cap $14.00); learning cost priced the paper's way $4.98.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 25 % | 15 % | 25 % | 12 | 0 | 0 / 1 / 0 of 32 | accepted (1) |
| 1 | $0.64 | 38 % | 55 % | 50 % | 5 | 4 | 28 / 28 / 28 of 32 | accepted (1) |
| 2 | $1.08 | 62 % | 55 % | 50 % | 0 | 4 | 24 / 27 / 29 of 32 | accepted (1) |
| 3 | $1.57 | 38 % | 55 % | 50 % | 1 | 4 | 25 / 30 / 30 of 32 | accepted (1) |
| 4 | $2.17 | 50 % | 55 % | 75 % | 1 | 4 | 25 / 31 / 31 of 32 | accepted (1) |
| 5 | $2.25 | 62 % | 60 % | 75 % | 1 | 4 | 25 / 29 / 29 of 32 | accepted (1) |
| 6 | $2.73 | 38 % | 40 % | 25 % | 0 | 4 | 26 / 30 / 31 of 32 | accepted (1) |
| 7 | $3.48 | 25 % | 45 % | 25 % | 1 | 4 | 22 / 30 / 30 of 32 | accepted (1) |
| 8 | $3.91 | 62 % | 60 % | 75 % | 1 | 4 | 22 / 30 / 30 of 32 | accepted (1) |
| 9 | $4.31 | 12 % | 50 % | 25 % | 1 | 4 | 24 / 32 / 32 of 32 | accepted (1) |
| 10 | $4.84 | 38 % | 60 % | 25 % | 0 | 4 | 24 / 28 / 28 of 32 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 9296.0 points per $1,000.
- Saturation fit (Eq. 4): S0 = 15.0 %, rise = 38.5 points, h = 7.11.
- P_sat (Eq. 5, paper rules): 59959.4 points per $1,000 (saturated).
- Rise against a flat curve: p = 0.00811; it passes the p < 0.05 gate from report 03.
