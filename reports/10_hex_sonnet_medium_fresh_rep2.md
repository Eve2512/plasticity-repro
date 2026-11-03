# 10 Lineage `hex_sonnet_medium_fresh_rep2`: anthropic/claude-sonnet-5.5 on 6x6 Hex

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: fresh.
Billed $12.21 (cap $15.50); learning cost priced the paper's way $10.82.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 62 % | 50 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (2) |
| 1 | $0.79 | 88 % | 33 % | 50 % | 0 | 2 | 24 / 13 / 13 of 24 | accepted (1) |
| 2 | $1.61 | 25 % | 67 % | 25 % | 0 | 2 | 24 / 22 / 21 of 24 | accepted (1) |
| 3 | $2.63 | 50 % | 75 % | 25 % | 1 | 2 | 23 / 17 / 17 of 24 | accepted (1) |
| 4 | $3.63 | 25 % | 42 % | 25 % | 0 | 2 | 24 / 19 / 20 of 24 | accepted (1) |
| 5 | $4.59 | 38 % | 8 % | 50 % | 0 | 2 | 24 / 20 / 20 of 24 | accepted (1) |
| 6 | $5.75 | 62 % | 58 % | 25 % | 0 | 2 | 24 / 13 / 13 of 24 | accepted (1) |
| 7 | $6.59 | 50 % | 50 % | 25 % | 0 | 2 | 24 / 16 / 16 of 24 | accepted (1) |
| 8 | $8.00 | 75 % | 42 % | 50 % | 0 | 2 | 24 / 14 / 14 of 24 | accepted (1) |
| 9 | $8.93 | 38 % | 75 % | 25 % | 0 | 2 | 24 / 19 / 19 of 24 | accepted (1) |
| 10 | $9.95 | 38 % | 58 % | 25 % | 0 | 2 | 23 / 20 / 20 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 837.8 points per $1,000.
- Saturation fit (Eq. 4): S0 = 47.2 %, rise = 20.6 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 1752.4 points per $1,000 (extrapolated).
- Rise against a flat curve: p = 0.611; it does not pass the p < 0.05 gate from report 03.
