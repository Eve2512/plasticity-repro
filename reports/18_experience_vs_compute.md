# 18 Experience vs compute (limitation test 5)

Hex 6×6, Sonnet 5.5, actor effort medium, reflection effort high, 8 / 12 / 4 games per checkpoint,
checkpoints 0–7, same opening bank. The no-feedback lineages played and paid for the same training
games, but reflection found only a note saying no records were available, with the same 50-call
budget, its inventory and the protocol files (`--no-feedback`).

## Per lineage

| Lineage | Reflection saw | Held-out ID per checkpoint (%) | Fit rise (pp) | p | Reflection calls (of 50) | Functional inventory files per checkpoint | Games calling a saved tool | Billed |
|---|---|---|---|---|---|---|---|---|
| `sonnet_reflect_high` | game records | 50, 50, 83, 75, 75, 75, 75, 75 | 26.7 | 0.13 | 10.3 | 0, 3, 3, 3, 3, 3, 3, 3 | 85 % | $7.44 |
| `sonnet_reflect_high_rep2` | game records | 75, 67, 92, 92, 92, 92, 92, 92 | 20.9 | 0.12 | 8.0 | 0, 2, 2, 2, 2, 2, 2, 2 | 88 % | $7.77 |
| `sonnet_nofeedback_high` | no game records | 75, 75, 75, 50, 58, 58, 58, 42 | 4.1 | 1 | 4.0 | 0, 0, 0, 0, 0, 0, 0, 0 | 0 % | $7.00 |
| `sonnet_nofeedback_high_rep2` | no game records | 50, 83, 75, 58, 58, 50, 83, 42 | 14.3 | 0.83 | 4.0 | 0, 0, 0, 0, 0, 0, 0, 0 | 0 % | $6.85 |

## Held-out ID pooled, early (checkpoints 0–2) → late (3 onward)

| Reflection saw | Early | Late | z | p |
|---|---|---|---|---|
| game records | 50/72 = 69 % | 100/120 = 83 % | 2.25 | 0.024 |
| no game records | 52/72 = 72 % | 67/120 = 56 % | -2.26 | 0.024 |

Late, game records vs none: z = 4.63, p = 3.7e-06.

## Same openings, checkpoint by checkpoint

All four lineages play the same 12 held-out ID openings, against the same deterministic opponents,
at every checkpoint, so the arms can be compared game by game. Lineage 1 is paired with lineage 1,
rep2 with rep2.

| Checkpoint | Game records (wins of 24) | No game records (wins of 24) | Difference |
|---|---|---|---|
| 0 | 15 | 15 | +0 |
| 1 | 14 | 19 | -5 |
| 2 | 21 | 18 | +3 |
| 3 | 20 | 13 | +7 |
| 4 | 20 | 14 | +6 |
| 5 | 20 | 13 | +7 |
| 6 | 20 | 17 | +3 |
| 7 | 20 | 10 | +10 |

Early: 8 games won only with game records, 10 only without; sign test p = 0.81.

Late: 38 games won only with game records, 5 only without; sign test p = 2.5e-07.

## Baselines without tools

| Source | Held-out ID |
|---|---|
| No-feedback lineages, all checkpoints (inventory always empty) | 119/192 = 62 % |
| Report 17, `empty` arm (feedback lineages' final checkpoint, inventory removed) | 25/48 = 52 % |

Difference: z = -1.25, p = 0.21 (different openings: report 17 drew 24 from checkpoint 7's bank).

## Thinking summaries in reflection

| Lineage | Reflection turns with a summary |
|---|---|
| `sonnet_reflect_high` | 0/72 |
| `sonnet_reflect_high_rep2` | 0/56 |
| `sonnet_nofeedback_high` | 6/28 |
| `sonnet_nofeedback_high_rep2` | 7/28 |

## Reading

- Without game records the reflector built nothing. In all 14 reflections it used 4 of its 50 calls,
  read the note and its empty inventory, ran the validator and stopped. Its thinking summaries say why:
  the protocol asks every functional file to address an observed failure mode, and with nothing observed
  any tool would be a guess. The extra compute was offered but not used.
- So this test does not separate experience from compute the way it was planned. It shows that, under
  the paper's reflection prompt, game records are what makes the agent build anything at all. A
  stricter control would require the reflector to spend its budget (e.g. build a general Hex player from
  the rules alone) and compare that with the feedback arm.
- The no-feedback lineages are an untrained control on the same openings. Before tools mattered
  (checkpoints 0–2) the arms are level (sign test p = 0.81); from checkpoint 3 the feedback arm wins
  38 games the control loses and loses 5 the control wins (p = 2.5e-07). This paired test is much
  stronger than either feedback lineage's own flat-curve test (p = 0.12–0.13, report 15).
- The control's held-out ID falls from 72 % to 56 % (p = 0.024 if games are treated as independent)
  although nothing changed: same empty inventory, same 12 openings at every checkpoint, deterministic
  opponents. The drop is spread over six openings. The only varying part is the actor's sampling, plus
  any drift in the served model during the ~3 hours of the run. A single lineage's curve can move this
  much without any learning, and repeated openings make games far from independent.
- The control ran three days after the feedback lineages (2026-10-28/29 vs 2026-10-25), so the paired
  test controls for openings and opponents, not for time. At checkpoint 0 the arms are level (15 vs 15
  wins), and the feedback lineages' late rate (83 %) is above the control's best stretch (72 %) too.
- The control's pooled rate (62 %) and report 17's `empty` arm (52 %) do not differ significantly
  (p = 0.21); both put the no-tool actor at roughly 50–60 %.
- These are the first lineages with thinking recorded during the run (report 16 covers replayed
  thinking for the older runs).
