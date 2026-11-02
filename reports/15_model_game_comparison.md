# 15 Sonnet 5.5 vs Haiku 5.5 on Hex and Go (reflection effort high)

Actor effort medium, reflection effort high, two lineages per cell. Hex: 6×6, pooled openings,
8 / 12 / 4 games per checkpoint (train / ID / OOD), opponents 3k–100k nodes. Go: 5×5, pooled openings,
8 / 20 / 4, GNU Go levels 5–9 (ID) and 10 (OOD), training openings redrawn every checkpoint (report 13).
Early = checkpoints 0–2 (checkpoint 0 is before any reflection); late = checkpoint 3 onward.

## Held-out ID, early → late

| Game | Model | Lineages (checkpoints done) | Early | Late | Change | z | p |
|---|---|---|---|---|---|---|---|
| Hex | Sonnet 5.5 | `sonnet_reflect_high` (11), `sonnet_reflect_high_rep2` (11) | 50/72 = 69 % | 160/192 = 83 % | +14 pp | 2.49 | 0.013 |
| Hex | Haiku 5.5 | `hex_haiku_reflect_high` (11), `hex_haiku_reflect_high_rep2` (11) | 32/72 = 44 % | 77/192 = 40 % | -4 pp | -0.64 | 0.52 |
| Go | Sonnet 5.5 | `go_sonnet_reflect_high` (11), `go_sonnet_reflect_high_rep2` (11) | 68/120 = 57 % | 191/320 = 60 % | +3 pp | 0.57 | 0.57 |
| Go | Haiku 5.5 | `go_haiku_reflect_high` (11), `go_haiku_reflect_high_rep2` (11) | 66/120 = 55 % | 150/320 = 47 % | -8 pp | -1.52 | 0.13 |

## Sonnet vs Haiku, late checkpoints

| Game | Sonnet late | Haiku late | z | p |
|---|---|---|---|---|
| Hex | 160/192 = 83 % | 77/192 = 40 % | 8.71 | 2.9e-18 |
| Go | 191/320 = 60 % | 150/320 = 47 % | 3.25 | 0.0012 |

## Per colour (first player: Hex red, Go Black; second: Hex blue, Go White)

| Game | Model | Colour | Early | Late |
|---|---|---|---|---|
| Hex | Sonnet 5.5 | first player | 29/36 = 81 % | 88/96 = 92 % |
| Hex | Sonnet 5.5 | second player | 21/36 = 58 % | 72/96 = 75 % |
| Hex | Haiku 5.5 | first player | 18/36 = 50 % | 54/96 = 56 % |
| Hex | Haiku 5.5 | second player | 14/36 = 39 % | 23/96 = 24 % |
| Go | Sonnet 5.5 | first player | 31/60 = 52 % | 103/160 = 64 % |
| Go | Sonnet 5.5 | second player | 37/60 = 62 % | 88/160 = 55 % |
| Go | Haiku 5.5 | first player | 28/60 = 47 % | 80/160 = 50 % |
| Go | Haiku 5.5 | second player | 38/60 = 63 % | 70/160 = 44 % |

## Per lineage

