# 10 Lineage `haiku_r20`: anthropic/claude-haiku-5.5 on 6x6 Hex

Checkpoints 0–20; games per checkpoint {'train': 20, 'id': 24, 'ood': 8}; openings: pooled.
Billed $7.86 (cap $9.00); learning cost priced the paper's way $9.05.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 15 % | 29 % | 0 % | 0 | 0 | 0 / 0 / 0 of 52 | accepted (1) |
| 1 | $0.26 | 30 % | 29 % | 0 % | 0 | 2 | 49 / 49 / 36 of 52 | accepted (1) |
| 2 | $0.78 | 25 % | 38 % | 25 % | 0 | 2 | 46 / 48 / 46 of 52 | accepted (1) |
| 3 | $1.20 | 30 % | 42 % | 0 % | 0 | 2 | 49 / 51 / 49 of 52 | accepted (1) |
| 4 | $1.64 | 10 % | 38 % | 0 % | 0 | 2 | 49 / 52 / 49 of 52 | accepted (1) |
| 5 | $2.06 | 15 % | 17 % | 0 % | 0 | 2 | 35 / 0 / 17 of 52 | accepted (1) |
| 6 | $2.46 | 15 % | 25 % | 12 % | 0 | 2 | 41 / 0 / 28 of 52 | accepted (1) |
| 7 | $3.08 | 5 % | 33 % | 0 % | 0 | 2 | 34 / 0 / 22 of 52 | accepted (1) |
| 8 | $3.56 | 10 % | 29 % | 0 % | 0 | 2 | 43 / 0 / 28 of 52 | accepted (1) |
| 9 | $4.19 | 20 % | 42 % | 0 % | 0 | 2 | 35 / 0 / 18 of 52 | accepted (1) |
| 10 | $4.83 | 25 % | 29 % | 0 % | 0 | 2 | 30 / 1 / 4 of 52 | accepted (1) |
| 11 | $5.21 | 30 % | 33 % | 12 % | 0 | 3 | 31 / 0 / 6 of 52 | accepted (1) |
| 12 | $5.61 | 25 % | 46 % | 38 % | 0 | 3 | 29 / 0 / 2 of 52 | accepted (1) |
| 13 | $6.00 | 30 % | 42 % | 12 % | 0 | 3 | 30 / 0 / 5 of 52 | accepted (1) |
| 14 | $6.41 | 20 % | 12 % | 0 % | 0 | 3 | 39 / 0 / 22 of 52 | accepted (1) |
| 15 | $7.03 | 20 % | 8 % | 0 % | 0 | 4 | 41 / 0 / 6 of 52 | accepted (1) |
| 16 | $7.33 | 35 % | 33 % | 0 % | 0 | 4 | 39 / 1 / 4 of 52 | accepted (1) |
| 17 | $7.65 | 25 % | 21 % | 12 % | 0 | 4 | 39 / 0 / 8 of 52 | accepted (1) |
| 18 | $8.15 | 20 % | 46 % | 0 % | 0 | 4 | 37 / 0 / 8 of 52 | accepted (1) |
| 19 | $8.49 | 25 % | 38 % | 0 % | 0 | 4 | 30 / 0 / 4 of 52 | accepted (1) |
| 20 | $8.81 | 30 % | 33 % | 12 % | 0 | 4 | 36 / 0 / 2 of 52 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 472.8 points per $1,000.
- Saturation fit (Eq. 4): S0 = 30.9 %, rise = 69.1 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 4380.9 points per $1,000 (extrapolated).
- Rise against a flat curve: p = 0.941; it does not pass the p < 0.05 gate from report 03.
