# 10 Lineage `go_sonnet_reflect_high`: anthropic/claude-sonnet-5.5 on 5x5 Go

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 20, 'ood': 4}; openings: pooled.
Billed $20.93 (cap $22.50); learning cost priced the paper's way $35.26.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 62 % | 55 % | 50 % | 0 | 0 | 0 / 0 / 0 of 32 | accepted (1) |
| 1 | $1.23 | 38 % | 30 % | 50 % | 6 | 2 | 32 / 32 / 28 of 32 | accepted (1) |
| 2 | $6.26 | 50 % | 30 % | 75 % | 0 | 2 | 32 / 32 / 32 of 32 | accepted (1) |
| 3 | $10.19 | 25 % | 35 % | 25 % | 2 | 2 | 31 / 32 / 32 of 32 | accepted (1) |
| 4 | $14.89 | 62 % | 35 % | 50 % | 0 | 2 | 32 / 32 / 32 of 32 | accepted (1) |
| 5 | $18.50 | 25 % | 60 % | 50 % | 0 | 2 | 31 / 32 / 32 of 32 | accepted (1) |
| 6 | $23.12 | 0 % | 20 % | 50 % | 20 | 2 | 0 / 32 / 32 of 32 | accepted (1) |
| 7 | $25.00 | 38 % | 15 % | 50 % | 1 | 2 | 0 / 32 / 32 of 32 | accepted (1) |
| 8 | $29.81 | 50 % | 15 % | 50 % | 0 | 2 | 1 / 32 / 32 of 32 | accepted (1) |
| 9 | $32.21 | 25 % | 15 % | 50 % | 0 | 2 | 0 / 32 / 32 of 32 | accepted (1) |
| 10 | $34.00 | 75 % | 50 % | 50 % | 0 | 2 | 2 / 32 / 32 of 32 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): -147.1 points per $1,000.
- Saturation fit (Eq. 4): S0 = 32.7 %, rise = 13.7 points, h = 9.36.
- P_sat (Eq. 5, paper rules): 0.0 points per $1,000 (to_date).
- Rise against a flat curve: p = 1; it does not pass the p < 0.05 gate from report 03.
