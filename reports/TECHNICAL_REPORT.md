# Reflection effort and model, not reuse, limit agent plasticity: a reproduction of "Agent Plasticity" on 6×6 Hex and 5×5 Go

Independent, scaled-down reproduction of *Agent Plasticity: Measuring Self-Improvement
Through Experience* (Singh et al., arXiv:2610.08902, October 2026). The authors released
no code; everything here was rebuilt from the paper's equations (Section 2) and appendix
(Appendix B settings, Appendix I prompts). Data: the Hugging Face dataset
`Eve39570/agent-plasticity-hex` (3,282 game transcripts on both games, 94 reflection logs).

## Summary

- **Plasticity depends on how hard the agent reflects.** With the same model (Claude
  Sonnet 5.5), the same games and the same per-game budget, reflection at effort
  `medium` gave no held-out gain in two lineages (59 % → 62 %), while reflection at effort
  `high` gave a gain in two lineages (73 % → 83 %). Over checkpoints 4–7, high ends at
  83 % against 62 % for medium (z = 3.25, p = 0.001), from an identical start.
- **The failure mode at medium effort was shallow reflection, not missing reuse.** The
  agent ran its saved tool in most games, but each reflection used 4–6 of 50 calls,
  rarely opened the per-move diagnostics it was given, and never improved the tool.
- **A second model (Haiku 5.5) stayed flat over 21 checkpoints** despite busy reflection
  (code revised at 9 checkpoints): artifacts were built, changed and used, and failures
  remained. At reflection effort `high` it stayed flat too, on Hex and on Go, so its flat
  result is not an effort artefact.
- **On 5×5 Go the Sonnet result carries over, unevenly.** Pooled over two lineages,
  Sonnet at effort `high` rises from 57 % to 71 % held-out ID (p = 0.01); one lineage
  reaches 90 % and passes the flat-curve test, the other stays near 30–35 % until late
  and stops at its cost cap. Haiku goes from 55 % to 48 %.
- **How the agent adapts to its limits differs by model.** When Go games ran into the
  32-call budget, Sonnet moved play into its saved tool at the next checkpoint; Haiku used
  more calls per game over time. One Sonnet lineage later broke the time limit instead,
  by calling its tool with a much larger search budget.
- **The plasticity metric is fragile at this scale.** On synthetic lineages, the paper's
  10-point rule alone assigns P_sat > 0 to 26–43 % of agents that do not learn; two models
  25 % apart in true P_sat swap rank in 37–46 % of single-lineage comparisons; and the
  choice of price table alone can reverse a ranking.

## 1. Setup

**Protocol (as in the paper).** A frozen model plays games in fresh contexts. Between
checkpoints the same model reflects on its training games and edits a persistent
inventory (Python tools, notes, `failure_modes.json`, `artifacts.json`). An edit becomes
persistent only if the tracking files validate and every tool loads in the sandbox;
rejected attempts are retried (3 for Hex) and their cost counts. Held-out ID and OOD
games are never shown to reflection. Learning cost (Eq. 2) is the cost of training games
and reflections, priced without cache discounts as in the paper; P_sat (Eq. 5) uses the
4-parameter saturation fit (Eq. 4).

**This reproduction.** 6×6 Hex against a pure-Python alpha-beta engine, and 5×5 Go
against GNU Go 3.8 over GTP (scored by its `final_score`, Chinese rules); actor budget 32
calls per game, reflection 50 calls; models through OpenRouter's Anthropic-format
endpoint; agent tools sandboxed with macOS `sandbox-exec` (no network, no reads outside
the inventory and session, empty environment).

**Deviations** (full list: `docs/PROTOCOL_NOTES.md`):

| Paper | Here |
|---|---|
| Chess, Go, Hex, NetHack; 8 models | Hex and 5×5 Go; Sonnet 5.5 and Haiku 5.5 |
| 20 checkpoints; Hex 40 / 40 / 32 games | 8 checkpoints with 8 / 12 / 4 games (Sonnet); 21 checkpoints with 20 / 24 / 8 (Haiku) |
| Native engine, 10k–1M nodes (train/ID), 10M (OOD) | Python engine, 3k–100k (train/ID), 1M (OOD) |
| 10/11-ply openings | 4/5-ply openings from one pool, filtered (a weak player loses, a 30k-node engine wins) and dealt to splits by engine-scored difficulty |
| Container sandbox; prompts in Appendix I | `sandbox-exec`; prompts paraphrased with the same rules and budgets |
| One reflection effort (not stated) | Reflection effort varied: `medium` and `high` |
| Go: 20 / 20 / 12 games, GNU Go 5–9 / 10 | 8 / 20 / 4 games, same levels (GNU Go 3.8); 2/3-ply contested openings, because from the empty board GNU Go as Black always wins (report 13) |

