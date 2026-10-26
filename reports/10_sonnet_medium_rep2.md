# 10 Lineage `sonnet_medium_rep2`: anthropic/claude-sonnet-5.5 on 6x6 Hex

Checkpoints 0–7; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: pooled.
Billed $9.57 (cap $10.00); learning cost priced the paper's way $9.26.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 88 % | 58 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (2) |
| 1 | $0.69 | 75 % | 33 % | 50 % | 0 | 1 | 18 / 0 / 0 of 24 | accepted (1) |
| 2 | $1.32 | 50 % | 67 % | 0 % | 0 | 1 | 13 / 0 / 0 of 24 | accepted (1) |
| 3 | $2.12 | 75 % | 67 % | 25 % | 0 | 1 | 14 / 0 / 0 of 24 | accepted (1) |
| 4 | $3.28 | 75 % | 58 % | 25 % | 0 | 1 | 17 / 0 / 0 of 24 | accepted (1) |
| 5 | $4.75 | 50 % | 67 % | 25 % | 0 | 1 | 19 / 0 / 0 of 24 | accepted (1) |
| 6 | $6.50 | 62 % | 75 % | 0 % | 0 | 1 | 17 / 0 / 0 of 24 | accepted (1) |
| 7 | $8.00 | 62 % | 58 % | 0 % | 0 | 1 | 18 / 0 / 0 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 0.0 points per $1,000.
- Saturation fit (Eq. 4): S0 = 45.9 %, rise = 19.6 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 13594.9 points per $1,000 (saturated).
- Rise against a flat curve: p = 0.436; it does not pass the p < 0.05 gate from report 03.
