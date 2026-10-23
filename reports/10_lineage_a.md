# 10 Lineage `lineage_a`: anthropic/claude-sonnet-5.5 on 6x6 Hex

Checkpoints 0–7; games per checkpoint {'train': 8, 'id': 12, 'ood': 4}; openings: contested.
Billed $0.97 (cap $17.00); learning cost priced the paper's way $0.63.

| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | Inventory files | Games reading / loading / calling saved artifacts | Reflection |
|---|---|---|---|---|---|---|---|---|
| 0 | $0.00 | 100 % | 17 % | 50 % | 0 | 0 | 0 / 0 / 0 of 24 | accepted (1) |

## Plasticity (held-out ID)

- Not enough checkpoints with learning cost to fit Eq. 4.

Stopped early: by hand after checkpoint 0 (see below).
## Why this run was stopped

At checkpoint 0 Sonnet 5.5 won **8/8 training games** (against every opponent, up to
100k nodes) but only **2/12 held-out ID games** (losing even to the 3k-node opponent).
Both splits used the same contested rule and opponent levels; only the openings
differed. With 8/8 vs 2/12 the two-proportion z is about 3.7. The contested banks
(report 09) were drawn from a separate seed per split, and the ID bank came out
harder; report 09's mid engine had already shown a smaller gap (train 29/40, ID 22/40).

Two consequences:

1. Training had no failures, so reflection (4 calls) saved nothing: no learning signal.
2. Held-out ID was not the same kind of game as training, so a later change on ID
   could not be read as generalisation.

The remaining seven checkpoints would have cost about $12 for a likely flat curve,
so the run was stopped by hand. Billed: $0.97 by the run's ledger (OpenRouter's
account total moved by $0.95 when checked shortly after). The fix is one shared opening pool
dealt to the splits by colour and engine-scored difficulty (report 11).
