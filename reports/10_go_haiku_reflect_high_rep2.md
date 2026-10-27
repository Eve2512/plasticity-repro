# 10 Lineage `go_haiku_reflect_high_rep2`: anthropic/claude-haiku-5.5 on 5x5 Go

Checkpoints 0–7; games per checkpoint {'train': 8, 'id': 20, 'ood': 4}; openings: pooled.
Billed $1.93 (cap $2.50); learning cost priced the paper's way $2.06.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 62 % | 50 % | 75 % | 0 | 0 | 0 / 0 / 0 of 32 | accepted (1) |
| 1 | $0.12 | 12 % | 55 % | 50 % | 1 | 4 | 25 / 0 / 0 of 32 | accepted (1) |
| 2 | $0.38 | 38 % | 50 % | 75 % | 0 | 5 | 16 / 1 / 0 of 32 | accepted (1) |
| 3 | $0.61 | 38 % | 50 % | 50 % | 0 | 5 | 24 / 4 / 2 of 32 | accepted (1) |
| 4 | $0.88 | 38 % | 45 % | 50 % | 0 | 5 | 17 / 0 / 0 of 32 | accepted (1) |
| 5 | $1.17 | 25 % | 60 % | 50 % | 1 | 5 | 20 / 0 / 0 of 32 | accepted (1) |
| 6 | $1.50 | 25 % | 50 % | 50 % | 0 | 5 | 13 / 5 / 7 of 32 | accepted (1) |
| 7 | $1.82 | 50 % | 55 % | 75 % | 0 | 5 | 18 / 17 / 17 of 32 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 2746.0 points per $1,000.
- Saturation fit (Eq. 4): S0 = 50.3 %, rise = 4.3 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 0.0 points per $1,000 (no_rise).
- Rise against a flat curve: p = 0.974; it does not pass the p < 0.05 gate from report 03.