## 2. The metric under test (no API cost)

Before any model run, the metric code was validated on synthetic lineages with a known
true curve (reports 01–04).

| Finding | Value |
|---|---|
| Fast learner recovered without bias, but widely | true P_sat 108; middle 90 % of estimates 41–311 (12 games/checkpoint) |
| Slow learners (90 % point extrapolated) | overestimated 2–3× |
| No learning, paper's 10-point rule only | P_sat > 0 in 26–43 % of lineages; the fits are step functions |
| Same, plus a likelihood-ratio test against a flat curve | 2 % |
| Two models 25 % apart, one lineage each | wrong order in 37–46 % of replays |
| Price table (cache discount or not) | can reverse a ranking with identical learning |
| Paper's own numbers | 11 of 14 scores match the stated game counts; 3 window averages cannot |

These results shaped the analysis below: every reported rise is tested against a flat
curve, and conclusions rest on pooled lineages, not one P_sat.

## 3. Results

| Lineage | Model | Reflection effort | Held-out ID per checkpoint (%) | Billed |
|---|---|---|---|---|
| `lineage_a2` | Sonnet 5.5 | medium | 67, 50, 67, 67, 67, 58, 67, 50 | $9.49 |
| `sonnet_medium_rep2` | Sonnet 5.5 | medium | 58, 33, 67, 67, 58, 67, 75, 58 | $9.57 |
| `sonnet_reflect_high` | Sonnet 5.5 | high | 50, 50, 83, 75, 75, 75, 75, 75 | $7.44 |
| `sonnet_reflect_high_rep2` | Sonnet 5.5 | high | 75, 67, 92, 92, 92, 92, 92, 92 | $7.77 |
| `haiku_r20` | Haiku 5.5 | medium | 29 … 33 (21 checkpoints; mean ≈ 31) | $7.86 |
| `hex_haiku_reflect_high` | Haiku 5.5 | high | 33, 42, 42, 33, 42, 33, 33, 42 | $1.49 |
| `hex_haiku_reflect_high_rep2` | Haiku 5.5 | high | 50, 58, 42, 50, 50, 33, 42, 33 | $1.58 |

On 5×5 Go (20 held-out ID games per checkpoint, report 15):

| Lineage | Model | Reflection effort | Held-out ID per checkpoint (%) | Billed |
|---|---|---|---|---|
| `go_sonnet_reflect_high` | Sonnet 5.5 | high | 55, 30, 30, 35, 35, 60 (stopped by its $13 cap) | $13.01 |
| `go_sonnet_reflect_high_rep2` | Sonnet 5.5 | high | 75, 60, 90, 85, 85, 90, 90, 90 | $12.59 |
| `go_haiku_reflect_high` | Haiku 5.5 | high | 55, 55, 65, 55, 40, 45, 45, 35 | $2.10 |
| `go_haiku_reflect_high_rep2` | Haiku 5.5 | high | 50, 55, 50, 50, 45, 60, 50, 55 | $1.93 |

### 3.1 Reflection effort separates learning from not learning

| Condition (2 lineages each) | ID, checkpoints 0–3 | ID, checkpoints 4–7 | Change |
|---|---|---|---|
| medium | 57/96 = 59 % | 60/96 = 62 % | z = 0.44, p = 0.66 |
| high | 70/96 = 73 % | 80/96 = 83 % | z = 1.75, p = 0.08 |

High against medium over checkpoints 4–7: 83 % vs 62 %, z = 3.25, p = 0.001. Checkpoint 0
is played before any reflection and is therefore the same condition for both: 15/24 each.
Training scores rise to 100 % in the second half for both high-effort lineages.

