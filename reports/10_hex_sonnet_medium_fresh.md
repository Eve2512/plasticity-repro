# 10 Lineage `hex_sonnet_medium_fresh`: anthropic/claude-sonnet-5.5 on 6x6 Hex

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: fresh.
Billed $11.09 (cap $15.50); learning cost priced the paper's way $8.42.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 75 % | 42 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 1 | $0.51 | 75 % | 58 % | 25 % | 0 | 1 | 22 / 0 / 0 of 24 | accepted (1) |
| 2 | $1.26 | 62 % | 50 % | 25 % | 0 | 1 | 16 / 0 / 0 of 24 | accepted (1) |
| 3 | $1.99 | 88 % | 83 % | 25 % | 0 | 1 | 14 / 0 / 0 of 24 | accepted (1) |
| 4 | $2.73 | 88 % | 67 % | 0 % | 0 | 1 | 16 / 0 / 0 of 24 | accepted (1) |
| 5 | $3.45 | 88 % | 67 % | 25 % | 0 | 1 | 19 / 0 / 0 of 24 | accepted (1) |
| 6 | $4.31 | 100 % | 67 % | 25 % | 0 | 1 | 11 / 0 / 0 of 24 | accepted (1) |
| 7 | $5.10 | 88 % | 75 % | 25 % | 0 | 1 | 17 / 0 / 0 of 24 | accepted (1) |
| 8 | $5.91 | 75 % | 58 % | 25 % | 0 | 1 | 17 / 0 / 0 of 24 | accepted (1) |
| 9 | $6.68 | 75 % | 58 % | 25 % | 0 | 1 | 13 / 0 / 0 of 24 | accepted (1) |
| 10 | $7.47 | 88 % | 58 % | 25 % | 0 | 1 | 15 / 0 / 0 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 2230.9 points per $1,000.
- Saturation fit (Eq. 4): S0 = 49.1 %, rise = 17.5 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 8524.6 points per $1,000 (saturated).
- Rise against a flat curve: p = 0.411; it does not pass the p < 0.05 gate from report 03.
