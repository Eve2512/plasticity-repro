# 22 Go: reflection effort medium vs high (Sonnet 5.5 and Haiku 5.5)

Plan C ran two Go lineages per model at reflection effort medium, with every other setting as in the
high-effort Go lineages of report 15: actor effort medium, 8 / 20 / 4 games per checkpoint (train /
held-out ID / OOD), checkpoints 0–10, GNU Go levels 5–9 (ID) and 10 (OOD).
Early = checkpoints 0–2; late = checkpoint 3 onward.

## Held-out ID, early → late

| Model | Reflection effort | Checkpoint 0 | Early | Late | Change | z | p |
|---|---|---|---|---|---|---|---|
| Sonnet 5.5 | medium | 24/40 = 60 % | 72/120 = 60 % | 196/320 = 61 % | +1 pp | 0.24 | 0.81 |
| Sonnet 5.5 | high | 26/40 = 65 % | 68/120 = 57 % | 191/320 = 60 % | +3 pp | 0.57 | 0.57 |
| Haiku 5.5 | medium | 19/40 = 48 % | 56/120 = 47 % | 165/320 = 52 % | +5 pp | 0.91 | 0.36 |
| Haiku 5.5 | high | 21/40 = 52 % | 66/120 = 55 % | 150/320 = 47 % | -8 pp | -1.52 | 0.13 |

## High against medium, late checkpoints

| Model | Medium late | High late | z | p |
|---|---|---|---|---|
| Sonnet 5.5 | 196/320 = 61 % | 191/320 = 60 % | -0.40 | 0.69 |
| Haiku 5.5 | 165/320 = 52 % | 150/320 = 47 % | -1.19 | 0.24 |

## Per lineage

| Lineage | Reflection effort | Held-out ID per checkpoint (%) | Fit rise (pp) | p | P_sat | Reflection calls | Code revisions | Games calling a saved tool | Billed |
|---|---|---|---|---|---|---|---|---|---|
| `go_sonnet_medium` | medium | 65, 55, 60, 65, 60, 60, 55, 55, 55, 60, 60 | 15.3 | 1 | 0 (to_date) | 6.7 | 2 | 1 % | $15.69 |
| `go_sonnet_medium_rep2` | medium | 55, 65, 60, 60, 65, 65, 65, 55, 65, 70, 65 | 33.6 | 0.89 | 761 (to_date) | 5.6 | 1 | 6 % | $16.76 |
| `go_sonnet_reflect_high` | high | 55, 30, 30, 35, 35, 60, 20, 15, 15, 15, 50 | 13.7 | 1 | 0 (to_date) | 23.5 | 8 | 90 % | $20.93 |
| `go_sonnet_reflect_high_rep2` | high | 75, 60, 90, 85, 85, 90, 90, 90, 90, 90, 90 | 21.4 | 0.019 | 3798 (saturated) | 15.4 | 8 | 85 % | $17.95 |
| `go_haiku_medium` | medium | 40, 45, 35, 40, 65, 65, 45, 40, 45, 55, 60 | 14.0 | 0.33 | 23266 (saturated) | 14.0 | 8 | 7 % | $2.26 |
| `go_haiku_medium_rep2` | medium | 55, 55, 50, 60, 30, 50, 50, 50, 50, 60, 60 | 17.8 | 0.75 | 9416 (extrapolated) | 10.8 | 6 | 0 % | $2.14 |
| `go_haiku_reflect_high` | high | 55, 55, 65, 55, 40, 45, 45, 35, 40, 45, 45 | 0.0 | 1 | 0 (no_rise) | 23.0 | 10 | 61 % | $2.97 |
| `go_haiku_reflect_high_rep2` | high | 50, 55, 50, 50, 45, 60, 50, 55, 35, 50, 55 | 50.0 | 0.99 | 10025 (extrapolated) | 20.4 | 8 | 21 % | $2.85 |

## Behaviour under constraints, effort medium

All splits, both lineages pooled per checkpoint; columns as in report 15 (high effort is there).

