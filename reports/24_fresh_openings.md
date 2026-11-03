# 24 Fresh held-out openings: Hex Sonnet 5.5, reflection effort high vs medium

Plan D re-ran the four Hex Sonnet 5.5 lineages of report 12 (two at reflection effort high, two at
medium; actor effort medium; 8 / 12 / 4 games per checkpoint; checkpoints 0–10) with one change:
the 12 held-out ID openings are new at every checkpoint, drawn from the same contested pool outside
the pooled banks and dealt to checkpoints by difficulty (`--openings fresh`). The four lineages
play the same openings at a given checkpoint, so high and medium effort can be compared opening by
opening. Training and OOD openings are the pooled banks of the original runs.
Early = checkpoints 0–3; late = 4–10 (report 12's split).

Held-out ID games: 528, on 132 distinct (opening, colour) pairs; no lineage played any held-out opening twice.

## Held-out ID, early → late, games pooled

| Openings | Reflection effort | Early | Late | Change | z | p |
|---|---|---|---|---|---|---|
| fresh (plan D) | high | 69/96 = 72 % | 147/168 = 88 % | +16 pp | 3.17 | 0.0015 |
| fresh (plan D) | medium | 55/96 = 57 % | 94/168 = 56 % | -1 pp | -0.21 | 0.83 |
| fixed (original) | high | 70/96 = 73 % | 140/168 = 83 % | +10 pp | 2.02 | 0.044 |
| fixed (original) | medium | 57/96 = 59 % | 110/168 = 65 % | +6 pp | 0.99 | 0.32 |

## Openings as the unit

Paired tests compare the same openings; early → late compares different openings.

| Comparison | Openings | A | B | B better / worse | Sign test p | Permutation p |
|---|---|---|---|---|---|---|
| High vs medium, late (A medium, B high) | 84 | 56 % | 88 % | 46 / 6 | 1e-08 | 1e-05 |
| High vs medium, early (A medium, B high) | 48 | 57 % | 72 % | 15 / 2 | 0.0023 | 0.0022 |
| High, early → late (A early, B late) | 48 + 84 | 72 % | 88 % | – | – | 0.015 |
| Medium, early → late (A early, B late) | 48 + 84 | 57 % | 56 % | – | – | 0.91 |

## Per lineage

| Lineage | Reflection effort | Held-out ID per checkpoint (of 12) | Fit rise (pp) | p | P_sat | Code revisions | Games calling a saved tool | Billed |
|---|---|---|---|---|---|---|---|---|
| `hex_sonnet_high_fresh` | high | 7, 10, 9, 11, 9, 9, 11, 11, 11, 11, 12 | 23.9 | 0.046 | 1782 (extrapolated) | 2 | 88 % | $10.60 |
| `hex_sonnet_high_fresh_rep2` | high | 4, 8, 10, 10, 9, 10, 11, 10, 11, 10, 12 | 66.6 | 0.00059 | 2529 (extrapolated) | 2 | 88 % | $11.04 |
| `hex_sonnet_medium_fresh` | medium | 5, 7, 6, 10, 8, 8, 8, 9, 7, 7, 7 | 17.5 | 0.41 | 8525 (saturated) | 0 | 0 % | $11.09 |
| `hex_sonnet_medium_fresh_rep2` | medium | 6, 4, 8, 9, 5, 1, 7, 6, 5, 9, 7 | 20.6 | 0.61 | 1752 (extrapolated) | 1 | 66 % | $12.21 |

## Reading

- With no held-out game played twice, the effort result holds and is much better supported. Over
  checkpoints 4–10 high effort scores 88 % against 56 % for medium; per opening it is better on 46 of
  84 and worse on 6 (sign test p = 1e-08; no permutation draw was as extreme, p ≤ 1e-05). With the
  original fixed openings the same comparison rested on 12 openings (10 better, 1 worse, p = 0.012,
  report 23).
- The gap opens after the first reflection. Checkpoint 0 plays with an empty inventory in all four
  lineages and both conditions score 11/24 there; over checkpoints 0–3 high effort is already ahead
  (72 % against 57 %, 15 openings better, 2 worse, p = 0.0023).
- The learning curve holds. High effort rises from 72 % at checkpoints 0–3 to 88 % at 4–10, measured
  on 48 and 84 different openings (permutation p = 0.015 with openings as the unit; pooled games
  p = 0.0015). Medium effort stays level (57 % → 56 %, p = 0.91). The late gain is on positions the
  lineage had never played, so it is not a replay.
- Plan D's numbers are close to the original lineages' (high 73 % → 83 %, medium 59 % → 65 %). The
  fresh openings include more easy ones than the 12 original held-out openings (64 % against 50 % at
  the top difficulty score), so levels across the two plans are not strictly comparable; the
  comparisons inside plan D are.
- Per lineage, both high-effort lineages pass the flat-curve gate (p = 0.046 and 0.00059) and end at
  12/12. Neither medium lineage does, although `hex_sonnet_medium_fresh` gets P_sat 8,525
  ("saturated") from a fit with p = 0.41, the 10-point-rule false positive of reports 02 and 15.
  Medium effort again built little: `hex_sonnet_medium_fresh` never changed its code, and
  `hex_sonnet_medium_fresh_rep2` wrote one tool that its actor called in 66 % of games without a
  lasting gain (it fell to 1/12 at checkpoint 5).
- Training and OOD openings were fixed, as in the original runs, so training games can still repeat;
  the held-out measurement, on which plasticity is defined, no longer does.
