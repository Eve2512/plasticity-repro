"""Repeated held-out games: what flat scores mean, and the main tests with openings as the unit.
Writes reports/23_repeated_games.md. No API calls.

Every checkpoint plays the same held-out ID openings, and both opponents (the alpha-beta engine
and GNU Go) reply the same way to the same position. Once the actor's play stops changing, a
checkpoint replays the games of the one before. The pooled z-tests of reports 12, 15, 21 and 22
count every game as independent; here each (opening, colour) is one unit, scored by its mean
over the checkpoints compared, and two conditions are compared opening by opening.

    uv run python scripts/check_repeats.py
"""

import hashlib
import json
import sys
from itertools import product
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_models import ROOT, pct, z_test  # noqa: E402

REPORT = ROOT / "reports" / "23_repeated_games.md"
LINEAGES = [
    "lineage_a2", "sonnet_medium_rep2", "sonnet_reflect_high", "sonnet_reflect_high_rep2",
    "hex_haiku_medium_rep2", "hex_haiku_reflect_high", "hex_haiku_reflect_high_rep2", "haiku_r20",
    "hex_glm_reflect_high", "hex_glm_reflect_high_rep2", "sonnet_nofeedback_high", "sonnet_nofeedback_high_rep2",
    "go_sonnet_medium", "go_sonnet_medium_rep2", "go_sonnet_reflect_high", "go_sonnet_reflect_high_rep2",
    "go_haiku_medium", "go_haiku_medium_rep2", "go_haiku_reflect_high", "go_haiku_reflect_high_rep2",
    "go_glm_reflect_high", "go_glm_reflect_high_rep2",
]
HEX_SONNET_MED = ["lineage_a2", "sonnet_medium_rep2"]
HEX_SONNET_HIGH = ["sonnet_reflect_high", "sonnet_reflect_high_rep2"]
HEX_HAIKU = ["hex_haiku_reflect_high", "hex_haiku_reflect_high_rep2"]
HEX_GLM = ["hex_glm_reflect_high", "hex_glm_reflect_high_rep2"]
NOFEEDBACK = ["sonnet_nofeedback_high", "sonnet_nofeedback_high_rep2"]
GO_SONNET_MED = ["go_sonnet_medium", "go_sonnet_medium_rep2"]
GO_SONNET = ["go_sonnet_reflect_high", "go_sonnet_reflect_high_rep2"]
GO_HAIKU = ["go_haiku_reflect_high", "go_haiku_reflect_high_rep2"]
GO_GLM = ["go_glm_reflect_high", "go_glm_reflect_high_rep2"]
# (label, report, condition A, checkpoints A, condition B, checkpoints B): B minus A
TESTS = [
    ("Hex Sonnet, high vs medium effort, checkpoints 4–10", "12", HEX_SONNET_MED, (4, 10), HEX_SONNET_HIGH, (4, 10)),
    ("Hex Sonnet high, checkpoints 0–3 → 4–10", "12", HEX_SONNET_HIGH, (0, 3), HEX_SONNET_HIGH, (4, 10)),
    ("Hex Sonnet medium, checkpoints 0–3 → 4–10", "12", HEX_SONNET_MED, (0, 3), HEX_SONNET_MED, (4, 10)),
    ("Hex, feedback vs no game records, checkpoints 3–7", "18", NOFEEDBACK, (3, 7), HEX_SONNET_HIGH, (3, 7)),
    ("Hex late, Sonnet vs Haiku", "15", HEX_HAIKU, (3, 10), HEX_SONNET_HIGH, (3, 10)),
    ("Hex late, Sonnet vs GLM", "21", HEX_GLM, (3, 10), HEX_SONNET_HIGH, (3, 10)),
    ("Hex late, Haiku vs GLM", "21", HEX_GLM, (3, 10), HEX_HAIKU, (3, 10)),
    ("Go late, Sonnet vs Haiku", "15", GO_HAIKU, (3, 10), GO_SONNET, (3, 10)),
    ("Go late, Sonnet vs GLM", "21", GO_GLM, (3, 10), GO_SONNET, (3, 10)),
    ("Go late, Sonnet high vs medium effort", "22", GO_SONNET_MED, (3, 10), GO_SONNET, (3, 10)),
]


def id_games(name: str) -> list[dict]:
    """Held-out ID games of completed checkpoints: checkpoint, opening key, score, full move record."""
    d = ROOT / "runs" / name
    done = len(json.loads((d / "results.json").read_text())["checkpoints"])
    out = []
    for t in range(done):
        for f in sorted((d / "games" / f"checkpoint_{t:03d}" / "id").glob("*.json")):
            g = json.loads(f.read_text())
            r = g["result"]
            out.append({"t": t, "key": (json.dumps(g["opening"]), r["actor"]), "score": r["score"],
                        "moves": json.dumps(r["moves"])})
    return out


