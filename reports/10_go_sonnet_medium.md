# 10 Lineage `go_sonnet_medium`: anthropic/claude-sonnet-5.5 on 5x5 Go

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 20, 'ood': 4}; openings: pooled.
Billed $15.69 (cap $21.00); learning cost priced the paper's way $13.08.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 50 % | 65 % | 50 % | 0 | 0 | 0 / 0 / 0 of 32 | accepted (2) |
| 1 | $1.01 | 38 % | 55 % | 75 % | 0 | 2 | 10 / 0 / 0 of 32 | accepted (1) |
| 2 | $2.28 | 100 % | 60 % | 50 % | 0 | 2 | 11 / 0 / 0 of 32 | accepted (1) |
| 3 | $3.05 | 88 % | 65 % | 75 % | 0 | 2 | 16 / 0 / 0 of 32 | accepted (1) |
| 4 | $4.03 | 50 % | 60 % | 75 % | 0 | 2 | 19 / 0 / 0 of 32 | accepted (1) |
| 5 | $5.61 | 62 % | 60 % | 75 % | 0 | 2 | 17 / 0 / 0 of 32 | accepted (1) |
| 6 | $6.73 | 62 % | 55 % | 75 % | 0 | 2 | 19 / 0 / 0 of 32 | accepted (1) |
| 7 | $7.89 | 75 % | 55 % | 75 % | 0 | 2 | 18 / 0 / 0 of 32 | accepted (1) |
| 8 | $9.24 | 62 % | 55 % | 50 % | 0 | 2 | 24 / 0 / 0 of 32 | accepted (1) |
| 9 | $10.28 | 62 % | 60 % | 50 % | 0 | 2 | 17 / 0 / 0 of 32 | accepted (1) |
| 10 | $11.48 | 50 % | 60 % | 50 % | 0 | 2 | 28 / 23 / 3 of 32 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): -435.6 points per $1,000.
- Saturation fit (Eq. 4): S0 = 59.1 %, rise = 15.3 points, h = 6.95.
- P_sat (Eq. 5, paper rules): 0.1 points per $1,000 (to_date).
- Rise against a flat curve: p = 1; it does not pass the p < 0.05 gate from report 03.
