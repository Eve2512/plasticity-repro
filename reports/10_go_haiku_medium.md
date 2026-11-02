# 10 Lineage `go_haiku_medium`: anthropic/claude-haiku-5.5 on 5x5 Go

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 20, 'ood': 4}; openings: pooled.
Billed $2.26 (cap $4.00); learning cost priced the paper's way $1.76.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 38 % | 40 % | 50 % | 0 | 0 | 0 / 0 / 0 of 32 | accepted (1) |
| 1 | $0.11 | 50 % | 45 % | 50 % | 0 | 3 | 25 / 4 / 2 of 32 | accepted (1) |
| 2 | $0.24 | 38 % | 35 % | 50 % | 0 | 3 | 15 / 6 / 6 of 32 | accepted (1) |
| 3 | $0.40 | 75 % | 40 % | 50 % | 0 | 4 | 11 / 4 / 5 of 32 | accepted (1) |
| 4 | $0.56 | 38 % | 65 % | 50 % | 1 | 4 | 12 / 5 / 5 of 32 | accepted (2) |
| 5 | $0.78 | 50 % | 65 % | 50 % | 0 | 5 | 17 / 4 / 2 of 32 | accepted (1) |
| 6 | $0.91 | 38 % | 45 % | 50 % | 0 | 5 | 17 / 6 / 5 of 32 | accepted (1) |
| 7 | $1.13 | 62 % | 40 % | 100 % | 1 | 5 | 9 / 0 / 0 of 32 | accepted (1) |
| 8 | $1.29 | 25 % | 45 % | 50 % | 0 | 5 | 13 / 2 / 1 of 32 | accepted (1) |
| 9 | $1.48 | 50 % | 55 % | 50 % | 0 | 6 | 18 / 0 / 0 of 32 | accepted (1) |
| 10 | $1.64 | 25 % | 60 % | 50 % | 0 | 6 | 8 / 0 / 0 of 32 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 12205.0 points per $1,000.
- Saturation fit (Eq. 4): S0 = 39.4 %, rise = 14.0 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 23265.7 points per $1,000 (saturated).
- Rise against a flat curve: p = 0.328; it does not pass the p < 0.05 gate from report 03.
