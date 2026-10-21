# 06 Dry run of the Hex harness (scripted model, no API calls)

A scripted model plays the first legal action until its inventory has a tool; its first
reflection writes a greedy connection-distance tool. This tests the pipeline, not a model.
Token counts are estimates (4 characters per token) priced at a hypothetical $3 / $15 per
million input / output tokens.

| Checkpoint | Cumulative learning cost | Train | Held-out ID | Held-out OOD | Reflection |
|---|---|---|---|---|---|
| 0 | $0.000 | 0 % (6) | 0 % (8) | 0 % (4) | accepted after 1 attempt(s) |
| 1 | $0.052 | 17 % (6) | 25 % (8) | 0 % (4) | accepted after 1 attempt(s) |
| 2 | $0.104 | 17 % (6) | 25 % (8) | 0 % (4) | accepted after 1 attempt(s) |
| 3 | $0.156 | 17 % (6) | 25 % (8) | 0 % (4) | – |

Held-out ID P_sat: 485161 points per $1,000 (saturated), rise p-value 0.273.
The P_sat value is meaningless here: the scripted model's cost is a few cents, so any
gain divided by it is huge, and with 8 held-out games the rise is not significant.
What the run shows: the reflection wrote a tool, the validator accepted it, the next
checkpoint's actor loaded and used it, held-out games stayed hidden, and the costs
and scores reached Eq. 2–5. Checkpoints 1–3 match because the engine is deterministic
and the inventory did not change.
