"""Plan D: Hex Sonnet 5.5, reflection effort high vs medium, with held-out ID openings new at every
checkpoint. Writes reports/24_fresh_openings.md. No API calls.

Report 23 found that the original lineages replay the same 12 held-out games once their play stops
changing. Plan D (scripts/plan_d.sh) re-ran the four Hex Sonnet lineages with every setting as before
except the held-out ID openings: 12 per checkpoint, new at each of checkpoints 0-10 and shared by the
four lineages at a checkpoint (data/hex_openings_fresh_id.json). Early / late is checkpoints 0-3 /
4-10, the split of report 12, fixed before these runs.

Tests with openings as the unit: an opening's score is its mean over the two lineages of a condition.
High vs medium pairs the same openings (sign test, sign-flip permutation); early vs late compares
different openings (label permutation). Permutation p-values are Monte Carlo, 100,000 draws, seeded.

    uv run python scripts/compare_fresh.py
"""

import random
import sys
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_repeats import id_games, per_opening, pooled  # noqa: E402
from compare_models import ROOT, pct, z_test  # noqa: E402
from compare_runs import summarize  # noqa: E402

REPORT = ROOT / "reports" / "24_fresh_openings.md"
FRESH = {"high": ["hex_sonnet_high_fresh", "hex_sonnet_high_fresh_rep2"],
         "medium": ["hex_sonnet_medium_fresh", "hex_sonnet_medium_fresh_rep2"]}
ORIGINAL = {"high": ["sonnet_reflect_high", "sonnet_reflect_high_rep2"],
            "medium": ["lineage_a2", "sonnet_medium_rep2"]}
EARLY, LATE = (0, 3), (4, 10)
DRAWS = 100_000


def sign_p(pos: int, neg: int) -> float:
    m = pos + neg
    return min(1.0, 2 * sum(comb(m, i) for i in range(min(pos, neg) + 1)) / 2 ** m) if m else 1.0


def paired(a: dict, b: dict) -> dict:
    """Same openings in both conditions, B minus A: sign test and sign-flip permutation."""
    keys = sorted(set(a) & set(b))
    d = [b[k] - a[k] for k in keys]
    pos, neg = sum(x > 0 for x in d), sum(x < 0 for x in d)
    rng, obs = random.Random(0), abs(sum(d))
    hits = sum(abs(sum(x if rng.random() < 0.5 else -x for x in d)) >= obs - 1e-12 for _ in range(DRAWS))
    return {"n": len(keys), "a": sum(a[k] for k in keys) / len(keys), "b": sum(b[k] for k in keys) / len(keys),
            "pos": pos, "neg": neg, "p_sign": sign_p(pos, neg), "p_perm": (hits + 1) / (DRAWS + 1)}


def unpaired(a: dict, b: dict) -> dict:
    """Different openings, mean of B minus mean of A: permutation of the condition labels."""
    xs, ys = list(a.values()), list(b.values())
    both, n, obs = xs + ys, len(xs), abs(sum(ys) / len(ys) - sum(xs) / len(xs))
    rng, hits = random.Random(0), 0
    for _ in range(DRAWS):
        rng.shuffle(both)
        hits += abs(sum(both[n:]) / len(ys) - sum(both[:n]) / n) >= obs - 1e-12
    return {"na": len(xs), "nb": len(ys), "a": sum(xs) / len(xs), "b": sum(ys) / len(ys),
            "p_perm": (hits + 1) / (DRAWS + 1)}


READING = [
    "", "## Reading",
    "",
    "- With no held-out game played twice, the effort result holds and is much better supported. Over",
    "  checkpoints 4–10 high effort scores 88 % against 56 % for medium; per opening it is better on 46 of",
    "  84 and worse on 6 (sign test p = 1e-08; no permutation draw was as extreme, p ≤ 1e-05). With the",
    "  original fixed openings the same comparison rested on 12 openings (10 better, 1 worse, p = 0.012,",
    "  report 23).",
    "- The gap opens after the first reflection. Checkpoint 0 plays with an empty inventory in all four",
    "  lineages and both conditions score 11/24 there; over checkpoints 0–3 high effort is already ahead",
    "  (72 % against 57 %, 15 openings better, 2 worse, p = 0.0023).",
    "- The learning curve holds. High effort rises from 72 % at checkpoints 0–3 to 88 % at 4–10, measured",
    "  on 48 and 84 different openings (permutation p = 0.015 with openings as the unit; pooled games",
    "  p = 0.0015). Medium effort stays level (57 % → 56 %, p = 0.91). The late gain is on positions the",
    "  lineage had never played, so it is not a replay.",
    "- Plan D's numbers are close to the original lineages' (high 73 % → 83 %, medium 59 % → 65 %). The",
    "  fresh openings include more easy ones than the 12 original held-out openings (64 % against 50 % at",
    "  the top difficulty score), so levels across the two plans are not strictly comparable; the",
    "  comparisons inside plan D are.",
    "- Per lineage, both high-effort lineages pass the flat-curve gate (p = 0.046 and 0.00059) and end at",
    "  12/12. Neither medium lineage does, although `hex_sonnet_medium_fresh` gets P_sat 8,525",
    "  (\"saturated\") from a fit with p = 0.41, the 10-point-rule false positive of reports 15 and 22.",
    "  Medium effort again built little: `hex_sonnet_medium_fresh` never changed its code, and",
    "  `hex_sonnet_medium_fresh_rep2` wrote one tool that its actor called in 66 % of games without a",
    "  lasting gain (it fell to 1/12 at checkpoint 5).",
    "- Training and OOD openings were fixed, as in the original runs, so training games can still repeat;",
    "  the held-out measurement, on which plasticity is defined, no longer does.",
]


