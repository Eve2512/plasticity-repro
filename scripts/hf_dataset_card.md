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
- config_name: traces_hex_sonnet_high_fresh
  data_files:
  - split: train
    path: traces/games/hex_sonnet_high_fresh/*.jsonl
- config_name: traces_hex_sonnet_high_fresh_rep2
  data_files:
  - split: train
    path: traces/games/hex_sonnet_high_fresh_rep2/*.jsonl
- config_name: traces_hex_sonnet_medium_fresh
  data_files:
  - split: train
    path: traces/games/hex_sonnet_medium_fresh/*.jsonl
- config_name: traces_hex_sonnet_medium_fresh_rep2
  data_files:
  - split: train
    path: traces/games/hex_sonnet_medium_fresh_rep2/*.jsonl
- config_name: probe_finding2_runs
  data_files: probes/finding2/data/runs.jsonl
- config_name: probe_finding2_checkpoints
  data_files: probes/finding2/data/checkpoints.jsonl
- config_name: probe_finding2_games
  data_files: probes/finding2/data/games.jsonl
- config_name: probe_finding2_replay_games
  data_files: probes/finding2/data/replay_games.jsonl
- config_name: probe_finding2_reflections
  data_files: probes/finding2/data/reflections.jsonl
- config_name: probe_finding2_inventories
  data_files: probes/finding2/data/inventories.jsonl
- config_name: probe_finding2_calls
  data_files: probes/finding2/data/calls.jsonl
- config_name: traces_probe_finding2
  data_files:
  - split: train
    path: probes/finding2/traces/*/*.jsonl
- config_name: probe_stream_runs
  data_files: probes/stream/data/runs.jsonl
- config_name: probe_stream_checkpoints
  data_files: probes/stream/data/checkpoints.jsonl
- config_name: probe_stream_games
  data_files: probes/stream/data/games.jsonl
- config_name: probe_stream_hex_eval_games
  data_files: probes/stream/data/hex_eval_games.jsonl
- config_name: probe_stream_reflections
  data_files: probes/stream/data/reflections.jsonl
- config_name: probe_stream_inventories
  data_files: probes/stream/data/inventories.jsonl
- config_name: probe_stream_calls
  data_files: probes/stream/data/calls.jsonl
