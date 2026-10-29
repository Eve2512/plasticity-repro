# 10 Lineage `sonnet_nofeedback_high_rep2`: anthropic/claude-sonnet-5.5 on 6x6 Hex

Checkpoints 0–7; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: pooled.
Reflection saw no game records (limitation test 5: experience vs compute).
Billed $6.85 (cap $9.00); learning cost priced the paper's way $4.74.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 62 % | 50 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 1 | $0.53 | 75 % | 83 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 2 | $1.15 | 88 % | 75 % | 50 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 3 | $1.73 | 75 % | 58 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 4 | $2.32 | 50 % | 58 % | 0 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 5 | $2.84 | 62 % | 50 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 6 | $3.53 | 62 % | 83 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |
| 7 | $4.21 | 75 % | 42 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): -1979.0 points per $1,000.
- Saturation fit (Eq. 4): S0 = 50.0 %, rise = 14.3 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 27033.4 points per $1,000 (saturated).
- Rise against a flat curve: p = 0.828; it does not pass the p < 0.05 gate from report 03.
