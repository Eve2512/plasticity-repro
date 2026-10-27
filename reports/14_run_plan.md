# 14 Cost probe and costed plan for a cross-model comparison

## Go cost probe (2026-10-27, billed $2.20)

Each probe: 5x5 Go, 1 round (checkpoints 0–1), 2 train / 2 ID / 1 OOD games per
checkpoint, actor effort medium, reflection effort high, OpenRouter. Billed
amounts are OpenRouter's reported costs.

| Model | Games | Per game | Model calls per game | Actor moves per game | Reflection | Billed |
|---|---|---|---|---|---|---|
| Sonnet 5.5 | 10 | $0.041 (max $0.057) | 12.2 | 9.8 | $0.19 (10 calls) | $0.60 |
| Haiku 5.5 | 10 | $0.006 (max $0.015) | 12.9 | 8.1 | $0.03 (16 calls) | $0.09 |
| Opus 5.5 | 5 | $0.230 (max $0.422) | 18.2 | 10.8 | $0.37, cut off by the cap | $1.52 |

Every game finished (no budget or timeout losses). Opus costs about 5.7× Sonnet per
game: twice the token price, and about 1.5× the calls with longer turns. Probe
results are too small to read (Sonnet ID 1/2 then 2/2; Haiku 1/2 then 1/2; Opus
stopped in its first reflection); per-run reports are `10_go_probe_*.md`.

## Hex costs already measured (reports 10, 12)

| Model, reflection effort | Per game | Per reflection | Lineage, 7 rounds, 8/12/4 |
|---|---|---|---|
| Sonnet 5.5, high | $0.033–0.036 | $0.12–0.15 | $7.44, $7.77 (two lineages, done) |
| Sonnet 5.5, medium | $0.048 | $0.05 | $9.49, $9.57 (two lineages, done) |
| Haiku 5.5, medium | $0.007 | $0.016 | $7.86 for 20 rounds at 20/24/8 (done) |
| Opus 5.5 | not measured; ~5.7× Sonnet if Go's ratio holds | | |

## Cost per lineage

Cost = games per checkpoint × (rounds + 1) × per-game cost + rounds × per-reflection cost.

| Lineage | Rounds | Games (train/ID/OOD) | Games in all | Estimate |
|---|---|---|---|---|
| Go, Sonnet 5.5 | 7 | 8 / 20 / 4 | 256 | **$11.7** |
| Go, Haiku 5.5 | 7 | 8 / 20 / 4 | 256 | **$1.8** |
| Go, Opus 5.5 | 7 | 8 / 20 / 4 | 256 | $61.5 |
| Go, Opus 5.5 (small) | 4 | 8 / 20 / 2 | 150 | **$36** |
| Hex, Haiku 5.5, reflection high | 7 | 8 / 12 / 4 | 192 | **$1.6** |
| Hex, Opus 5.5 | 7 | 8 / 12 / 4 | 192 | ~$40 (Go ratio, unmeasured) |

Go uses 20 ID games: the full ID bank matches training difficulty, a 12-game prefix
is a little harder (report 13). Two lineages per condition, as for Hex, because one
lineage was not enough to separate a rise from noise (report 12).

## Plans

All runs: actor effort medium, reflection effort high (the condition that showed
plasticity on Hex), caps at about 1.3× the estimate.

| Plan | Runs | Estimate | Caps | Answers |
|---|---|---|---|---|
| **A (recommended)** | Go Sonnet ×2, Go Haiku ×2, Hex Haiku (reflection high) ×2 | **$30** | $15 + $15 + $2.5 + $2.5 + $2 + $2 = $39 | Does Sonnet's Hex plasticity carry over to Go? Is Haiku flat in both games at matched effort? |
| B | A + Go Opus (small) ×1 | $66 | A + $45 | Adds one Opus lineage; one lineage alone cannot pass the significance gate |
| C | A + Go Opus (small) ×2 | $102 | A + $90 | Opus with two lineages |

The key had about $3.65 left after the probe (limit $50, $46.35 spent), so every plan
needs more credit first: about $36 more for plan A.

Not in any plan: Opus on Hex (unmeasured, ~$40 per lineage), paper-size Go (20 rounds,
20/20/12: ~$48 per Sonnet lineage).
