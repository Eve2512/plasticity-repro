"""
Add a `trace_viewer` config to Eve39570/agent-plasticity-hex.

Dry run (writes and checks the files on your Mac, uploads nothing):
    uv run --with datasets --with huggingface_hub python add_trace_viewer.py

Push (also uploads the files and updates the dataset card):
    uv run --with datasets --with huggingface_hub python add_trace_viewer.py --push
"""

# ---------------------------------------------------------------- 1. Imports
import argparse
import json
import shutil
import sys
from pathlib import Path

from datasets import load_dataset
from huggingface_hub import DatasetCard, HfApi

# ---------------------------------------------------------------- 2. Settings
REPO = "Eve39570/agent-plasticity-hex"
HARNESS = "agent-plasticity-hex"
OUT = Path("traces")
CONFIG = {
    "config_name": "trace_viewer",
    "data_files": [
        {
            "split": "train",
            "path": ["traces/games/*.jsonl", "traces/reflections/*.jsonl"],
        }
    ],
}
TRANSCRIPT_COLUMNS = ["messages", "transcript", "conversation"]
TABLE_ROW = (
    "| `trace_viewer` | 1,959 | a game or reflection transcript in the Hub "
    "Session Trace format, for the trace viewer |"
)


# ---------------------------------------------------------------- 3. Small helpers
def as_list(value):
    """Return the transcript as a list, also if it is stored as a JSON string."""
    if isinstance(value, str):
        value = json.loads(value)
    return value or []


