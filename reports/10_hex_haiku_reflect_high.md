# 10 Lineage `hex_haiku_reflect_high`: anthropic/claude-haiku-5.5 on 6x6 Hex

Checkpoints 0–7; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: pooled.
Billed $1.49 (cap $2.00); learning cost priced the paper's way $2.23.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 25 % | 33 % | 0 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 1 | $0.14 | 12 % | 42 % | 25 % | 0 | 4 | 23 / 24 / 20 of 24 | accepted (1) |
| 2 | $0.45 | 12 % | 42 % | 0 % | 0 | 4 | 22 / 23 / 23 of 24 | accepted (1) |
| 3 | $0.70 | 12 % | 33 % | 0 % | 0 | 4 | 20 / 23 / 23 of 24 | accepted (1) |
| 4 | $0.91 | 12 % | 42 % | 0 % | 0 | 4 | 24 / 24 / 24 of 24 | accepted (1) |
| 5 | $1.30 | 25 % | 33 % | 0 % | 0 | 4 | 24 / 24 / 24 of 24 | accepted (1) |
| 6 | $1.64 | 25 % | 33 % | 0 % | 0 | 5 | 21 / 23 / 22 of 24 | accepted (1) |
| 7 | $2.00 | 0 % | 42 % | 0 % | 0 | 6 | 20 / 22 / 22 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 4162.3 points per $1,000.
- Saturation fit (Eq. 4): S0 = 33.3 %, rise = 4.8 points, h = 7.97.
- P_sat (Eq. 5, paper rules): 0.0 points per $1,000 (no_rise).
- Rise against a flat curve: p = 0.991; it does not pass the p < 0.05 gate from report 03.
