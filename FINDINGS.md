# Agent Plasticity reproduction: findings

A short read of what this reproduction found. Methods, every table and the limitations are in
[reports/TECHNICAL_REPORT.md](reports/TECHNICAL_REPORT.md); every number comes from reports 01–25 in
[reports/](reports/). Data: the Hugging Face dataset `Eve39570/agent-plasticity-hex-go` (8,474
games, 276 reflections, 384 ablation and fresh-opening games). Total API spend: $282.36, plus
$88.69 for four paid probes whose code is not in the repo (marked "probe" below):
Finding 2 ($45.39), drift ($3.99), the Hex → Go stream ($15.63) and its shared-files variants
($19.72 plain, $3.96 warned).

## The question

The paper (Singh et al., arXiv:2610.08902) freezes a model and lets it improve only through
files it writes between rounds of games: tools, notes, tracking files. Agent plasticity is
the held-out gain per $1,000 of learning cost. No code was released. We rebuilt the protocol
and ran it at small scale on 6×6 Hex and 5×5 Go with Claude Sonnet 5.5, Claude Haiku 5.5 and
GLM 5.3, 11 checkpoints per lineage, two lineages per condition.

## Why some results were re-run

Held-out openings were fixed and both opponents are deterministic. Once a tool stops
changing, each checkpoint replays the games of the checkpoint before, move for move (64–70 %
of the high-effort Hex Sonnet held-out games, report 23). So the pooled z-tests counted the
same game many times. Two fixes:

- **Openings as the unit.** Every direction held; most p-values grew by orders of magnitude,
  and the Go model gaps were no longer below 0.05 (report 23).
- **New openings.** Plan D re-ran the Hex Sonnet effort comparison with 12 new held-out
  openings at every checkpoint ($44.94, report 24). Option D played the final Go inventories
  on 40 new Go openings ($5.40, report 25).

Each result below says which kind of evidence carries it.

## Against the paper's findings

- **Finding 1** (self-improvement depends on model and task; transfer to stronger opponents is
  not uniform): reproduced for model and task. Sonnet 5.5 learns on Hex, Haiku 5.5 on neither
  game, and Sonnet's Hex gain does not carry over to Go. Transfer is only weakly tested: OOD is
  4 fixed Hex games per checkpoint, and on 5×5 Go the GNU Go levels barely differ.
- **Finding 2** (the best performer is not the most plastic): reproduced in a probe on Hex,
  with one Opus 5.5 lineage against a harder held-out opponent. Opus starts 24 points above
  Sonnet 5.5, Sonnet gains 29 points to Opus's 8, and by checkpoints 3–5 the two are level
  (section 9). In the main runs it shows only through GLM's failed checkpoint 0.

## What we found, in order of confidence

### 1. On Hex, reflection effort decides whether Sonnet learns (fresh openings)

| Held-out ID, Hex Sonnet 5.5 | Checkpoints 0–3 | Checkpoints 4–10 |
|---|---|---|
| Effort high, fixed openings | 73 % | 83 % |
| Effort medium, fixed openings | 59 % | 65 % |
| Effort high, new openings every checkpoint | 72 % | 88 % |
| Effort medium, new openings every checkpoint | 57 % | 56 % |

On new openings, late high effort is better on 46 of 84 openings and worse on 6 (sign test
p = 1e-08). The high-effort curve rises on positions it never played (openings as the unit,
p = 0.015); medium stays level (p = 0.91). Checkpoint 0, before any reflection, is 11/24 for
both. Both high-effort lineages pass the flat-curve test and end at 12/12; neither medium one
does. This is the strongest result of the project, and it is a learning curve, not only an
endpoint.

### 2. The gain lives in the saved tools (test 6, report 17)

Remove the final inventory of the two high-effort Hex Sonnet lineages: held-out ID falls from
92 % / 92 % to 54 % / 50 %, about where they began. Telling the actor to use its tools adds
nothing; it already used them in every game.

### 3. The tools come from game records (test 5, report 18)