def as_text(content):
    """Return message content as one string. Join text blocks if it is a list."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(block.get("text") or "")
            else:
                parts.append(str(block))
        return "\n".join(p for p in parts if p)
    return json.dumps(content, ensure_ascii=False)


def as_json_string(arguments):
    """STS needs tool arguments as a JSON string, not as a dict."""
    if arguments is None:
        return "{}"
    if isinstance(arguments, str):
        return arguments
    return json.dumps(arguments, ensure_ascii=False)


# ---------------------------------------------------------------- 4. Convert one transcript
def convert(messages):
    """Convert one transcript (OpenAI chat shape) to STS message lines."""
    lines = []
    open_calls = []  # ids of tool calls that have no result yet, in order

    for m in messages:
        role = m.get("role")
        if role not in ("user", "assistant", "system", "tool"):
            raise ValueError(f"Unknown role: {role!r}")
        msg = {"role": role, "content": as_text(m.get("content"))}

        calls = m.get("tool_calls") or []
        if calls:
            msg["toolCalls"] = []
            for i, c in enumerate(calls):
                fn = c.get("function") or {}
                call_id = c.get("id") or f"call_{len(lines)}_{i}"
                msg["toolCalls"].append(
                    {
                        "id": call_id,
                        "function": {
                            "name": fn.get("name") or "",
                            "arguments": as_json_string(fn.get("arguments")),
                        },
                    }
                )
                open_calls.append(call_id)

        if role == "tool":
            call_id = m.get("tool_call_id")
            if call_id is None and open_calls:
                call_id = open_calls[0]  # no id: link to the oldest open call
            if call_id in open_calls:
                open_calls.remove(call_id)
            if call_id:
                msg["toolCallId"] = call_id

        lines.append({"type": "message", "message": msg})
    return lines


# ---------------------------------------------------------------- 5. Names, writing, checking
def find_column(ds, name):
    for col in TRANSCRIPT_COLUMNS:
        if col in ds.column_names:
            return col
    sys.exit(
        f"No transcript column in '{name}'. Columns are: {ds.column_names}. "
        "Add the correct name to TRANSCRIPT_COLUMNS."
    )


def session_id(row, i, kind):
    parts = [str(row.get("run_id") or "run"), kind]
    for key in ("checkpoint", "episode", "attempt"):
        if row.get(key) is not None:
            parts.append(str(row[key]))
    parts.append(f"{i:05d}")  # the row number makes each id unique
    return "__".join(parts)


def session_name(row, kind):
    parts = [str(row.get("run_id") or "run"), kind]
    if row.get("checkpoint") is not None:
        parts.append(f"checkpoint {row['checkpoint']}")
    for key in ("episode", "attempt"):
        if row.get(key) is not None:
            parts.append(str(row[key]))
    return " · ".join(parts)


def write_session(path, header, messages):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(header, ensure_ascii=False) + "\n")
        for line in convert(messages):
            f.write(json.dumps(line, ensure_ascii=False) + "\n")


def check(path):
    """Read a file back and make sure it obeys the STS rules."""
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]
    head, body = rows[0], rows[1:]
    assert head["type"] == "session" and head["harness"] and head["id"], f"{path}: bad header"
    call_ids = set()
    for r in body:
        assert r["type"] == "message", f"{path}: a line is not a message"
        msg = r["message"]
        assert "role" in msg and "content" in msg, f"{path}: no role or content"
        for c in msg.get("toolCalls", []):
            assert isinstance(c["function"]["arguments"], str), f"{path}: arguments not a string"
            call_ids.add(c["id"])
        if "toolCallId" in msg:
            assert msg["toolCallId"] in call_ids, f"{path}: tool result has no matching call"
    return len(body)


# ---------------------------------------------------------------- 6. Main procedure
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--push", action="store_true", help="upload files and update the card")
    args = parser.parse_args()

    # 6a. Load the two tables that hold transcripts
    games = load_dataset(REPO, "games", split="train")
    reflections = load_dataset(REPO, "reflections", split="train")
    g_col = find_column(games, "games")
    r_col = find_column(reflections, "reflections")

    # 6b. Show the keys of the first messages, so you can check the shape
    print(f"games column: {g_col} | reflections column: {r_col}")
    print("Keys in the first 3 messages of game 0:")
    for m in as_list(games[0][g_col])[:3]:
        print("   ", sorted(k for k, v in m.items() if v is not None))

    # 6c. Start with an empty output folder
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "games").mkdir(parents=True)
    (OUT / "reflections").mkdir(parents=True)

    # 6d. Write one file per game and one file per reflection
    for kind, ds, col in (("game", games, g_col), ("reflection", reflections, r_col)):
        folder = OUT / ("games" if kind == "game" else "reflections")
        for i, row in enumerate(ds):
            sid = session_id(row, i, kind)
            run = str(row.get("run_id") or "")
            header = {
                "type": "session",
                "harness": HARNESS,
                "id": sid,
                "name": session_name(row, kind),
                "model": "claude-haiku-5.5" if "haiku" in run else "claude-sonnet-5.5",
                "kind": kind,
            }
            write_session(folder / f"{sid}.jsonl", header, as_list(row[col]))

    # 6e. Check every file
    files = sorted(OUT.rglob("*.jsonl"))
    total = sum(check(p) for p in files)
    print(f"OK: {len(files)} files, {total} messages, all pass the STS checks.")

    if not args.push:
        print("Dry run. Open one file in traces/ and look at it. Then run again with --push.")
        return

    # 6f. Upload the files
    HfApi().upload_folder(
        folder_path=str(OUT),
        path_in_repo="traces",
        repo_id=REPO,
        repo_type="dataset",
        commit_message="Add trace_viewer files (Session Trace format)",
    )

    # 6g. Add the config, the tag and a table row to the dataset card
    card = DatasetCard.load(REPO)
    configs = [c for c in (card.data.get("configs") or []) if c.get("config_name") != "trace_viewer"]
    configs.append(CONFIG)
    card.data.configs = configs

    tags = list(card.data.get("tags") or [])
    if "agent-traces" not in tags:
        tags.append("agent-traces")
    card.data.tags = tags

    if "`trace_viewer`" not in card.text:
        lines = card.text.split("\n")
        for n, line in enumerate(lines):
            if line.startswith("| `openings`"):
                lines.insert(n + 1, TABLE_ROW)
                break
        card.text = "\n".join(lines)

    card.push_to_hub(REPO, commit_message="Add trace_viewer config and agent-traces tag")
    print("Pushed. Open Data Studio, select trace_viewer, and click a row.")


if __name__ == "__main__":
    main()