def main():
    lines = [
        "# 24 Fresh held-out openings: Hex Sonnet 5.5, reflection effort high vs medium",
        "",
        "Plan D re-ran the four Hex Sonnet 5.5 lineages of report 12 (two at reflection effort high, two at",
        "medium; actor effort medium; 8 / 12 / 4 games per checkpoint; checkpoints 0–10) with one change:",
        "the 12 held-out ID openings are new at every checkpoint, drawn from the same contested pool outside",
        "the pooled banks and dealt to checkpoints by difficulty (`--openings fresh`). The four lineages",
        "play the same openings at a given checkpoint, so high and medium effort can be compared opening by",
        "opening. Training and OOD openings are the pooled banks of the original runs.",
        f"Early = checkpoints {EARLY[0]}–{EARLY[1]}; late = {LATE[0]}–{LATE[1]} (report 12's split).",
        "",
    ]
    distinct = {g["key"] for names in FRESH.values() for n in names for g in id_games(n)}
    games = sum(len(id_games(n)) for names in FRESH.values() for n in names)
    lines += [f"Held-out ID games: {games}, on {len(distinct)} distinct (opening, colour) pairs; no lineage "
              "played any held-out opening twice.", ""]

    lines += ["## Held-out ID, early → late, games pooled", "",
              "| Openings | Reflection effort | Early | Late | Change | z | p |", "|---|---|---|---|---|---|---|"]
    for label, plan in (("fresh (plan D)", FRESH), ("fixed (original)", ORIGINAL)):
        for effort in ("high", "medium"):
            e, l_ = pooled(plan[effort], *EARLY), pooled(plan[effort], *LATE)
            z, p = z_test(*e, *l_)
            lines.append(f"| {label} | {effort} | {pct(*e)} | {pct(*l_)} | "
                         f"{100 * (l_[0] / l_[1] - e[0] / e[1]):+.0f} pp | {z:.2f} | {p:.2g} |")

    lines += ["", "## Openings as the unit", "",
              "Paired tests compare the same openings; early → late compares different openings.", "",
              "| Comparison | Openings | A | B | B better / worse | Sign test p | Permutation p |",
              "|---|---|---|---|---|---|---|"]
    hi_late, med_late = per_opening(FRESH["high"], *LATE), per_opening(FRESH["medium"], *LATE)
    for label, a, b in (("High vs medium, late", med_late, hi_late),
                        ("High vs medium, early", per_opening(FRESH["medium"], *EARLY),
                         per_opening(FRESH["high"], *EARLY))):
        r = paired(a, b)
        lines.append(f"| {label} (A medium, B high) | {r['n']} | {100 * r['a']:.0f} % | {100 * r['b']:.0f} % | "
                     f"{r['pos']} / {r['neg']} | {r['p_sign']:.2g} | {r['p_perm']:.2g} |")
    for effort in ("high", "medium"):
        r = unpaired(per_opening(FRESH[effort], *EARLY), per_opening(FRESH[effort], *LATE))
        lines.append(f"| {effort.capitalize()}, early → late (A early, B late) | {r['na']} + {r['nb']} | "
                     f"{100 * r['a']:.0f} % | {100 * r['b']:.0f} % | – | – | {r['p_perm']:.2g} |")

    lines += ["", "## Per lineage", "",
              "| Lineage | Reflection effort | Held-out ID per checkpoint (of 12) | Fit rise (pp) | p | P_sat | "
              "Code revisions | Games calling a saved tool | Billed |", "|---|---|---|---|---|---|---|---|---|"]
    for effort, names in FRESH.items():
        for n in names:
            r = summarize(n)
            rise = "–" if r["rise"] is None else f"{r['rise']:.1f}"
            pv = "–" if r["p"] is None else f"{r['p']:.2g}"
            psat = "–" if r["psat"] is None else f"{r['psat']:.0f} ({r['kind']})"
            lines.append(f"| `{n}` | {effort} | {', '.join(f'{x * 12 / 100:.0f}' for x in r['ids'])} | {rise} | {pv} | "
                         f"{psat} | {r['code_revisions']} | {100 * r['tool_called_share']:.0f} % | ${r['billed']:.2f} |")
    lines += READING
    lines.append("")
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
