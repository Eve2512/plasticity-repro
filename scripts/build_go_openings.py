"""Build the 5x5 Go opening pool once and save it.

Per colour: 10 held-out ID and 6 OOD openings (the paper's 20 ID and 12 OOD,
half per colour) and a 40-opening training reservoir that each checkpoint draws
from. Runs read the saved file, so every run uses the same held-out games.

    uv run python scripts/build_go_openings.py
    uv run python scripts/build_go_openings.py --redeal   # re-deal the saved pool, no games
"""

import json
import os
import sys

from envs.go_openings import POOLED_FILE, build_pooled_banks, redeal


def main():
    if "--redeal" in sys.argv[1:]:
        POOLED_FILE.write_text(json.dumps(redeal(json.loads(POOLED_FILE.read_text())), indent=1))
        print(f"re-dealt {POOLED_FILE.relative_to(POOLED_FILE.parent.parent)}")
        return
    workers = max(1, (os.cpu_count() or 2) - 1)
    data = build_pooled_banks(
        workers=workers, progress=lambda a, k, n, t: print(f"{a}: {k}/{n} kept ({t} tried)", flush=True))
    POOLED_FILE.parent.mkdir(exist_ok=True)
    POOLED_FILE.write_text(json.dumps(data, indent=1))
    print(f"wrote {POOLED_FILE.relative_to(POOLED_FILE.parent.parent)}: {data['candidates_tried']} candidates tried")


if __name__ == "__main__":
    main()