Two lineages reflected with the same 50-call budget but no game records. The reflector built
nothing; its thinking: "There's no data to map, so an empty inventory is actually valid here."
So the test did not isolate extra compute. As an untrained control on the same 12 held-out
openings, feedback won 38 games the control lost and lost 5 it won from checkpoint 3. Per
opening that is 8 better and 1 worse (p = 0.039): still significant, but much weaker than the
game count suggested.

### 4. Model gaps: clear against GLM, not established between Sonnet and Haiku on Go

| Comparison | Evidence | Better / worse openings | p |
|---|---|---|---|
| Hex late, Sonnet vs Haiku | fixed openings, per opening | 10 / 1 | 0.012 |
| Hex late, Sonnet vs GLM | fixed openings, per opening | 11 / 0 | 0.00098 |
| Go final, Sonnet vs GLM | 40 new openings | 24 / 1 | 1.5e-06 |
| Go final, Haiku vs GLM | 40 new openings | 18 / 3 | 0.0015 |
| Go final, Sonnet vs Haiku | 40 new openings | 13 / 8 | 0.38 |

The two Go Sonnet lineages at effort high score 95 % and 50 % on the new openings; the 50 %
one is below both Haiku lineages (68 %, 58 %). Which Sonnet lineage you ran decides the Go
ranking. The original Go levels were right (each final inventory within about 10 points of
its checkpoint-10 score, one Haiku lineage excepted); the problem was 20 openings, not wrong
levels.

### 5. Haiku does not learn, on either game, at either effort

Hex: 32 % → 31 % over 21 checkpoints at medium; 44 % → 40 % at high. Go: 55 % → 47 % at
high. Its reflections were busy (15–25 calls, code changed at most checkpoints). More effort
made its reflection longer, not its play better.

### 6. On Go, nothing shows a pooled learning curve, and effort does not matter

Through checkpoint 7 Go Sonnet high read 57 % → 71 % (p = 0.01); checkpoints 8–10 took it
back to 57 % → 60 % (p = 0.57). One lineage reaches 90 % and passes the flat-curve test; the
other falls to 15–20 % after timeouts and a search cap it set itself. Sonnet at medium is 61 %
late against 60 % at high (p = 0.69). The Hex effort result does not carry over.

### 7. Reuse is not what separates learners: tool quality is

Every lineage that had a tool used it. Haiku on Hex called its tool in 80 of 84 held-out
games and did not improve. What differs is how often the agent loses *while using* its tool
(held-out ID games through checkpoint 7, split by whether the game called a saved tool):

| Lineage group | Held-out games lost when a tool was called |
|---|---|
| Hex Sonnet high | 27 %, 12 % |
| Go Sonnet rep2 | 14 % |
| Go Sonnet run 1 | 63 % |
| Hex Haiku high | 62 %, 60 % |
| Go Haiku high | 53 %, 38 % |

The two Go Sonnet lineages share model and effort and differ by 49 points, so tool quality
varies between lineages, not only between models. This differs from the paper's chess
result, where reuse separated strong from weak improvers.

### 8. How good tools get made: the thinking (reports 16, 19)

Old runs kept no thinking, so every saved reflection turn of 13 runs was replayed with
thinking summaries on ($9.40). The replay repeats the recorded tool calls in only 5–40 % of
turns, so it shows how the model reasons at each recorded step, not what the run thought.

- **Learners test before installing.** High-effort Hex Sonnet played a new tool version
  against the current one in a third of its reflections (e.g. RAVE beat its MCTS 25 of 32
  before it was installed); Go Sonnet rep2 in over half. No Haiku reflection and no
  medium-effort Sonnet reflection ever did.
- **Haiku is an auditor.** About 60 % of its summaries are bookkeeping: failure-mode IDs,
  tracking files, the validator. It finds real bugs in how its tools are called, but never
  checks whether a change plays better.
- **Medium-effort Sonnet barely reflects.** 4–6 of 50 calls per round, one tool written once
  and never revised, or none at all.
