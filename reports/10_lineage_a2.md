# 10 Lineage `lineage_a2`: anthropic/claude-sonnet-5.5 on 6x6 Hex

Checkpoints 0–7; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: pooled.
Billed $9.49 (cap $17.00); learning cost priced the paper's way $9.09.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 88 % | 67 % | 25 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (2) |
| 1 | $0.74 | 88 % | 50 % | 25 % | 0 | 1 | 24 / 0 / 0 of 24 | accepted (1) |
| 2 | $1.49 | 62 % | 67 % | 50 % | 0 | 2 | 22 / 22 / 22 of 24 | accepted (1) |
| 3 | $2.85 | 62 % | 67 % | 25 % | 0 | 2 | 21 / 21 / 21 of 24 | accepted (1) |
| 4 | $4.05 | 50 % | 67 % | 25 % | 0 | 2 | 19 / 19 / 19 of 24 | accepted (1) |
| 5 | $5.47 | 62 % | 58 % | 50 % | 0 | 2 | 18 / 18 / 18 of 24 | accepted (1) |
| 6 | $6.49 | 62 % | 67 % | 25 % | 0 | 2 | 21 / 21 / 21 of 24 | accepted (1) |
| 7 | $7.75 | 62 % | 50 % | 0 % | 0 | 2 | 16 / 16 / 16 of 24 | – |

## Plasticity (held-out ID)

- Average plasticity (Eq. 3, last checkpoint): -2149.4 points per $1,000.
- Saturation fit (Eq. 4): S0 = 58.5 %, rise = 4.0 points, h = 10.00.
- P_sat (Eq. 5, paper rules): 0.0 points per $1,000 (no_rise).
- Rise against a flat curve: p = 0.99; it does not pass the p < 0.05 gate from report 03.

## Analysis (written after the run)

Run of 2026-10-23 through OpenRouter, effort `medium`, pooled openings (report 11).
Two connection drops during the run were ridden out by the adapter's retries; no game
was unfinished.

### No plasticity

Held-out ID stays between 50 % and 67 % at every checkpoint. The saturation fit finds a
4-point rise that is not significant (p = 0.99), so P_sat = 0. The negative average
plasticity (Eq. 3) only compares checkpoint 7 (50 %) with checkpoint 0 (67 %); with 12
games per checkpoint that difference is within noise.

### Before and after the tool

The second reflection wrote `tools/hexeval.py` (44 lines: board parser, connection
distance, candidate moves scored own − 1.2 × opponent distance). From checkpoint 2 on,
the actor ran it in 16–22 of 24 games.

| | Before the tool (checkpoints 0–1) | With the tool (checkpoints 2–7) | z |
|---|---|---|---|
| Train | 14/16 = 88 % | 29/48 = 60 % | 2.0 |
| Held-out ID | 14/24 = 58 % | 45/72 = 62 % | −0.4 |
| Held-out OOD | 2/8 = 25 % | 7/24 = 29 % | −0.2 |

Games that called the tool won 68/117 (58 %), games that did not 13/27 (48 %); this is
observational and does not show that the tool helped. Training got worse with the tool
(borderline, z = 2.0) and held-out play did not change.

### Where the improvement loop broke: reflection effort

- The tool was written once (checkpoint 2) and **never revised** in the five later
  reflections. Only one failure mode (FM-0001) was ever recorded; every later loss was
  filed under it.
- Each reflection used **4–6 of its 50 calls**. The model's own summaries say so:
  "I didn't open the move-by-move session logs", "I did not change `tools/hexeval.py`
  or test any of this in play".
- What changed each round was a paragraph of lessons appended to
  `memory/hex_strategy.md` ("block on the opponent's shortest path", "run hexeval every
  turn"). Writing a rule down did not change results, as the paper also observes
  ("writing down an instruction is not the same as following it").

In the paper's terms (Section 3.5) this lineage has **high reuse** (most games called the
artifact) but the failures remain while the artifact is used, and the artifact itself
was not improved. Here the evidence points at **shallow reflection** as the bottleneck,
not retrieval: the reflector rarely read the per-move diagnostics it was given.

### Colour

On held-out ID the agent won 39/48 as red and 20/48 as blue. The banks are balanced for
engines (report 11), so this is the model's own weakness as the second mover; the agent
named it in its notes ("Blue (second mover) loses races").

### Cost and time

$9.49 billed: $9.12 for 192 games ($0.048 per game) and $0.36 for 7 reflections
($0.052 each; short because the reflector used few calls). About 6.5 hours of wall
clock, including a slow, unstable connection during the first checkpoint.

### What this suggests next

1. **Reflection effort as a variable.** The paper treats plasticity as protocol-dependent;
   effort `medium` may cap how deeply the reflector works. A lineage with reflection at
   effort `high` would test that directly.
2. **The no-feedback control (option B)** is less informative while the main lineage
   shows no gain; it becomes the right next test once a lineage improves.
3. **More held-out games.** With 12 ID games at about 60 %, two single checkpoints need
   to differ by about 40 points to be distinguishable (2 standard errors); pooling the
   first and last four checkpoints (48 games each) brings that to about 20 points.
