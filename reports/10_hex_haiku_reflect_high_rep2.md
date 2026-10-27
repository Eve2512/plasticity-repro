# 10 Lineage `hex_haiku_reflect_high_rep2`: anthropic/claude-haiku-5.5 on 6x6 Hex

Checkpoints 0–7; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: pooled.
Billed $1.58 (cap $2.00); learning cost priced the paper's way $1.94.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 38 % | 50 % | 0 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 1 | $0.13 | 38 % | 58 % | 50 % | 0 | 4 | 19 / 21 / 10 of 24 | accepted (1) |
| 2 | $0.41 | 25 % | 42 % | 25 % | 0 | 4 | 21 / 0 / 6 of 24 | accepted (1) |
| 3 | $0.65 | 12 % | 50 % | 0 % | 0 | 4 | 20 / 0 / 18 of 24 | accepted (1) |
| 4 | $0.89 | 25 % | 50 % | 25 % | 0 | 4 | 19 / 0 / 14 of 24 | accepted (1) |
| 5 | $1.22 | 25 % | 33 % | 0 % | 0 | 4 | 17 / 1 / 13 of 24 | accepted (1) |
| 6 | $1.44 | 25 % | 42 % | 0 % | 0 | 5 | 23 / 0 / 21 of 24 | accepted (1) |
| 7 | $1.74 | 25 % | 33 % | 0 % | 0 | 5 | 24 / 0 / 21 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): -9600.6 points per $1,000.
- Saturation fit (Eq. 4): S0 = 44.8 %, rise = 2.3 points, h = 6.85.
- P_sat (Eq. 5, paper rules): 0.0 points per $1,000 (no_rise).
- Rise against a flat curve: p = 1; it does not pass the p < 0.05 gate from report 03.