def tool_hash(name: str, t: int) -> str:
    """Hash of the Python files in the inventory a checkpoint played with."""
    h = hashlib.sha1()
    root = ROOT / "runs" / name / "inventories" / f"checkpoint_{t:03d}"
    for f in sorted(root.rglob("*.py")):
        h.update(str(f.relative_to(root)).encode() + f.read_bytes())
    return h.hexdigest()


def opponent_conflicts(split: str) -> tuple[int, int]:
    """Positions of one split met more than once (same game, opponent level, position and actor
    move) and how often the opponent's reply differed. Uses the local export (scripts/export_hf.py)."""
    seen, positions, conflicts = {}, 0, 0
    path = ROOT / "export" / "agent-plasticity-hex-go" / "data" / "games.jsonl"
    for line in path.read_text().splitlines():
        r = json.loads(line)
        if r["split"] != split:
            continue
        for m in r["moves"]:
            if not m.get("opponent_action"):
                continue
            k = (r["game"], r.get("opponent_level"), tuple(m["before"]), m["action"])
            if k in seen:
                positions += 1
                conflicts += seen[k] != m["opponent_action"]
            seen.setdefault(k, m["opponent_action"])
    return positions, conflicts


def flat_stretch(name: str, games: list[dict]) -> dict:
    """The longest run of checkpoints with the same held-out score, and what was replayed in it."""
    ts = sorted({g["t"] for g in games})
    score = {t: sum(g["score"] for g in games if g["t"] == t) for t in ts}
    best, start = (1, ts[0]), ts[0]
    for a, b in zip(ts, ts[1:]):
        start = start if score[b] == score[a] else b
        if b - start + 1 > best[0]:
            best = (b - start + 1, start)
    length, first = best
    span = range(first, first + length)
    by = {(g["t"], g["key"]): g for g in games}
    same = total = 0
    for t in span[1:]:
        for g in games:
            if g["t"] == t:
                total += 1
                same += g["moves"] == by[(t - 1, g["key"])]["moves"]
    return {"first": first, "last": first + length - 1, "score": score[first],
            "n": sum(g["t"] == first for g in games), "tools_fixed": len({tool_hash(name, t) for t in span}) == 1,
            "identical": (same, total)}


def per_opening(names, lo, hi) -> dict:
    acc = {}
    for n in names:
        for g in id_games(n):
            if lo <= g["t"] <= hi:
                acc.setdefault(g["key"], []).append(g["score"])
    return {k: sum(v) / len(v) for k, v in acc.items()}


def opening_test(a: dict, b: dict) -> dict:
    """Sign test and exact sign-flip permutation test over openings, B minus A."""
    keys = sorted(set(a) & set(b))
    d = [b[k] - a[k] for k in keys]
    pos, neg = sum(x > 0 for x in d), sum(x < 0 for x in d)
    m = pos + neg
    p_sign = min(1.0, 2 * sum(comb(m, i) for i in range(min(pos, neg) + 1)) / 2 ** m) if m else 1.0
    obs = abs(sum(d))
    hits = sum(abs(sum(s * x for s, x in zip(signs, d))) >= obs - 1e-12 for signs in product((1, -1), repeat=len(d)))
    return {"n": len(keys), "a": sum(a[k] for k in keys) / len(keys), "b": sum(b[k] for k in keys) / len(keys),
            "pos": pos, "neg": neg, "p_sign": p_sign, "p_perm": hits / 2 ** len(d)}


def pooled(names, lo, hi) -> tuple[float, int]:
    s = [g["score"] for n in names for g in id_games(n) if lo <= g["t"] <= hi]
    return sum(s), len(s)


READING = [
    "", "## Reading",
    "",
    "- A flat held-out score in these runs is a replay, not a fresh measurement. The held-out openings are",
    "  the same at every checkpoint and no held-out opponent ever answered the same position two ways, so",
    "  once a lineage's tool code stops changing, each checkpoint plays the previous one's games again,",
    "  most of them move for move. `sonnet_reflect_high` kept the same tool code from checkpoint 3 to 10",
    "  and `sonnet_reflect_high_rep2` from checkpoint 2 to 10; at 75 % and 92 % their later checkpoints",
    "  add almost no new information. In `go_sonnet_reflect_high_rep2` the tool code kept changing but",
    "  every held-out result from checkpoint 6 on matched the checkpoint before.",
    "- Repeats are not only a tool effect. Sonnet at medium effort on Go ran a saved tool in 1–6 % of",
    "  games, yet 42 % of its held-out games repeat an earlier one move for move: on 5×5 the model itself",
    "  often plays the same line from the same opening.",
    "- The pooled z-tests of reports 12, 15, 21 and 22 count each game as independent, so repeats make",
    "  them far too confident. With openings as the unit, the direction of every main result holds, but",
    "  the evidence is much weaker. High against medium effort on Hex: better on 10 of 12 openings, worse",
    "  on 1 (sign test p = 0.012, permutation p = 0.066), against p = 0.0002 pooled. High effort's",
    "  early → late gain: 9 better, 1 worse (p = 0.021 / 0.051). Feedback against no game records",
    "  (test 5): 8 better, 1 worse (p = 0.039 / 0.035); report 18's p = 2.5e-07 counted the same",
    "  openings once per checkpoint. Sonnet against GLM on Hex survives (11 of 12, p = 0.001); Haiku",
    "  against GLM on Hex is borderline (7 better, 1 worse, p = 0.07 / 0.039); the Go model gaps do not",
    "  reach p < 0.05. These per-opening tests still pool the two lineages of a condition, so they do not",
    "  account for lineage-to-lineage spread either.",
    "- Twelve Hex openings cap what any test here can show: even 12 better and 0 worse gives a sign-test",
    "  p of 0.0005. More openings per checkpoint, or new openings at each checkpoint, would add",
    "  information; more checkpoints with a fixed tool would not.",
    "- The same holds for the plasticity fits. A fit treats each checkpoint's score as a new noisy",
    "  measurement; a replayed score is not one, so a long flat tail makes a curve look saturated with",
    "  more certainty than the data have (`go_sonnet_reflect_high_rep2`, P_sat \"saturated\", p = 0.019).",
]


