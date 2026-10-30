"""Wait until the OpenRouter account has at least the given dollars left, checking every 5 minutes.

Prints the balance only, never the key.

    uv run python scripts/wait_for_credit.py 45
"""

import json
import sys
import time
import urllib.request

from harness.keys import load_key


def credit_left(key: str) -> float:
    request = urllib.request.Request("https://openrouter.ai/api/v1/credits", headers={"Authorization": f"Bearer {key}"})
    data = json.load(urllib.request.urlopen(request, timeout=30))["data"]
    return data["total_credits"] - data["total_usage"]


def main():
    need = float(sys.argv[1])
    key = load_key("OPENROUTER_API_KEY")
    if not key:
        print("no OPENROUTER_API_KEY in the environment or .env")
        return 1
    while True:
        try:
            left = credit_left(key)
        except OSError as exc:
            print(f"credit check failed ({type(exc).__name__}); trying again in 5 minutes", flush=True)
        else:
            if left >= need:
                print(f"${left:.2f} left on the account (need ${need:.2f})", flush=True)
                return 0
            print(f"${left:.2f} left on the account, waiting for ${need:.2f}", flush=True)
        time.sleep(300)


if __name__ == "__main__":
    sys.exit(main())
