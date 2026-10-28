# Protocol notes (from arXiv:2610.08902v1)

Section and table numbers refer to the paper. Values here are the reference for
the harness in phase 2.

## Agent lineage (Section 2.1)

- Agent at checkpoint t = frozen model M + inventory I_t (Python tools, strategies or skills, memory).
- Each acting episode starts in a fresh context. Only the inventory persists.
- Reflection: I_{t+1} = U_M(I_t, E_t^train). The same model acts and reflects.
- Updates must pass structural and executable checks. A rejected attempt keeps I_t.
  Retry limit: 6 attempts in chess, 3 in Go and Hex. Rejected attempts count toward cost.
- Splits: train (seen by reflection), held-out ID (same difficulty), held-out OOD (stronger opponent).
  Held-out games and scores never reach reflection.

## Metrics (Sections 2.1–2.2)

- Score: S = 100 (W + 0.5 D) / N. An unfinished game is a loss.
- Cumulative cost (Eq. 2): C_t = Σ_{u<t} (c_train_u + c_reflect_u), C_0 = 0. Dollars from token counts.
- Average plasticity (Eq. 3): P = (S_T − S_0) / C_T, reported per $1,000.
- Saturation fit (Eq. 4): Ŝ(C) = S0 + A C^h / (C^h + C50^h), all four parameters fitted
  jointly by binomial maximum likelihood on held-out ID scores.
- P_sat (Eq. 5): C* = cost of the first observed checkpoint where the fit reaches 90 % of its rise;
  P_sat = (Ŝ(C*) − S0) / C*.
  - If 0.9 A < 10 pp, P_sat = 0 ("no rise").
  - If no observed checkpoint reaches 90 %, extrapolate the 90 % point up to 3× the final cost.
  - If it is beyond 3×, report plasticity to date: fitted rise at final cost / final cost.
  - Intervals: parametric bootstrap.

## Hex and Go settings (Table 2, Appendix I)

| | 5×5 Go | 6×6 Hex |
|---|---|---|
| Rules | Chinese area scoring, positional superko, no suicide, komi 9.5, 75-action cap | first connection wins; red north–south, blue west–east |
| Opponent train / ID | GNU Go levels 5–9 | alpha–beta, 10k–1M nodes per move |
| Opponent OOD | GNU Go level 10 | alpha–beta, 10M nodes per move |
| Games per checkpoint | 20 train, 20 ID, 12 OOD, both colours | 40 train, 40 ID, 32 OOD, both colours |
| Openings | training seeds change per checkpoint, held-out seeds fixed | fixed banks; 10-ply (red) / 11-ply (blue) openings |
| Actor budget | 32 model calls per game, 240 s per tool call | same |
| Reflection budget | 50 model calls, 300 s per Bash call | same |
| Reflection feedback | captures, liberties, self-atari, passing while behind, area margin | missed immediate wins, preventable immediate losses, connection distance |

## Deviations in this reproduction

| Paper | Here | Why |
|---|---|---|
| Native alpha–beta, 10k–1M nodes (train/ID), 10M (OOD) | Python alpha–beta, 3k–100k (train/ID), 1M (OOD) | A pure-Python engine runs about 20–30k nodes per second |
| Isolated Python container | macOS `sandbox-exec`: no network, no reads under `/Users` or the run folder except the inventory and workspace, writes only to the session or workspace, empty environment | No container runtime on this machine |
| Prompts in Appendix I | Paraphrased in `harness/prompts.py` (same rules, budgets, schemas) | The wording is the paper's; only the substance is reused |
| Restricted Python (imports unavailable) | Safe-builtins whitelist; `import` raises; `load_python` reads only the inventory and session | The paper's exact whitelist is not given |
| After a tool timeout: one recovery call | Same; play then continues with a fresh interpreter, and a second timeout forfeits | The paper does not say what follows the recovery call |
| Go: "training seeds change per checkpoint, held-out seeds fixed" (no openings described) | 2-ply (Black) / 3-ply (White) random openings, kept if the first-legal player loses and GNU Go 10 wins vs level 5; difficulty = GNU Go 10's mean final margin vs levels 5/7/9; one pool dealt by quantile to ID (10/colour), OOD (6/colour) and a 40/colour training reservoir (`data/go_openings_pooled.json`). Each checkpoint draws its training games from the reservoir, one per difficulty stratum, with seeds that depend on the checkpoint; GNU Go gets a fixed seed per game | From the empty board GNU Go as Black wins every game by 15.5, so White could never win (report 13) |
| Go "authoritative scorer" with dead-stone adjudication | GNU Go 3.8 `final_score` (Chinese rules, level 10) on the real board; the actor's analysis board counts every stone as alive | The scorer is not named |
| GNU Go levels 5–9 / 10 | Same levels, GNU Go 3.8 (`brew install gnu-go`), positional superko, never resigns | On 5×5 the levels play almost alike (report 13) |
| Go: 20 train, 20 ID, 12 OOD games per checkpoint, 20 checkpoints | 8 train, 20 ID, 4 OOD, 8 checkpoints; actor effort `medium`, reflection effort `high`; runs stop at a per-lineage cost cap, and a checkpoint cut off by the cap is not counted | Cost: Sonnet 5.5 Go games cost $0.04–0.06 each (report 14); ID kept at 20 so held-out changes are measurable |
| 10-ply (red) / 11-ply (blue) openings from fixed banks | 4-ply (red) / 5-ply (blue) openings from one shared pool (`data/hex_openings_pooled.json`): kept only if always playing the first legal action loses and a 30k-node engine wins against the weakest train opponent, scored for difficulty by engines only, and dealt to train / ID / OOD by colour and difficulty | With 10/11 plies the smoke run's games lasted 2–7 actor moves and blue was much harder (reports 07–09). Per-split seeds then made the ID bank harder than train (lineage A: Sonnet 8/8 train, 2/12 ID; report 10). Banks are not published |

## Thinking

The models use adaptive thinking on every call; the paper does not say whether its
transcripts include reasoning. Runs up to plan A (2026-10-27) sent no `thinking` field:
Sonnet 5.5 through OpenRouter then returns short thinking summaries and Haiku 5.5 returns
empty thinking blocks (probe, 2026-10-28). The blocks went back to the model unchanged but
were not saved. From 2026-10-28 `--thinking-display summarized` (the default) asks for
summaries and saves them in each assistant turn of the transcript as `thinking`. The copy
of the actor's transcript that reflection reads has them removed, so recording them does
not change what reflection learns from.

## Not specified in the paper

- Exact Hex opening banks and the alpha–beta evaluation function.
- Go and Hex seeds, and what a Go seed sets (openings, opponent randomness or both).
- Which program adjudicates dead stones in Go.
- Price tables used for cost ("fixed undiscounted input/output prices").
- The structural validator beyond "persistent tool load" smoke checks.