def main():
    positions, conflicts = opponent_conflicts("id")
    train_positions, train_conflicts = opponent_conflicts("train")
    lines = [
        "# 23 Repeated held-out games",
        "",
        "Several lineages hold one held-out ID score for many checkpoints (e.g. `sonnet_reflect_high_rep2`",
        "at 92 % for checkpoints 2–10). This report checks whether those are new games with the same result",
        "or the same games played again, and what that means for the tests in earlier reports.",
        "",
        "## Why games repeat",
        "",
        "- Held-out ID openings are fixed: every checkpoint plays the same 12 (Hex) or 20 (Go) openings with",
        "  the same colours, each against the same opponent level, and all Hex lineages on the pooled bank",
        "  (except `haiku_r20`, 24 openings) and all Go lineages share one set. So two conditions can be",
        "  compared opening by opening.",
        f"- The opponents are deterministic. Over all held-out games, {positions:,} times the opponent met a",
        f"  position it had already answered (same game, level, position and actor move); it replied",
        f"  differently {conflicts} times. (In training games: {train_positions:,} repeated positions,",
        f"  {train_conflicts} different replies, all from GNU Go at level 5.)",
        "- So when the actor plays the same moves, the whole game repeats.",
        "",
        "## Repeats per lineage",
        "",
        "\"Exact repeats\": held-out games whose full move record matches an earlier game of the same",
        "lineage on the same opening. \"Longest flat stretch\": the longest run of checkpoints with one",
        "held-out score; \"same as previous checkpoint\": games in that run, after its first checkpoint,",
        "identical move for move to the same opening one checkpoint earlier.",
        "",
        "| Lineage | Held-out games | Exact repeats | Longest flat stretch | Score | Tool code unchanged in it | "
        "Same as previous checkpoint |",
        "|---|---|---|---|---|---|---|",
    ]
    for n in LINEAGES:
        games = id_games(n)
        seen, dup = set(), 0
        for g in sorted(games, key=lambda g: g["t"]):
            dup += (g["key"], g["moves"]) in seen
            seen.add((g["key"], g["moves"]))
        f = flat_stretch(n, games)
        same, total = f["identical"]
        stretch = f"{f['first']}–{f['last']}" if f["last"] > f["first"] else "–"
        lines.append(f"| `{n}` | {len(games)} | {dup} ({100 * dup / len(games):.0f} %) | {stretch} | "
                     f"{pct(f['score'], f['n']) if f['last'] > f['first'] else '–'} | "
                     f"{('yes' if f['tools_fixed'] else 'no') if f['last'] > f['first'] else '–'} | "
                     f"{f'{same}/{total}' if total else '–'} |")

    lines += [
        "", "## Main tests, games against openings as the unit",
        "",
        "Pooled: two-proportion z-test over all held-out games, as in the reports. Per opening: each",
        "(opening, colour) scored by its mean over both lineages and the checkpoints compared; \"better\" /",
        "\"worse\" count openings where B's mean is above / below A's; sign test (ties dropped) and exact",
        "sign-flip permutation test on the per-opening differences, both two-sided.",
        "",
        "| Comparison (A → B) | Report | Pooled A → B | Pooled p | Openings | Per opening A → B | Better / worse | "
        "Sign p | Permutation p |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for label, rep, a, (alo, ahi), b, (blo, bhi) in TESTS:
        pa, pb = pooled(a, alo, ahi), pooled(b, blo, bhi)
        _, p = z_test(*pa, *pb)
        r = opening_test(per_opening(a, alo, ahi), per_opening(b, blo, bhi))
        lines.append(f"| {label} | {rep} | {100 * pa[0] / pa[1]:.0f} % → {100 * pb[0] / pb[1]:.0f} % | {p:.2g} | "
                     f"{r['n']} | {100 * r['a']:.0f} % → {100 * r['b']:.0f} % | {r['pos']} / {r['neg']} | "
                     f"{r['p_sign']:.2g} | {r['p_perm']:.2g} |")
    lines += READING
    lines.append("")
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
