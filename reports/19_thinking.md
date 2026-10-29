# 19 What the thinking shows about how learning happens

Reflection: thinking summaries from the replay of every saved reflection turn (report 16), a new
sample on the recorded input, so they show how the model reasons at each recorded step, not what the
original run thought. Actor: thinking recorded live in the limitation-test games (reports 17, 18).
Codes are regular expressions, checked by reading samples; they count mentions, not meaning.

## Reflection, per group

| Group | Learned | Attempts | Turns (with a summary) | Mean summary (chars) | Attempts testing a candidate in games against the current tool | Attempts discussing move time or timeouts | Summaries about bookkeeping | Summaries citing a game position | Turns running code in a scratch folder or match loop |
|---|---|---|---|---|---|---|---|---|---|
| Sonnet, medium | no | 16 | 88 (11) | 292 | 0 % | 0 % | 36 % | 0 % | 0 % |
| Sonnet, high | yes | 14 | 128 (78) | 525 | 33 % | 25 % | 23 % | 15 % | 37 % |
| Haiku, medium | no | 20 | 306 (299) | 675 | 0 % | 10 % | 61 % | 14 % | 2 % |
| Haiku, high | no | 14 | 290 (285) | 2175 | 0 % | 93 % | 58 % | 45 % | 9 % |
| Go Sonnet, run 1 | late, partly | 6 | 152 (135) | 1013 | 100 % | 100 % | 18 % | 30 % | 57 % |
| Go Sonnet, rep2 | yes | 7 | 99 (71) | 663 | 57 % | 71 % | 24 % | 52 % | 35 % |
| Go Haiku, high | no | 14 | 296 (293) | 2128 | 0 % | 0 % | 60 % | 43 % | 1 % |

Testing a candidate counts attempts with at least one summary that reports or plans games between a
new tool and the current one ("head-to-head", "arena", "self-play", "25/32 against the old").
Bookkeeping: failure-mode IDs, tracking files, schema, validator. Medium-effort Sonnet thought on few
turns, so its shares rest on few summaries.

## Actor thinking with and without saved tools

| Source | Inventory | Games | Actor turns | Turns with a summary | Mean summary (chars) |
|---|---|---|---|---|---|
| Report 17, `with` arm | final tools | 48 | 554 | 31 (6 %) | 166 |
| Report 17, `forced` arm | final tools, use required | 48 | 546 | 21 (4 %) | 179 |
| Report 17, `empty` arm | none | 48 | 338 | 236 (70 %) | 280 |
| Report 18, no-feedback lineages | none | 384 | 2699 | 1789 (66 %) | 293 |

## Reading

- **The groups that learned tested candidate tools in games before installing them.** Hex Sonnet at
  effort high did so in a third of its reflections, Go Sonnet rep2 in over half; no Haiku group and no
  medium-effort Sonnet reflection ever did. Example (`sonnet_reflect_high`, checkpoint 2): after one
  loss in 8 it built a RAVE variant, played it against its current MCTS in parallel background matches
  ("RAVE wins 25/32 at 15k vs 30k playouts"), timed it against the 240 s limit, and only then
  installed it and filed the loss as a new failure mode.
- **Haiku reflects like an auditor.** At effort high its summaries are about four times as long as
  Sonnet's, and at both efforts about 60 % are about bookkeeping: failure-mode IDs, tracking files, the
  validator. It traces concrete bugs in how the actor called its tools (e.g. `winning_cells()` called
  with one argument) and files them, and on Hex it worries about move time in almost every reflection.
  It never played a new version of a tool against the old one; once it planned to score a rewrite on
  reconstructed losing positions. Its tools change; its results do not.
- **Medium-effort Sonnet barely thinks.** Adaptive thinking produced a summary on 11 of 88 replayed
  turns; the reflections read the records, ran the validator and stopped (report 12).
- **Testing is necessary, not sufficient: the two Go Sonnet lineages.** Both tested candidates. Run 1
  tested in every reflection, but only against its own previous engine, and its summaries say so
  ("self-play results between my own engines aren't the real benchmark"). Its new engines often lost
  those matches (7 of 8, 2 of 8), it alternated between calling the opponent weak and strong, and it
  decided Black was lost from move 1 under komi 9.5. It still installed a rewritten alpha-beta engine at
  every checkpoint (six versions); its own closing notes say it "could not show that either one wins
  more games" and that none of the changes was "tested in a real game". Rep2 found the bug that made
  its first helper unusable in every game (`load_python` returns a string), switched to MCTS at
  checkpoint 1, checked it on positions from the lost games, accepted the next version after a
  colour-balanced 15/24 match, sized its playouts to the time limit, and from checkpoint 5 (8 of 8
  won) changed no code. It reached 85–90 %; run 1 stayed at 30–35 % until its last counted checkpoint.
- **Learned tools take over the actor's reasoning.** With its final tools the actor wrote a thinking
  summary on 4–6 % of its turns and handed each move to the tool; without them it thought on 66–70 % of
  turns, about bridges and connections, and won about 40 points less often (report 17). The learning
  sits in the code, and the model stops reasoning about the game once the code exists.
- **Without game records the reflector reasons that it should do nothing** (report 18): "There's no
  data to map, so an empty inventory is actually valid here." The protocol's rule that every tool must
  address an observed failure keeps it from building anything.

## Limits of this analysis

- Reflection summaries are replayed, not original: the replayed turn made the recorded tool calls in
  only 5–40 % of turns (report 16). They show how the model reasons at each recorded step.
- Summaries are summaries; the raw chain of thought is not available.
- The codes are keyword matches. The candidate-testing code first counted Haiku's timing checks and
  validator "baselines" as tests; it was narrowed to games between versions after reading the matches.
- Medium-effort Sonnet has few summaries, so its row says little.
- Seven groups, one or two lineages each; this describes these runs, it does not establish causes.
