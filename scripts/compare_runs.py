"""Compare finished lineages side by side. Writes reports/12_comparison.md.

    uv run python scripts/compare_runs.py lineage_a2 sonnet_reflect_high haiku_r20
"""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_hex import artifact_use  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "12_comparison.md"


def summarize(name: str) -> dict:
    d = ROOT / "runs" / name
    res = json.loads((d / "results.json").read_text())
    cps = res["checkpoints"]
    ids = [100 * c["id"]["points"] / c["id"]["games"] for c in cps]
    half = max(1, len(cps) // 2)

    def pooled(rows, split):
        return 100 * sum(c[split]["points"] for c in rows) / max(1, sum(c[split]["games"] for c in rows))

    calls = [a["calls"] for c in cps if c.get("reflection") for a in c["reflection"]["attempts"]]
    rejected = sum(1 for c in cps if c.get("reflection") for a in c["reflection"]["attempts"] if a["error"])
    revisions, prev, called, games = 0, None, 0, 0
    for c in cps:
        inv = d / "inventories" / f"checkpoint_{c['t']:03d}"
        digest = hashlib.md5(b"".join(
            p.read_bytes() for p in sorted(inv.rglob("*.py")) if "tracking" not in p.parts)).hexdigest()
        if prev is not None and digest != prev:
            revisions += 1
        prev = digest
        _, _, call, n = artifact_use(d, c["t"])
        called, games = called + call, games + n
    p = res.get("plasticity") or {}
    return {
        "name": name, "model": res["model"].split("/")[-1], "checkpoints": len(cps), "ids": ids,
        "first_half_id": pooled(cps[:half], "id"), "second_half_id": pooled(cps[half:], "id"),
        "first_half_train": pooled(cps[:half], "train"), "second_half_train": pooled(cps[half:], "train"),
        "psat": p.get("p_sat"), "kind": p.get("p_sat_kind"), "p": p.get("rise_p_value"),
        "rise": 100 * p["fit"]["rise"] if "fit" in p else None,
        "reflect_calls": sum(calls) / max(1, len(calls)), "rejected": rejected, "code_revisions": revisions,
        "tool_called_share": called / max(1, games), "billed": res["billed"], "stopped": res["stopped"],
    }


def main(names):
    rows = [summarize(n) for n in names]
    lines = [
        "# 12 Lineages compared",
        "",
        "| Lineage | Model | Checkpoints | ID first half → second half | Train first → second half | "
        "Fit rise (pp) | p | P_sat | Mean reflection calls | Rejected attempts | Code revisions | "
        "Games calling a saved tool | Billed |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        rise = "–" if r["rise"] is None else f"{r['rise']:.1f}"
        pv = "–" if r["p"] is None else f"{r['p']:.2g}"
        psat = "–" if r["psat"] is None else f"{r['psat']:.0f} ({r['kind']})"
        lines.append(
            f"| {r['name']} | {r['model']} | {r['checkpoints']} | {r['first_half_id']:.0f} % → {r['second_half_id']:.0f} % | "
            f"{r['first_half_train']:.0f} % → {r['second_half_train']:.0f} % | {rise} | {pv} | {psat} | "
            f"{r['reflect_calls']:.1f} | {r['rejected']} | {r['code_revisions']} | {100 * r['tool_called_share']:.0f} % | "
            f"${r['billed']:.2f} |"
        )
    lines += ["", "Held-out ID per checkpoint (%):", ""]
    for r in rows:
        lines.append(f"- `{r['name']}`: " + ", ".join(f"{x:.0f}" for x in r["ids"]))
    lines.append("")
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1:] or ["lineage_a2"])
