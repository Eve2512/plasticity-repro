# 10 Lineage `go_sonnet_reflect_high_rep2`: anthropic/claude-sonnet-5.5 on 5x5 Go

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 20, 'ood': 4}; openings: pooled.
Billed $17.95 (cap $18.10); learning cost priced the paper's way $25.43.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 62 % | 75 % | 50 % | 0 | 0 | 0 / 0 / 0 of 32 | accepted (1) |
| 1 | $1.63 | 50 % | 60 % | 50 % | 0 | 3 | 6 / 32 / 11 of 32 | accepted (1) |
| 2 | $5.61 | 88 % | 90 % | 75 % | 0 | 3 | 1 / 32 / 32 of 32 | accepted (1) |
| 3 | $8.04 | 88 % | 85 % | 50 % | 0 | 3 | 0 / 32 / 32 of 32 | accepted (1) |
| 4 | $10.06 | 88 % | 85 % | 50 % | 0 | 3 | 0 / 32 / 32 of 32 | accepted (1) |
| 5 | $12.04 | 100 % | 90 % | 50 % | 0 | 3 | 3 / 32 / 32 of 32 | accepted (1) |
| 6 | $13.59 | 88 % | 90 % | 50 % | 0 | 3 | 5 / 32 / 32 of 32 | accepted (1) |
| 7 | $15.76 | 88 % | 90 % | 50 % | 0 | 3 | 4 / 32 / 32 of 32 | accepted (1) |
| 8 | $17.80 | 88 % | 90 % | 50 % | 0 | 3 | 16 / 32 / 32 of 32 | accepted (2) |
| 9 | $20.71 | 88 % | 90 % | 50 % | 0 | 3 | 11 / 32 / 32 of 32 | accepted (2) |
| 10 | $24.12 | 100 % | 90 % | 50 % | 0 | 3 | 16 / 32 / 32 of 32 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 621.9 points per $1,000.
- Saturation fit (Eq. 4): S0 = 67.5 %, rise = 21.4 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 3798.2 points per $1,000 (saturated).
- Rise against a flat curve: p = 0.0189; it passes the p < 0.05 gate from report 03.
