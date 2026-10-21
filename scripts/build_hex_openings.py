"""Build the contested, colour-balanced Hex opening banks once and save them.

Paper-size banks per checkpoint: 40 train, 40 held-out ID, 32 held-out OOD,
half per colour. Writes data/hex_openings_contested.json; runs then read it, so
every run uses exactly the same openings.
"""

import json

from envs.hex_openings import BANK_FILE, build_contested_banks

GAMES = {"train": 40, "id": 40, "ood": 32}


def progress(split, actor, kept, count, tried):
    print(f"{split} {actor}: {kept}/{count} kept ({tried} candidates tried)", flush=True)


def main():
    data = build_contested_banks(GAMES, progress=progress)
    BANK_FILE.parent.mkdir(exist_ok=True)
    BANK_FILE.write_text(json.dumps(data, indent=1))
    print(f"wrote {BANK_FILE.relative_to(BANK_FILE.parent.parent)}: {data['candidates_tried']} candidates tried")


if __name__ == "__main__":
    main()
