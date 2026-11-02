# 10 Lineage `go_sonnet_medium_rep2`: anthropic/claude-sonnet-5.5 on 5x5 Go

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 20, 'ood': 4}; openings: pooled.
Billed $16.76 (cap $21.00); learning cost priced the paper's way $14.07.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 62 % | 55 % | 75 % | 0 | 0 | 0 / 0 / 0 of 32 | accepted (1) |
| 1 | $0.85 | 38 % | 65 % | 75 % | 0 | 2 | 12 / 0 / 0 of 32 | accepted (1) |
| 2 | $1.83 | 75 % | 60 % | 75 % | 0 | 2 | 13 / 0 / 2 of 32 | accepted (1) |
| 3 | $2.60 | 75 % | 60 % | 50 % | 0 | 3 | 26 / 2 / 2 of 32 | accepted (1) |
| 4 | $3.89 | 50 % | 65 % | 75 % | 0 | 3 | 27 / 2 / 2 of 32 | accepted (1) |
| 5 | $5.56 | 62 % | 65 % | 50 % | 0 | 3 | 22 / 2 / 2 of 32 | accepted (1) |
| 6 | $6.71 | 75 % | 65 % | 75 % | 0 | 3 | 28 / 0 / 0 of 32 | accepted (1) |
| 7 | $8.01 | 62 % | 55 % | 50 % | 0 | 3 | 25 / 4 / 4 of 32 | accepted (1) |
| 8 | $9.67 | 62 % | 65 % | 75 % | 0 | 3 | 25 / 2 / 2 of 32 | accepted (1) |
| 9 | $10.82 | 50 % | 70 % | 50 % | 0 | 3 | 30 / 5 / 5 of 32 | accepted (1) |
| 10 | $12.57 | 62 % | 65 % | 75 % | 0 | 3 | 27 / 3 / 2 of 32 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 795.3 points per $1,000.
- Saturation fit (Eq. 4): S0 = 55.1 %, rise = 33.6 points, h = 0.20.
- P_sat (Eq. 5, paper rules): 760.7 points per $1,000 (to_date).
- Rise against a flat curve: p = 0.893; it does not pass the p < 0.05 gate from report 03.
