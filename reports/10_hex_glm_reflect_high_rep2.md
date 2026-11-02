# 10 Lineage `hex_glm_reflect_high_rep2`: z-ai/glm-5.3 on 6x6 Hex

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: pooled.
Billed $11.21 (cap $18.00); learning cost priced the paper's way $5.46.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 25 % | 0 % | 0 % | 18 | 0 | 0 / 2 / 0 of 24 | accepted (1) |
| 1 | $0.57 | 0 % | 25 % | 0 % | 0 | 4 | 20 / 22 / 22 of 24 | accepted (2) |
| 2 | $1.31 | 12 % | 8 % | 0 % | 2 | 5 | 23 / 23 / 23 of 24 | accepted (1) |
| 3 | $1.98 | 0 % | 8 % | 0 % | 4 | 5 | 19 / 24 / 24 of 24 | accepted (1) |
| 4 | $2.78 | 12 % | 17 % | 0 % | 0 | 5 | 22 / 24 / 24 of 24 | accepted (1) |
| 5 | $3.20 | 25 % | 17 % | 0 % | 0 | 5 | 20 / 23 / 24 of 24 | accepted (1) |
| 6 | $3.70 | 38 % | 8 % | 25 % | 0 | 5 | 18 / 24 / 24 of 24 | accepted (1) |
| 7 | $4.05 | 0 % | 0 % | 0 % | 0 | 5 | 20 / 24 / 24 of 24 | accepted (1) |
| 8 | $4.59 | 25 % | 25 % | 25 % | 0 | 5 | 20 / 24 / 24 of 24 | accepted (1) |
| 9 | $4.93 | 12 % | 17 % | 25 % | 0 | 5 | 21 / 24 / 24 of 24 | accepted (1) |
| 10 | $5.40 | 0 % | 17 % | 25 % | 0 | 5 | 19 / 23 / 23 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 3084.2 points per $1,000.
- Saturation fit (Eq. 4): S0 = 0.0 %, rise = 14.2 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 24657.5 points per $1,000 (saturated).
- Rise against a flat curve: p = 0.323; it does not pass the p < 0.05 gate from report 03.