| Lineage | Held-out ID per checkpoint (%) | Fit rise (pp) | p | P_sat | Reflection calls | Code revisions | Games calling a saved tool | Billed | Stopped |
|---|---|---|---|---|---|---|---|---|---|
| `sonnet_reflect_high` | 50, 50, 83, 75, 75, 75, 75, 75, 75, 75, 75 | 26.2 | 0.11 | 6372 (saturated) | 8.8 | 3 | 89 % | $10.05 | – |
| `sonnet_reflect_high_rep2` | 75, 67, 92, 92, 92, 92, 92, 92, 92, 92, 92 | 20.8 | 0.087 | 5427 (saturated) | 6.8 | 2 | 91 % | $11.06 | – |
| `hex_haiku_reflect_high` | 33, 42, 42, 33, 42, 33, 33, 42, 42, 42, 42 | 5.1 | 0.97 | 0 (no_rise) | 24.5 | 9 | 84 % | $2.11 | – |
| `hex_haiku_reflect_high_rep2` | 50, 58, 42, 50, 50, 33, 42, 33, 33, 42, 50 | 56.6 | 0.99 | 12383 (extrapolated) | 19.4 | 5 | 62 % | $2.19 | – |
| `go_sonnet_reflect_high` | 55, 30, 30, 35, 35, 60, 20, 15, 15, 15, 50 | 13.7 | 1 | 0 (to_date) | 23.5 | 8 | 90 % | $20.93 | – |
| `go_sonnet_reflect_high_rep2` | 75, 60, 90, 85, 85, 90, 90, 90, 90, 90, 90 | 21.4 | 0.019 | 3798 (saturated) | 15.4 | 8 | 85 % | $17.95 | – |
| `go_haiku_reflect_high` | 55, 55, 65, 55, 40, 45, 45, 35, 40, 45, 45 | 0.0 | 1 | 0 (no_rise) | 23.0 | 10 | 61 % | $2.97 | – |
| `go_haiku_reflect_high_rep2` | 50, 55, 50, 50, 45, 60, 50, 55, 35, 50, 55 | 50.0 | 0.99 | 10025 (extrapolated) | 20.4 | 8 | 21 % | $2.85 | – |

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
| Hex | Sonnet 5.5 | 7 | 48 | 11.8 | 0 % | 0 | 0 | 0.61 | 6 / 4 | 0 |
| Hex | Sonnet 5.5 | 8 | 48 | 11.8 | 0 % | 0 | 0 | 0.61 | 6 / 4 | 0 |
| Hex | Sonnet 5.5 | 9 | 48 | 11.7 | 0 % | 0 | 0 | 0.61 | 4 / 4 | 0 |
| Hex | Sonnet 5.5 | 10 | 48 | 11.7 | 0 % | 0 | 0 | 0.61 | – | – |
| Hex | Haiku 5.5 | 0 | 48 | 10.1 | 0 % | 0 | 0 | 0.60 | 16 / 14 | 0 |
| Hex | Haiku 5.5 | 1 | 48 | 13.8 | 4 % | 0 | 0 | 0.49 | 27 / 25 | 0 |
| Hex | Haiku 5.5 | 2 | 48 | 15.4 | 4 % | 0 | 0 | 0.45 | 18 / 19 | 0 |
| Hex | Haiku 5.5 | 3 | 48 | 15.7 | 4 % | 0 | 0 | 0.46 | 14 / 20 | 0 |
| Hex | Haiku 5.5 | 4 | 48 | 16.3 | 4 % | 0 | 2 | 0.46 | 29 / 26 | 0 |
| Hex | Haiku 5.5 | 5 | 48 | 15.0 | 4 % | 0 | 0 | 0.50 | 22 / 13 | 0 |
| Hex | Haiku 5.5 | 6 | 48 | 15.4 | 4 % | 0 | 0 | 0.52 | 28 / 19 | 0 |
| Hex | Haiku 5.5 | 7 | 48 | 16.7 | 10 % | 0 | 0 | 0.49 | 34 / 12 | 0 |
| Hex | Haiku 5.5 | 8 | 48 | 15.2 | 6 % | 0 | 0 | 0.53 | 28 / 28 | 0 |
| Hex | Haiku 5.5 | 9 | 48 | 15.6 | 4 % | 0 | 0 | 0.53 | 29 / 18 | 0 |
| Hex | Haiku 5.5 | 10 | 48 | 14.5 | 2 % | 0 | 0 | 0.54 | – | – |
| Go | Sonnet 5.5 | 0 | 64 | 10.1 | 0 % | 0 | 8 | 0.85 | 11 / 14 | 0 |
| Go | Sonnet 5.5 | 1 | 64 | 20.2 | 31 % | 6 | 5 | 0.51 | 19 / 18 | 0 |
| Go | Sonnet 5.5 | 2 | 64 | 10.7 | 0 % | 0 | 0 | 1.30 | 27 / 17 | 0 |
| Go | Sonnet 5.5 | 3 | 64 | 10.5 | 0 % | 2 | 1 | 1.17 | 37 / 11 | 0 |
| Go | Sonnet 5.5 | 4 | 64 | 13.5 | 0 % | 0 | 0 | 0.91 | 26 / 11 | 0 |
| Go | Sonnet 5.5 | 5 | 64 | 11.0 | 0 % | 0 | 0 | 0.99 | 32 / 8 | 0 |
| Go | Sonnet 5.5 | 6 | 64 | 9.5 | 0 % | 20 | 1 | 0.89 | 18 / 20 | 0 |
| Go | Sonnet 5.5 | 7 | 64 | 11.8 | 0 % | 1 | 0 | 0.99 | 36 / 17 | 0 |
| Go | Sonnet 5.5 | 8 | 64 | 12.3 | 0 % | 0 | 0 | 1.01 | 16 / 30 | 1 |
| Go | Sonnet 5.5 | 9 | 64 | 12.0 | 0 % | 0 | 1 | 1.03 | 13 / 39 | 1 |
| Go | Sonnet 5.5 | 10 | 64 | 11.6 | 0 % | 0 | 0 | 0.99 | – | – |
| Go | Haiku 5.5 | 0 | 64 | 11.3 | 0 % | 0 | 10 | 0.83 | 16 / 14 | 0 |
| Go | Haiku 5.5 | 1 | 64 | 12.0 | 2 % | 1 | 7 | 0.73 | 18 / 19 | 0 |
| Go | Haiku 5.5 | 2 | 64 | 11.2 | 0 % | 0 | 7 | 0.79 | 20 / 25 | 0 |
| Go | Haiku 5.5 | 3 | 64 | 14.9 | 6 % | 0 | 8 | 0.60 | 27 / 18 | 0 |
| Go | Haiku 5.5 | 4 | 64 | 15.2 | 6 % | 1 | 1 | 0.65 | 30 / 21 | 0 |
| Go | Haiku 5.5 | 5 | 64 | 15.1 | 8 % | 3 | 7 | 0.62 | 26 / 20 | 0 |
| Go | Haiku 5.5 | 6 | 64 | 14.9 | 5 % | 0 | 4 | 0.66 | 21 / 21 | 0 |
| Go | Haiku 5.5 | 7 | 64 | 15.7 | 5 % | 1 | 1 | 0.65 | 23 / 19 | 0 |
| Go | Haiku 5.5 | 8 | 64 | 16.8 | 11 % | 1 | 3 | 0.66 | 24 / 27 | 0 |
| Go | Haiku 5.5 | 9 | 64 | 15.8 | 5 % | 0 | 0 | 0.69 | 25 / 20 | 0 |
| Go | Haiku 5.5 | 10 | 64 | 15.4 | 5 % | 0 | 3 | 0.61 | – | – |

