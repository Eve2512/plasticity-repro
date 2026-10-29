"""What the thinking summaries show about how learning happens. Writes reports/19_thinking.md.

Sources: the thinking replay of past reflections (report 16) and the thinking recorded live
in the limitation-test runs (reports 17, 18). The codes below are regular expressions over
the summaries and commands, checked by reading samples; they count mentions, not meaning.

    uv run python scripts/compare_thinking.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "19_thinking.md"
GROUPS = [  # (label, model, game, reflection effort, runs, learned per reports 12/15)
    ("Sonnet, medium", "Sonnet 5.5", "Hex", "medium", ["lineage_a2", "sonnet_medium_rep2"], "no"),
    ("Sonnet, high", "Sonnet 5.5", "Hex", "high", ["sonnet_reflect_high", "sonnet_reflect_high_rep2"], "yes"),
    ("Haiku, medium", "Haiku 5.5", "Hex", "medium", ["haiku_r20"], "no"),
    ("Haiku, high", "Haiku 5.5", "Hex", "high", ["hex_haiku_reflect_high", "hex_haiku_reflect_high_rep2"], "no"),
    ("Go Sonnet, run 1", "Sonnet 5.5", "Go", "high", ["go_sonnet_reflect_high"], "late, partly"),
    ("Go Sonnet, rep2", "Sonnet 5.5", "Go", "high", ["go_sonnet_reflect_high_rep2"], "yes"),
    ("Go Haiku, high", "Haiku 5.5", "Go", "high", ["go_haiku_reflect_high", "go_haiku_reflect_high_rep2"], "no"),
]
# A candidate tool played in games against the current one (not timing, not a validator "baseline").
MATCH = re.compile(r"head-to-head|\barena\b|tournament|self-play|\bwins? \d+ ?(/|of|out of) ?\d+ (games )?(against|vs)"
                   r"|\d+ ?/ ?\d+ (games )?(against|vs)\.? (the )?(old|current)", re.I)
TIMING = re.compile(r"\btim(e|ing)\b.*\b(per move|seconds?|\d+ ?s\b)|240 ?s|timeout", re.I)
BOOKKEEPING = re.compile(r"failure.mode|FM-\d|artifacts\.json|tracking|schema|validator|game_index", re.I)
POSITION = re.compile(r"\bg\d{2}\b.*\b(mv|move)\b|\bmove \d+\b|at move|\b[a-f][1-6]\b", re.I)
SCRATCH = re.compile(r"scratch|arena|par\.sh|for s in")  # commands that run code outside feedback and inventory


def replay(run: str) -> list[list[dict]]:
    """Replayed turns per reflection attempt."""
    return [[json.loads(x) for x in f.read_text().splitlines()]
            for f in sorted((ROOT / "runs" / run / "thinking_replay").glob("checkpoint_*_attempt_*.jsonl"))]


def commands(turn: dict) -> str:
    return " ".join(c["args"].get("command", "") for c in turn["replayed"]["tool_calls"])


def group_row(runs: list[str]) -> dict | None:
    attempts = [a for r in runs for a in replay(r)]
    if not attempts:
        return None
    turns = [t for a in attempts for t in a]
    thought = [t["thinking"] for t in turns if t["thinking"].strip()]
    with_thinking = [a for a in attempts if any(t["thinking"].strip() for t in a)]

    def share(rx, texts):
        return 100 * sum(bool(rx.search(x)) for x in texts) / max(1, len(texts))

    return {
        "attempts": len(attempts), "turns": len(turns), "thought": len(thought),
        "chars": sum(map(len, thought)) / max(1, len(thought)),
        "match": 100 * sum(any(MATCH.search(t["thinking"]) for t in a) for a in with_thinking) / max(1, len(with_thinking)),
        "timing": 100 * sum(any(TIMING.search(t["thinking"]) for t in a) for a in with_thinking) / max(1, len(with_thinking)),
        "bookkeeping": share(BOOKKEEPING, thought), "position": share(POSITION, thought),
        "scratch": share(SCRATCH, [commands(t) for t in turns]),
    }


def actor_thinking(paths: list[Path]) -> tuple[int, int, int, float]:
    """(games, assistant turns, turns with a summary, mean summary length)."""
    turns = thought = chars = 0
    for f in paths:
        for m in json.loads(f.read_text())["messages"]:
            if m["role"] == "assistant":
                turns += 1
                t = (m.get("thinking") or "").strip()
                thought += bool(t)
                chars += len(t)
    return len(paths), turns, thought, chars / max(1, thought)


def main():
    lines = [
        "# 19 What the thinking shows about how learning happens",
        "",
        "Reflection: thinking summaries from the replay of every saved reflection turn (report 16), a new",
        "sample on the recorded input, so they show how the model reasons at each recorded step, not what the",
        "original run thought. Actor: thinking recorded live in the limitation-test games (reports 17, 18).",
        "Codes are regular expressions, checked by reading samples; they count mentions, not meaning.",
        "",
        "## Reflection, per group",
        "",
        "| Group | Learned | Attempts | Turns (with a summary) | Mean summary (chars) | Attempts testing a candidate "
        "in games against the current tool | Attempts discussing move time or timeouts | Summaries about bookkeeping | "
        "Summaries citing a game position | Turns running code in a scratch folder or match loop |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for label, _, _, _, runs, learned in GROUPS:
        r = group_row(runs)
        if r is None:
            lines.append(f"| {label} | {learned} | – | not replayed | | | | | | |")
            continue
        lines.append(f"| {label} | {learned} | {r['attempts']} | {r['turns']} ({r['thought']}) | {r['chars']:.0f} | "
                     f"{r['match']:.0f} % | {r['timing']:.0f} % | {r['bookkeeping']:.0f} % | {r['position']:.0f} % | "
                     f"{r['scratch']:.0f} % |")
    lines += [
        "",
        "Testing a candidate counts attempts with at least one summary that reports or plans games between a",
        "new tool and the current one (\"head-to-head\", \"arena\", \"self-play\", \"25/32 against the old\").",
        "Bookkeeping: failure-mode IDs, tracking files, schema, validator. Medium-effort Sonnet thought on few",
        "turns, so its shares rest on few summaries.",
    ]

    lines += ["", "## Actor thinking with and without saved tools", "",
              "| Source | Inventory | Games | Actor turns | Turns with a summary | Mean summary (chars) |",
              "|---|---|---|---|---|---|"]
    for arm, label in (("with", "final tools"), ("forced", "final tools, use required"), ("empty", "none")):
        paths = sorted(ROOT.glob(f"runs/sonnet_reflect_high*/ablation_checkpoint_007/{arm}/games/*.json"))
        g, n, t, c = actor_thinking(paths)
        lines.append(f"| Report 17, `{arm}` arm | {label} | {g} | {n} | {t} ({100 * t / max(1, n):.0f} %) | {c:.0f} |")
    paths = sorted(ROOT.glob("runs/sonnet_nofeedback_high*/games/checkpoint_*/*/*.json"))
    g, n, t, c = actor_thinking(paths)
    lines.append(f"| Report 18, no-feedback lineages | none | {g} | {n} | {t} ({100 * t / max(1, n):.0f} %) | {c:.0f} |")

    lines += READING
    lines.append("")
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines))


READING = [
    "", "## Reading",
    "",
    "- **The groups that learned tested candidate tools in games before installing them.** Hex Sonnet at",
    "  effort high did so in a third of its reflections, Go Sonnet rep2 in over half; no Haiku group and no",
    "  medium-effort Sonnet reflection ever did. Example (`sonnet_reflect_high`, checkpoint 2): after one",
    "  loss in 8 it built a RAVE variant, played it against its current MCTS in parallel background matches",
    "  (\"RAVE wins 25/32 at 15k vs 30k playouts\"), timed it against the 240 s limit, and only then",
    "  installed it and filed the loss as a new failure mode.",
    "- **Haiku reflects like an auditor.** At effort high its summaries are about four times as long as",
    "  Sonnet's, and at both efforts about 60 % are about bookkeeping: failure-mode IDs, tracking files, the",
    "  validator. It traces concrete bugs in how the actor called its tools (e.g. `winning_cells()` called",
    "  with one argument) and files them, and on Hex it worries about move time in almost every reflection.",
    "  It never played a new version of a tool against the old one; once it planned to score a rewrite on",
    "  reconstructed losing positions. Its tools change; its results do not.",
    "- **Medium-effort Sonnet barely thinks.** Adaptive thinking produced a summary on 11 of 88 replayed",
    "  turns; the reflections read the records, ran the validator and stopped (report 12).",
    "- **Testing is necessary, not sufficient: the two Go Sonnet lineages.** Both tested candidates. Run 1",
    "  tested in every reflection, but only against its own previous engine, and its summaries say so",
    "  (\"self-play results between my own engines aren't the real benchmark\"). Its new engines often lost",
    "  those matches (7 of 8, 2 of 8), it alternated between calling the opponent weak and strong, and it",
    "  decided Black was lost from move 1 under komi 9.5. It still installed a rewritten alpha-beta engine at",
    "  every checkpoint (six versions); its own closing notes say it \"could not show that either one wins",
    "  more games\" and that none of the changes was \"tested in a real game\". Rep2 found the bug that made",
    "  its first helper unusable in every game (`load_python` returns a string), switched to MCTS at",
    "  checkpoint 1, checked it on positions from the lost games, accepted the next version after a",
    "  colour-balanced 15/24 match, sized its playouts to the time limit, and from checkpoint 5 (8 of 8",
    "  won) changed no code. It reached 85–90 %; run 1 stayed at 30–35 % until its last counted checkpoint.",
    "- **Learned tools take over the actor's reasoning.** With its final tools the actor wrote a thinking",
    "  summary on 4–6 % of its turns and handed each move to the tool; without them it thought on 66–70 % of",
    "  turns, about bridges and connections, and won about 40 points less often (report 17). The learning",
    "  sits in the code, and the model stops reasoning about the game once the code exists.",
    "- **Without game records the reflector reasons that it should do nothing** (report 18): \"There's no",
    "  data to map, so an empty inventory is actually valid here.\" The protocol's rule that every tool must",
    "  address an observed failure keeps it from building anything.",
    "",
    "## Limits of this analysis",
    "",
    "- Reflection summaries are replayed, not original: the replayed turn made the recorded tool calls in",
    "  only 5–40 % of turns (report 16). They show how the model reasons at each recorded step.",
    "- Summaries are summaries; the raw chain of thought is not available.",
    "- The codes are keyword matches. The candidate-testing code first counted Haiku's timing checks and",
    "  validator \"baselines\" as tests; it was narrowed to games between versions after reading the matches.",
    "- Medium-effort Sonnet has few summaries, so its row says little.",
    "- Seven groups, one or two lineages each; this describes these runs, it does not establish causes.",
]


if __name__ == "__main__":
    main()
