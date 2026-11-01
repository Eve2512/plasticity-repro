# 10 Lineage `go_haiku_reflect_high`: anthropic/claude-haiku-5.5 on 5x5 Go

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 20, 'ood': 4}; openings: pooled.
Billed $2.97 (cap $3.30); learning cost priced the paper's way $3.36.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 38 % | 55 % | 100 % | 0 | 0 | 0 / 0 / 0 of 32 | accepted (1) |
| 1 | $0.16 | 25 % | 55 % | 50 % | 0 | 3 | 27 / 3 / 6 of 32 | accepted (1) |
| 2 | $0.37 | 38 % | 65 % | 75 % | 0 | 3 | 19 / 7 / 7 of 32 | accepted (1) |
| 3 | $0.61 | 75 % | 55 % | 50 % | 0 | 4 | 29 / 28 / 28 of 32 | accepted (1) |
| 4 | $0.97 | 38 % | 40 % | 50 % | 1 | 4 | 28 / 27 / 27 of 32 | accepted (1) |
| 5 | $1.36 | 25 % | 45 % | 75 % | 2 | 4 | 29 / 26 / 26 of 32 | accepted (1) |
| 6 | $1.69 | 50 % | 45 % | 50 % | 0 | 4 | 29 / 27 / 27 of 32 | accepted (1) |
| 7 | $2.06 | 38 % | 35 % | 75 % | 1 | 4 | 27 / 26 / 26 of 32 | accepted (1) |
| 8 | $2.40 | 38 % | 40 % | 50 % | 0 | 4 | 28 / 25 / 25 of 32 | accepted (1) |
| 9 | $2.80 | 62 % | 45 % | 75 % | 0 | 4 | 22 / 20 / 20 of 32 | accepted (1) |
| 10 | $3.13 | 25 % | 45 % | 75 % | 0 | 4 | 23 / 23 / 23 of 32 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): -3193.3 points per $1,000.
- Saturation fit (Eq. 4): S0 = 47.7 %, rise = 0.0 points, h = 5.28.
- P_sat (Eq. 5, paper rules): 0.0 points per $1,000 (no_rise).
- Rise against a flat curve: p = 1; it does not pass the p < 0.05 gate from report 03.
