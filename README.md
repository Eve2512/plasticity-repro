# Agent Plasticity: reproduction and limitation tests

A scaled-down reproduction of
[Agent Plasticity: Measuring Self-Improvement Through Experience](https://arxiv.org/abs/2610.08902)
(Singh et al., Meta Superintelligence Labs / UC Berkeley, October 2026).


TLDR: they studied self-improvement in a controlled setting where agents amortize
past experience into reusable artifacts that are inherited by future instances. they measured performance on training  at specific checkpoints and held-out environment interactions while accounting for learning cost. 
The whole crux of this paper is that they introduce agent plasticity, the efficiency with which an agent converts 
experience into gains in future held-out performance.



The paper freezes a model's weights and lets it improve only through persistent
artifacts (Python tools, notes, skills) that it writes after each round of games.
**Agent plasticity** is the held-out score gain per $1,000 of learning cost.

The authors did not release code. This repository rebuilds the protocol from the
paper's equations (Section 2) and appendix (Appendix B settings, Appendix I prompts).

## Scope

| Part | Paper | This repo |
|---|---|---|
| Metrics (Eq. 2–5, bootstrap) | yes | **phase 1 done**, no API cost |
| Harness (sandbox, reflection, validator, ledger) | not released | **phase 2: built, dry-run tested and run on Hex and 5×5 Go** |
| Games | Chess, 5×5 Go, 6×6 Hex, NetHack | 6×6 Hex and 5×5 Go (GNU Go opponent, calibration in report 13) |
| Models | 8 frontier models | Sonnet 5.5 and Haiku 5.5; GLM 5.3 in plan C (reports [20](reports/20_glm_tool_rewrite.md), [21](reports/21_glm_vs_claude.md)); Opus 5.5 probed only |
| Checkpoints | 20 (NetHack 40) | 11 (checkpoints 0–10); one Haiku lineage 21 |
| Learning cost per lineage | about $1,000–3,000 (chess) | measured on a smoke run first |

## Limitation tests

1. Fit and threshold sensitivity of P_sat (10 pp rule, 90 % point, 3× extrapolation).
2. Checkpoint noise: the paper runs one lineage per model; how stable is a P_sat ranking?
3. Pricing dependence of P_sat.
4. Consistency of the reported numbers with the stated game counts.
5. (Phase 2) Experience versus compute: reflection with the same budget but no feedback
   ([report 18](reports/18_experience_vs_compute.md)).
6. (Phase 2) Artifact ablation: remove the inventory, or force its use
   ([report 17](reports/17_artifact_ablation.md)).

## Results so far

Full write-up with methods and limitations: [reports/TECHNICAL_REPORT.md](reports/TECHNICAL_REPORT.md).

| Lineage | Model | Reflection effort | Held-out ID, early → late | Report |
|---|---|---|---|---|
| `lineage_a2`, `sonnet_medium_rep2` | Sonnet 5.5 | medium | 59 % → 65 % (p = 0.32) | [10](reports/10_lineage_a2.md), [12](reports/12_comparison.md) |
| `sonnet_reflect_high`, `..._rep2` | Sonnet 5.5 | high | 73 % → **83 %** (p = 0.04) | [12](reports/12_comparison.md) |
| `haiku_r20` (21 checkpoints) | Haiku 5.5 | medium | 32 % → 31 % (no plasticity) | [12](reports/12_comparison.md) |
| `hex_haiku_medium_rep2` | Haiku 5.5 | medium | 50 % → 38 % (no plasticity) | [10](reports/10_hex_haiku_medium_rep2.md) |
| `hex_haiku_reflect_high`, `..._rep2` | Haiku 5.5 | high | 44 % → 40 % (no plasticity) | [15](reports/15_model_game_comparison.md) |
| `go_sonnet_reflect_high`, `..._rep2` (Go) | Sonnet 5.5 | high | 57 % → 60 % (p = 0.57; one lineage 75 % → 90 %) | [15](reports/15_model_game_comparison.md) |
| `go_haiku_reflect_high`, `..._rep2` (Go) | Haiku 5.5 | high | 55 % → 47 % (no plasticity) | [15](reports/15_model_game_comparison.md) |
| `go_sonnet_medium`, `..._rep2` (Go) | Sonnet 5.5 | medium | 60 % → 61 % (no plasticity) | [22](reports/22_go_effort.md) |
| `go_haiku_medium`, `..._rep2` (Go) | Haiku 5.5 | medium | 47 % → 52 % (p = 0.36) | [22](reports/22_go_effort.md) |

With two lineages per condition, high-effort reflection ends at 83 % held-out ID against
65 % for medium over checkpoints 4–10 (z = 3.75, p = 0.0002), from the same starting point. At medium effort the
reflector rarely read its game logs and wrote at most one version of a tool; at high effort it revised
its code and the actor used it in most games. Phase 1 (reports 01–04) found that a single
lineage's P_sat is noisy and that the paper's 10-point rule alone lets false rises
through; both shaped how these results are tested.

Early → late is checkpoints 0–3 → 4–10 for the Hex Sonnet rows, 0–9 → 10–20 for
`haiku_r20`, and 0–2 → 3–10 for the rest (report 15). Haiku at high effort stays flat on
both games, so Haiku's flat result is not an effort artefact. On 5×5 Go the pooled Sonnet
gain read 57 % → 71 % (p = 0.01) through checkpoint 7 and is gone at checkpoint 10. The two
Go Sonnet lineages diverge: one reaches 90 % and passes the per-lineage flat-curve test
(p = 0.019); the other forfeited 20 of 32 games on time at checkpoint 6, capped its own
search, and sat at 15 % for checkpoints 7–9 before ending at 50 %. How agents adapt to their
limits differs too: Sonnet moved play into a saved tool once games ran into the 32-call
budget, while Haiku used more calls per game over time and kept submitting illegal Go moves.
The effort result is a Hex result: on Go, late held-out ID is 61 % at medium and 60 % at high
for Sonnet (p = 0.69), and 52 % and 47 % for Haiku ([report 22](reports/22_go_effort.md)).

GLM 5.3 on Hex (plan C) shows a different way to fail: one reflection rewrote its search
tool with a one-line bug, held-out ID fell from 75 % to 0 %, and the next reflection fixed a
different bug it took for the cause ([report 20](reports/20_glm_tool_rewrite.md)).
Against Claude ([report 21](reports/21_glm_vs_claude.md)), GLM lost most of its checkpoint-0
games to the time and call limits and fixed that in one reflection. That jump alone passes
the flat-curve test in three of its four lineages and gives its Go lineages P_sat of
48,000–60,000, the highest in the project, although its held-out ID after checkpoint 1 is
flat or falling (late: Hex 24 %, Go 46 %, against Sonnet's 83 % and 60 %).

Limitation tests 5 and 6 (Hex, Sonnet, reflection effort high):

| Test | Result | Report |
|---|---|---|
| 6: remove the final inventory | held-out ID 92 % / 92 % with tools, 54 % / 50 % without; forcing tool use adds nothing | [17](reports/17_artifact_ablation.md) |
| 5: reflection without game records | the reflector builds no tools (4 of 50 calls per round); held-out ID stays at 62 % pooled | [18](reports/18_experience_vs_compute.md) |
| 5: same openings, feedback vs none | level at checkpoints 0–2; from checkpoint 3 on, 38 games won only with feedback, 5 only without (p = 2.5e-07) | [18](reports/18_experience_vs_compute.md) |

The gain lives in the saved tools, and the tools come from the game records. Without records the
reflector chose not to spend its budget, so test 5 does not isolate extra reflection compute. The
no-feedback lineages still work as a control on identical openings. With nothing changing, the control
still fell from 72 % to 56 % held-out ID. A single lineage's curve can move that much without any learning.

Thinking: the original runs kept no thinking. [Report 16](reports/16_thinking_replay.md) replays every
saved reflection turn of all 13 runs with thinking summaries on ($9.40). Haiku returned a summary on
96–100 % of turns, Sonnet on 0–89 %. The replayed turn matched the recorded calls in only 5–40 % of
turns, so these summaries describe the model's reasoning on the same input, not the original run's.
Runs from test 5 on record thinking summaries as they go.

[Report 19](reports/19_thinking.md) reads those summaries for how learning happened. The lineages
that learned tested new tool versions in games against the current one before installing them.
Haiku reflected like an auditor (failure-mode bookkeeping, never a match between versions). One Go
Sonnet lineage tested only against its own engines and kept installing unproven rewrites. With its
final tools the actor thinks on 4–6 % of its turns; without them, on 66–70 %.

## Layout

```
plasticity/   metric code (score, cost, fit, P_sat, bootstrap, pricing)
envs/         6x6 Hex and 5x5 Go rules, opponents (alpha-beta, GNU Go over GTP), opening banks, move diagnostics
harness/      sandbox, game API, inventory validator, prompts, episode, reflection, runner
tests/        pytest suite
scripts/      experiments that write the markdown files in reports/
reports/      results
docs/         protocol notes and deviations from the paper
runs/         run output (git-ignored)
```

## How a lineage runs

```
checkpoint t, inventory I_t
 ├─ train games ──► actor (fresh context, sandboxed Bash + Python, 32 calls)
 ├─ held-out ID ──► same, scored only, never shown to reflection
 ├─ held-out OOD ─► same, stronger opponent
 └─ reflection on train games (Bash only, 50 calls)
       └─ validator: tracking schemas + every tool loads ─► I_{t+1}, or keep I_t after 3 rejections
```

The scripted dry run (`uv run python scripts/dry_run_hex.py`) exercises all of this
without an API: see [reports/06_dry_run.md](reports/06_dry_run.md).
Deviations from the paper are listed in [docs/PROTOCOL_NOTES.md](docs/PROTOCOL_NOTES.md).

## Usage

```bash
uv sync
uv run pytest
uv run python scripts/validate_recovery.py
```

What you see:

```
$ uv run pytest
........................................................................ [ 43%]
........................................................................ [ 87%]
.....................                                                    [100%]
170 passed
$ uv run python scripts/validate_recovery.py
wrote reports/01_parameter_recovery.md
```
