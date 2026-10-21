# Agent Plasticity: reproduction and limitation tests

A scaled-down reproduction of
[Agent Plasticity: Measuring Self-Improvement Through Experience](https://arxiv.org/abs/2610.08902)
(Singh et al., Meta Superintelligence Labs / UC Berkeley, October 2026).

The paper freezes a model's weights and lets it improve only through persistent
artifacts (Python tools, notes, skills) that it writes after each round of games.
**Agent plasticity** is the held-out score gain per $1,000 of learning cost.

The authors did not release code. This repository rebuilds the protocol from the
paper's equations (Section 2) and appendix (Appendix B settings, Appendix I prompts).

## Scope

| Part | Paper | This repo |
|---|---|---|
| Metrics (Eq. 2–5, bootstrap) | yes | **phase 1 done**, no API cost |
| Harness (sandbox, reflection, validator, ledger) | not released | **phase 2: built and dry-run tested for Hex**, no API cost |
| Games | Chess, 5×5 Go, 6×6 Hex, NetHack | 6×6 Hex now, 5×5 Go next |
| Models | 8 frontier models | 1–2 inexpensive models |
| Checkpoints | 20 (NetHack 40) | 5–10 |
| Learning cost per lineage | about $1,000–3,000 (chess) | measured on a smoke run first |

## Limitation tests

1. Fit and threshold sensitivity of P_sat (10 pp rule, 90 % point, 3× extrapolation).
2. Checkpoint noise: the paper runs one lineage per model; how stable is a P_sat ranking?
3. Pricing dependence of P_sat.
4. Consistency of the reported numbers with the stated game counts.
5. (Phase 2) Experience versus compute: reflection with the same budget but no feedback.
6. (Phase 2) Artifact ablation: remove the inventory, or force its use.

## Layout

```
plasticity/   metric code (score, cost, fit, P_sat, bootstrap, pricing)
envs/         6x6 Hex rules, alpha-beta opponent, opening banks, move diagnostics
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
........................................................................ [ 76%]
......................                                                   [100%]
94 passed
$ uv run python scripts/validate_recovery.py
wrote reports/01_parameter_recovery.md
```
