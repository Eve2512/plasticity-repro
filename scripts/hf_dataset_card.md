---
pretty_name: "Agent Plasticity on 6x6 Hex and 5x5 Go: Claude Sonnet 5.5 and Haiku 5.5 traces"
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
    - traces/games/*.jsonl
    - traces/reflections/*.jsonl
    - traces/ablation/*.jsonl
---

# Agent Plasticity on 6x6 Hex and 5x5 Go: Claude Sonnet 5.5 and Haiku 5.5 traces

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
| `runs` | 11 + 4 | a lineage: settings, cost, plasticity fit |
| `checkpoints` | 88 + 30 | a checkpoint: wins per split, learning cost, reflection outcome |
| `games` | 2,674 + 992 | a game: opening, moves, per-move diagnostics, token use, **full transcript** |
| `reflections` | 81 + 27 | a reflection attempt: full transcript, validator result |
| `inventories` | 352 + 155 | a file the agent saved, at a checkpoint (code, notes, tracking JSON) |
| `calls` | 32,651 + 13,525 | a model call: tokens (input, cached, cache write, output) and charged cost |
| `openings` | 234 + 112 | a starting position from the legacy, contested or pooled bank |
| `thinking_replay` | 830 + 547 | a saved reflection turn sent again with thinking summaries on: recorded and replayed calls, summary |
| `ablation_games` | 144 + 0 | a held-out ID game from a final checkpoint with the inventory kept, removed or forced (`arm`) |
| `trace_viewer` | 636 | a reflection, ablation game or game with thinking, as a transcript in Pi's session format with thinking summaries (live, or replayed and labelled), for the trace viewer |

In `trace_viewer` the `harness` column says `pi`. The traces were not run in Pi. The harness
here is this project's own; its transcripts are written in Pi's session format because the
Hub's trace viewer reads that format, so the Hub names the harness after the format.

Runs (via OpenRouter; games always at effort `medium`):

| `run_id` | Game | Model | Reflection effort | Checkpoints | Games per checkpoint (train / ID / OOD) | Openings |
|---|---|---|---|---|---|---|
| `smoke` | Hex | Sonnet 5.5 | medium | 0–1 | 4 / 4 / 2 | legacy (10/11-ply) |
| `lineage_a` | Hex | Sonnet 5.5 | medium | 0 (+2 games of 1) | 8 / 12 / 4 | contested (stopped: ID bank harder than train) |
| `lineage_a2` | Hex | Sonnet 5.5 | medium | 0–7 | 8 / 12 / 4 | pooled |
| `sonnet_medium_rep2` | Hex | Sonnet 5.5 | medium | 0–7 | 8 / 12 / 4 | pooled |
| `sonnet_reflect_high` | Hex | Sonnet 5.5 | high | 0–7 | 8 / 12 / 4 | pooled |
| `sonnet_reflect_high_rep2` | Hex | Sonnet 5.5 | high | 0–7 | 8 / 12 / 4 | pooled |
| `haiku_r20` | Hex | Haiku 5.5 | medium | 0–20 | 20 / 24 / 8 | pooled |
| `hex_haiku_reflect_high`, `..._rep2` | Hex | Haiku 5.5 | high | 0–7 | 8 / 12 / 4 | pooled |
| `go_sonnet_reflect_high` | Go | Sonnet 5.5 | high | 0–5 (6 played, stopped by its cost cap) | 8 / 20 / 4 | pooled, training draw changes per checkpoint |
| `go_sonnet_reflect_high_rep2` | Go | Sonnet 5.5 | high | 0–7 | 8 / 20 / 4 | as above |
| `go_haiku_reflect_high`, `..._rep2` | Go | Haiku 5.5 | high | 0–7 | 8 / 20 / 4 | as above |
| `sonnet_nofeedback_high`, `..._rep2` | Hex | Sonnet 5.5 | high, **no game records** | 0–7 | 8 / 12 / 4 | pooled |

## Main result

With reflection at effort `medium`, Sonnet 5.5 shows **no plasticity** in two lineages
(held-out ID 59 % → 62 % between checkpoints 0–3 and 4–7): the reflector used 5–6 of its
50 calls, rarely read its game logs, and wrote at most one version of a tool. With
reflection at effort `high`, two lineages rise from 73 % to **83 %**, revising their code
and running it in most games. From the same start (15/24 each at checkpoint 0), high ends
at 83 % against 62 % for medium over checkpoints 4–7 (z = 3.25, p = 0.001). Haiku 5.5 stays
near 31 % over 21 checkpoints despite busy reflection. Details: `reports/12_comparison.md`
in the source repository.

All later runs reflect at effort `high` (report 15). Between checkpoints 0–2 and 3 onward,
Sonnet rises on both games (Hex 69 % → 83 %, Go 57 % → 71 %) and Haiku does not (Hex 44 % →
39 %, Go 55 % → 48 %). The two Go Sonnet lineages diverge: one reaches 90 %, the other stays
near 30–35 % until its last complete checkpoint and then loses 9 of 32 games to tool
timeouts after calling its own tool with a much larger search budget.

Two limitation tests on Hex Sonnet at reflection effort `high` (reports 17 and 18).
Removing the final inventory drops held-out ID from 92 % to 50–54 % (`ablation_games`).
Reflection without game records (`runs.reflection_feedback = "none"`) built no tools at all;
on the same held-out openings the feedback lineages won 38 games the no-feedback lineages
lost, and lost 5 they won, from checkpoint 3 on (sign test p = 2.5e-07).

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
  (two `lineage_a` games and checkpoint 6 of `go_sonnet_reflect_high`).
- `openings.difficulty`: Hex, engine-scored; Go, GNU Go level 10's mean final margin
  against levels 5, 7 and 9. Not comparable across games.
- `inventories`: one row per file per checkpoint, so artifact changes can be diffed.
- `calls.cost_usd`: OpenRouter's reported charge for that call.
- `runs.reflection_feedback`: `full`, or `none` when reflection got only a note in place of
  the game records (limitation test 5).
- `games.messages[].thinking`, `reflections.messages[].thinking`: the model's thinking
  summary for that turn. Only in the `sonnet_nofeedback_high` lineages; earlier runs did
  not save it.
- `thinking_replay`: `recorded` and `replayed` are the original and the new turn's text and
  tool calls; `same_call` is true when the replayed turn made exactly the recorded calls;
  `thinking` is the new turn's summary. A new sample on the same input, not the original
  reasoning. Every model run with reflection logs is replayed.

## How it differs from the paper

- 6×6 Hex and 5×5 Go only (no chess or NetHack); two models; 8 checkpoints instead of 20
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

- **Thinking only in the newest runs.** The models thought on every call, but until the
  no-feedback lineages the harness did not save the thinking blocks (Sonnet 5.5 through
  OpenRouter returned short summaries; Haiku 5.5 returned them empty unless asked). Earlier
  transcripts contain actions and visible text only; `thinking_replay` gives summaries on
  the same reflection inputs. Thinking is always a summary, never the raw chain of thought.
- **Small samples.** 12 (Hex) or 20 (Go) held-out ID games per checkpoint; differences under about 20 points
  between halves of the run are not detectable.
- **Two lineages** per condition, except `haiku_r20` (one).
- **Not every dollar is here.** About $0.07 from a first start of `lineage_a2` (restarted to
  add connection retries), $0.002 from an endpoint probe, $2.21 of Go cost probes and $0.33
  of a `go_sonnet_reflect_high` checkpoint redone after a crash are not included.

## Privacy and provenance

Local file paths are replaced by `<repo>` and `/Users/<user>`. The export script stops if
any string looks like an API key, bearer token or email address. No personal data is in
the games; the model only saw game states and its own files.

Model outputs are from Claude Sonnet 5.5 and Claude Haiku 5.5 (Anthropic) accessed through OpenRouter; check
both providers' terms before reuse.

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
