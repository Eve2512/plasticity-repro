# Reflection effort and model, not reuse, limit agent plasticity: a reproduction of "Agent Plasticity" on 6×6 Hex and 5×5 Go

Independent, scaled-down reproduction of *Agent Plasticity: Measuring Self-Improvement
Through Experience* (Singh et al., arXiv:2610.08902, October 2026). The authors released
no code; everything here was rebuilt from the paper's equations (Section 2) and appendix
(Appendix B settings, Appendix I prompts). Data: the Hugging Face dataset
`Eve39570/agent-plasticity-hex-go` (7,418 game transcripts on both games, 235 reflection logs, 1,377 replayed reflection turns, 144 ablation games, all also in the Hub's trace viewer).

## Summary

- **Plasticity depends on how hard the agent reflects.** With the same model (Claude
  Sonnet 5.5), the same games and the same per-game budget, reflection at effort
  `medium` gave no clear held-out gain in two lineages (59 % → 65 %, p = 0.32), while
  reflection at effort `high` gave a gain in two lineages (73 % → 83 %, p = 0.04). Over
  checkpoints 4–10, high ends at 83 % against 65 % for medium (z = 3.75, p = 0.0002),
  from an identical start. That z-test counts every game as independent, but later
  checkpoints largely replay the same 12 held-out games (section 3.12); counted per opening,
  high effort is better on 10 and worse on 1 (sign test p = 0.012, permutation p = 0.066). This is a Hex result: on 5×5 Go, effort made no measurable
  difference for either model (Sonnet late 61 % at medium vs 60 % at high, p = 0.69).
- **The failure mode at medium effort was shallow reflection, not missing reuse.** The
  agent ran its saved tool in most games, but each reflection used 4–6 of 50 calls,
  rarely opened the per-move diagnostics it was given, and never improved the tool.
- **A second model (Haiku 5.5) stayed flat over 21 checkpoints** despite busy reflection
  (code revised at 9 checkpoints): artifacts were built, changed and used, and failures
  remained. At reflection effort `high` it stayed flat too, on Hex and on Go, so its flat
  result is not an effort artefact.
- **On 5×5 Go the Sonnet result does not hold up when pooled.** Through checkpoint 7,
  Sonnet at effort `high` rose from 57 % to 71 % held-out ID (p = 0.01). Over checkpoints
  0–10 the pooled gain is +3 pp (57 % → 60 %, p = 0.57): one lineage reaches 90 % and passes
  the flat-curve test (p = 0.019), the other falls to 15–20 % at checkpoints 6–9 after
  timeouts and a search cap it set itself. Haiku goes from 55 % to 47 %.
- **How the agent adapts to its limits differs by model.** When Go games ran into the
  32-call budget, Sonnet moved play into its saved tool at the next checkpoint; Haiku used
  more calls per game over time. One Sonnet lineage later broke the time limit instead,
  forfeiting 20 of 32 games at one checkpoint; after it capped its own search, held-out ID
  stayed at 15 % for three checkpoints.
- **The gain lives in the saved tools, and the tools come from game records.** Removing
  the final inventory of the two high-effort Hex Sonnet lineages drops held-out ID from
  92 % to 50–54 % (test 6). Reflection without game records built no tools at all; on the
  same held-out openings, the feedback lineages won 38 games the no-feedback control lost
  and lost 5 it won from checkpoint 3 on (test 5); per opening, 8 better and 1 worse
  (p = 0.039).
- **Flat scores are replays.** Held-out openings are fixed and the opponents deterministic,
  so once a tool stops changing, each checkpoint replays the last one's games: 64–70 % of
  the high-effort Hex Sonnet lineages' held-out games repeat an earlier game move for move.
  Every main result keeps its direction when openings are the unit, but most p-values grow
  by orders of magnitude, and the Go model gaps are no longer below 0.05 (report 23).
- **Learning showed up as testing, in the thinking.** Thinking summaries (replayed for old
  runs) show the lineages that learned playing new tool versions against the current one
  before installing them; Haiku never did, and one Go Sonnet lineage tested only against its
  own engines and kept installing unproven rewrites. With its final tools the actor thinks
  on 4–6 % of its turns, without them on 66–70 %.
- **A single lineage's curve can move a lot without learning.** The no-feedback control
  never changed and played the same openings against the same deterministic opponents at
  every checkpoint, yet its held-out ID fell from 72 % to 56 % (p = 0.024 treating games as
  independent).
- **A third model shows the metric rewarding a bad start.** GLM 5.3 lost most of its
  checkpoint-0 games to the time and call limits, then finished them after one reflection.
  That one jump makes three of its four lineages pass the flat-curve test and gives its Go
  lineages P_sat over ten times the one Claude lineage that passes, while ID after checkpoint 1
  is flat or falling and ends below Haiku on Hex (report 21). On Hex, one GLM reflection
  wrote a one-line bug into its search tool that took held-out ID from 75 % to 0 % (report 20).
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
| Chess, Go, Hex, NetHack; 8 models | Hex and 5×5 Go; Sonnet 5.5 and Haiku 5.5, and GLM 5.3 at reflection effort high (plan C) |
| 20 checkpoints; Hex 40 / 40 / 32 games | 11 checkpoints with 8 / 12 / 4 games; one Haiku lineage with 21 checkpoints and 20 / 24 / 8 |
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
Plan B extended every lineage below to checkpoint 10 (the no-feedback controls and
`haiku_r20` were not extended) and added `hex_haiku_medium_rep2`.

| Lineage | Model | Reflection effort | Held-out ID per checkpoint (%) | Billed |
|---|---|---|---|---|
| `lineage_a2` | Sonnet 5.5 | medium | 67, 50, 67, 67, 67, 58, 67, 50, 58, 58, 75 | $13.74 |
| `sonnet_medium_rep2` | Sonnet 5.5 | medium | 58, 33, 67, 67, 58, 67, 75, 58, 75, 75, 75 | $14.50 |
| `sonnet_reflect_high` | Sonnet 5.5 | high | 50, 50, 83, 75, 75, 75, 75, 75, 75, 75, 75 | $10.05 |
| `sonnet_reflect_high_rep2` | Sonnet 5.5 | high | 75, 67, 92, 92, 92, 92, 92, 92, 92, 92, 92 | $11.06 |
| `haiku_r20` | Haiku 5.5 | medium | 29 … 33 (21 checkpoints; mean ≈ 31) | $7.86 |
| `hex_haiku_medium_rep2` | Haiku 5.5 | medium | 42, 50, 58, 58, 33, 50, 17, 42, 25, 50, 25 | $2.07 |
| `hex_haiku_reflect_high` | Haiku 5.5 | high | 33, 42, 42, 33, 42, 33, 33, 42, 42, 42, 42 | $2.11 |
| `hex_haiku_reflect_high_rep2` | Haiku 5.5 | high | 50, 58, 42, 50, 50, 33, 42, 33, 33, 42, 50 | $2.19 |
| `sonnet_nofeedback_high` | Sonnet 5.5 | high, no game records | 75, 75, 75, 50, 58, 58, 58, 42 | $7.00 |
| `sonnet_nofeedback_high_rep2` | Sonnet 5.5 | high, no game records | 50, 83, 75, 58, 58, 50, 83, 42 | $6.85 |

On 5×5 Go (20 held-out ID games per checkpoint, report 15):

| Lineage | Model | Reflection effort | Held-out ID per checkpoint (%) | Billed |
|---|---|---|---|---|
| `go_sonnet_reflect_high` | Sonnet 5.5 | high | 55, 30, 30, 35, 35, 60, 20, 15, 15, 15, 50 | $20.93 |
| `go_sonnet_reflect_high_rep2` | Sonnet 5.5 | high | 75, 60, 90, 85, 85, 90, 90, 90, 90, 90, 90 | $17.95 |
| `go_haiku_reflect_high` | Haiku 5.5 | high | 55, 55, 65, 55, 40, 45, 45, 35, 40, 45, 45 | $2.97 |
| `go_haiku_reflect_high_rep2` | Haiku 5.5 | high | 50, 55, 50, 50, 45, 60, 50, 55, 35, 50, 55 | $2.85 |

### 3.1 Reflection effort separates learning from not learning

| Condition (2 lineages each) | ID, checkpoints 0–3 | ID, checkpoints 4–10 | Change |
|---|---|---|---|
| medium | 57/96 = 59 % | 110/168 = 65 % | z = 0.99, p = 0.32 |
| high | 70/96 = 73 % | 140/168 = 83 % | z = 2.02, p = 0.04 |

High against medium over checkpoints 4–10: 83 % vs 65 %, z = 3.75, p = 0.0002; per opening
10 better, 1 worse, sign test p = 0.012 (section 3.12) (over 4–7,
before plan B: 83 % vs 62 %, p = 0.001). Checkpoint 0 is played before any reflection and is
therefore the same condition for both: 15/24 each. Training scores reach 100 % from
checkpoint 3 on for both high-effort lineages, and their held-out ID has not changed since
checkpoint 3: they had saturated by then. The medium replicate `sonnet_medium_rep2` crept up
late (75 % at checkpoints 8–10) without ever running a saved tool; its flat-curve test is
p = 0.24.

| Behaviour | medium | high |
|---|---|---|
| Calls per reflection (of 50) | 5.3–5.5 | 6.8–8.8 |
| Checkpoints with changed tool code | 0–1 | 2–3 |
| Games running a saved tool | 0–64 % | 89–91 % |

### 3.2 Where the loop broke at medium effort

In `lineage_a2` the second reflection wrote a 44-line tool (connection distances,
candidate moves). The actor then ran it in 16–22 of 24 games per checkpoint, but training
scores fell (88 % → 60 % before vs with the tool, z = 2.0) and held-out scores did not move.
None of the eight later reflections changed the tool; through checkpoint 7 they filed
every loss under one failure mode and appended a paragraph of advice to a notes file. The reflector's own summaries say so:
"I didn't open the move-by-move session logs", "I did not change `tools/hexeval.py`".
In the paper's terms this is high reuse with failures remaining; here the cause is the
reflection step, not retrieval. In the medium replicate, no saved tool was ever run.

### 3.3 Haiku 5.5: busy but not better

Over 21 checkpoints Haiku stays near 31 % on held-out ID (checkpoints 0–9: 32 %, 10–20:
31 %, p = 0.81). Its reflections were active (15 calls on average, code changed at 9
checkpoints, a saved tool run in a third of games). The saturation fit reports a 69-point
"rise" by extrapolation that the flat-curve test rejects (p = 0.94), a live example of the
false-rise problem from Section 2.

Haiku at reflection effort `high` (two lineages, 11 checkpoints each) also stays flat on
Hex: 44 % → 40 % between checkpoints 0–2 and 3–10 (p = 0.52), with 19–25 reflection calls
per round. More effort made its reflection longer, not its play better. A second
medium-effort Hex lineage at the high-effort lineages' game counts (`hex_haiku_medium_rep2`,
plan B) went from 50 % to 38 % (p = 0.19) while revising its code at 7 of 10 reflections.

