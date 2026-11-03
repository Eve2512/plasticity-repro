# 10 Lineage `hex_sonnet_high_fresh_rep2`: anthropic/claude-sonnet-5.5 on 6x6 Hex

Checkpoints 0–10; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: fresh.
Billed $11.04 (cap $12.00); learning cost priced the paper's way $14.51.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 38 % | 33 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 1 | $1.07 | 100 % | 67 % | 50 % | 0 | 2 | 24 / 24 / 17 of 24 | accepted (1) |
| 2 | $2.57 | 100 % | 83 % | 50 % | 0 | 2 | 24 / 24 / 24 of 24 | accepted (1) |
| 3 | $4.03 | 100 % | 83 % | 50 % | 0 | 2 | 24 / 24 / 24 of 24 | accepted (1) |
| 4 | $5.33 | 100 % | 75 % | 50 % | 0 | 2 | 24 / 24 / 24 of 24 | accepted (1) |
| 5 | $6.70 | 100 % | 83 % | 50 % | 0 | 2 | 24 / 24 / 24 of 24 | accepted (1) |
| 6 | $8.07 | 100 % | 92 % | 50 % | 0 | 2 | 24 / 24 / 24 of 24 | accepted (1) |
| 7 | $9.33 | 100 % | 83 % | 50 % | 0 | 2 | 24 / 24 / 24 of 24 | accepted (1) |
| 8 | $10.64 | 100 % | 92 % | 50 % | 0 | 2 | 24 / 24 / 24 of 24 | accepted (1) |
| 9 | $11.93 | 100 % | 83 % | 50 % | 1 | 2 | 24 / 24 / 24 of 24 | accepted (1) |
| 10 | $13.24 | 100 % | 100 % | 50 % | 0 | 2 | 24 / 24 / 24 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): 5035.1 points per $1,000.
- Saturation fit (Eq. 4): S0 = 33.4 %, rise = 66.6 points, h = 0.70.
- P_sat (Eq. 5, paper rules): 2529.2 points per $1,000 (extrapolated).
- Rise against a flat curve: p = 0.000586; it passes the p < 0.05 gate from report 03.
