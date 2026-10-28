# 15 Sonnet 5.5 vs Haiku 5.5 on Hex and Go (reflection effort high)

Actor effort medium, reflection effort high, two lineages per cell. Hex: 6×6, pooled openings,
8 / 12 / 4 games per checkpoint (train / ID / OOD), opponents 3k–100k nodes. Go: 5×5, pooled openings,
8 / 20 / 4, GNU Go levels 5–9 (ID) and 10 (OOD), training openings redrawn every checkpoint (report 13).
Early = checkpoints 0–2 (checkpoint 0 is before any reflection); late = checkpoint 3 onward.

## Held-out ID, early → late

| Game | Model | Lineages (checkpoints done) | Early | Late | Change | z | p |
|---|---|---|---|---|---|---|---|
| Hex | Sonnet 5.5 | `sonnet_reflect_high` (8), `sonnet_reflect_high_rep2` (8) | 50/72 = 69 % | 100/120 = 83 % | +14 pp | 2.25 | 0.024 |
| Hex | Haiku 5.5 | `hex_haiku_reflect_high` (8), `hex_haiku_reflect_high_rep2` (8) | 32/72 = 44 % | 47/120 = 39 % | -5 pp | -0.72 | 0.47 |
| Go | Sonnet 5.5 | `go_sonnet_reflect_high` (6), `go_sonnet_reflect_high_rep2` (8) | 68/120 = 57 % | 114/160 = 71 % | +15 pp | 2.53 | 0.011 |
| Go | Haiku 5.5 | `go_haiku_reflect_high` (8), `go_haiku_reflect_high_rep2` (8) | 66/120 = 55 % | 96/200 = 48 % | -7 pp | -1.21 | 0.23 |

## Sonnet vs Haiku, late checkpoints

| Game | Sonnet late | Haiku late | z | p |
|---|---|---|---|---|
| Hex | 100/120 = 83 % | 47/120 = 39 % | 7.02 | 2.2e-12 |
| Go | 114/160 = 71 % | 96/200 = 48 % | 4.45 | 8.7e-06 |

## Per colour (first player: Hex red, Go Black; second: Hex blue, Go White)

| Game | Model | Colour | Early | Late |
|---|---|---|---|---|
| Hex | Sonnet 5.5 | first player | 29/36 = 81 % | 55/60 = 92 % |
| Hex | Sonnet 5.5 | second player | 21/36 = 58 % | 45/60 = 75 % |
| Hex | Haiku 5.5 | first player | 18/36 = 50 % | 32/60 = 53 % |
| Hex | Haiku 5.5 | second player | 14/36 = 39 % | 15/60 = 25 % |
| Go | Sonnet 5.5 | first player | 31/60 = 52 % | 63/80 = 79 % |
| Go | Sonnet 5.5 | second player | 37/60 = 62 % | 51/80 = 64 % |
| Go | Haiku 5.5 | first player | 28/60 = 47 % | 51/100 = 51 % |
| Go | Haiku 5.5 | second player | 38/60 = 63 % | 45/100 = 45 % |

## Per lineage

| Lineage | Held-out ID per checkpoint (%) | Fit rise (pp) | p | P_sat | Reflection calls | Code revisions | Games calling a saved tool | Billed | Stopped |
|---|---|---|---|---|---|---|---|---|---|
| `sonnet_reflect_high` | 50, 50, 83, 75, 75, 75, 75, 75 | 26.7 | 0.13 | 6484 (saturated) | 10.3 | 3 | 85 % | $7.44 | – |
| `sonnet_reflect_high_rep2` | 75, 67, 92, 92, 92, 92, 92, 92 | 20.9 | 0.12 | 5428 (saturated) | 8.0 | 2 | 88 % | $7.77 | – |
| `hex_haiku_reflect_high` | 33, 42, 42, 33, 42, 33, 33, 42 | 4.8 | 0.99 | 0 (no_rise) | 22.0 | 6 | 82 % | $1.49 | – |
| `hex_haiku_reflect_high_rep2` | 50, 58, 42, 50, 50, 33, 42, 33 | 2.3 | 1 | 0 (no_rise) | 19.4 | 5 | 54 % | $1.58 | – |
| `go_sonnet_reflect_high` | 55, 30, 30, 35, 35, 60 | 63.5 | 0.34 | 2331 (extrapolated) | 25.3 | 5 | 81 % | $13.01 | cap |
| `go_sonnet_reflect_high_rep2` | 75, 60, 90, 85, 85, 90, 90, 90 | 20.8 | 0.04 | 3702 (saturated) | 14.1 | 5 | 79 % | $12.59 | – |
| `go_haiku_reflect_high` | 55, 55, 65, 55, 40, 45, 45, 35 | 0.0 | 1 | 0 (no_rise) | 22.6 | 7 | 57 % | $2.10 | – |
| `go_haiku_reflect_high_rep2` | 50, 55, 50, 50, 45, 60, 50, 55 | 4.3 | 0.97 | 0 (no_rise) | 19.7 | 6 | 10 % | $1.93 | – |