### 3.4 5×5 Go: the model matters more than the game

Report 15 compares both models at reflection effort `high` on both games. Early is
checkpoints 0–2, late is checkpoint 3 onward; this split was fixed before the Go results
were seen.

| Game | Model | Early | Late | p | Late Sonnet vs Haiku |
|---|---|---|---|---|---|
| Hex | Sonnet 5.5 | 69 % | 83 % | 0.013 | +43 pp (p < 0.001) |
| Hex | Haiku 5.5 | 44 % | 40 % | 0.52 | |
| Go | Sonnet 5.5 | 57 % | 60 % | 0.57 | +13 pp (p = 0.001) |
| Go | Haiku 5.5 | 55 % | 47 % | 0.13 | |

Late is checkpoints 3–10. Through checkpoint 7 Go Sonnet read 57 % → 71 % (p = 0.01); the
three added checkpoints removed that gain. The pooled tests treat games as independent and
ignore lineage, so they summarise rather than decide. Per lineage, only
`go_sonnet_reflect_high_rep2` passes the flat-curve test (75 % → 90 %, p = 0.019). Its tool
was called in every game from checkpoint 2 on. The other Go Sonnet lineage called its tool
from checkpoint 1 but stayed at 30–35 % until checkpoint 5 (60 %), then fell to 15–20 % for
checkpoints 6–9 (section 3.5) and ended at 50 %. Same model, same settings, opposite
outcomes: one lineage is not enough to rank anything, and eight checkpoints were not enough
to see where this one was going.

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

