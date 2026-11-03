---
pretty_name: "Agent Plasticity on 6x6 Hex and 5x5 Go: Claude Sonnet 5.5, Haiku 5.5 and GLM 5.3 traces"
license: cc-by-4.0
language:
- en
tags:
- agents
- self-improvement
- tool-use
- reflection
- hex
- go
- reproduction
- agent-traces
size_categories:
- 1K<n<10K
configs:
- config_name: runs
  data_files: data/runs.jsonl
- config_name: checkpoints
  data_files: data/checkpoints.jsonl
- config_name: games
  data_files: data/games.jsonl
- config_name: reflections
  data_files: data/reflections.jsonl
- config_name: inventories
  data_files: data/inventories.jsonl
- config_name: calls
  data_files: data/calls.jsonl
- config_name: openings
  data_files: data/openings.jsonl
- config_name: thinking_replay
  data_files: data/thinking_replay.jsonl
- config_name: ablation_games
  data_files: data/ablation_games.jsonl
- config_name: trace_viewer
  data_files:
  - split: train
    path:
    - traces/reflections/*.jsonl
    - traces/ablation/*.jsonl
- config_name: traces_smoke
  data_files:
  - split: train
    path: traces/games/smoke/*.jsonl
- config_name: traces_lineage_a
  data_files:
  - split: train
    path: traces/games/lineage_a/*.jsonl
- config_name: traces_lineage_a2
  data_files:
  - split: train
    path: traces/games/lineage_a2/*.jsonl
- config_name: traces_sonnet_reflect_high
  data_files:
  - split: train
    path: traces/games/sonnet_reflect_high/*.jsonl
- config_name: traces_sonnet_reflect_high_rep2
  data_files:
  - split: train
    path: traces/games/sonnet_reflect_high_rep2/*.jsonl
- config_name: traces_sonnet_medium_rep2
  data_files:
  - split: train
    path: traces/games/sonnet_medium_rep2/*.jsonl
- config_name: traces_haiku_r20
  data_files:
  - split: train
    path: traces/games/haiku_r20/*.jsonl
- config_name: traces_hex_haiku_reflect_high
  data_files:
  - split: train
    path: traces/games/hex_haiku_reflect_high/*.jsonl
- config_name: traces_hex_haiku_reflect_high_rep2
  data_files:
  - split: train
    path: traces/games/hex_haiku_reflect_high_rep2/*.jsonl
- config_name: traces_go_sonnet_reflect_high
  data_files:
  - split: train
    path: traces/games/go_sonnet_reflect_high/*.jsonl
- config_name: traces_go_sonnet_reflect_high_rep2
  data_files:
  - split: train
    path: traces/games/go_sonnet_reflect_high_rep2/*.jsonl
- config_name: traces_go_haiku_reflect_high
  data_files:
  - split: train
    path: traces/games/go_haiku_reflect_high/*.jsonl
- config_name: traces_go_haiku_reflect_high_rep2
  data_files:
  - split: train
    path: traces/games/go_haiku_reflect_high_rep2/*.jsonl
- config_name: traces_hex_haiku_medium_rep2
  data_files:
  - split: train
    path: traces/games/hex_haiku_medium_rep2/*.jsonl
- config_name: traces_go_sonnet_medium
  data_files:
  - split: train
    path: traces/games/go_sonnet_medium/*.jsonl
- config_name: traces_go_sonnet_medium_rep2
  data_files:
  - split: train
    path: traces/games/go_sonnet_medium_rep2/*.jsonl
- config_name: traces_go_haiku_medium
  data_files:
  - split: train
    path: traces/games/go_haiku_medium/*.jsonl
- config_name: traces_go_haiku_medium_rep2
  data_files:
  - split: train
    path: traces/games/go_haiku_medium_rep2/*.jsonl
- config_name: traces_go_glm_reflect_high
  data_files:
  - split: train
    path: traces/games/go_glm_reflect_high/*.jsonl
- config_name: traces_go_glm_reflect_high_rep2
  data_files:
  - split: train
    path: traces/games/go_glm_reflect_high_rep2/*.jsonl
- config_name: traces_hex_glm_reflect_high
  data_files:
  - split: train
    path: traces/games/hex_glm_reflect_high/*.jsonl
- config_name: traces_hex_glm_reflect_high_rep2
  data_files:
  - split: train
    path: traces/games/hex_glm_reflect_high_rep2/*.jsonl
- config_name: traces_sonnet_nofeedback_high
  data_files:
  - split: train
    path: traces/games/sonnet_nofeedback_high/*.jsonl
- config_name: traces_sonnet_nofeedback_high_rep2
  data_files:
  - split: train
    path: traces/games/sonnet_nofeedback_high_rep2/*.jsonl
---

# Agent Plasticity on 6x6 Hex and 5x5 Go: Claude Sonnet 5.5, Haiku 5.5 and GLM 5.3 traces

Agent traces from a scaled-down, independent reproduction of
[Agent Plasticity: Measuring Self-Improvement Through Experience](https://arxiv.org/abs/2610.08902)
(Singh et al., 2026). The paper's authors did not release code or data; this harness was
rebuilt from the paper's equations and appendix.

A frozen model plays 6×6 Hex against an alpha-beta engine, or 5×5 Go against GNU Go. Between checkpoints the same
model reflects on its training games and edits a persistent inventory (Python tools,
notes, tracking files) that the next checkpoint inherits. Held-out games are never shown
to reflection.

## What is in it

Every table has a `game` column (`hex` or `go`).

| Config | Rows (Hex + Go) | One row is |
|---|---|---|
| `runs` | 14 + 10 | a lineage: settings, cost, plasticity fit |
| `checkpoints` | 139 + 110 | a checkpoint: wins per split, learning cost, reflection outcome |
| `games` | 3,898 + 3,520 | a game: opening, moves, per-move diagnostics, token use, **full transcript** with thinking where recorded |
| `reflections` | 130 + 105 | a reflection attempt: **full transcript** with thinking where recorded, validator result |
| `inventories` | 656 + 578 | a file the agent saved, at a checkpoint (code, notes, tracking JSON) |
| `calls` | 50,587 + 48,269 | a model call: tokens (input, cached, cache write, output) and charged cost |
| `openings` | 234 + 112 | a starting position from the legacy, contested or pooled bank |
| `thinking_replay` | 830 + 547 | a saved reflection turn sent again with thinking summaries on: recorded and replayed calls, summary |
| `ablation_games` | 144 + 0 | a held-out ID game from a final checkpoint with the inventory kept, removed or forced (`arm`) |
| `trace_viewer` | 379 | every reflection (with replayed summaries, labelled, where none was recorded) and ablation game, as a transcript in Pi's session format, for the trace viewer |
| `traces_<run_id>` | 7,418 in all | every game of one run, in the same format (one config per run: the Hub's conversion timed out on one config of 3,918 files) |

In `trace_viewer` and `traces_*` the `harness` column says `pi`. The traces were not run in Pi. The harness
here is this project's own; its transcripts are written in Pi's session format because the
Hub's trace viewer reads that format, so the Hub names the harness after the format.

Runs (via OpenRouter; games always at effort `medium`):

| `run_id` | Game | Model | Reflection effort | Checkpoints | Games per checkpoint (train / ID / OOD) | Openings |
|---|---|---|---|---|---|---|
| `smoke` | Hex | Sonnet 5.5 | medium | 0–1 | 4 / 4 / 2 | legacy (10/11-ply) |
| `lineage_a` | Hex | Sonnet 5.5 | medium | 0 (+2 games of 1) | 8 / 12 / 4 | contested (stopped: ID bank harder than train) |
| `lineage_a2`, `sonnet_medium_rep2` | Hex | Sonnet 5.5 | medium | 0–10 | 8 / 12 / 4 | pooled |
| `sonnet_reflect_high`, `..._rep2` | Hex | Sonnet 5.5 | high | 0–10 | 8 / 12 / 4 | pooled |
| `haiku_r20` | Hex | Haiku 5.5 | medium | 0–20 | 20 / 24 / 8 | pooled |
| `hex_haiku_medium_rep2` | Hex | Haiku 5.5 | medium | 0–10 | 8 / 12 / 4 | pooled |
| `hex_haiku_reflect_high`, `..._rep2` | Hex | Haiku 5.5 | high | 0–10 | 8 / 12 / 4 | pooled |
| `hex_glm_reflect_high`, `..._rep2` | Hex | GLM 5.3 | high | 0–10 | 8 / 12 / 4 | pooled |
| `sonnet_nofeedback_high`, `..._rep2` | Hex | Sonnet 5.5 | high, **no game records** | 0–7 | 8 / 12 / 4 | pooled |
| `go_sonnet_medium`, `..._rep2` | Go | Sonnet 5.5 | medium | 0–10 | 8 / 20 / 4 | pooled, training draw changes per checkpoint |
| `go_sonnet_reflect_high`, `..._rep2` | Go | Sonnet 5.5 | high | 0–10 | 8 / 20 / 4 | as above |
| `go_haiku_medium`, `..._rep2` | Go | Haiku 5.5 | medium | 0–10 | 8 / 20 / 4 | as above |
| `go_haiku_reflect_high`, `..._rep2` | Go | Haiku 5.5 | high | 0–10 | 8 / 20 / 4 | as above |
| `go_glm_reflect_high`, `..._rep2` | Go | GLM 5.3 | high | 0–10 | 8 / 20 / 4 | as above |

GLM 5.3 (`z-ai/glm-5.3`) ran through OpenRouter's chat-completions API with 2 games at a time per
lineage (Claude: 4); all four GLM lineages were stopped by the API key's spending limit and resumed,
replaying the unfinished checkpoint.

## Main result

Held-out ID, early → late (checkpoints 0–3 → 4–10 for Hex Sonnet, 0–2 → 3–10 otherwise):

- **Hex Sonnet 5.5:** at reflection effort `medium`, 59 % → 65 % (p = 0.32); the reflector used
  5–6 of its 50 calls and wrote at most one version of a tool. At effort `high`, 73 % → **83 %**
  (p = 0.04), revising its code and running it in most games. Over checkpoints 4–10 high ends at
  83 % against 65 % for medium (z = 3.75, p = 0.0002) from the same start.
- **Go Sonnet 5.5:** effort makes no difference (late 61 % at medium, 60 % at high, p = 0.69). The
  two high-effort lineages split: one holds 85–90 %, the other falls to 15–20 % at checkpoints 6–9
  after tool timeouts and a search cap it set itself.
- **Haiku 5.5** stays flat on both games at both efforts (e.g. `haiku_r20` near 31 % over 21
  checkpoints) despite busy reflection.
- **GLM 5.3** lost most of its checkpoint-0 games to the time and call limits and fixed that in one
  reflection. That jump alone passes the flat-curve test in three of four lineages and gives its Go
  lineages P_sat of 48,000–60,000, the highest here, while its held-out ID after checkpoint 1 is flat
  or falling (late: Hex 24 %, Go 46 %). In `hex_glm_reflect_high` one reflection wrote a one-line bug
  into its search tool, and held-out ID fell from 75 % to 0 %.

Two limitation tests on Hex Sonnet at reflection effort `high` (reports 17 and 18).
Removing the final inventory drops held-out ID from 92 % to 50–54 % (`ablation_games`).
Reflection without game records (`runs.reflection_feedback = "none"`) built no tools at all;
on the same held-out openings the feedback lineages won 38 games the no-feedback lineages
lost, and lost 5 they won, from checkpoint 3 on (sign test p = 2.5e-07).

Details: `reports/TECHNICAL_REPORT.md` and reports 12, 15, 21 and 22 in the source repository.

## Fields worth knowing

- `games.messages`: the actor's conversation. Assistant turns hold visible text and tool
  calls (`bash`, `python`, `submit_action`); `tool` turns hold outputs.
- `games.diagnostics`: the feedback reflection received, per actor move. Hex: missed
  immediate wins, preventable immediate losses, connection distance before and after. Go:
  stones captured, largest capture available, liberties after, stones in atari, area margin
  before and after, and the labels `self_atari` and `pass_while_behind`.
- `games.opponent_level`: Hex, alpha-beta nodes per move; Go, GNU Go 3.8 level (5–9 train
  and ID, 10 OOD).
- `games.actor`: `red`/`blue` (Hex) or `black`/`white` (Go).
- `games.end_reason`: `finished`, `budget` (32 model calls used) or `timeout` (a second
  tool call over 240 s); the last two count as losses.
- `games.checkpoint_complete`: false for games of a checkpoint the run never completed
  (two `lineage_a` games).
- `openings.difficulty`: Hex, engine-scored; Go, GNU Go level 10's mean final margin
  against levels 5, 7 and 9. Not comparable across games.
- `inventories`: one row per file per checkpoint, so artifact changes can be diffed.
- `calls.cost_usd`: OpenRouter's reported charge for that call.
- `runs.reflection_feedback`: `full`, or `none` when reflection got only a note in place of
  the game records (limitation test 5).
- `games.messages[].thinking`, `reflections.messages[].thinking`: the model's thinking for that
  turn, as the provider returned it: a short summary for Claude, the reasoning text for GLM 5.3
  (see Limits). Recorded from the `sonnet_nofeedback_high` lineages on, so in every plan B and
  plan C run and in later checkpoints of the extended plan A runs; earlier turns did not save it.
- `thinking_replay`: `recorded` and `replayed` are the original and the new turn's text and
  tool calls; `same_call` is true when the replayed turn made exactly the recorded calls;
  `thinking` is the new turn's summary. A new sample on the same input, not the original
  reasoning. Every model run with reflection logs is replayed.

## How it differs from the paper

- 6×6 Hex and 5×5 Go only (no chess or NetHack); three models; 11 checkpoints instead of 20
  (21 for `haiku_r20`); far fewer games per checkpoint.
- Opponent: a pure-Python alpha-beta engine at 3k–100k nodes per move (train and ID) and
  1M (OOD), scaled down from the paper's 10k–1M and 10M.
- Openings: 4/5-ply instead of 10/11-ply (except `smoke`), filtered so a weak player loses
  and a 30k-node engine wins, and for `lineage_a2` dealt to the splits by engine-scored
  difficulty.
- Go: 2-ply (Black) / 3-ply (White) openings, kept if always playing the first legal action
  loses and GNU Go level 10 wins; from the empty board GNU Go as Black wins every game.
  Scored by GNU Go's `final_score` (Chinese rules, dead stones removed), komi 9.5.
- Prompts are paraphrased from the paper's Appendix I (same rules, budgets and schemas).
- Sandbox: macOS `sandbox-exec` instead of a container.

## Limits

- **What "thinking" is depends on the provider.** Closed frontier models do not return their
  raw reasoning. Through the API, Claude 4 and later return a summary of it, which Anthropic
  describes as keeping the benefits of extended thinking "while preventing misuse"; protecting
  the reasoning against distillation is another commonly cited reason for hiding it. Sonnet 5.5
  through OpenRouter returned short summaries (median about 220 characters per turn) and Haiku
  5.5 returned them only when asked. GLM 5.3 is open-weights, and OpenRouter returns the
  reasoning text it produced (median about 1,800 characters per reflection turn, up to 45,000).
  For studying how an agent learns, the GLM traces show far more of the reasoning behind each
  edit. The two kinds are not comparable: a Claude summary is a condensed account, the GLM text
  is the reasoning as generated.
- **Thinking only in the newer runs.** The models thought on every call, but until the
  no-feedback lineages the harness did not save the thinking blocks. Earlier transcripts
  contain actions and visible text only; `thinking_replay` gives summaries on the same
  reflection inputs (new samples, not the original reasoning).
- **Small samples.** 12 (Hex) or 20 (Go) held-out ID games per checkpoint; differences under about 20 points
  between halves of the run are not detectable.
- **Two lineages** per condition, except `haiku_r20` and `hex_haiku_medium_rep2` (one each).
- **Not every dollar is here.** About $0.07 from a first start of `lineage_a2` (restarted to
  add connection retries), $0.002 from an endpoint probe, $2.21 of Go cost probes and $0.33
  of a `go_sonnet_reflect_high` checkpoint redone after a crash are not included. Nor are the
  calls of checkpoints replayed after an interruption (`ledger_discarded.jsonl` in the source
  repository: $0.29–2.31 per affected lineage, $6.85 in all); the replay's games replace them.

## Privacy and provenance

Local file paths are replaced by `<repo>` and `/Users/<user>`. The export script stops if
any string looks like an API key, bearer token or email address. No personal data is in
the games; the model only saw game states and its own files.

Model outputs are from Claude Sonnet 5.5 and Claude Haiku 5.5 (Anthropic) and GLM 5.3 (Z.ai), accessed
through OpenRouter; check the providers' terms before reuse.

## Citation

Please cite the original paper:

```
@article{singh2026agentplasticity,
  title  = {Agent Plasticity: Measuring Self-Improvement Through Experience},
  author = {Singh, Harman and Bakhtin, Anton and Shao, Rulin and Synnaeve, Gabriel and
            Kulikov, Ilia and Fergus, Rob and Arora, Sanjeev and Keutzer, Kurt and
            Weston, Jason and Mahajan, Anuj and Goyal, Anirudh},
  journal = {arXiv preprint arXiv:2610.08902},
  year   = {2026}
}
```
