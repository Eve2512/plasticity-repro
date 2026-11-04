"""Go model gaps on fresh held-out openings: each Go lineage's final inventory (reflection effort high)
plays 40 held-out openings no run has played. Writes reports/25_go_fresh_openings.md. No API calls.

Report 23 found that with openings as the unit the late Go gaps between models are not below 0.05
(20 openings, replayed across checkpoints). Here the final inventory of each of the six Go
lineages plays the same 40 new openings once (scripts/ablate_inventory.py --arms fresh --id 40;
data/go_openings_fresh_id.json), at the run's settings: actor effort medium, GNU Go levels 5-9 in
turn. An opening's score for a model is its mean over the model's two lineages; models are
compared opening by opening (sign test, sign-flip permutation, 100,000 seeded draws).

    uv run python scripts/compare_go_fresh.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_fresh import paired  # noqa: E402
from compare_models import ROOT, pct  # noqa: E402

REPORT = ROOT / "reports" / "25_go_fresh_openings.md"
BANK = ROOT / "data" / "go_openings_fresh_id.json"
MODELS = {
    "Sonnet 5.5": ["go_sonnet_reflect_high", "go_sonnet_reflect_high_rep2"],
    "Haiku 5.5": ["go_haiku_reflect_high", "go_haiku_reflect_high_rep2"],
    "GLM 5.3": ["go_glm_reflect_high", "go_glm_reflect_high_rep2"],
}
PAIRS = [("Haiku 5.5", "Sonnet 5.5"), ("GLM 5.3", "Sonnet 5.5"), ("GLM 5.3", "Haiku 5.5")]
FINAL = 10


def games(name: str) -> list[dict]:
    out = []
    for f in sorted((ROOT / "runs" / name / f"ablation_checkpoint_{FINAL:03d}" / "fresh" / "games").glob("*.json")):
        g = json.loads(f.read_text())
        r = g["result"]
        out.append({"key": (" ".join(g["opening"]), r["actor"]), "score": r["score"],
                    "unfinished": r["end_reason"] != "finished"})
    return out


def original_final(name: str) -> tuple[float, int]:
    c = json.loads((ROOT / "runs" / name / "results.json").read_text())["checkpoints"][FINAL]["id"]
    return c["points"], c["games"]


def per_opening(names, keep=None) -> dict:
    acc = {}
    for n in names:
        for g in games(n):
            if keep is None or g["key"] in keep:
                acc.setdefault(g["key"], []).append(g["score"])
    return {k: sum(v) / len(v) for k, v in acc.items()}


READING = [
    "", "## Reading",
    "",
    "- Both gaps to GLM hold on new openings. Sonnet beats GLM on 24 of 40 openings and loses on 1",
    "  (sign test p = 1.5e-06); Haiku beats GLM on 18 and loses on 3 (p = 0.0015). With the original",
    "  20 openings, replayed across checkpoints 3–10, Sonnet against GLM was 11 better and 6 worse",
    "  (p = 0.33) and Haiku against GLM was not tested on Go (report 23). Both gaps stay below 0.05",
    "  without the 10 Black openings that are rotations or reflections of training openings.",
    "- Sonnet against Haiku is not established: 72 % against 62 %, 13 openings better and 8 worse",
    "  (p = 0.38). The two Sonnet lineages are far apart, as on the original openings: 95 % for",
    "  `go_sonnet_reflect_high_rep2` and 50 % for `go_sonnet_reflect_high`, below both Haiku lineages",
    "  (68 % and 58 %). Which Sonnet lineage one ran decides the comparison; two lineages per model",
    "  cannot say what Sonnet does on average.",
    "- The fresh openings reproduce each final inventory's level on the original openings within",
    "  about 10 points, except `go_haiku_reflect_high` (68 % against 45 %). A checkpoint-10 score on 20",
    "  openings carries about ±11 points of sampling error on its own, so the original Go endpoints",
    "  were not misleading; the problem in report 23 was too few openings for a test, not wrong levels.",
    "- These are endpoints, not learning curves: the final inventories play once. On Go no model's",
    "  pooled held-out ID rose from early to late checkpoints (reports 15, 21, 22), so there was no Go",
    "  learning curve to re-test.",
    "- GLM lost 7 of its 80 games to the time and call limits, Haiku 3 of 80, Sonnet none.",
]


def main():
    bank = json.loads(BANK.read_text())["banks"]["id"]
    unique = {(" ".join(e["moves"]), actor) for actor, entries in bank.items() for e in entries
              if not e.get("train_symmetric")}
    sym = sum(e.get("train_symmetric", False) for entries in bank.values() for e in entries)
    lines = [
        "# 25 Go model gaps on fresh held-out openings",
        "",
        "Each Go lineage at reflection effort high plays 40 held-out openings no run has played (20 per colour),",
        f"with its final inventory (checkpoint {FINAL}) and the run's settings. The 40 come from the same contested",
        "pool as the original bank, with the same median difficulty per colour; none is in the symmetry class",
        "(rotations and reflections of the 5×5 board) of an original held-out opening, and no two share one.",
        f"5×5 Go has few distinct 2-move openings for Black, so {sym} of the 20 Black openings are rotations or",
        "reflections of training openings; the last table leaves them out.",
        "",
        "## Per lineage", "",
        "| Lineage | Model | Fresh openings | Lost to limits | Original 20 openings, checkpoint 10 |",
        "|---|---|---|---|---|",
    ]
    for model, names in MODELS.items():
        for n in names:
            g = games(n)
            lines.append(f"| `{n}` | {model} | {pct(sum(x['score'] for x in g), len(g))} | "
                         f"{sum(x['unfinished'] for x in g)} | {pct(*original_final(n))} |")
    for title, keep in (("All 40 fresh openings", None),
                        (f"Leaving out the {sym} Black openings symmetric to training openings", unique)):
        lines += ["", f"## {title}", "",
                  "| Comparison (A vs B) | Openings | A | B | B better / worse | Sign test p | Permutation p |",
                  "|---|---|---|---|---|---|---|"]
        for a, b in PAIRS:
            r = paired(per_opening(MODELS[a], keep), per_opening(MODELS[b], keep))
            lines.append(f"| {b} vs {a} | {r['n']} | {100 * r['a']:.0f} % | {100 * r['b']:.0f} % | "
                         f"{r['pos']} / {r['neg']} | {r['p_sign']:.2g} | {r['p_perm']:.2g} |")
    lines += READING
    lines.append("")
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