The adaptation can overshoot. `go_sonnet_reflect_high` played checkpoint 6 twice. Under
plan A it finished before the $13 cap stopped the lineage and was not counted: the actor
called its tool with a far larger search budget (`budget=2500000`), the calls ran past
240 s and 9 of 32 games were forfeited. Plan B's resume replayed it: this time the actor
followed its playbook's 3M nodes per search, which the engine applied to every deepening
iteration, and 20 of 32 games were forfeited (all 8 training games scored 0). The next
reflection diagnosed this and capped total search at 1.5M nodes. Timeouts stopped, but
held-out ID stayed at 15 % for checkpoints 7–9, while the reflections reported White
positions that read +8 to +12 early and then collapsed. It came back to 50 % at checkpoint
10 after a reflection that changed only the tool's description and the playbook. The
lineage that relaxed one limit (model calls) broke another (time), and its repair for that
coincided with its worst stretch. The other Go Sonnet lineage never did this.

### 3.6 Artifact ablation (limitation test 6)

From checkpoint 7 of each high-effort Hex Sonnet lineage (the final one before plan B; both
held the same score through checkpoint 10), 24 held-out ID games per arm with the same
model, openings and opponents (report 17, $4.75):

| Lineage | With final inventory | Empty inventory | Inventory, actor told to use it |
|---|---|---|---|
| `sonnet_reflect_high` | 92 % | 54 % | 92 % |
| `sonnet_reflect_high_rep2` | 92 % | 50 % | 83 % |

