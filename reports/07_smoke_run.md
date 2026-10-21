# 07 Smoke run: anthropic/claude-sonnet-5.5 on 6x6 Hex

Games per checkpoint: {'train': 4, 'id': 4, 'ood': 2}. Billed: $0.77 (cap $19.00).
Learning cost, undiscounted as in the paper: $0.71.

| Checkpoint | Train | Held-out ID | Held-out OOD | Unfinished games | Reflection |
|---|---|---|---|---|---|
| 0 | 50 % | 50 % | 50 % | 0 | accepted (2 attempt(s)) |
| 1 | 50 % | 50 % | 50 % | 0 | – |
## Analysis (written after the run)

Run of 2026-10-21 through OpenRouter, effort `medium`. All costs are OpenRouter's reported charges.

### Cost

| Item | Measured |
|---|---|
| Games | 20, mean **$0.032** per game (range $0.011–0.066), 5.8 model calls per game |
| Prompt cache | 76 % of game input tokens were cache reads |
| Reflection | 2 attempts, 14 calls in total, **$0.13** |
| Whole run | **$0.77** billed; $0.71 learning cost priced the paper's way (no cache discount) |

A full paper-size Hex lineage (40 train + 40 ID + 32 OOD games per checkpoint,
checkpoints 0–20) would be about 2,350 games: roughly **$75–90** with this model,
plus reflections. Reflection cost will grow as the inventory and game logs grow,
so this is a lower bound.

### What happened

- **Reflection attempt 1 was rejected**: the tool used `import`, which the sandbox
  forbids. The retry removed it and passed. The paper reports the same failure
  ("illegal Python imports").
- The accepted inventory: a 15-line tool that picks the empty cell nearest the
  centre, and a note. The note's diagnosis was right ("opponent distance fell to 1
  while ours stayed 3-4. Block the opponent's shortest path"), but the tool does
  not do it. Only 14 of the 50 reflection calls were used.
- At checkpoint 1 the actor read or loaded the tool in 7 of 10 games but **ran it in
  none**; it chose every move by its own reasoning. This is the paper's "artifact
  available, not used" failure (Section 3.5). Moves changed in 6 of 10 games, but
  **no result changed**: 50 % on every split at both checkpoints.

### Can learning show on these games? (report 08)

From the same openings, always playing the first legal action wins 0 of 10, and the
100k-node engine wins 7 of 10. So the result depends on play, and an agent at 5 of
10 has room to improve. Blue openings are harder: the engine wins 2 of 5 as blue
and 5 of 5 as red.

### Before a longer run

1. Games are short (2–7 actor moves after a 10–11 ply opening). Shorter openings
   would give more decisions per game and more for reflection to learn from.
2. The colour imbalance should be reported per colour, or the blue openings
   rebalanced.
3. Two checkpoints with 4 held-out games cannot show plasticity; this run measured
   cost and checked the pipeline, nothing more.
