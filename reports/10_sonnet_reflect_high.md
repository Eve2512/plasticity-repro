# 10 Lineage `sonnet_reflect_high`: anthropic/claude-sonnet-5.5 on 6x6 Hex

Checkpoints 0–7; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: pooled.
Billed $7.44 (cap $14.00); learning cost priced the paper's way $10.35.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 75 % | 50 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 1 | $1.33 | 25 % | 50 % | 25 % | 0 | 3 | 20 / 24 / 20 of 24 | accepted (1) |
| 2 | $4.11 | 88 % | 83 % | 50 % | 0 | 3 | 24 / 24 / 24 of 24 | accepted (1) |
| 3 | $5.79 | 100 % | 75 % | 75 % | 0 | 3 | 24 / 24 / 24 of 24 | accepted (1) |
| 4 | $6.72 | 100 % | 75 % | 75 % | 0 | 3 | 24 / 24 / 24 of 24 | accepted (1) |
| 5 | $7.67 | 100 % | 75 % | 75 % | 0 | 3 | 24 / 24 / 24 of 24 | accepted (1) |
| 6 | $8.62 | 100 % | 75 % | 75 % | 0 | 3 | 24 / 24 / 24 of 24 | accepted (1) |
| 7 | $9.52 | 100 % | 75 % | 75 % | 0 | 3 | 24 / 24 / 24 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 2626.5 points per $1,000.
- Saturation fit (Eq. 4): S0 = 49.7 %, rise = 26.7 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 6484.3 points per $1,000 (saturated).
- Rise against a flat curve: p = 0.13; it does not pass the p < 0.05 gate from report 03.
