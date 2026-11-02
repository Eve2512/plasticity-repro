# 10 Lineage `hex_glm_reflect_high`: z-ai/glm-5.3 on 6x6 Hex

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: pooled.
Billed $11.25 (cap $18.00); learning cost priced the paper's way $5.48.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 25 % | 17 % | 0 % | 14 | 0 | 0 / 1 / 0 of 24 | accepted (1) |
| 1 | $0.81 | 50 % | 75 % | 25 % | 5 | 5 | 21 / 22 / 23 of 24 | accepted (1) |
| 2 | $1.35 | 0 % | 0 % | 0 % | 1 | 6 | 23 / 23 / 24 of 24 | accepted (1) |
| 3 | $1.77 | 0 % | 0 % | 0 % | 0 | 5 | 22 / 24 / 24 of 24 | accepted (1) |
| 4 | $2.38 | 12 % | 25 % | 0 % | 0 | 6 | 23 / 24 / 24 of 24 | accepted (1) |
| 5 | $2.92 | 12 % | 17 % | 0 % | 1 | 6 | 23 / 24 / 24 of 24 | accepted (1) |
| 6 | $3.45 | 12 % | 42 % | 0 % | 0 | 6 | 23 / 23 / 24 of 24 | accepted (1) |
| 7 | $3.95 | 12 % | 42 % | 0 % | 1 | 7 | 22 / 23 / 24 of 24 | accepted (1) |
| 8 | $4.40 | 12 % | 42 % | 0 % | 0 | 7 | 24 / 24 / 24 of 24 | accepted (1) |
| 9 | $4.90 | 38 % | 50 % | 25 % | 0 | 7 | 22 / 24 / 24 of 24 | accepted (1) |
| 10 | $5.38 | 62 % | 58 % | 25 % | 0 | 7 | 24 / 24 / 24 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 7740.2 points per $1,000.
- Saturation fit (Eq. 4): S0 = 22.5 %, rise = 33.1 points, h = 8.10.
- P_sat (Eq. 5, paper rules): 5806.9 points per $1,000 (saturated).
- Rise against a flat curve: p = 0.0312; it passes the p < 0.05 gate from report 03.
