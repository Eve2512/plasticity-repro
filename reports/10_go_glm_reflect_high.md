# 10 Lineage `go_glm_reflect_high`: z-ai/glm-5.3 on 5x5 Go

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 20, 'ood': 4}; openings: pooled.
Billed $14.88 (cap $18.00); learning cost priced the paper's way $7.04.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 25 % | 10 % | 50 % | 17 | 0 | 0 / 1 / 0 of 32 | accepted (1) |
| 1 | $0.68 | 38 % | 60 % | 75 % | 0 | 4 | 25 / 31 / 31 of 32 | accepted (1) |
| 2 | $1.17 | 75 % | 60 % | 50 % | 1 | 4 | 25 / 30 / 30 of 32 | accepted (1) |
| 3 | $1.92 | 62 % | 55 % | 75 % | 0 | 4 | 28 / 32 / 32 of 32 | accepted (1) |
| 4 | $2.28 | 62 % | 50 % | 75 % | 1 | 4 | 26 / 30 / 30 of 32 | accepted (2) |
| 5 | $3.47 | 25 % | 25 % | 25 % | 0 | 4 | 28 / 32 / 32 of 32 | accepted (1) |
| 6 | $4.05 | 0 % | 35 % | 25 % | 1 | 4 | 26 / 31 / 31 of 32 | accepted (1) |
| 7 | $4.74 | 25 % | 35 % | 50 % | 0 | 4 | 23 / 31 / 31 of 32 | accepted (1) |
| 8 | $5.32 | 25 % | 35 % | 25 % | 2 | 4 | 25 / 31 / 31 of 32 | accepted (1) |
| 9 | $5.97 | 12 % | 50 % | 25 % | 1 | 4 | 27 / 32 / 32 of 32 | accepted (1) |
| 10 | $6.90 | 0 % | 25 % | 50 % | 1 | 4 | 20 / 29 / 29 of 32 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 2174.4 points per $1,000.
- Saturation fit (Eq. 4): S0 = 10.0 %, rise = 33.0 points, h = 7.66.
- P_sat (Eq. 5, paper rules): 48432.4 points per $1,000 (saturated).
- Rise against a flat curve: p = 0.0204; it passes the p < 0.05 gate from report 03.