- config_name: traces_probe_stream
  data_files:
  - split: train
    path: probes/stream/traces/*/*.jsonl
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
| `runs` | 18 + 10 | a lineage: settings, cost, plasticity fit |
| `checkpoints` | 183 + 110 | a checkpoint: wins per split, learning cost, reflection outcome |
| `games` | 4,954 + 3,520 | a game: opening, moves, per-move diagnostics, token use, **full transcript** with thinking where recorded |
| `reflections` | 171 + 105 | a reflection attempt: **full transcript** with thinking where recorded, validator result |
| `inventories` | 814 + 578 | a file the agent saved, at a checkpoint (code, notes, tracking JSON) |
| `calls` | 62,236 + 48,269 | a model call: tokens (input, cached, cache write, output) and charged cost |
| `openings` | 366 + 152 | a starting position from the legacy, contested, pooled or fresh bank (fresh: held-out openings no original run played; on Hex `checkpoint` says which checkpoint plays it) |
| `thinking_replay` | 830 + 547 | a saved reflection turn sent again with thinking summaries on: recorded and replayed calls, summary |
| `ablation_games` | 144 + 240 | a held-out ID game from a final checkpoint with the inventory kept, removed or forced, or on 40 fresh Go openings (`arm` = `fresh`) |
| `trace_viewer` | 660 | every reflection (with replayed summaries, labelled, where none was recorded) and ablation game, as a transcript in Pi's session format, for the trace viewer |
| `traces_<run_id>` | 8,474 in all | every game of one run, in the same format (one config per run: the Hub's conversion timed out on one config of 3,918 files) |

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
| `hex_sonnet_high_fresh`, `..._rep2` | Hex | Sonnet 5.5 | high | 0–10 | 8 / 12 / 4 | fresh: held-out ID new at every checkpoint, train and OOD pooled |
| `hex_sonnet_medium_fresh`, `..._rep2` | Hex | Sonnet 5.5 | medium | 0–10 | 8 / 12 / 4 | as above |
| `go_sonnet_medium`, `..._rep2` | Go | Sonnet 5.5 | medium | 0–10 | 8 / 20 / 4 | pooled, training draw changes per checkpoint |
| `go_sonnet_reflect_high`, `..._rep2` | Go | Sonnet 5.5 | high | 0–10 | 8 / 20 / 4 | as above |
| `go_haiku_medium`, `..._rep2` | Go | Haiku 5.5 | medium | 0–10 | 8 / 20 / 4 | as above |
| `go_haiku_reflect_high`, `..._rep2` | Go | Haiku 5.5 | high | 0–10 | 8 / 20 / 4 | as above |
| `go_glm_reflect_high`, `..._rep2` | Go | GLM 5.3 | high | 0–10 | 8 / 20 / 4 | as above |

GLM 5.3 (`z-ai/glm-5.3`) ran through OpenRouter's chat-completions API with 2 games at a time per
lineage (Claude: 4); all four GLM lineages were stopped by the API key's spending limit and resumed,
replaying the unfinished checkpoint.

## Finding 2 probe (`probes/finding2/`)

A probe of the paper's Finding 2 (the best performer is not the most plastic), run outside the
repository's scripts; the result is in `FINDINGS.md`, section 9, of the source repository. Held-out
ID games are played against the alpha-beta engine at 1M nodes per move (the OOD level) on the
`hex_sonnet_high_fresh` fresh openings; everything else is as in those runs. $45.39 in all
($3.19 of an earlier screening at the usual levels is not here: its games were not kept).

| Config | Rows | One row is |
|---|---|---|
| `probe_finding2_runs`, `_checkpoints`, `_games`, `_reflections`, `_inventories`, `_calls` | 1, 6, 84, 5, 27, 687 | as in the main tables, for `probe_f2_opus_lineage`: Opus 5.5 (`anthropic/claude-opus-5.5`), checkpoints 0–5, 8 training games per checkpoint, reflection at effort high, held-out ID only at checkpoints 3–5, no OOD games |
| `probe_finding2_replay_games` | 300 | a held-out ID game vs 1M nodes with a saved or an empty inventory; `inventory`, `inventory_checkpoint` and `opening_bank_checkpoint` say which |
| `traces_probe_finding2` | 389 | every probe game and reflection in Pi's session format |

`replay_games` holds six `run_id`s: `probe_f2_sonnet_replay_1` / `_2` (the saved inventories of
`hex_sonnet_high_fresh` / `_rep2`, checkpoints 0–5), `probe_f2_opus_empty_cp0` (Opus, empty
inventory, checkpoint-0 openings), and the start test on the 48 fresh openings of checkpoints
6–9, which no run had played at 1M: `probe_f2_opus_empty_start` (Opus, one game per opening)
and `probe_f2_sonnet_empty_start_1` / `_2` (Sonnet, two games per opening).

## Hex → Go stream probe (`probes/stream/`)

A continual-learning probe after
[Are Self-Evolving Agents Continual Learners?](https://arxiv.org/abs/2610.25858) (Chen et al., 2026),
run outside the repository's scripts and not written up yet. Two Go lineages (Sonnet 5.5, reflection
at effort high, checkpoints 0–5, 8 training games per checkpoint) start from the checkpoint-10
inventory of a Hex lineage instead of an empty one: `probe_stream_high_1` from
`hex_sonnet_high_fresh`, `probe_stream_high_2` from `hex_sonnet_high_fresh_rep2`. Go held-out ID
(20 games) is played only at checkpoints 0, 3 and 5, with no OOD games. At the same checkpoints the
current inventory also plays 24 held-out Hex games (fresh openings of banks 9 and 10, usual levels) to
measure forgetting; they are hidden from reflection and not in the learning cost. $15.63 in all.

| Config | Rows | One row is |
|---|---|---|
| `probe_stream_runs`, `_checkpoints`, `_games`, `_reflections`, `_inventories`, `_calls` | 2, 12, 216, 10, 78, 4,000 | as in the main tables (Go); `runs.inventory_source` names the starting Hex inventory |
| `probe_stream_hex_eval_games` | 144 | a held-out Hex game played with the stream's inventory at checkpoint `inventory_checkpoint` (0, 3 or 5); `opening_bank` is 9 or 10 |
| `traces_probe_stream` | 370 | every stream game (Go and Hex) and reflection in Pi's session format |

`probe_stream_calls` also holds the Hex eval games' calls; their cost is in `billed_usd`, not in
`learning_cost_usd`.

## Main result

Held-out ID, early → late (checkpoints 0–3 → 4–10 for Hex Sonnet, 0–2 → 3–10 otherwise):

- **Hex Sonnet 5.5:** at reflection effort `medium`, 59 % → 65 % (p = 0.32); the reflector used
  5–6 of its 50 calls and wrote at most one version of a tool. At effort `high`, 73 % → **83 %**
  (p = 0.04), revising its code and running it in most games. Over checkpoints 4–10 high ends at
  83 % against 65 % for medium (z = 3.75, p = 0.0002) from the same start. Held-out openings
  are fixed and the opponents deterministic, so later checkpoints largely replay the same games;
  per opening, high effort is better on 10 of 12 and worse on 1 (sign test p = 0.012, report 23).
  Re-run with held-out openings new at every checkpoint (`*_fresh`, report 24), so no held-out game
  repeats: high effort 72 % → 88 %, medium 57 % → 56 %, and over checkpoints 4–10 high is better on
  46 of 84 openings and worse on 6 (sign test p = 1e-08).
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
- **Go, fresh openings:** each Go lineage's final inventory played 40 openings no run had played
  (`ablation_games`, `arm = "fresh"`). Sonnet and Haiku both beat GLM opening by opening (24 better /
  1 worse, 18 / 3); Sonnet against Haiku is not established (13 / 8, p = 0.38) because the two Sonnet
  lineages score 95 % and 50 % (report 25).

Two limitation tests on Hex Sonnet at reflection effort `high` (reports 17 and 18).
Removing the final inventory drops held-out ID from 92 % to 50–54 % (`ablation_games`).
Reflection without game records (`runs.reflection_feedback = "none"`) built no tools at all;
on the same held-out openings the feedback lineages won 38 games the no-feedback lineages
lost, and lost 5 they won, from checkpoint 3 on (per opening: 8 better, 1 worse, p = 0.039).

Details: `reports/TECHNICAL_REPORT.md` and reports 12, 15, 21–25 in the source repository.

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
- **Small samples, replayed.** 12 (Hex) or 20 (Go) held-out ID games per checkpoint, the same openings
  at every checkpoint except in the `*_fresh` runs, so later checkpoints often replay earlier games
  (report 23); differences under about 20 points between halves of a run are not detectable.
- **Two lineages** per condition, except `haiku_r20` and `hex_haiku_medium_rep2` (one each).
- **Not every dollar is here.** About $0.07 from a first start of `lineage_a2` (restarted to
  add connection retries), $0.002 from an endpoint probe, $2.21 of Go cost probes and $0.33
  of a `go_sonnet_reflect_high` checkpoint redone after a crash are not included, nor $2.27 from a
  doubled start of the `*_fresh` runs, which were restarted from checkpoint 0. Nor are the
  calls of checkpoints replayed after an interruption (`ledger_discarded.jsonl` in the source
  repository: $0.29–2.31 per affected lineage, $6.85 in all); the replay's games replace them.

## Privacy and provenance

Local file paths are replaced by `<repo>` and `/Users/<user>` (in the Finding 2 probe also
`<probe>` and `<tmp>`, the session folders it ran from). The export script stops if
any string looks like an API key, bearer token or email address. No personal data is in
the games; the model only saw game states and its own files.

Model outputs are from Claude Sonnet 5.5, Claude Haiku 5.5 and, in the Finding 2 probe, Claude
Opus 5.5 (Anthropic) and GLM 5.3 (Z.ai), accessed
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
