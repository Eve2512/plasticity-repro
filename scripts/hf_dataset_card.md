---
pretty_name: "Agent Plasticity on 6x6 Hex: Claude Sonnet 5.5 traces"
license: cc-by-4.0
language:
- en
tags:
- agents
- self-improvement
- tool-use
- reflection
- hex
- reproduction
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
---

# Agent Plasticity on 6x6 Hex: Claude Sonnet 5.5 traces

Agent traces from a scaled-down, independent reproduction of
[Agent Plasticity: Measuring Self-Improvement Through Experience](https://arxiv.org/abs/2610.08902)
(Singh et al., 2026). The paper's authors did not release code or data; this harness was
rebuilt from the paper's equations and appendix.

A frozen model plays 6×6 Hex against an alpha-beta engine. Between checkpoints the same
model reflects on its training games and edits a persistent inventory (Python tools,
notes, tracking files) that the next checkpoint inherits. Held-out games are never shown
to reflection.

## What is in it

| Config | Rows | One row is |
|---|---|---|
| `runs` | 7 | a lineage: settings, cost, plasticity fit |
| `checkpoints` | 56 | a checkpoint: wins per split, learning cost, reflection outcome |
| `games` | 1,906 | a game: opening, moves, per-move diagnostics, token use, **full transcript** |
| `reflections` | 53 | a reflection attempt: full transcript, validator result |
| `inventories` | 227 | a file the agent saved, at a checkpoint (code, notes, tracking JSON) |
| `calls` | 23,919 | a model call: tokens (input, cached, cache write, output) and charged cost |
| `openings` | 234 | a starting position from the legacy, contested or pooled bank |

Runs (via OpenRouter; games always at effort `medium`):

| `run_id` | Model | Reflection effort | Checkpoints | Games per checkpoint (train / ID / OOD) | Openings |
|---|---|---|---|---|---|
| `smoke` | Sonnet 5.5 | medium | 0–1 | 4 / 4 / 2 | legacy (10/11-ply) |
| `lineage_a` | Sonnet 5.5 | medium | 0 (+2 games of 1) | 8 / 12 / 4 | contested (stopped: ID bank harder than train) |
| `lineage_a2` | Sonnet 5.5 | medium | 0–7 | 8 / 12 / 4 | pooled |
| `sonnet_medium_rep2` | Sonnet 5.5 | medium | 0–7 | 8 / 12 / 4 | pooled |
| `sonnet_reflect_high` | Sonnet 5.5 | high | 0–7 | 8 / 12 / 4 | pooled |
| `sonnet_reflect_high_rep2` | Sonnet 5.5 | high | 0–7 | 8 / 12 / 4 | pooled |
| `haiku_r20` | Haiku 5.5 | medium | 0–20 | 20 / 24 / 8 | pooled |

## Main result

With reflection at effort `medium`, Sonnet 5.5 shows **no plasticity** in two lineages
(held-out ID 59 % → 62 % between checkpoints 0–3 and 4–7): the reflector used 5–6 of its
50 calls, rarely read its game logs, and wrote at most one version of a tool. With
reflection at effort `high`, two lineages rise from 73 % to **83 %**, revising their code
and running it in most games. From the same start (15/24 each at checkpoint 0), high ends
at 83 % against 62 % for medium over checkpoints 4–7 (z = 3.25, p = 0.001). Haiku 5.5 stays
near 31 % over 21 checkpoints despite busy reflection. Details: `reports/12_comparison.md`
in the source repository.

## Fields worth knowing

- `games.messages`: the actor's conversation. Assistant turns hold visible text and tool
  calls (`bash`, `python`, `submit_action`); `tool` turns hold outputs.
- `games.diagnostics`: per actor move, missed immediate wins, preventable immediate
  losses, and connection distance before and after (the feedback reflection received).
- `games.checkpoint_complete`: false for the two `lineage_a` games played after the
  checkpoint it stopped at.
- `inventories`: one row per file per checkpoint, so artifact changes can be diffed.
- `calls.cost_usd`: OpenRouter's reported charge for that call.

## How it differs from the paper

- 6×6 Hex only; one model; 8 checkpoints instead of 20; far fewer games per checkpoint.
- Opponent: a pure-Python alpha-beta engine at 3k–100k nodes per move (train and ID) and
  1M (OOD), scaled down from the paper's 10k–1M and 10M.
- Openings: 4/5-ply instead of 10/11-ply (except `smoke`), filtered so a weak player loses
  and a 30k-node engine wins, and for `lineage_a2` dealt to the splits by engine-scored
  difficulty.
- Prompts are paraphrased from the paper's Appendix I (same rules, budgets and schemas).
- Sandbox: macOS `sandbox-exec` instead of a container.

## Limits

- **No hidden reasoning.** The API returns thinking blocks empty by default, so transcripts
  contain actions and visible text only.
- **Small samples.** 12 held-out ID games per checkpoint; differences under about 20 points
  between halves of the run are not detectable.
- **Two lineages** per reflection-effort condition for Sonnet, one for Haiku.
- **Not every dollar is here.** About $0.07 from a first start of `lineage_a2` (restarted to
  add connection retries) and $0.002 from an endpoint probe are not included.

## Privacy and provenance

Local file paths are replaced by `<repo>` and `/Users/<user>`. The export script stops if
any string looks like an API key, bearer token or email address. No personal data is in
the games; the model only saw game states and its own files.

Model outputs are from Claude Sonnet 5.5 (Anthropic) accessed through OpenRouter; check
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
