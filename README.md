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
| Models | 8 frontier models | Sonnet 5.5 and Haiku 5.5 (Opus 5.5 probed only) |
| Checkpoints | 20 (NetHack 40) | 5–10 |
| Learning cost per lineage | about $1,000–3,000 (chess) | measured on a smoke run first |

## Limitation tests

1. Fit and threshold sensitivity of P_sat (10 pp rule, 90 % point, 3× extrapolation).
2. Checkpoint noise: the paper runs one lineage per model; how stable is a P_sat ranking?
3. Pricing dependence of P_sat.
4. Consistency of the reported numbers with the stated game counts.
5. (Phase 2) Experience versus compute: reflection with the same budget but no feedback.
6. (Phase 2) Artifact ablation: remove the inventory, or force its use.

## Results so far

Full write-up with methods and limitations: [reports/TECHNICAL_REPORT.md](reports/TECHNICAL_REPORT.md).

| Lineage | Model | Reflection effort | Held-out ID, early → late | Report |
|---|---|---|---|---|
| `lineage_a2`, `sonnet_medium_rep2` | Sonnet 5.5 | medium | 59 % → 62 % (no plasticity) | [10](reports/10_lineage_a2.md), [12](reports/12_comparison.md) |
| `sonnet_reflect_high`, `..._rep2` | Sonnet 5.5 | high | 73 % → **83 %** | [12](reports/12_comparison.md) |
| `haiku_r20` (21 checkpoints) | Haiku 5.5 | medium | 32 % → 31 % (no plasticity) | [12](reports/12_comparison.md) |
| `hex_haiku_reflect_high`, `..._rep2` | Haiku 5.5 | high | 44 % → 39 % (no plasticity) | [15](reports/15_model_game_comparison.md) |
| `go_sonnet_reflect_high`, `..._rep2` (Go) | Sonnet 5.5 | high | 57 % → **71 %** | [15](reports/15_model_game_comparison.md) |
| `go_haiku_reflect_high`, `..._rep2` (Go) | Haiku 5.5 | high | 55 % → 48 % (no plasticity) | [15](reports/15_model_game_comparison.md) |

With two lineages per condition, high-effort reflection ends at 83 % held-out ID against
62 % for medium (z = 3.25, p = 0.001), from the same starting point. At medium effort the
reflector rarely read its game logs and wrote at most one version of a tool; at high effort it revised
its code and the actor used it in most games. Phase 1 (reports 01–04) found that a single
lineage's P_sat is noisy and that the paper's 10-point rule alone lets false rises
through; both shaped how these results are tested.

Early → late is checkpoints 0–3 → 4–7 for the reports 10–12 rows and 0–2 → 3 onward for
report 15. On 5×5 Go (report 15) Sonnet at high effort also improves
(57 % → 71 %, p = 0.01) and Haiku at high effort stays flat on both games, so Haiku's flat
result is not an effort artefact. The two Go Sonnet lineages diverge: one reaches 90 % and
passes the per-lineage flat-curve test (p = 0.04), the other stays near 30–35 % until its
last checkpoint and stops at its cost cap. How agents adapt to their limits differs too:
Sonnet moved play into a saved tool once games ran into the 32-call budget, while Haiku used
more calls per game over time and kept submitting illegal Go moves.

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
165 passed
$ uv run python scripts/validate_recovery.py
wrote reports/01_parameter_recovery.md
```
