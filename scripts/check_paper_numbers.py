"""Check reported numbers in arXiv:2610.08902v1 against the stated game counts.

A score over N games can only take values k / (2N) * 100 (draws give half points).
An average over several checkpoints with N games each is a multiple of
100 / (2 N x checkpoints). A value printed to one decimal must lie within 0.05
of such a multiple. Writes reports/02_paper_number_checks.md.
"""

from pathlib import Path

REPORT = Path(__file__).resolve().parent.parent / "reports" / "02_paper_number_checks.md"
TOL = 0.05 + 1e-9  # values are printed to one decimal

# (claim, section, reported value, games per checkpoint, checkpoints averaged, draws possible)
GRID_CHECKS = [
    ("Hard chess, Fable 5, held-out ID, checkpoint 0", "3.2", 37.5, 12, 1, True),
    ("Hard chess, Opus 5, held-out ID, checkpoint 0", "3.2", 25.0, 12, 1, True),
    ("Hard chess, Fable 5, held-out ID, mean of checkpoints 16–20", "3.2", 73.3, 12, 5, True),
    ("Hard chess, Opus 5, held-out ID, mean of checkpoints 16–20", "3.2", 66.4, 12, 5, True),
    ("Hard chess, GPT-5.6 Sol, held-out ID, mean of checkpoints 16–20", "3.2", 36.9, 12, 5, True),
    ("Easy chess, Opus 4.8, held-out ID, late value", "3.2", 19.0, 16, 5, True),
    ("Go, Fable 5, held-out ID, checkpoint 0", "3.3", 20.0, 20, 1, False),
    ("Go, Fable 5, held-out ID, checkpoint 20", "3.3", 80.0, 20, 1, False),
    ("Go, Fable 5, held-out OOD, checkpoint 20", "3.3", 50.0, 12, 1, False),
    ("Hex, GPT-5.6 Sol, held-out ID, checkpoint 0", "3.3", 40.0, 40, 1, False),
    ("Hex, GPT-5.6 Sol, held-out ID, checkpoint 20", "3.3", 77.5, 40, 1, False),
    ("Hex, GPT-5.6 Sol, held-out OOD, checkpoint 0", "3.3", 28.1, 32, 1, False),
    ("Hex, GPT-5.6 Sol, held-out OOD, checkpoint 20", "3.3", 78.1, 32, 1, False),
    ("Go, Opus 4.8, held-out ID, checkpoint 0", "3.5", 40.0, 20, 1, False),
]


def grid_check(value, games, checkpoints, draws):
    step = 100.0 / (games * checkpoints * (2 if draws else 1))
    k = round(value / step)
    nearest = [round(j * step, 3) for j in (k - 1, k, k + 1) if j >= 0]
    return abs(value - k * step) <= TOL, step, nearest


def nethack_checks():
    """Section 3.3 and Appendix C: anchors, 90 % rule and P_sat arithmetic."""
    lo, hi = 213.6, 6526.98

    def norm(raw):
        return 100 * (raw - lo) / (hi - lo)

    rise, gain, cost, reported = 68.95, 66.25, 1072.73, 61.75
    psat = 1000 * gain / cost
    early, late = norm(2019), norm(5831)
    return [
        (
            "P_sat = 1000 x fitted gain / cost",
            f"1000 x {gain} / {cost} = {psat:.3f}; reported {reported}",
            abs(psat - reported) < 0.01,
        ),
        (
            "Fitted gain at C* is at least 90 % of the fitted rise",
            f"{gain} >= 0.9 x {rise} = {0.9 * rise:.2f}",
            gain >= 0.9 * rise,
        ),
        (
            "Raw early/late means fit the fitted gain",
            f"normalised means: checkpoints 0–2 = {early:.1f}, 36–40 = {late:.1f}, "
            f"difference {late - early:.1f} vs fitted gain {gain}",
            abs((late - early) - gain) < 10,
        ),
    ]


def main():
    lines = [
        "# 02 Consistency of reported numbers",
        "",
        "Every check uses only numbers printed in the paper (v1) and the game counts in Table 2.",
        "",
        "## Score values versus game counts",
        "",
        "A score over N games (draws count half in chess) can only take a fixed set of values.",
        "",
        "| Claim | Section | Reported | Games × checkpoints | Step | Nearest possible values | Consistent |",
        "|---|---|---|---|---|---|---|",
    ]
    failures = []
    for claim, section, value, games, checkpoints, draws in GRID_CHECKS:
        ok, step, nearest = grid_check(value, games, checkpoints, draws)
        if not ok:
            failures.append(claim)
        lines.append(
            f"| {claim} | {section} | {value} | {games} × {checkpoints} | {step:.4g} | "
            f"{', '.join(f'{n:g}' for n in nearest)} | {'yes' if ok else '**no**'} |"
        )

    lines += ["", "## NetHack P_sat arithmetic (Appendix C)", "", "| Check | Arithmetic | Holds |", "|---|---|---|"]
    for name, arithmetic, ok in nethack_checks():
        lines.append(f"| {name} | {arithmetic} | {'yes' if ok else '**no**'} |")

    lines += [
        "",
        "## Reading",
        "",
        f"{len(GRID_CHECKS) - len(failures)} of {len(GRID_CHECKS)} score values match the stated game counts.",
    ]
    if failures:
        lines += [
            "The values that do not match are window averages or late values:",
            "",
            *[f"- {f}" for f in failures],
            "",
            "Possible causes, none confirmed: some checkpoints had a different number of games",
            "(for example games dropped after an infrastructure error), or the window differs",
            "from checkpoints 16–20. The Easy chess value has no stated window, so that row tests",
            "the most likely reading only. A mean of per-colour or per-opponent scores cannot",
            "explain the gap, because every colour and opponent has the same number of games.",
            "A mismatch of this size does not change the paper's conclusions, but it means the",
            "curves cannot be rebuilt exactly from the text alone.",
        ]
    lines.append("")
    REPORT.write_text("\n".join(lines))
    print(f"wrote {REPORT.relative_to(REPORT.parent.parent)}")


if __name__ == "__main__":
    main()
