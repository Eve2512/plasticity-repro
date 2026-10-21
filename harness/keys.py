"""API keys from the environment or the repository's git-ignored .env file."""

import os
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def load_key(name: str, env_file: Path = ENV_FILE) -> str | None:
    """The value of `name`, from the environment first, then from .env. Never printed."""
    if os.environ.get(name):
        return os.environ[name]
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            key, _, value = line.partition("=")
            if key.strip() == name and value.strip():
                return value.strip().strip("'\"")
    return None
