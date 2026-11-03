# 21 GLM 5.3 vs Sonnet 5.5 and Haiku 5.5 on Hex and Go (reflection effort high)

Plan C ran GLM 5.3 (`z-ai/glm-5.3`) with the settings of report 15: actor effort medium, reflection
effort high, two lineages per game, checkpoints 0–10; Hex 8 / 12 / 4 games per checkpoint, Go 8 / 20 / 4.
Early = checkpoints 0–2; late = checkpoint 3 onward. GLM ran 2 games at a time per lineage
(Claude 4), and all four GLM lineages were stopped by the key's spending limit and resumed with
the unfinished checkpoint replayed (docs/PROTOCOL_NOTES.md).

## Held-out ID, early → late

| Game | Model | Early | Late | Change | z | p |
|---|---|---|---|---|---|---|
| Hex | GLM 5.3 | 15/72 = 21 % | 46/192 = 24 % | +3 pp | 0.54 | 0.59 |
| Hex | Sonnet 5.5 | 50/72 = 69 % | 160/192 = 83 % | +14 pp | 2.49 | 0.013 |
| Hex | Haiku 5.5 | 32/72 = 44 % | 77/192 = 40 % | -4 pp | -0.64 | 0.52 |
| Go | GLM 5.3 | 51/120 = 42 % | 147/320 = 46 % | +3 pp | 0.65 | 0.52 |
| Go | Sonnet 5.5 | 68/120 = 57 % | 191/320 = 60 % | +3 pp | 0.57 | 0.57 |
| Go | Haiku 5.5 | 66/120 = 55 % | 150/320 = 47 % | -8 pp | -1.52 | 0.13 |

## GLM against each Claude model, late checkpoints

| Game | GLM late | Against | Their late | z | p |
|---|---|---|---|---|---|
| Hex | 46/192 = 24 % | Sonnet 5.5 | 160/192 = 83 % | -11.67 | 1.9e-31 |
| Hex | 46/192 = 24 % | Haiku 5.5 | 77/192 = 40 % | -3.39 | 0.0007 |
| Go | 147/320 = 46 % | Sonnet 5.5 | 191/320 = 60 % | -3.48 | 0.00049 |
| Go | 147/320 = 46 % | Haiku 5.5 | 150/320 = 47 % | -0.24 | 0.81 |

## Per colour, GLM (first player: Hex red, Go Black)

| Game | Colour | Early | Late |
|---|---|---|---|
| Hex | first player | 8/36 = 22 % | 35/96 = 36 % |
| Hex | second player | 7/36 = 19 % | 11/96 = 11 % |
| Go | first player | 29/60 = 48 % | 70/160 = 44 % |
| Go | second player | 22/60 = 37 % | 77/160 = 48 % |

## Per lineage

| Lineage | Held-out ID per checkpoint (%) | Fit rise (pp) | p | P_sat | Reflection calls | Code revisions | Games calling a saved tool | Billed | Of which replayed | Learning cost, paper's pricing |
|---|---|---|---|---|---|---|---|---|---|---|
| `hex_glm_reflect_high` | 17, 75, 0, 0, 25, 17, 42, 42, 42, 50, 58 | 33.1 | 0.031 | 5807 (saturated) | 49.1 | 9 | 91 % | $11.25 | $0.88 | $5.38 |
| `hex_glm_reflect_high_rep2` | 0, 25, 8, 8, 17, 17, 8, 0, 25, 17, 17 | 14.2 | 0.32 | 24658 (saturated) | 46.4 | 9 | 89 % | $11.21 | $0.93 | $5.40 |
| `sonnet_reflect_high` | 50, 50, 83, 75, 75, 75, 75, 75, 75, 75, 75 | 26.2 | 0.11 | 6372 (saturated) | 8.8 | 3 | 89 % | $10.05 | $0.00 | $12.37 |
| `sonnet_reflect_high_rep2` | 75, 67, 92, 92, 92, 92, 92, 92, 92, 92, 92 | 20.8 | 0.087 | 5427 (saturated) | 6.8 | 2 | 91 % | $11.06 | $0.00 | $14.38 |
| `hex_haiku_reflect_high` | 33, 42, 42, 33, 42, 33, 33, 42, 42, 42, 42 | 5.1 | 0.97 | 0 (no_rise) | 24.5 | 9 | 84 % | $2.11 | $0.00 | $3.20 |
| `hex_haiku_reflect_high_rep2` | 50, 58, 42, 50, 50, 33, 42, 33, 33, 42, 50 | 56.6 | 0.99 | 12383 (extrapolated) | 19.4 | 5 | 62 % | $2.19 | $0.00 | $2.55 |
| `go_glm_reflect_high` | 10, 60, 60, 55, 50, 25, 35, 35, 35, 50, 25 | 33.0 | 0.02 | 48432 (saturated) | 43.8 | 9 | 88 % | $14.88 | $1.86 | $6.90 |
| `go_glm_reflect_high_rep2` | 15, 55, 55, 55, 55, 60, 40, 45, 60, 50, 60 | 38.5 | 0.0081 | 59959 (saturated) | 38.8 | 8 | 85 % | $10.71 | $0.29 | $4.84 |
| `go_sonnet_reflect_high` | 55, 30, 30, 35, 35, 60, 20, 15, 15, 15, 50 | 13.7 | 1 | 0 (to_date) | 23.5 | 8 | 90 % | $20.93 | $2.31 | $34.00 |
| `go_sonnet_reflect_high_rep2` | 75, 60, 90, 85, 85, 90, 90, 90, 90, 90, 90 | 21.4 | 0.019 | 3798 (saturated) | 15.4 | 8 | 85 % | $17.95 | $0.58 | $24.12 |
| `go_haiku_reflect_high` | 55, 55, 65, 55, 40, 45, 45, 35, 40, 45, 45 | 0.0 | 1 | 0 (no_rise) | 23.0 | 10 | 61 % | $2.97 | $0.00 | $3.13 |
| `go_haiku_reflect_high_rep2` | 50, 55, 50, 50, 45, 60, 50, 55, 35, 50, 55 | 50.0 | 0.99 | 10025 (extrapolated) | 20.4 | 8 | 21 % | $2.85 | $0.00 | $2.77 |