Without its inventory the agent falls back to about where it started (50 % and 75 % at
checkpoint 0). Forcing tool use adds nothing because the actor already called its tool in
every game. The saved tools are the learned part.

### 3.7 Reflection without game records (limitation test 5)

Two more Hex Sonnet lineages ran exactly like the high-effort ones, but reflection found a
note saying no game records were available in place of the transcripts and diagnostics
(report 18, $13.85). In all 14 reflections the reflector used 4 of its 50 calls and saved
nothing. Its thinking summaries give the reason: with nothing observed, any tool would be
a guess, and the protocol asks every file to address an observed failure mode. The extra
reflection compute was offered but not used, so this test does not separate experience
from compute as planned.

The lineages still serve as an untrained control. All four Hex Sonnet high-effort lineages
play the same 12 held-out ID openings against the same deterministic opponents at every
checkpoint, so the arms can be compared game by game:

| | Checkpoints 0–2 | Checkpoints 3–7 |
|---|---|---|
| Games won only with game records | 8 | 38 |
| Games won only without | 10 | 5 |
| Sign test p | 0.81 | 2.5e-07 |

The paired test is far stronger than either lineage's own flat-curve test (p = 0.12–0.13
over checkpoints 0–7), but it counts each opening once per checkpoint, and the same games
repeat across checkpoints (section 3.12). Per opening over checkpoints 3–7, feedback is
better on 8 and worse on 1 (sign test p = 0.039, permutation p = 0.035). The controls stop at checkpoint 7, so the comparison does too.
It controls for openings and opponents but not for time: the control ran three days later
(2026-10-28/29 vs 2026-10-25). At checkpoint 0 the arms are level (15 vs 15 wins).

The control also shows how much a curve can move without learning. Nothing changed
between its checkpoints, yet its held-out ID fell from 72 % to 56 % (p = 0.024 if games
are treated as independent, which repeated openings make them not). The drop is spread
over six openings. The only varying part is the actor's sampling, plus any drift in the
served model during the run.

### 3.8 Thinking: how the learning happened

The runs up to plan A kept no thinking (section 4). To see the reasoning behind past
reflections, every saved reflection turn of all 13 runs was sent again with the same context
and thinking summaries on (report 16, $9.40). Haiku returned a summary on 96–100 % of turns,
often 2,000+ characters; Sonnet on 52–89 % at reflection effort high and 0–43 % at medium,
where adaptive thinking often skips simple turns. The replayed turn made the same tool calls
as the recorded one in only 5–40 % of turns, so a replayed summary is the model's reasoning
on the same input, not a recovery of what the original run thought. The test 5 and 6 runs
recorded actor and reflection thinking live.