| Behaviour | medium | high |
|---|---|---|
| Calls per reflection (of 50) | 5.4–5.6 | 8.0–10.3 |
| Checkpoints with changed tool code | 0–1 | 2–3 |
| Games running a saved tool | 0–61 % | 85–88 % |

### 3.2 Where the loop broke at medium effort

In `lineage_a2` the second reflection wrote a 44-line tool (connection distances,
candidate moves). The actor then ran it in 16–22 of 24 games per checkpoint, but training
scores fell (88 % → 60 % before vs with the tool, z = 2.0) and held-out scores did not move.
Five later reflections left the tool unchanged, filed every loss under one failure mode,
and appended a paragraph of advice to a notes file. The reflector's own summaries say so:
"I didn't open the move-by-move session logs", "I did not change `tools/hexeval.py`".
In the paper's terms this is high reuse with failures remaining; here the cause is the
reflection step, not retrieval. In the medium replicate, no saved tool was ever run.

### 3.3 Haiku 5.5: busy but not better

Over 21 checkpoints Haiku stays near 31 % on held-out ID (checkpoints 0–9: 32 %, 10–20:
31 %, p = 0.81). Its reflections were active (15 calls on average, code changed at 9
checkpoints, a saved tool run in a third of games). The saturation fit reports a 69-point
"rise" by extrapolation that the flat-curve test rejects (p = 0.94), a live example of the
false-rise problem from Section 2.

Haiku at reflection effort `high` (two lineages, 8 checkpoints each) also stays flat on Hex:
44 % → 39 % between checkpoints 0–2 and 3–7 (p = 0.47), with 19–22 reflection calls per
round. More effort made its reflection longer, not its play better.

### 3.4 5×5 Go: the model matters more than the game

Report 15 compares both models at reflection effort `high` on both games. Early is
checkpoints 0–2, late is checkpoint 3 onward; this split was fixed before the Go results
were seen.

| Game | Model | Early | Late | p | Late Sonnet vs Haiku |
|---|---|---|---|---|---|
| Hex | Sonnet 5.5 | 69 % | 83 % | 0.02 | +44 pp (p < 0.001) |
| Hex | Haiku 5.5 | 44 % | 39 % | 0.47 | |
| Go | Sonnet 5.5 | 57 % | 71 % | 0.01 | +23 pp (p < 0.001) |
| Go | Haiku 5.5 | 55 % | 48 % | 0.23 | |

The pooled tests treat games as independent and ignore lineage, so they summarise rather
than decide. Per lineage, only `go_sonnet_reflect_high_rep2` passes the flat-curve test
(75 % → 90 %, p = 0.04). Its tool was called in every game from checkpoint 2 on. The other
Go Sonnet lineage called its tool from checkpoint 1 but stayed at 30–35 % until checkpoint
5 (60 %), used almost twice as many reflection calls (25 vs 14 per round) and so reached its
$13 cap after 6 checkpoints. Same model, same settings, opposite outcomes: one lineage is
not enough to rank anything.

OOD (GNU Go level 10) does not move for any condition. On 5×5 the GNU Go levels play almost
alike (report 13), so Go OOD tests new openings more than a stronger opponent.

### 3.5 Behaviour under constraints

Every game has hard limits: 32 model calls (a game not finished is lost) and 240 s per
tool call (a second timeout forfeits). Adapting to these limits is part of what experience
can change, and the two models adapted differently.

| Go, both lineages pooled | Checkpoint 0 | 1 | 2 | 5 |
|---|---|---|---|---|
| Sonnet: calls per game | 10.1 | 20.2 | 10.7 | 11.0 |
| Sonnet: games near the budget (28+ calls) | 0 % | 31 % | 0 % | 0 % |
| Sonnet: games lost to limits | 0 | 6 | 0 | 0 |
| Sonnet: moves per model call | 0.85 | 0.51 | 1.30 | 0.99 |
| Haiku: calls per game | 11.3 | 12.0 | 11.2 | 15.1 |
| Haiku: illegal submissions | 10 | 7 | 7 | 7 |

After its first reflection, Sonnet spent twice as many calls per Go game and lost 6 games
to the budget. At the next checkpoint it handed play to its saved tool: more than one move
per model call, no game near the budget. Haiku drifted the other way on both games (Hex
10 → 17 calls per game, Go 11 → 16) and kept submitting illegal Go moves.

