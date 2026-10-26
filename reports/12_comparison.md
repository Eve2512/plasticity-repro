# 12 Lineages compared

| Lineage | Model | Checkpoints | ID first half → second half | Train first → second half | Fit rise (pp) | p | P_sat | Mean reflection calls | Rejected attempts | Code revisions | Games calling a saved tool | Billed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lineage_a2 | claude-sonnet-5.5 | 8 | 62 % → 60 % | 75 % → 59 % | 4.0 | 0.99 | 0 (no_rise) | 5.6 | 1 | 1 | 61 % | $9.49 |
| sonnet_medium_rep2 | claude-sonnet-5.5 | 8 | 56 % → 65 % | 72 % → 62 % | 19.6 | 0.44 | 13595 (saturated) | 5.4 | 1 | 0 | 0 % | $9.57 |
| sonnet_reflect_high | claude-sonnet-5.5 | 8 | 65 % → 75 % | 72 % → 100 % | 26.7 | 0.13 | 6484 (saturated) | 10.3 | 0 | 3 | 85 % | $7.44 |
| sonnet_reflect_high_rep2 | claude-sonnet-5.5 | 8 | 81 % → 92 % | 88 % → 100 % | 20.9 | 0.12 | 5428 (saturated) | 8.0 | 0 | 2 | 88 % | $7.77 |
| haiku_r20 | claude-haiku-5.5 | 21 | 32 % → 31 % | 18 % → 26 % | 69.1 | 0.94 | 4381 (extrapolated) | 15.3 | 0 | 9 | 33 % | $7.86 |

Held-out ID per checkpoint (%):

- `lineage_a2`: 67, 50, 67, 67, 67, 58, 67, 50
- `sonnet_medium_rep2`: 58, 33, 67, 67, 58, 67, 75, 58
- `sonnet_reflect_high`: 50, 50, 83, 75, 75, 75, 75, 75
- `sonnet_reflect_high_rep2`: 75, 67, 92, 92, 92, 92, 92, 92
- `haiku_r20`: 29, 29, 38, 42, 38, 17, 25, 33, 29, 42, 29, 33, 46, 42, 12, 8, 33, 21, 46, 38, 33

All lineages: 6×6 Hex, pooled openings, games played at effort `medium`; 8 checkpoints
(Sonnet) or 21 (Haiku); games per checkpoint 8 / 12 / 4 (Sonnet) and 20 / 24 / 8 (Haiku).
"Code revisions" counts checkpoints at which the saved Python changed. "Fit rise" and "p"
are the saturation fit (Eq. 4) and the likelihood-ratio test from report 03; P_sat values
are large because learning costs are a few dollars.

## Reflection effort: two lineages per condition

| Condition | Lineages | ID, checkpoints 0–3 | ID, checkpoints 4–7 | Within-condition change |
|---|---|---|---|---|
| Reflection effort `medium` | `lineage_a2`, `sonnet_medium_rep2` | 57/96 = 59 % | 60/96 = 62 % | z = 0.44, p = 0.66 |
| Reflection effort `high` | `sonnet_reflect_high`, `sonnet_reflect_high_rep2` | 70/96 = 73 % | 80/96 = 83 % | z = 1.75, p = 0.08 |

- **High against medium at checkpoints 4–7: 83 % against 62 %, z = 3.25, p = 0.001.**
- Checkpoint 0 is played before any reflection, so it is the same condition for both:
  15/24 each. The conditions start level and separate only after reflection begins.
- Both high-effort lineages improve their held-out ID score and then hold it (50 → 75 %,
  and 75 → 92 %); neither medium lineage does.
- Behaviour matches: with high effort, reflections use more calls (8–10 vs 5–6), the
  saved code is revised 2–3 times (vs 0–1), and 85–88 % of games run a saved tool (vs
  0–61 %).
- Per lineage, no single fit passes p < 0.05 (0.12 and 0.13 for the high-effort runs):
  12 held-out games per checkpoint are too few for one lineage. The pooled two-lineage
  comparison is what carries the evidence.

**Reading.** In this setup, how much the model invests in reflection decides whether
experience turns into held-out gains. The paper treats plasticity as protocol-dependent
and does not vary reflection effort; here it is the factor that separates "no
plasticity" from "plasticity" for the same model, with the same budget per game.

Caveats: two lineages per condition; one model; one game; the split into checkpoints
0–3 and 4–7 is the halfway point fixed by the 8-checkpoint design, not chosen after the
fact, but the high-vs-medium question itself was raised after seeing the first
high-effort run.

## Haiku 5.5 over 21 checkpoints

Held-out ID stays around 31 % (checkpoints 0–9: 32 %, 10–20: 31 %, p = 0.81); the fit's
69-point "rise" is an extrapolation the test rejects (p = 0.94). Reflection was busy
(15 calls per reflection, code revised at 9 checkpoints, a saved tool run in a third of
games) but did not help. In the paper's terms this is the failure despite use: artifacts
were built, changed and used, and the failures remained, pointing at artifact quality or
application rather than retrieval.

## Totals

5 lineages here, 1,860 games, $42.13 billed (A2 $9.49, medium rep $9.57, high $7.44,
high rep $7.77, Haiku $7.86).
