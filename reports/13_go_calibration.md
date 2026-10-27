# 13 Go calibration: GNU Go levels, first-legal player, train vs held-out ID

Engines only, no model calls. Openings: data/go_openings_pooled.json (scripts/build_go_openings.py; rule in envs/go_openings.py). Margins are the actor's final margin after komi 9.5, scored by GNU Go's final_score (dead stones removed).

## 1. GNU Go levels from the 20 held-out ID openings (10 per colour)

| Actor level | Wins vs level 5 | Wins vs level 9 | Mean margin vs 5 | Seconds per game |
|---|---|---|---|---|
| 1 | 17/20 | 15/20 | +15.5 | 0.7 |
| 3 | 16/20 | 16/20 | +15.5 | 0.7 |
| 5 | 18/20 | 15/20 | +17.9 | 0.9 |
| 7 | 18/20 | 15/20 | +17.4 | 1.4 |
| 9 | 20/20 | 17/20 | +20.3 | 2.2 |
| 10 | 20/20 | 17/20 | +20.3 | 1.8 |

## 2. First-legal player (always the first legal action: A1, B1, ...)

Against the runner's opponent in every slot below: 0 wins in 80 games (mean margin -25.0).

## 3. Train vs held-out ID

Difficulty: GNU Go level 10's mean final margin against levels 5, 7 and 9 from the opening (higher is easier). Check player: GNU Go level 1, not used to build the pool, against the runner's opponent per slot.

### Run sizes: train 8 per checkpoint (pooled over checkpoints 0–7), ID 12, OOD 4

| Split | Games | Mean difficulty (black / white) | Level-1 check wins (black / white) | Total |
|---|---|---|---|---|
| train | 64 | 12.0 / 24.2 | 20/32 / 28/32 | 48/64 |
| id | 12 | 8.8 / 19.6 | 4/6 / 4/6 | 8/12 |
| ood | 4 | 7.5 / 17.8 | 1/2 / 1/2 | 2/4 |

Train vs ID, level-1 check player: z = 0.60 (|z| < 2: no detectable difference).

### Training draws above vs the full 20-game ID bank

| Split | Games | Mean difficulty (black / white) | Level-1 check wins (black / white) | Total |
|---|---|---|---|---|
| train | 64 | 12.0 / 24.2 | 20/32 / 28/32 | 48/64 |
| id | 20 | 11.5 / 24.0 | 7/10 / 8/10 | 15/20 |

Train vs ID, level-1 check player: z = 0.00 (|z| < 2: no detectable difference).

## Reading

- GNU Go levels 5–10 (and even 1 and 3) play almost alike on 5×5: from these openings every level
  wins most games against level 5 and level 9. The paper's level split (5–9 train/ID, 10 OOD) is kept,
  but OOD is barely harder than ID here; Go OOD results say little about a stronger opponent.
- Openings are contested by construction (the first-legal player loses, GNU Go 10 wins), so each game
  has room to improve. The bar is GNU Go strength: a model must play about as well as GNU Go to win.
- White openings score easier than Black ones (3 random plies leave Black's random first stone weak);
  results should be reported per colour.
- The full 20-game ID bank matches the training draws in difficulty; a 12-game prefix is a little
  harder. Go runs should use ID 20 (10 per colour), the paper's count.

