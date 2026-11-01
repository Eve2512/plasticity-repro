# 10 Lineage `hex_haiku_medium_rep2`: anthropic/claude-haiku-5.5 on 6x6 Hex

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: pooled.
Billed $2.07 (cap $5.50); learning cost priced the paper's way $1.92.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 12 % | 42 % | 0 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 1 | $0.12 | 38 % | 50 % | 25 % | 0 | 3 | 19 / 23 / 13 of 24 | accepted (1) |
| 2 | $0.30 | 38 % | 58 % | 25 % | 0 | 3 | 20 / 21 / 10 of 24 | accepted (1) |
| 3 | $0.53 | 50 % | 58 % | 25 % | 0 | 3 | 17 / 20 / 16 of 24 | accepted (1) |
| 4 | $0.70 | 62 % | 33 % | 50 % | 0 | 3 | 18 / 19 / 13 of 24 | accepted (1) |
| 5 | $0.88 | 0 % | 50 % | 50 % | 0 | 4 | 15 / 21 / 15 of 24 | accepted (1) |
| 6 | $1.17 | 25 % | 17 % | 0 % | 0 | 4 | 11 / 14 / 9 of 24 | accepted (1) |
| 7 | $1.30 | 25 % | 42 % | 0 % | 0 | 4 | 11 / 11 / 10 of 24 | accepted (1) |
| 8 | $1.47 | 25 % | 25 % | 25 % | 0 | 4 | 15 / 17 / 14 of 24 | accepted (1) |
| 9 | $1.61 | 25 % | 50 % | 25 % | 0 | 4 | 15 / 16 / 12 of 24 | accepted (1) |
| 10 | $1.79 | 12 % | 25 % | 0 % | 0 | 4 | 5 / 6 / 6 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): -9316.9 points per $1,000.
- Saturation fit (Eq. 4): S0 = 40.9 %, rise = 0.2 points, h = 3.37.
- P_sat (Eq. 5, paper rules): 0.0 points per $1,000 (no_rise).
- Rise against a flat curve: p = 1; it does not pass the p < 0.05 gate from report 03.