The adaptation can overshoot. In the last checkpoint `go_sonnet_reflect_high` played
before its cap (checkpoint 6, all 32 games played but not counted), the actor called its
tool with a far larger search budget (`budget=2500000`); the calls ran past 240 s and 9 of
32 games were forfeited. The lineage that relaxed one limit (model calls) broke another
(time). The other Go Sonnet lineage never did this.

### 3.6 Problems found in our own pipeline

- **Opening banks.** Banks drawn from a separate seed per split made held-out ID harder
  than train (Sonnet 8/8 train vs 2/12 ID, z ≈ 3.7). That run was stopped after one
  checkpoint and the banks rebuilt from one pool (reports 09–11).
- **Colour.** In `lineage_a2` Sonnet won 81 % as red and 42 % as blue on held-out ID even
  with engine-balanced openings (not measured for the other lineages); results should be
  read per colour.
- **Prompt adherence.** First reflection attempts often failed validation because tools
  used `import`, as the paper also reports.
- **Sandbox crash.** Once, the sandboxed Python child died mid-game and the harness raised
  `BrokenPipeError`, which stopped the whole run; `--resume` redid that checkpoint ($0.33
  discarded). It is now counted as a failed tool call.
- **Go cost.** Sonnet's Go games cost $0.048–0.059 each after the first reflection, above
  the $0.041 probe, because the actor made more calls; both Go Sonnet lineages ran close to
  or into their caps.

## 4. Limitations

- **Two small games.** 6×6 Hex and 5×5 Go only; no chess or NetHack. On 5×5 the GNU Go
  levels barely differ, so Go train/ID/OOD differ mostly by opening.
- **Two models, one provider.** No cross-family comparison; OpenRouter routing was used.
- **Small held-out sets.** 12 ID games per checkpoint on Hex (24 for `haiku_r20`), 20 on Go. Single lineages do
  not pass the flat-curve test (p = 0.12–0.13 for the high-effort runs); the effort result
  rests on pooling two lineages per condition.
- **Two lineages per condition**, all with the same opening bank; no seeds varied beyond
  model sampling.
- **Cost caps shape the Go data.** One Go Sonnet lineage stopped after 6 of 8
  checkpoints, and its uncounted last checkpoint is the one where it lost games to timeouts.
- **The effort question was raised after seeing data.** The first high-effort run was
  motivated by the medium-effort failure; the replicates were run afterwards, but a
  pre-registered study would be stronger.
- **Fewer checkpoints than the paper** for Sonnet (8 vs 20) and scaled-down opponents.
- **No hidden reasoning.** Thinking blocks are returned empty; diagnoses of reflection
  depth rest on visible actions and the model's own summaries.
- **Artifact-use counts are textual**: a game counts as calling a tool if its Python code
  calls an entrypoint; the paper's semantic judge was not reproduced.
- **Cost-based P_sat is unstable here.** Learning costs are a few dollars, so P_sat values
  are in the thousands and highly sensitive to fits; comparisons use held-out scores.

## 5. Recommendations for measuring plasticity

1. Report the reflection protocol, including effort, as part of the agent; it can decide
   the outcome.
2. Test every rise against a flat curve; the 10-point rule alone admits many false rises.
3. Run at least two lineages per condition before ranking.
4. Build held-out splits from one pool and check that train and ID are exchangeable.
5. Report per-colour (or per-role) results in asymmetric games.
6. Log reflection behaviour (calls used, files read, code changed): it explained more
   than artifact reuse did.
7. Log behaviour under the run's limits (calls per game, games lost to budget or timeouts,
   moves per call): adapting to them is part of plasticity, and it can go wrong.

## 6. Reproducing this

```bash
uv sync && uv run pytest
uv run python scripts/run_hex.py --model anthropic/claude-sonnet-5.5 --rounds 7 \
    --train 8 --id 12 --ood 4 --workers 4 --reflect-effort high --cap 14 --name my_run --yes
uv run python scripts/compare_runs.py lineage_a2 sonnet_reflect_high my_run
brew install gnu-go          # for Go
scripts/plan_a.sh            # the six reflection-effort-high lineages of report 15
uv run python scripts/compare_models.py
```

Total API spend for the whole project: $79.05 (all lineages, smoke runs and probes).
Reports 01–15 in `reports/` hold every number above.