- **Testing is necessary, not sufficient.** Go Sonnet run 1 tested in every reflection, but
  only against its own previous engine, and installed a rewrite at every checkpoint even when
  the new engine lost (7 of 8, 2 of 8). Rep2 checked its tool on positions from lost games,
  accepted the next version after a colour-balanced 15/24 match, and stopped changing code
  once it won 8 of 8.
- **Learned tools replace the actor's reasoning.** With its final tools the actor thinks on
  4–6 % of its turns; without them on 66–70 %, and wins about 40 points less often.

### 9. The metric rewards a bad start (GLM 5.3, reports 20, 21)

GLM lost most of its checkpoint-0 games to the time and call limits, then finished them
after one reflection. That one jump makes three of its four lineages pass the flat-curve test
(against one of eight Claude lineages at effort high) and gives its Go lineages P_sat of
48,000–60,000, over ten times the one Claude lineage that passes, while held-out ID after
checkpoint 1 is flat or falling. `go_glm_reflect_high` gets 48,432 and ends at 25 %. On Hex one
GLM reflection wrote a one-line off-by-one into its search tool and took held-out ID from 75 %
to 0 %; a model-free replay with the line fixed scores 12/12. The next reflection fixed a
different bug, called it the root cause, and never looked at the filter again.

**Finding 2 of the paper** (probe, $45.39; code not in the repo, games and traces in the dataset under `probes/finding2/`). The main runs
reproduce it only through this GLM effect: by P_sat GLM is the most "plastic" model and the
worst performer, because its curve starts from games it could not finish. A real test needs a
model that starts above Sonnet. At the repo's opponent levels Opus 5.5 is that model (10 of 12
checkpoint-0 Hex openings won, against 22 of 48 for Sonnet; $3.19), but Sonnet at effort high
ends at 12/12, so Hex leaves no room to compare gains. The probe therefore played held-out ID
against the alpha-beta engine at 1M nodes per move (the OOD level), on the plan D fresh
openings. Training games and reflection stayed as in plan D: 8 training games per checkpoint,
reflection at effort high, checkpoints 0–5.

| Held-out ID vs 1M nodes | Checkpoint 0, empty inventory | Checkpoints 3–5 | Learning cost to checkpoint 5 |
|---|---|---|---|
| Sonnet 5.5 (2 plan D lineages, inventories replayed) | 38 % (60 openings) | 67 % (36 openings) | $6.47, $6.70 |
| Opus 5.5 (1 new lineage) | 62 % (60 openings) | 69 % (36 openings) | $35.45 |

- Opus starts higher: better on 20 openings, worse on 5 (sign test p = 0.004).
- Sonnet rises 29 points (p = 0.002, openings as the unit); Opus rises 8 (p = 0.51).
- By checkpoints 3–5 the two are level: Sonnet is better on 5 openings and worse on 8
  (p = 0.58). The gap shrinks from 24 points to about 3 (one-sided p = 0.024).
- Gain per $1,000 of learning cost: about 4,400 points for Sonnet, about 200 for Opus. Most of
  that ratio is price: Opus's learning cost is five times Sonnet's.

So the better starter is not the more plastic model, in points and per dollar. Limits: one Opus
lineage; the 1M-node held-out level is a probe setting, not the repo's; Sonnet's curve replays
inventories its lineages built in plan D, which is valid because held-out games never reach
reflection; the gap test is one-sided, in the direction of the paper's claim.

### 10. Adapting to limits is part of plasticity, and it can backfire

After its first Go reflection Sonnet doubled its calls per game and lost 6 games to the
32-call budget; at the next checkpoint it moved play into its tool. Haiku drifted the other
way: more calls per game over time and illegal Go moves every checkpoint. One Go Sonnet
lineage later broke the 240 s tool limit (20 of 32 games forfeited at one checkpoint); after
it capped its own search, held-out ID stayed at 15 % for three checkpoints.

### 11. The metric is fragile at this scale

- The paper's 10-point rule alone gives P_sat > 0 to 26–43 % of synthetic agents that do not
  learn; every rise must be tested against a flat curve.