## Behaviour under constraints

Limits: 32 model calls per game (a game not finished within them is lost), 240 s per tool call
(a second timeout forfeits), 50 reflection calls and 3 attempts per round. Adapting to these limits is
part of what experience can change: e.g. handing play to a saved tool (more moves per model call),
staying clear of the call budget, fewer illegal submissions. All splits; per checkpoint, both lineages
pooled. "Near budget" = 28+ of 32 calls.

| Game | Model | Checkpoint | Games | Calls per game | Near budget | Lost to limits | Illegal submissions | Moves per call | Reflection calls (of 50) | Rejected attempts |
|---|---|---|---|---|---|---|---|---|---|---|
| Hex | Sonnet 5.5 | 0 | 48 | 7.1 | 0 % | 0 | 0 | 0.86 | 14 / 10 | 0 |
| Hex | Sonnet 5.5 | 1 | 48 | 13.5 | 0 % | 0 | 0 | 0.47 | 21 / 23 | 0 |
| Hex | Sonnet 5.5 | 2 | 48 | 11.4 | 0 % | 0 | 0 | 0.61 | 17 / 5 | 0 |
| Hex | Sonnet 5.5 | 3 | 48 | 11.6 | 0 % | 0 | 0 | 0.61 | 5 / 5 | 0 |
| Hex | Sonnet 5.5 | 4 | 48 | 11.7 | 0 % | 0 | 0 | 0.61 | 6 / 5 | 0 |
| Hex | Sonnet 5.5 | 5 | 48 | 11.6 | 0 % | 0 | 0 | 0.61 | 5 / 4 | 0 |
| Hex | Sonnet 5.5 | 6 | 48 | 11.7 | 0 % | 0 | 0 | 0.61 | 4 / 4 | 0 |
| Hex | Sonnet 5.5 | 7 | 48 | 11.8 | 0 % | 0 | 0 | 0.61 | – | – |
| Hex | Haiku 5.5 | 0 | 48 | 10.1 | 0 % | 0 | 0 | 0.60 | 16 / 14 | 0 |
| Hex | Haiku 5.5 | 1 | 48 | 13.8 | 4 % | 0 | 0 | 0.49 | 27 / 25 | 0 |
| Hex | Haiku 5.5 | 2 | 48 | 15.4 | 4 % | 0 | 0 | 0.45 | 18 / 19 | 0 |
| Hex | Haiku 5.5 | 3 | 48 | 15.7 | 4 % | 0 | 0 | 0.46 | 14 / 20 | 0 |
| Hex | Haiku 5.5 | 4 | 48 | 16.3 | 4 % | 0 | 2 | 0.46 | 29 / 26 | 0 |
| Hex | Haiku 5.5 | 5 | 48 | 15.0 | 4 % | 0 | 0 | 0.50 | 22 / 13 | 0 |
| Hex | Haiku 5.5 | 6 | 48 | 15.4 | 4 % | 0 | 0 | 0.52 | 28 / 19 | 0 |
| Hex | Haiku 5.5 | 7 | 48 | 16.7 | 10 % | 0 | 0 | 0.49 | – | – |
| Go | Sonnet 5.5 | 0 | 64 | 10.1 | 0 % | 0 | 8 | 0.85 | 11 / 14 | 0 |
| Go | Sonnet 5.5 | 1 | 64 | 20.2 | 31 % | 6 | 5 | 0.51 | 19 / 18 | 0 |
| Go | Sonnet 5.5 | 2 | 64 | 10.7 | 0 % | 0 | 0 | 1.30 | 27 / 17 | 0 |
| Go | Sonnet 5.5 | 3 | 64 | 10.5 | 0 % | 2 | 1 | 1.17 | 37 / 11 | 0 |
| Go | Sonnet 5.5 | 4 | 64 | 13.5 | 0 % | 0 | 0 | 0.91 | 26 / 11 | 0 |
| Go | Sonnet 5.5 | 5 | 64 | 11.0 | 0 % | 0 | 0 | 0.99 | 32 / 8 | 0 |
| Go | Sonnet 5.5 | 6 | 32 | 11.1 | 0 % | 0 | 1 | 0.79 | 20 | 0 |
| Go | Sonnet 5.5 | 7 | 32 | 11.5 | 0 % | 0 | 0 | 0.80 | – | – |
| Go | Haiku 5.5 | 0 | 64 | 11.3 | 0 % | 0 | 10 | 0.83 | 16 / 14 | 0 |
| Go | Haiku 5.5 | 1 | 64 | 12.0 | 2 % | 1 | 7 | 0.73 | 18 / 19 | 0 |
| Go | Haiku 5.5 | 2 | 64 | 11.2 | 0 % | 0 | 7 | 0.79 | 20 / 25 | 0 |
| Go | Haiku 5.5 | 3 | 64 | 14.9 | 6 % | 0 | 8 | 0.60 | 27 / 18 | 0 |
| Go | Haiku 5.5 | 4 | 64 | 15.2 | 6 % | 1 | 1 | 0.65 | 30 / 21 | 0 |
| Go | Haiku 5.5 | 5 | 64 | 15.1 | 8 % | 3 | 7 | 0.62 | 26 / 20 | 0 |
| Go | Haiku 5.5 | 6 | 64 | 14.9 | 5 % | 0 | 4 | 0.66 | 21 / 21 | 0 |
| Go | Haiku 5.5 | 7 | 64 | 15.7 | 5 % | 1 | 1 | 0.65 | – | – |

