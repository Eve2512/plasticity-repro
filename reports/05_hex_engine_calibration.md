# 05 Hex engine calibration

12 openings from the training bank (half per colour). Score = share of games
won by the listed level. A stronger level should score higher against both
references.

| Nodes per move | Split | vs greedy 1-ply | vs weakest train level | Seconds per game |
|---|---|---|---|---|
| 3,000 | train / ID | 92 % | 50 % | 0.4 |
| 10,000 | train / ID | 92 % | 67 % | 0.9 |
| 30,000 | train / ID | 100 % | 83 % | 2.3 |
| 100,000 | train / ID | 100 % | 92 % | 6.1 |
| 1,000,000 | OOD | 100 % | 92 % | 48.5 |

Both references above are beaten almost every time by the stronger levels, so they
cannot separate them. Head to head against the strongest train/ID level
(100,000 nodes), same openings, both colours:

| OOD nodes per move | Score vs strongest train/ID level |
|---|---|
| 1,000,000 | 83 % |

The paper's budgets are 10k–1M nodes (train and ID) and 10M (OOD) in a native
engine. This pure-Python engine is scaled down to keep games under a minute.
