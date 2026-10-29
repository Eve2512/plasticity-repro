"""
Add a `trace_viewer` config to Eve39570/agent-plasticity-hex-go.

Dry run (writes and checks the files on your Mac, uploads nothing):
    uv run --with huggingface_hub python add_trace_viewer.py

Push (also uploads the files and updates the dataset card):
    uv run --with huggingface_hub python add_trace_viewer.py --push
"""

# ---------------------------------------------------------------- 1. Imports
import argparse
import fnmatch
import json
import shutil
import sys
from pathlib import Path

from huggingface_hub import DatasetCard, HfApi, hf_hub_download

# ---------------------------------------------------------------- 2. Settings
REPO = "Eve39570/agent-plasticity-hex-go"
HARNESS = "agent-plasticity-hex-go"
OUT = Path("traces")
CONFIG = {
    "config_name": "trace_viewer",
    "data_files": [
        {
            "split": "train",
            "path": ["traces/games/*.jsonl", "traces/reflections/*.jsonl", "traces/ablation/*.jsonl"],
        }
    ],
}
TRANSCRIPT_COLUMNS = ["messages", "transcript", "conversation"]
TABLE_ROW = (
    "| `trace_viewer` | {n} | a game, reflection or ablation-game transcript in the Hub "
    "Session Trace format, with thinking summaries (live, or replayed and labelled), for the trace viewer |"
)
REPLAYED = ("[Replayed thinking summary: the same input was sent again with thinking on; "
            "a new sample, not what this run thought.]\n\n")
KINDS = (("game", "games", "games"), ("reflection", "reflections", "reflections"),
         ("ablation game", "ablation_games", "ablation"))  # (kind, config, folder)


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
        if m.get("thinking"):
            msg["reasoningContent"] = m["thinking"]  # a thinking summary, not the raw chain of thought

        calls = as_list(m.get("tool_calls"))
        if calls:
            msg["toolCalls"] = []
            for i, c in enumerate(calls):
                # Our transcripts store {id, name, args}; OpenAI-style ones store {id, function: {name, arguments}}.
                fn = c.get("function") or {"name": c.get("name"), "arguments": c.get("args")}
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
def data_file_patterns(config):
    """Return the file patterns from one config's data_files, in any YAML shape."""
    df = config.get("data_files")
    items = df if isinstance(df, list) else list(df.values()) if isinstance(df, dict) else [df]
    patterns = []
    for item in items:
        if isinstance(item, dict):
            item = item.get("path")
        if isinstance(item, str):
            patterns.append(item)
        elif isinstance(item, list):
            patterns.extend(item)
    return patterns


def load_rows(config_name):
    """Download the raw JSON files of one config and return its rows as dicts.
    This skips the schema in the dataset card, so a wrong type there cannot stop us."""
    card = DatasetCard.load(REPO)
    config = next(
        (c for c in (card.data.get("configs") or []) if c.get("config_name") == config_name),
        None,
    )
    if config is None:
        sys.exit(f"No config named '{config_name}' in the dataset card.")
    patterns = data_file_patterns(config)
    all_files = HfApi().list_repo_files(REPO, repo_type="dataset")
    files = sorted(f for f in all_files if any(fnmatch.fnmatch(f, p) for p in patterns))
    if not files:
        sys.exit(f"No files match {patterns} for config '{config_name}'.")

    rows = []
    for name in files:
        local = hf_hub_download(REPO, name, repo_type="dataset")
        text = Path(local).read_text(encoding="utf-8")
        if name.endswith(".jsonl"):
            rows.extend(json.loads(line) for line in text.splitlines() if line.strip())
        elif name.endswith(".json"):
            data = json.loads(text)
            rows.extend(data if isinstance(data, list) else [data])
        else:
            print(f"Skipped {name}: not .json or .jsonl")
    print(f"{config_name}: {len(rows)} rows from {len(files)} file(s)")
    return rows


def find_column(rows, name):
    columns = list(rows[0].keys())
    for col in TRANSCRIPT_COLUMNS:
        if col in columns:
            return col
    sys.exit(
        f"No transcript column in '{name}'. Columns are: {columns}. "
        "Add the correct name to TRANSCRIPT_COLUMNS."
    )


