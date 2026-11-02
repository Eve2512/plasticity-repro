# 20 GLM 5.3 Hex run 1: a tool rewrite that broke the tool

Lineage `hex_glm_reflect_high` (z-ai/glm-5.3, reflection effort high, 6x6 Hex). Its held-out ID
score went 17 % → 75 % at checkpoint 1, fell to 0 % at checkpoints 2 and 3 and climbed back to
58 % by checkpoint 10. This report finds the cause in the saved tool code.

Replay: each saved `hex/hex_glue.py` plays the 12 held-out ID openings (6 as X, 6 as O) against
the run's opponent, calling `turn()` every move and submitting what it returns. No model is in
the loop and no API calls are made, so the replay measures the tool alone; the reported score also
depends on the actor (whether it calls the tool, overrides it, or runs out of time).

## Replay of every saved tool

| Checkpoint | Reported held-out ID | Replay, tool alone | As X | As O |
|---|---|---|---|---|
| 0 | 17 % | – (no tool yet) | – | – |
| 1 | 75 % | 10/12 | 5/6 | 5/6 |
| 2 | 0 % | 0/12 | 0/6 | 0/6 |
| 3 | 0 % | 0/12 | 0/6 | 0/6 |
| 4 | 25 % | 3/12 | 3/6 | 0/6 |
| 5 | 17 % | 3/12 | 3/6 | 0/6 |
| 6 | 42 % | 5/12 | 4/6 | 1/6 |
| 7 | 42 % | 5/12 | 4/6 | 1/6 |
| 8 | 42 % | 5/12 | 4/6 | 1/6 |
| 9 | 50 % | 6/12 | 4/6 | 2/6 |
| 10 | 58 % | 7/12 | 5/6 | 2/6 |

The replay follows the reported scores closely, including the drop to zero: the collapse is in
the tool, not in the actor or the harness.

## What changed at checkpoint 2

In the checkpoint-1 reflection (41 of 50 calls) GLM replaced its depth-3 search with a
corridor-restricted alpha-beta search to depth 5–8, with a transposition table, a shared node
budget and a double-threat veto, and regenerated the glue file from the new engine. It validated
the rewrite with self-tests, timing runs, replays of its four lost games against the recorded
opponent replies, and engine-vs-engine self-play from those openings ("Self-play from all four
lost openings now wins all four"). It did not play the new tool against any model of the
opponent.

The rewrite had two bugs:

| Bug | Code (checkpoint 2) | Effect | Fixed |
|---|---|---|---|
| Corridor filter | `path_cells`: `fwd[p] + bwd[p] == best` | Both distances count the empty cell itself, so the test should be `fwd[p] + bwd[p] - 1 == best`. The filter misses the cells on the shortest connection paths, and the search only looks at the cells it keeps | Never; still in the checkpoint-10 engine and glue |
| Win check, O side | `winning_moves`: `connected(own \| (1 << p), opp, player)`, while `connected` takes `(mask_x, mask_o, player)` | As O, the tool does not see an immediate win or a cell it must block | Checkpoint 3, by GLM |

Patched copies of the checkpoint-2 tool, same replay:

| Checkpoint-2 tool | Replay |
|---|---|
| as saved | 0/12 |
| corridor filter fixed | 12/12 |
| corridor filter and win check fixed | 12/12 |
| candidate cap 16 → 99 | 0/12 |
| transposition table off | 1/12 |
| candidate cap 99 and table off | 1/12 |

The same one-line fix in later tools:

| Tool | As saved | Corridor filter fixed |
|---|---|---|
| Checkpoint 3 (win check already fixed by GLM) | 0/12 | 12/12 |
| Checkpoint 10 | 7/12 | 7/12 |

The corridor filter alone explains the collapse. The win-check bug cost nothing in these 12
games, and GLM's fix of it at checkpoint 3 left the replay at 0/12. By checkpoint 10 the filter no
longer decides these games: the root layers added since then pick the move, and the fixed
checkpoint-10 tool still scores 7/12.

## What GLM did next

- **Reflection 2** (after 0/8 training games): "The engine v2 lost all 8 games on the board". It
  traced the win-check bug, called it "the root cause of all 8 checkpoint_002 losses", and fixed
  it in both files. The corridor filter stayed.
- **Reflection 3** (after 0/8 again): it built a "greedy race opponent model", benchmarked
  variants against it, and added a race-aware root selector and veto layer (engine v4) on top of
  the existing search. From here on every reflection benchmarks candidates against its own
  opponent models ("anti", "smart", "anti+kill") before installing them.
- **Reflections 4–9**: engines v5 (2-ply lookahead root), v7 and v8, with held-out ID back to
  58 %. These layers work around the search; none of them touch the corridor filter.

## Reading

- GLM's collapse is a bug it wrote into its own tool, and the replay reproduces it with no model
  in the loop.
- Its checkpoint-1 checks did not catch the bug. Self-play put the same broken tool on both sides.
  The Claude lineages that learned tested candidates in games against their current tool
  (report 19); GLM started testing against opponent models only after two checkpoints at 0 %.
- GLM found a real bug, took it for the cause, and fixed it, so the actual cause was never looked
  for again. Recovery came from adding layers on top of the broken search. The checkpoint-2 rewrite
  with one line fixed scores 12/12 in replay; the final tool after eight more reflections scores
  7/12, with or without the fix. Eight reflections went into working around a one-line bug and
  ended below where the fix alone would have been (12 openings, so the gap is indicative).
- Hex run 2 (`hex_glm_reflect_high_rep2`) uses a different engine with no corridor filter; this
  bug does not explain its low scores (0–25 %).

Replays: `python scripts/replay_hex_glue.py runs/hex_glm_reflect_high 1,2,3`. The patched copies
change only the lines named above, in a copy of the run directory.