- Two models 25 % apart in true P_sat swap rank in 37–46 % of single-lineage comparisons.
- The price table alone can reverse a ranking.
- An unchanged control fell from 72 % to 56 % on the same openings and opponents (cause
  unknown: sampling or model drift).
- A replayed score is not a new measurement: a flat replayed tail makes a fit look saturated
  with more certainty than the data have.

## Probe: drift (one inventory, two games)

Opus 5.5, effort medium; checkpoint 0 trains on Hex, checkpoint 1 on Go, both games evaluated at
every checkpoint, 2 games per cell ($3.99). Far too few games to measure drift itself.

- The harness, prompts and validator handle two games in one inventory.
- The Go reflection kept `hex_engine.py` byte for byte, edited two lines of the Hex playbook,
  and added Go files plus a README that routes each game to its own engine. So forgetting, if
  any, would come through shared notes or the router, not lost tools.
- Opus won 2/2 Hex games before any reflection: at these opponent levels Hex may be at
  ceiling, and a real drift run would need harder Hex opponents.
- Full experiment: about $65 per lineage, $130 for two.

## Probe: Hex → Go stream, with and without shared files

After Chen et al. (arXiv:2610.25858): does learning a second game cost the first? Each lineage is
a Sonnet 5.5 Go lineage (effort high, 8 training games per checkpoint) whose checkpoint 0 starts
from the checkpoint-10 inventory of a Hex lineage (`hex_sonnet_high_fresh`, `_rep2`). At set
checkpoints the current inventory also plays 24 held-out Hex games (fresh openings, banks 9 and
10, usual levels), hidden from reflection and not part of the learning cost. Two lineages with
separate files, three with shared files; openings are the unit, paired sign tests. Code is private (scratchpad); the traces are on
the HF dataset under `probes/stream/` and `probes/pressure/`.

**Free stream** (checkpoints 0–5, $15.63). The inventory may grow any files.

- Hex did not move: 23/23/23 and 22/22/22 of 24 at checkpoints 0/3/5. Go reflection only added
  files (a Go playbook, `go_mcts.py`, a README that routes each game); the Hex playbook and tool
  are byte-identical at checkpoint 5. The Hex actor relays a deterministic tool, so this
  stability is structural, not tested.
- Go learned: 58 % → 92 % at checkpoint 3 (8 openings better, 0 worse, p 0.008).
- No interference at the start: Go at checkpoint 0 with the Hex inventory 58 % vs 62 % with an
  empty one (four old Go Sonnet lineages, 1/4, p 0.38).
- Forward transfer: at checkpoint 3 the stream beat the old Go high lineages, 92 % vs 60 % (11/0,
  p 0.001); at checkpoint 5 90 % vs 75 % (8/2, p 0.11). Both stream lineages built an MCTS tool at
  checkpoint 1, the pattern of their Hex tool. The old lineages ran earlier, so drift is
  not ruled out.

**Shared files** (checkpoints 0–3, $19.72). The inventory may hold only `memory/playbook.md`,
`tools/engine.py` and the two tracking files; the Hex inventory is renamed into these slots at
checkpoint 0, and the prompt and both validators enforce the rule. Reflection is not told that
Hex still matters.

| | Hex, checkpoints 0 → 1 → 2 → 3 (of 24) | Go, checkpoint 0 → 3 |
|---|---|---|
| Lineage 1 (from `hex_sonnet_high_fresh`) | 23 → 23 → 23 → 23 | 45 % → 90 % |
| Lineage 2 (from `_rep2`) | 22 → 18 → 19 → 19 | 50 % → 75 % |
| Lineage 3 (from `hex_sonnet_high_fresh`) | 23 → 11 → 16 → 16 | 65 % → 90 % |
| Pooled | 94 % → 72 % → 81 % → 81 % | 53 % → 85 % (11/0, p 0.001) |

Pooled Hex loss: checkpoint 0 → 1, 13 openings worse and none better (p 0.0002); 0 → 3, 0/8
(p 0.008).

