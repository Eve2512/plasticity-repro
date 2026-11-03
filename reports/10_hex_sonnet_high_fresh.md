# 10 Lineage `hex_sonnet_high_fresh`: anthropic/claude-sonnet-5.5 on 6x6 Hex

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: fresh.
Billed $10.60 (cap $12.00); learning cost priced the paper's way $12.25.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 75 % | 58 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 1 | $1.03 | 100 % | 83 % | 100 % | 0 | 2 | 24 / 24 / 21 of 24 | accepted (1) |
| 2 | $2.46 | 100 % | 75 % | 75 % | 0 | 2 | 24 / 24 / 22 of 24 | accepted (1) |
| 3 | $3.99 | 100 % | 92 % | 100 % | 0 | 2 | 24 / 24 / 22 of 24 | accepted (1) |
| 4 | $5.11 | 100 % | 75 % | 100 % | 0 | 2 | 24 / 24 / 23 of 24 | accepted (1) |
| 5 | $6.47 | 88 % | 75 % | 100 % | 0 | 2 | 24 / 24 / 23 of 24 | accepted (1) |
| 6 | $8.66 | 100 % | 92 % | 75 % | 0 | 2 | 24 / 24 / 24 of 24 | accepted (1) |
| 7 | $9.40 | 100 % | 92 % | 75 % | 0 | 2 | 24 / 24 / 24 of 24 | accepted (1) |
| 8 | $10.12 | 100 % | 92 % | 75 % | 0 | 2 | 24 / 24 / 24 of 24 | accepted (1) |
| 9 | $10.84 | 100 % | 92 % | 75 % | 0 | 2 | 24 / 24 / 24 of 24 | accepted (1) |
| 10 | $11.56 | 100 % | 100 % | 75 % | 0 | 2 | 24 / 24 / 24 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 3603.4 points per $1,000.
- Saturation fit (Eq. 4): S0 = 76.1 %, rise = 23.9 points, h = 6.66.
- P_sat (Eq. 5, paper rules): 1781.7 points per $1,000 (extrapolated).
- Rise against a flat curve: p = 0.0462; it passes the p < 0.05 gate from report 03.
