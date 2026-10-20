# 04 Pricing dependence of P_sat

Both agents follow the same score curve per learning round
(S0 = 20 %, rise 50 pp, half the rise after 4 rounds).
Only their token mix differs. All prices and token counts are hypothetical.

| Agent | Input / round | Output / round | Cached input |
|---|---|---|---|
| A (input-heavy) | 4.0 M | 0.1 M | 3.6 M |
| B (output-heavy) | 1.0 M | 0.4 M | 0.5 M |

| Price table ($/M tokens) | Cost / round A | Cost / round B | P_sat A | P_sat B | Higher P_sat |
|---|---|---|---|---|---|
| undiscounted, output 5× input (paper style) | $13.50 | $9.00 | 278 | 417 | B (output-heavy) |
| cache discount 90 %, output 5× input | $3.78 | $7.65 | 992 | 490 | A (input-heavy) |
| undiscounted, output 2× input | $12.60 | $5.40 | 298 | 694 | B (output-heavy) |

With identical learning per round, P_sat is inversely proportional to cost per round,
so the ranking follows whichever agent is cheaper under the chosen price table.
Undiscounted pricing (the paper's choice) penalises agents that re-read long,
cacheable contexts; a cache-aware table can reverse the ranking. The paper's
cross-provider P_sat comparisons inherit this dependence, as Section 3.4 notes.