What the summaries show (report 19; keyword codes checked by reading samples):

| Group | Learned | Reflections testing a candidate tool in games against the current one | Summaries about bookkeeping |
|---|---|---|---|
| Hex Sonnet, effort medium | no | 0 % | 36 % (few summaries) |
| Hex Sonnet, effort high | yes | 33 % | 23 % |
| Haiku, Hex and Go, both efforts | no | 0 % | 58–61 % |
| Go Sonnet, run 1 | late, partly | 100 % | 18 % |
| Go Sonnet, rep2 | yes | 57 % | 24 % |

- The lineages that learned tested new tools in games before installing them; for example,
  a RAVE variant was installed only after beating the current MCTS 25 of 32 times.
- Haiku reflects like an auditor: long summaries about failure-mode IDs, tracking files and
  call bugs, and no games between tool versions.
- Testing alone was not enough. Go Sonnet run 1 tested only against its own previous engine,
  noted that this was not the real benchmark, often saw the new engine lose, and still
  installed a rewrite at every checkpoint; its own notes say none was shown to win more.
  Rep2 fixed the bug that made its first tool unusable, switched to MCTS, checked it on
  positions from lost games, and stopped changing code once it won 8 of 8.
- With its final tools the actor wrote a thinking summary on 4–6 % of its turns; without
  them, on 66–70 %. The learned part sits in the code, and the model stops reasoning about
  the game once the code exists.

### 3.9 A third model: GLM 5.3 (plan C)