## Reading

- Sonnet improves with experience on both games; Haiku does not. Pooled early → late held-out ID: Sonnet
  +14 pp (Hex) and +15 pp (Go), Haiku −5 pp and −7 pp. Late Sonnet beats late Haiku by 44 pp (Hex) and
  23 pp (Go). The pooled z-tests treat games as independent and ignore lineage; they are a summary, not
  the gate. Haiku at reflection effort high stays flat, so the earlier Haiku result was not an effort artefact.
- Per lineage, only `go_sonnet_reflect_high_rep2` passes the p < 0.05 rise gate (75 → 90 %, p = 0.04). The
  two Hex Sonnet lineages rise by 21–27 pp but have p ≈ 0.12–0.13 with 12 ID games per checkpoint.
- The two Go Sonnet lineages diverge. Rep2's saved tool was in use in every game from checkpoint 2 and ID held
  at 85–90 %. Run 1 called its tool from checkpoint 1 but stayed at 30–35 % until checkpoint 5 (60 %), and
  cost almost twice as much per checkpoint (25 reflection calls per round vs 14). It hit its $13 cap after 6
  completed checkpoints.
- Behaviour under constraints (table above). After the first reflection, Go Sonnet roughly doubled its model
  calls per game (10 → 20), 31 % of games came near the 32-call budget and 6 were lost to it. At the next
  checkpoint it moved play into its saved tool: 1.3 moves per model call, none near the budget, none lost.
  Haiku went the other way on both games: calls per game rose (Hex 10 → 17, Go 11 → 16) and moves per call
  fell, while it kept submitting illegal Go moves (1–10 per checkpoint vs Sonnet's 0–1 after checkpoint 2).
- Not in the tables: run 1's checkpoint 6 finished all 32 games before the cap stopped it, so it is not
  counted. In it the actor called its tool with a much larger search budget (e.g. `budget=2500000`), the
  call ran past the 240 s tool limit and 9 of 32 games were forfeited (ID 7/20 = 35 %, 5 ID games lost this
  way). Rep2 never did this. An adaptation that relaxes one limit (model calls) can break another (time).
- OOD (GNU Go level 10) does not move for any cell; on 5×5 it plays almost like levels 5–9 (report 13), so
  OOD here tests openings more than opponent strength.
