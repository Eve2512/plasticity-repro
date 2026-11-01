# 10 Lineage `lineage_a2`: anthropic/claude-sonnet-5.5 on 6x6 Hex

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: pooled.
Billed $13.74 (cap $14.50); learning cost priced the paper's way $12.46.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 88 % | 67 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (2) |
| 1 | $0.74 | 88 % | 50 % | 25 % | 0 | 1 | 24 / 0 / 0 of 24 | accepted (1) |
| 2 | $1.49 | 62 % | 67 % | 50 % | 0 | 2 | 22 / 22 / 22 of 24 | accepted (1) |
| 3 | $2.85 | 62 % | 67 % | 25 % | 0 | 2 | 21 / 21 / 21 of 24 | accepted (1) |
| 4 | $4.05 | 50 % | 67 % | 25 % | 0 | 2 | 19 / 19 / 19 of 24 | accepted (1) |
| 5 | $5.47 | 62 % | 58 % | 50 % | 0 | 2 | 18 / 18 / 18 of 24 | accepted (1) |
| 6 | $6.49 | 62 % | 67 % | 25 % | 0 | 2 | 21 / 21 / 21 of 24 | accepted (1) |
| 7 | $7.75 | 62 % | 50 % | 0 % | 0 | 2 | 16 / 16 / 16 of 24 | accepted (1) |
| 8 | $9.17 | 62 % | 58 % | 25 % | 0 | 2 | 17 / 17 / 17 of 24 | accepted (1) |
| 9 | $10.01 | 75 % | 58 % | 25 % | 0 | 2 | 19 / 19 / 19 of 24 | accepted (1) |
| 10 | $11.59 | 75 % | 75 % | 75 % | 0 | 2 | 15 / 15 / 15 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 719.1 points per $1,000.
- Saturation fit (Eq. 4): S0 = 60.6 %, rise = 39.4 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 2252.6 points per $1,000 (extrapolated).
- Rise against a flat curve: p = 0.87; it does not pass the p < 0.05 gate from report 03.
