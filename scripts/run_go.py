"""Run one 5x5 Go lineage: scripts/run_hex.py with --game go.

    uv run python scripts/run_go.py --model anthropic/claude-sonnet-5.5 --rounds 7 \
        --train 8 --id 12 --ood 4 --cap 10 --name go_sonnet          # plan only
    ... --dry                                                          # scripted model, no API calls

Needs GNU Go (`brew install gnu-go`) and data/go_openings_pooled.json
(scripts/build_go_openings.py).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_hex import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(["--game", "go", *sys.argv[1:]]))