Plan C ran GLM 5.3 (`z-ai/glm-5.3`, through OpenRouter's chat endpoint) with the settings of
the high-effort Claude lineages, two lineages per game, checkpoints 0–10 (report 21).

| Game | GLM checkpoint 0 | GLM 1–2 | GLM 3–10 | Sonnet 3–10 | Haiku 3–10 |
|---|---|---|---|---|---|
| Hex | 2/24 = 8 % | 13/48 = 27 % | 46/192 = 24 % | 83 % | 40 % |
| Go | 5/40 = 12 % | 46/80 = 58 % | 147/320 = 46 % | 60 % | 47 % |

Every Claude game at checkpoint 0 finished. GLM lost 32 of 48 Hex games and 29 of 64 Go
games there to the limits (on Hex mostly tool calls past 240 s, on Go the 32-call budget).
After the first reflection nearly all its games finished and held-out ID jumped; after that
it did not improve (Hex 27 % → 24 %, p = 0.65; Go 58 % → 46 %, p = 0.064).

The metric reads the jump as plasticity. Three of the four GLM lineages pass the flat-curve
test (p = 0.008–0.031), against one of the eight Claude lineages at effort high, and the two
Go lineages get P_sat of 48,000–60,000 points per $1,000 against 3,798 for the one Claude
lineage that passes. `go_glm_reflect_high` gets 48,432 while ending at 25 %, below its
checkpoint-1 score of 60 %. Learning cost at GLM's prices was only $5–7 per lineage.

GLM reflected at the edge of its budget (39–49 of 50 calls, code revised at 8–9 of 10
reflections). In `hex_glm_reflect_high` the first reflection after its jump rewrote the
search tool with a corridor filter that dropped the shortest-path cells; held-out ID fell
from 75 % to 0 %. Model-free replays of the saved tools reproduce the fall, and fixing that
one line in the checkpoint-2 tool scores 12/12 (report 20). The next reflection found and
fixed a different, real bug, called it the root cause, and never looked at the filter
again. Later reflections built opponent models and added layers on top, back to 58 %; the
final tool scores 7/12 in replay, with or without the fix.

All four GLM lineages stopped when the API key reached its spending limit and were resumed
with the unfinished checkpoint replayed ($0.29–1.86 per lineage discarded); GLM ran 2 games
at a time per lineage, Claude 4.

### 3.10 Reflection effort on Go (plan C)

Plan C ran two Go lineages per Claude model at reflection effort medium, otherwise as the
high-effort Go lineages (report 22).

| Model | Effort | Checkpoint 0 | Early (0–2) | Late (3–10) | Late, high vs medium |
|---|---|---|---|---|---|
| Sonnet 5.5 | medium | 60 % | 60 % | 61 % | |
| Sonnet 5.5 | high | 65 % | 57 % | 60 % | p = 0.69 |
| Haiku 5.5 | medium | 48 % | 47 % | 52 % | |
| Haiku 5.5 | high | 52 % | 55 % | 47 % | p = 0.24 |

The Hex effort result does not carry over. Sonnet at medium effort reflected on Go as on
Hex (5.6–6.7 calls per round, code changed at 1–2 of 10 reflections, a saved tool run in
1–6 % of games) and its held-out ID stayed within 55–70 %; its play did not change either
(4–13 illegal submissions per checkpoint to the end). At high effort Sonnet's play did
change, but its two lineages split (one at 85–90 %, the other at 15–20 % for checkpoints
6–9, section 3.4) and pool to the medium score. Haiku stays flat at both efforts;
`go_haiku_medium` gets P_sat 23,266 from a rise that fails the flat-curve test (p = 0.33).

### 3.11 Problems found in our own pipeline

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

### 3.12 Repeated held-out games

Several lineages hold one held-out score for many checkpoints (`sonnet_reflect_high_rep2`
at 92 % for checkpoints 2–10). Every checkpoint plays the same held-out openings, each
against the same opponent level, and neither opponent ever answered a held-out position two
ways (17,048 repeated positions). Once the actor's play stops changing, the games repeat:
`sonnet_reflect_high` kept the same tool code from checkpoint 3 on, and 82 of 84 held-out
games at checkpoints 4–10 match the checkpoint before move for move. Over all checkpoints,
15–70 % of a lineage's held-out games repeat an earlier one exactly (report 23), including
42 % for Go Sonnet at medium effort, which rarely ran a tool.

So the pooled z-tests of reports 12, 15, 21 and 22 overstate the evidence. With each
(opening, colour) as one unit:

| Comparison | Pooled p | Per opening: better / worse | Sign p | Permutation p |
|---|---|---|---|---|
| Hex Sonnet, high vs medium, checkpoints 4–10 | 0.00018 | 10 / 1 | 0.012 | 0.066 |
| Hex Sonnet high, 0–3 → 4–10 | 0.044 | 9 / 1 | 0.021 | 0.051 |
| Hex, feedback vs none, 3–7 | 3.7e-06 | 8 / 1 | 0.039 | 0.035 |
| Hex late, Sonnet vs Haiku | 2.9e-18 | 10 / 1 | 0.012 | 0.0029 |
| Hex late, Sonnet vs GLM | 1.9e-31 | 11 / 0 | 0.00098 | 0.00098 |
| Go late, Sonnet vs Haiku | 0.0012 | 13 / 5 | 0.096 | 0.089 |
| Go late, Sonnet vs GLM | 0.00049 | 11 / 6 | 0.33 | 0.059 |

Every direction holds; the Hex results stay below 0.05 on at least one test, the Go model
gaps do not. With 12 Hex openings no comparison can reach a sign-test p below 0.0005. The
plasticity fits have the same problem: a replayed score is not a new measurement, so a
flat tail makes a curve look saturated with more certainty than the data have.

## 4. Limitations

- **Two small games.** 6×6 Hex and 5×5 Go only; no chess or NetHack. On 5×5 the GNU Go
  levels barely differ, so Go train/ID/OOD differ mostly by opening.
- **Few models.** Two Claude models and one GLM model, all through OpenRouter; GLM ran at
  reflection effort high only and with half the concurrency.
- **Small held-out sets, replayed.** 12 ID games per checkpoint on Hex (24 for `haiku_r20`), 20 on Go,
  the same openings at every checkpoint, so later checkpoints often replay earlier games
  (section 3.12) and the effective sample is the 12 or 20 openings, not the games. Single Hex lineages do
  not pass the flat-curve test (p = 0.09–0.11 for the high-effort runs over checkpoints
  0–10); the effort result rests on pooling two lineages per condition.
- **Two lineages per condition**, all with the same opening bank; no seeds varied beyond
  model sampling.
- **Cost caps shaped the Go data before plan B.** One Go Sonnet lineage stopped after 6 of
  8 checkpoints under plan A; plan B resumed it, replaying the uncounted checkpoint 6 as a
  new sample, so its checkpoint 6 is not the one first played.
- **The effort result holds on Hex only.** On Go, two lineages per cell show no effort
  difference; at high effort the Sonnet lineages split, so more lineages could move either way.
- **The effort question was raised after seeing data.** The first high-effort run was
  motivated by the medium-effort failure; the replicates were run afterwards, but a
  pre-registered study would be stronger.
- **Fewer checkpoints than the paper** (11 vs 20) and scaled-down opponents. Extending
  from 8 to 11 checkpoints moved one pooled result (Go Sonnet, +15 pp to +3 pp), so later
  checkpoints could move others.
- **No thinking in the saved transcripts.** The models think on every call and are billed
  for it. A probe on 2026-10-28 (`scripts/probe_thinking.py`) found that Sonnet 5.5 through
  OpenRouter returns a short thinking summary even without asking, and Haiku 5.5 returns one
  only when `display: "summarized"` is requested. The harness sent those blocks back to the
  model but dropped them when saving transcripts, so no run up to plan A kept any thinking,
  and it cannot be recovered. Diagnoses of reflection depth rest on visible actions and the
  model's own written summaries. A replay (section 3.8) gives summaries on the same inputs,
  but they are new samples. New runs record thinking summaries (`--thinking-display`,
  default `summarized`), never the raw chain of thought, which the API does not return.
- **Test 5 did not isolate compute.** Without game records the reflector chose not to
  spend its budget, so the extra-compute arm effectively had no compute.
- **Unexplained drift in the control.** The unchanged no-feedback control lost 16 points
  of held-out ID over its run (section 3.7). Actor sampling noise or model drift over time
  could explain it; the data cannot tell them apart, and the control ran days after the
  lineages it is compared with.
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
8. Run an untrained control on the same held-out openings, at the same time, and compare
   game by game; it separates learning from drift and noise and is much more sensitive
   than a single curve.
9. Save thinking summaries with every transcript from the start; they cannot be recovered
   later.
10. Check that the agent can finish its games at checkpoint 0. If it cannot, the first
    reflection's fix for the limits dominates the fit; report the curve from checkpoint 1
    as well (report 21).
11. Replay saved tools without the model. It separates a tool that got worse from an actor
    that used it badly, and a one-line patch can then test a suspected cause (report 20).
12. Draw new held-out openings at each checkpoint, or use many more of them. With fixed
    openings and deterministic opponents a frozen tool replays the same games, and tests
    must treat the opening, not the game, as the unit (report 23).

## 6. Reproducing this

```bash
uv sync && uv run pytest
uv run python scripts/run_hex.py --model anthropic/claude-sonnet-5.5 --rounds 7 \
    --train 8 --id 12 --ood 4 --workers 4 --reflect-effort high --cap 14 --name my_run --yes
uv run python scripts/compare_runs.py lineage_a2 sonnet_reflect_high my_run
brew install gnu-go          # for Go
scripts/plan_a.sh            # the six reflection-effort-high lineages of report 15
scripts/plan_b.sh            # extends every lineage to checkpoint 10
uv run python scripts/compare_models.py
uv run python scripts/compare_glm.py   # report 21 (plan C: scripts/plan_c.sh)
uv run python scripts/compare_go_effort.py   # report 22 (plan C)
uv run python scripts/check_repeats.py   # report 23 (no API cost)
uv run python scripts/ablate_inventory.py --yes --cap 8           # test 6, report 17
uv run python scripts/run_hex.py --model anthropic/claude-sonnet-5.5 --rounds 7 \
    --train 8 --id 12 --ood 4 --workers 4 --reflect-effort high --no-feedback --cap 9 \
    --name sonnet_nofeedback_high --yes                          # test 5 (and _rep2)
uv run python scripts/compare_feedback.py                        # report 18
uv run python scripts/replay_thinking.py --dry                   # report 16: plan, then --yes
```

Total API spend for the whole project: $229.27 as of 2026-11-02 (all lineages, smoke runs,
probes, tests 5 and 6, the thinking replay, plan B's extensions, and plan C's four GLM 5.3
lineages, $48.05 billed, reports 20–22). Reports 01–23 in `reports/` hold every number above.