- Lineage 1 added Go functions next to the Hex ones and left the Hex entry point alone.
- Lineage 2's first Go reflection made the Hex entry point `choose_move_from_api` serve both
  games (board text with "komi" → Go) and rewrote the playbook's quick start without the Hex
  budget argument, so Hex silently fell back to 30,000 playouts instead of 40,000.
- An offline replay (tool only, no model, free) reproduces the recorded games on 24/24 openings
  at checkpoint 0 and 23/24 at checkpoint 1. Checkpoint 1's code wins 19/24 at its new default
  and 22/24 with 40,000 playouts. So the budget change explains 3 of the 4 lost openings; in the
  fourth the actor played three moves itself instead of using the tool.
- Lineage 3's first Go reflection rewrote `tools/engine.py` as a Go-only engine (no Hex code
  left) and the playbook ("game changed from Hex", do not read the old Hex notes). Its Hex actor
  used the tool in 24/24 games at checkpoint 0 and in at most 1 game after that, playing by hand.
- Against the free stream at checkpoint 3: Hex 81 % vs 94 % (2/9, sign p 0.065, permutation
  p 0.013), Go 85 % vs 92 % (0/5, p 0.062).
- Go at checkpoint 0 with the renamed Hex inventory: 53 % vs 62 % with an empty one (2/7,
  p 0.18). At checkpoint 0 the Go actor never opens the inventory's files in any arm, so this is
  noise, not interference.

Reading: with separate files there was no forgetting to measure. With shared files, three
lineages gave three outcomes: Hex kept (1), Hex weakened by a changed shared default (2), and
Hex deleted (3). Lineages 1 and 3 started from the same inventory, so what happens is the
reflector's choice, not the start. Pooled, the Hex loss is significant (p 0.008 at
checkpoint 3), while Go still learns: the plasticity–stability trade-off of Chen et al.
appears once Go learning must share storage with Hex and nothing tells the reflector that Hex
still counts.

Why lineage 3 deleted Hex: after the Go training games, the first reflections of lineages 1 and 3
both concluded that the game had changed from Hex to Go. Lineage 1 then weighed keeping the Hex
code "since the games might come back" and kept it; lineage 3 replaced the engine directly and
never raised the question.

**Warned shared files** (checkpoints 0–1, $3.96). The same rule plus one line in the reflection
prompt: the inventory is still also used to play 6x6 Hex, so keep the Hex tool and notes working.
One lineage from each Hex inventory, one reflection, 24 Hex games at checkpoint 1 (checkpoint 0
is known: same inventories, deterministic tool).

- Both lineages kept the Hex code and the Hex budget in the playbook, and added Go behind a
  game check in the shared entry point.
- Hex at checkpoint 1: 22/24 and 20/24, 88 % against 72 % for the three unwarned lineages at
  checkpoint 1 (13 openings better, 2 worse, p 0.007), and against 94 % at their own checkpoint
  0 (0/3, p 0.25).
- So one sentence that the old task still counts prevented the deletion here. It is n = 2 at
  one checkpoint, and two of three unwarned lineages kept the Hex code too.

## What failed or stayed open

- **Test 5 did not isolate compute**: without records the reflector chose not to spend its
  budget.
- **The control ran three days after the lineages** it is compared with.
- **Go Sonnet is two lineages that disagree** (95 % vs 50 %); a third lineage is the cheapest
  way to settle the Go model ranking.
- **Training and OOD openings stayed fixed** in plan D; only held-out ID was made fresh.
- **The paper's Finding 2** rests on one Opus lineage, in a probe whose code is not in the repo.
- **No chess or NetHack**; Opus only in probes.
- **Thinking from the original runs is lost**; the replay is a proxy.
- **No per-move failure judge**, so the paper's absent / missed / used breakdown is
  approximated per game.

## Paid follow-ups not done (credit)

- A third Go Sonnet lineage at effort high (about $18–21 to checkpoint 10).
- Concurrent feedback and no-feedback lineages (about $15–30).
- A stricter test 5 that makes the reflector spend its budget without records (about $15).
- A second Opus 5.5 lineage for the Finding 2 probe (about $12–15).
- The drift experiment with harder Hex opponents (about $130 for two Opus lineages).