| Model | Checkpoint | Games | Calls per game | Near budget | Lost to limits | Illegal submissions | Moves per call |
|---|---|---|---|---|---|---|---|
| Sonnet 5.5 | 0 | 64 | 9.9 | 0 % | 0 | 11 | 0.85 |
| Sonnet 5.5 | 1 | 64 | 10.4 | 0 % | 0 | 12 | 0.83 |
| Sonnet 5.5 | 2 | 64 | 10.3 | 0 % | 0 | 13 | 0.81 |
| Sonnet 5.5 | 3 | 64 | 10.8 | 0 % | 0 | 4 | 0.80 |
| Sonnet 5.5 | 4 | 64 | 11.6 | 0 % | 0 | 12 | 0.79 |
| Sonnet 5.5 | 5 | 64 | 11.1 | 0 % | 0 | 8 | 0.80 |
| Sonnet 5.5 | 6 | 64 | 11.2 | 0 % | 0 | 9 | 0.77 |
| Sonnet 5.5 | 7 | 64 | 11.0 | 0 % | 0 | 8 | 0.78 |
| Sonnet 5.5 | 8 | 64 | 10.7 | 0 % | 0 | 5 | 0.77 |
| Sonnet 5.5 | 9 | 64 | 10.9 | 0 % | 0 | 7 | 0.78 |
| Sonnet 5.5 | 10 | 64 | 12.8 | 2 % | 0 | 4 | 0.68 |
| Haiku 5.5 | 0 | 64 | 12.0 | 2 % | 1 | 10 | 0.85 |
| Haiku 5.5 | 1 | 64 | 11.8 | 2 % | 2 | 5 | 0.81 |
| Haiku 5.5 | 2 | 64 | 11.4 | 2 % | 0 | 6 | 0.80 |
| Haiku 5.5 | 3 | 64 | 11.7 | 2 % | 0 | 7 | 0.79 |
| Haiku 5.5 | 4 | 64 | 12.7 | 3 % | 3 | 7 | 0.77 |
| Haiku 5.5 | 5 | 64 | 10.8 | 0 % | 0 | 5 | 0.79 |
| Haiku 5.5 | 6 | 64 | 12.5 | 5 % | 0 | 9 | 0.78 |
| Haiku 5.5 | 7 | 64 | 12.3 | 2 % | 1 | 4 | 0.73 |
| Haiku 5.5 | 8 | 64 | 12.4 | 2 % | 0 | 12 | 0.85 |
| Haiku 5.5 | 9 | 64 | 11.2 | 3 % | 1 | 13 | 0.74 |
| Haiku 5.5 | 10 | 64 | 11.4 | 2 % | 1 | 6 | 0.80 |

## Reading

- On Go, reflection effort makes no measurable difference. Late held-out ID is 61 % at medium and 60 % at
  high for Sonnet (p = 0.69), 52 % and 47 % for Haiku (p = 0.24), from the same start (checkpoint 0: Sonnet
  60 % and 65 %, Haiku 48 % and 52 %). No cell's pooled early → late change is significant. On Hex, high
  effort ended at 83 % against 65 % for medium (z = 3.75, p = 0.0002; report 12), so the Hex effort
  result does not carry over to Go.
- Sonnet at medium effort reflects on Go as it did on Hex: 5.6–6.7 calls per round, code changed at 1–2
  of 10 reflections, and the actor ran a saved tool in 1–6 % of games. Held-out ID stays within 55–70 %
  in both lineages and neither passes the flat-curve gate. Play does not change either: 10–13 model calls
  per game, under 0.9 moves per call, and 4–13 illegal submissions per checkpoint to the end, where
  Sonnet at high effort moved play into its tool (about 1 move per call) and stopped submitting
  illegal moves after checkpoint 2 (0–1 per checkpoint, report 15).
- High effort changed what Sonnet does on Go, but not its pooled score. Its two lineages split:
  `go_sonnet_reflect_high_rep2` holds 85–90 % from checkpoint 2, above every medium checkpoint, and
  `go_sonnet_reflect_high` falls to 15–20 % at checkpoints 6–9 after its time-limit failure (report 15).
  Pooled, they land on the medium lineages' score. With two lineages per cell, high effort here
  widened the spread of outcomes rather than moving the mean.
- Haiku at medium effort is busy, as at high: 11–14 reflection calls per round and code changed at 6–8
  of 10 reflections, but its actor ran a saved tool in 0–7 % of games (21–61 % at high effort). Much of
  the saved code checks Haiku's own moves and reflections (legality guards, a pass gate, loss audits).
- `go_haiku_medium` gets P_sat 23,266 ("saturated") from a 14-point fitted rise with p = 0.33: ID
  jumped to 65 % at checkpoints 4–5 and fell back to 40–45 %. It passes the paper's 10-point rule
  alone and fails the flat-curve gate, like the Haiku false positives of report 15.
- Medium effort was cheaper: billed $15.69–16.76 per Sonnet lineage (high: $17.95–20.93) and $2.14–2.26
  per Haiku lineage (high: $2.85–2.97).