def session_id(row, i, kind):
    parts = [str(row.get("run_id") or "run"), kind.replace(" ", "_")]
    for key in ("checkpoint", "arm", "game_id", "episode", "attempt"):
        if row.get(key) is not None:
            parts.append(str(row[key]))
    parts.append(f"{i:05d}")  # the row number makes each id unique
    return "__".join(parts)


def session_name(row, kind):
    parts = [str(row.get("run_id") or "run"), kind]
    if row.get("checkpoint") is not None:
        parts.append(f"checkpoint {row['checkpoint']}")
    if row.get("arm"):
        parts.append(f"{row['arm']} arm")
    for key in ("game_id", "episode", "attempt"):
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
            assert c["function"]["name"], f"{path}: tool call without a name"
            call_ids.add(c["id"])
        if "toolCallId" in msg:
            assert msg["toolCallId"] in call_ids, f"{path}: tool result has no matching call"
    return len(body)


# ---------------------------------------------------------------- 6. Main procedure
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--push", action="store_true", help="upload files and update the card")
    args = parser.parse_args()

    # 6a. Load the tables that hold transcripts
    tables = {config: load_rows(config) for _, config, _ in KINDS}
    columns = {config: find_column(rows, config) for config, rows in tables.items()}

    # 6a2. Reflections recorded before thinking was saved: attach the replayed summaries, labelled
    replay = {(r["run_id"], r["checkpoint"], r["attempt"], r["message_index"]): r["thinking"]
              for r in load_rows("thinking_replay") if r["thinking"].strip()}
    for row in tables["reflections"]:
        messages = as_list(row[columns["reflections"]])
        for i, m in enumerate(messages):
            key = (row["run_id"], row["checkpoint"], row["attempt"], i)
            if m.get("role") == "assistant" and not m.get("thinking") and key in replay:
                m["thinking"] = REPLAYED + replay[key]
        row[columns["reflections"]] = messages

    # 6b. Show the keys of the first messages, so you can check the shape
    print("Keys in the first 3 messages of game 0:")
    for m in as_list(tables["games"][0][columns["games"]])[:3]:
        print("   ", sorted(k for k, v in m.items() if v is not None))

    # 6c. Start with an empty output folder
    if OUT.exists():
        shutil.rmtree(OUT)

    # 6d. Write one file per game, reflection and ablation game
    for kind, config, folder_name in KINDS:
        folder = OUT / folder_name
        folder.mkdir(parents=True)
        for i, row in enumerate(tables[config]):
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
            write_session(folder / f"{sid}.jsonl", header, as_list(row[columns[config]]))

    # 6e. Check every file
    files = sorted(OUT.rglob("*.jsonl"))
    total = sum(check(p) for p in files)
    thinking = sum('"reasoningContent"' in p.read_text(encoding="utf-8") for p in files)
    print(f"OK: {len(files)} files, {total} messages, all pass the STS checks; {thinking} files carry thinking.")

    if not args.push:
        print("Dry run. Open one file in traces/ and look at it. Then run again with --push.")
        return

    # 6f. Upload the files; old trace files that are not in OUT any more are deleted
    HfApi().upload_folder(
        folder_path=str(OUT),
        path_in_repo="traces",
        repo_id=REPO,
        repo_type="dataset",
        delete_patterns=["*"],
        commit_message="Rebuild trace_viewer files (Session Trace format, with thinking)",
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

    lines = [x for x in card.text.split("\n") if not x.startswith("| `trace_viewer`")]
    for n, line in enumerate(lines):
        if line.startswith("| `ablation_games`"):
            lines.insert(n + 1, TABLE_ROW.format(n=f"{len(files):,}"))
            break
    card.text = "\n".join(lines)

    card.push_to_hub(REPO, commit_message="Add trace_viewer config and agent-traces tag")
    print("Pushed. Open Data Studio, select trace_viewer, and click a row.")


if __name__ == "__main__":
    main()