## Reading

- Checkpoints 0–10 (plan B extended every lineage from 7 or 5). Hex Sonnet improves with experience and
  Haiku does not on either game: pooled early → late held-out ID is +14 pp for Hex Sonnet, −4 pp (Hex) and
  −8 pp (Go) for Haiku. Go Sonnet, +15 pp (p = 0.011) through checkpoint 7, is now +3 pp (p = 0.57): run 1
  fell to 15–20 % at checkpoints 6–9 (below). Late Sonnet still beats late Haiku by 43 pp (Hex) and
  13 pp (Go). The pooled z-tests treat games as independent and ignore lineage; they are a summary, not
  the gate. Haiku at reflection effort high stays flat, so the earlier Haiku result was not an effort artefact.
- Per lineage, only `go_sonnet_reflect_high_rep2` passes the p < 0.05 rise gate (75 → 90 %, p = 0.019). The
  two Hex Sonnet lineages rise by 21–26 pp (p = 0.09–0.11, 12 ID games per checkpoint); both have held one
  score since checkpoint 2–3 (75 % and 92 %), so the extra checkpoints added no information about the rise.
  `hex_haiku_reflect_high_rep2` and `go_haiku_reflect_high_rep2` now get 50–57 pp extrapolated rises and
  P_sat above 10,000 from their last one or two checkpoints, with p = 0.99: the no-learning false positives
  of report 03, which the gate rejects.
- The two Go Sonnet lineages diverge. Rep2's saved tool was in use in every game from checkpoint 2 and ID held
  at 85–90 %. Run 1 reached 60 % at checkpoint 5, then 20 of its 32 checkpoint-6 games ran a tool call past
  the 240 s limit (all 8 training games scored 0). Its next reflection capped total search at 1.5M nodes: no
  timeouts after that, but ID stayed at 15 % for checkpoints 7–9 while the reflection reported that White
  scores read +8 to +12 and then collapsed. It returned to 50 % at checkpoint 10 after a reflection that
  changed only the tool description and playbook. Run 1 cost $20.93 against rep2's $17.95.
- Behaviour under constraints (table above). After the first reflection, Go Sonnet roughly doubled its model
  calls per game (10 → 20), 31 % of games came near the 32-call budget and 6 were lost to it. At the next
  checkpoint it moved play into its saved tool: 1.3 moves per model call, none near the budget, none lost.
  Haiku went the other way on both games: calls per game rose (Hex 10 → 17, Go 11 → 16) and moves per call
  fell, while it kept submitting illegal Go moves (1–10 per checkpoint vs Sonnet's 0–1 after checkpoint 2).
- Run 1's checkpoint 6 ran twice. Under plan A it finished before the $13 cap stopped the lineage and was
  not counted (9 of 32 games forfeited on time, ID 35 %); plan B's resume replayed it (20 of 32 on time,
  ID 20 %). Under plan A the actor raised the tool's search budget itself (e.g. `budget=2500000`); under
  plan B it followed the playbook's 3M nodes per search, which the engine applied to each deepening
  iteration separately (reflection 6's own diagnosis). Rep2 never did this. An adaptation that relaxes one limit (model calls) can break another (time).
- OOD (GNU Go level 10) does not move for any cell; on 5×5 it plays almost like levels 5–9 (report 13), so
  OOD here tests openings more than opponent strength.
