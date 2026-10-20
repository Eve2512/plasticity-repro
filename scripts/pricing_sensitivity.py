"""Can the price table alone change a P_sat ranking?

Two hypothetical agents learn at exactly the same rate per learning round, but
use tokens differently: agent A re-reads long contexts (input-heavy, mostly
cacheable), agent B writes more (output-heavy). All prices and token counts are
hypothetical. Writes reports/04_pricing_sensitivity.md.
"""

from pathlib import Path

import numpy as np

from plasticity.fit import SaturationFit
from plasticity.pricing import PriceTable
from plasticity.psat import plasticity_to_saturation

REPORT = Path(__file__).resolve().parent.parent / "reports" / "04_pricing_sensitivity.md"
ROUNDS = 20
# Same curve for both agents in units of learning rounds: half the rise after 4 rounds.
S0, RISE, HALF_ROUNDS, H = 0.20, 0.50, 4.0, 2.0

# Tokens per learning round (input, output, cached part of input).
AGENTS = {
    "A (input-heavy)": (4_000_000, 100_000, 3_600_000),
    "B (output-heavy)": (1_000_000, 400_000, 500_000),
}
TABLES = {
    "undiscounted, output 5× input (paper style)": PriceTable(3.0, 15.0),
    "cache discount 90 %, output 5× input": PriceTable(3.0, 15.0, cached_input_per_mtok=0.3),
    "undiscounted, output 2× input": PriceTable(3.0, 6.0),
}


def psat_for(cost_per_round: float) -> float:
    costs = cost_per_round * np.arange(ROUNDS + 1)
    curve = SaturationFit(S0, RISE, HALF_ROUNDS * cost_per_round, H, 0.0)
    return plasticity_to_saturation(curve, costs).value


def main():
    lines = [
        "# 04 Pricing dependence of P_sat",
        "",
        "Both agents follow the same score curve per learning round",
        f"(S0 = {100 * S0:.0f} %, rise {100 * RISE:.0f} pp, half the rise after {HALF_ROUNDS:.0f} rounds).",
        "Only their token mix differs. All prices and token counts are hypothetical.",
        "",
        "| Agent | Input / round | Output / round | Cached input |",
        "|---|---|---|---|",
    ]
    for name, (inp, out, cached) in AGENTS.items():
        lines.append(f"| {name} | {inp / 1e6:.1f} M | {out / 1e6:.1f} M | {cached / 1e6:.1f} M |")
    lines += [
        "",
        "| Price table ($/M tokens) | Cost / round A | Cost / round B | P_sat A | P_sat B | Higher P_sat |",
        "|---|---|---|---|---|---|",
    ]
    for table_name, table in TABLES.items():
        cost = {name: table.cost(inp, out, cached) for name, (inp, out, cached) in AGENTS.items()}
        psat = {name: psat_for(c) for name, c in cost.items()}
        a, b = AGENTS
        winner = a if psat[a] > psat[b] else b
        lines.append(
            f"| {table_name} | ${cost[a]:.2f} | ${cost[b]:.2f} | {psat[a]:.0f} | {psat[b]:.0f} | {winner} |"
        )
    lines += [
        "",
        "With identical learning per round, P_sat is inversely proportional to cost per round,",
        "so the ranking follows whichever agent is cheaper under the chosen price table.",
        "Undiscounted pricing (the paper's choice) penalises agents that re-read long,",
        "cacheable contexts; a cache-aware table can reverse the ranking. The paper's",
        "cross-provider P_sat comparisons inherit this dependence, as Section 3.4 notes.",
        "",
    ]
    REPORT.write_text("\n".join(lines))
    print(f"wrote {REPORT.relative_to(REPORT.parent.parent)}")


if __name__ == "__main__":
    main()
