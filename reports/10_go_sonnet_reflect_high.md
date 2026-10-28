# 10 Lineage `go_sonnet_reflect_high`: anthropic/claude-sonnet-5.5 on 5x5 Go

Checkpoints 0–7; games per checkpoint {'train': 8, 'id': 20, 'ood': 4}; openings: pooled.
Billed $13.01 (cap $13.00); learning cost priced the paper's way $24.66.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 62 % | 55 % | 50 % | 0 | 0 | 0 / 0 / 0 of 32 | accepted (1) |
| 1 | $1.23 | 38 % | 30 % | 50 % | 6 | 2 | 32 / 32 / 28 of 32 | accepted (1) |
| 2 | $6.26 | 50 % | 30 % | 75 % | 0 | 2 | 32 / 32 / 32 of 32 | accepted (1) |
| 3 | $10.19 | 25 % | 35 % | 25 % | 2 | 2 | 31 / 32 / 32 of 32 | accepted (1) |
| 4 | $14.89 | 62 % | 35 % | 50 % | 0 | 2 | 32 / 32 / 32 of 32 | accepted (1) |
| 5 | $18.50 | 25 % | 60 % | 50 % | 0 | 2 | 31 / 32 / 32 of 32 | accepted (1) |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 270.2 points per $1,000.
- Saturation fit (Eq. 4): S0 = 36.5 %, rise = 63.5 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 2330.9 points per $1,000 (extrapolated).
- Rise against a flat curve: p = 0.34; it does not pass the p < 0.05 gate from report 03.

Stopped early: spent $13.01 of the $13.00 cap.
