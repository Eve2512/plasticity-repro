"""Build the Hex opening banks once and save them.

Paper-size banks per checkpoint: 40 train, 40 held-out ID, 32 held-out OOD,
half per colour. Runs read the saved file, so every run uses the same openings.

    uv run python scripts/build_hex_openings.py              # pooled (default)
    uv run python scripts/build_hex_openings.py --kind contested
"""

import argparse
import json

from envs.hex_openings import BANK_FILE, POOLED_FILE, build_contested_banks, build_pooled_banks

GAMES = {"train": 40, "id": 40, "ood": 32}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", default="pooled", choices=["pooled", "contested"])
    kind = parser.parse_args().kind
    if kind == "pooled":
        data = build_pooled_banks(GAMES, workers=7, progress=lambda a, k, n, t: print(f"{a}: {k}/{n} kept ({t} tried)", flush=True))
        path = POOLED_FILE
    else:
        data = build_contested_banks(
            GAMES, progress=lambda s, a, k, n, t: print(f"{s} {a}: {k}/{n} kept ({t} tried)", flush=True))
        path = BANK_FILE
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=1))
    print(f"wrote {path.relative_to(path.parent.parent)}: {data['candidates_tried']} candidates tried")


if __name__ == "__main__":
    main()