## GLM behaviour under constraints

All splits, both lineages pooled per checkpoint; columns as in report 15.

| Game | Checkpoint | Games | Calls per game | Near budget | Lost to limits | Illegal submissions | Moves per call |
|---|---|---|---|---|---|---|---|
| Hex | 0 | 48 | 21.7 | 31 % | 32 | 2 | 0.17 |
| Hex | 1 | 48 | 17.2 | 8 % | 5 | 1 | 0.38 |
| Hex | 2 | 48 | 14.5 | 2 % | 3 | 0 | 0.44 |
| Hex | 3 | 48 | 14.7 | 6 % | 4 | 1 | 0.43 |
| Hex | 4 | 48 | 13.0 | 2 % | 0 | 0 | 0.56 |
| Hex | 5 | 48 | 13.5 | 4 % | 1 | 0 | 0.53 |
| Hex | 6 | 48 | 12.5 | 0 % | 0 | 0 | 0.56 |
| Hex | 7 | 48 | 11.7 | 0 % | 1 | 0 | 0.54 |
| Hex | 8 | 48 | 12.1 | 2 % | 0 | 0 | 0.58 |
| Hex | 9 | 48 | 13.6 | 0 % | 0 | 0 | 0.55 |
| Hex | 10 | 48 | 14.9 | 2 % | 0 | 0 | 0.55 |
| Go | 0 | 64 | 26.6 | 62 % | 29 | 24 | 0.40 |
| Go | 1 | 64 | 17.9 | 14 % | 5 | 7 | 0.63 |
| Go | 2 | 64 | 16.2 | 11 % | 1 | 8 | 0.58 |
| Go | 3 | 64 | 14.0 | 8 % | 1 | 7 | 0.66 |
| Go | 4 | 64 | 14.1 | 6 % | 2 | 1 | 0.72 |
| Go | 5 | 64 | 15.5 | 5 % | 1 | 0 | 0.74 |
| Go | 6 | 64 | 16.0 | 9 % | 1 | 4 | 0.72 |
| Go | 7 | 64 | 14.8 | 6 % | 1 | 0 | 0.71 |
| Go | 8 | 64 | 14.0 | 3 % | 3 | 2 | 0.73 |
| Go | 9 | 64 | 14.6 | 8 % | 2 | 2 | 0.69 |
| Go | 10 | 64 | 15.1 | 3 % | 1 | 5 | 0.76 |

## Reading

- GLM plays worse than both Claude models on Hex (late 24 % vs Sonnet 83 % and Haiku 40 %) and level with
  Haiku on Go (46 % vs 47 %), below Sonnet (60 %). Its pooled early → late change is +3 pp on both games.
- GLM's checkpoint 0 is not a normal start. Every Claude game at checkpoint 0 finished; GLM lost 32 of 48
  Hex games and 29 of 64 Go games there to the limits, mostly tool calls past 240 s on Hex and the 32-call
  budget on Go. Its held-out ID at checkpoint 0 was 2/24 (Hex) and 5/40 (Go). After the first reflection
  nearly every game finished, and ID jumped to 12/24 and 23/40.
- That jump is what the metric sees. Three of the four GLM lineages pass the p < 0.05 flat-curve gate,
  against one of the eight Claude lineages here, and the two Go lineages get P_sat of 48,000–60,000 points
  per $1,000, over ten times the one Claude lineage that passes (3,798): a 33–39-point rise bought with $5–7 of learning cost at
  GLM's prices. After checkpoint 1 GLM does not improve: pooled ID from checkpoints 1–2 to 3–10 goes 27 %
  → 24 % on Hex (p = 0.65) and 58 % → 46 % on Go (p = 0.064); `go_glm_reflect_high` ends at 25 %, below
  its checkpoint-1 score of 60 %. Eq. 4–5 reward a low start and a cheap first fix as plasticity. A
  baseline that starts from games the agent can finish (or a fit that leaves out checkpoint 0) would not.
- GLM reflects at the edge of its budget: 39–49 of 50 calls per round, against 7–9 for Hex Sonnet and
  15–24 for Go Sonnet, and it revised code at 8–9 of 10 reflections. More reflection did not mean better
  reflection here, as with Haiku at effort high (report 15).
- Hex run 1's fall from 75 % to 0 % at checkpoints 2–3 is a bug its own reflection wrote into its search
  tool; model-free replays reproduce it, and a one-line fix of the checkpoint-2 tool scores 12/12 (report
  20). Hex run 2 never passed 25 %.
- At the paper's pricing GLM's learning cost was $5–7 per lineage, against $12–34 for Sonnet and $3 for
  Haiku, but its lineages billed $11–15 each in total, close to Hex Sonnet: held-out games and replayed
  checkpoints ($0.29–1.86 per lineage) are not learning cost.
- Per colour, GLM's Hex gain is first-player only (22 % → 36 %); as second player it fell (19 % → 11 %).
- Caveats: GLM ran 2 games at a time per lineage, Claude 4, so GLM's tool calls had less CPU contention
  under the 240 s limit, which would favour GLM, not explain its lower scores. Every GLM lineage was
  interrupted and resumed, replaying one checkpoint as a new sample.
