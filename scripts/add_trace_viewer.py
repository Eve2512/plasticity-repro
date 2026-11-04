"""
Write the `trace_viewer` configs of Eve39570/agent-plasticity-hex-go into the local export.

Each transcript is written in Pi's session format (version 3), which the Hub's trace
viewer reads natively: every reflection, every ablation game and every game. The Hub's
conversion timed out twice on one config of 3,918 files, so games get one config per run
(`traces_<run_id>`, at most 1,092 files) and reflections and ablation games share
`trace_viewer`. The Hub's own Session Trace format was tried first; the viewer parsed it
as Pi and dropped every assistant turn. Timestamps are placeholders (one second per
message): the harness did not record times.

Reads export/agent-plasticity-hex-go/data/ and writes export/agent-plasticity-hex-go/traces/,
so run it after scripts/export_hf.py. Nothing is uploaded; `hf upload` of the export folder
sends the traces with the data and the card (scripts/hf_dataset_card.md lists the configs).

    uv run python scripts/add_trace_viewer.py
"""

# ---------------------------------------------------------------- 1. Imports
import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


# ---------------------------------------------------------------- 2. Settings
HARNESS = "agent-plasticity-hex-go"
EXPORT = Path(__file__).resolve().parent.parent / "export" / "agent-plasticity-hex-go"
DATA = EXPORT / "data"
OUT = EXPORT / "traces"
TRANSCRIPT_COLUMNS = ["messages", "transcript", "conversation"]
REPLAYED = ("[Replayed thinking summary: the same input was sent again with thinking on; "
            "a new sample, not what this run thought.]\n\n")
KINDS = (("game", "games", "games"), ("reflection", "reflections", "reflections"),
         ("ablation game", "ablation_games", "ablation"))  # (kind, config, folder)
START = datetime(2026, 10, 1, tzinfo=timezone.utc)  # placeholder clock for the timestamps
NO_USAGE = {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0, "totalTokens": 0,
            "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0, "total": 0}}


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


def as_args(arguments):
    """Pi needs tool arguments as an object, not as a JSON string."""
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            return {"input": arguments}
    return arguments if isinstance(arguments, dict) else {}


# ---------------------------------------------------------------- 4. Convert one transcript
def convert(messages, model, api):
    """Convert one transcript (chat shape) to Pi session entries."""
    lines = []
    names = {}  # tool call id -> tool name, for the results
    for n, m in enumerate(messages):
        role = m.get("role")
        if role not in ("user", "assistant", "system", "tool"):
            raise ValueError(f"Unknown role: {role!r}")
        when = START + timedelta(seconds=n + 1)
        ms = int(when.timestamp() * 1000)

        if role == "assistant":
            content = []
            if m.get("thinking"):  # Claude: a summary; GLM: the reasoning text OpenRouter returned
                content.append({"type": "thinking", "thinking": m["thinking"]})
            if as_text(m.get("content")):
                content.append({"type": "text", "text": as_text(m.get("content"))})
            calls = as_list(m.get("tool_calls"))
            for i, c in enumerate(calls):
                # Our transcripts store {id, name, args}; OpenAI-style ones store {id, function: {name, arguments}}.
                fn = c.get("function") or {"name": c.get("name"), "arguments": c.get("args")}
                call_id = c.get("id") or f"call_{n}_{i}"
                names[call_id] = fn.get("name") or ""
                content.append({"type": "toolCall", "id": call_id, "name": names[call_id],
                                "arguments": as_args(fn.get("arguments"))})
            msg = {"role": "assistant", "content": content, "api": api, "provider": "openrouter",
                   "model": model, "usage": NO_USAGE, "stopReason": "toolUse" if calls else "stop", "timestamp": ms}
        elif role == "tool":
            call_id = m.get("tool_call_id") or ""
            msg = {"role": "toolResult", "toolCallId": call_id, "toolName": names.get(call_id, ""),
                   "content": [{"type": "text", "text": as_text(m.get("content"))}], "isError": False, "timestamp": ms}
        else:  # user, and the rare system message, shown as user text
            msg = {"role": "user", "content": as_text(m.get("content")), "timestamp": ms}

        lines.append({"type": "message", "id": f"{n + 1:08x}", "parentId": f"{n:08x}" if n else None,
                      "timestamp": when.isoformat().replace("+00:00", "Z"), "message": msg})
    return lines


# ---------------------------------------------------------------- 5. Names, writing, checking
def load_rows(config_name):
    """Return the rows of one table of the local export."""
    path = DATA / f"{config_name}.jsonl"
    if not path.exists():
        sys.exit(f"No {path}: run scripts/export_hf.py first.")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"{config_name}: {len(rows)} rows")
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


def make_header(sid, name, model, kind):
    """Pi session header; `harness`, `name`, `model` and `kind` are extra fields for the Hub."""
    return {"type": "session", "version": 3, "id": sid, "timestamp": START.isoformat().replace("+00:00", "Z"),
            "cwd": "<repo>", "harness": HARNESS, "name": name, "model": model, "kind": kind}


def write_session(path, header, messages):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(header, ensure_ascii=False) + "\n")
        api = "openai-completions" if header["model"].startswith("z-ai/") else "anthropic-messages"
        for line in convert(messages, header["model"], api):
            f.write(json.dumps(line, ensure_ascii=False) + "\n")


def check(path):
    """Read a file back and make sure it follows Pi's session format."""
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]
    head, body = rows[0], rows[1:]
    assert head["type"] == "session" and head["version"] == 3 and head["id"], f"{path}: bad header"
    call_ids, prev = set(), None
    for r in body:
        assert r["type"] == "message" and r["id"] and r["parentId"] == prev, f"{path}: broken entry chain"
        prev = r["id"]
        msg = r["message"]
        assert msg["role"] in ("user", "assistant", "toolResult"), f"{path}: bad role"
        if msg["role"] == "assistant":
            for c in msg["content"]:
                if c["type"] == "toolCall":
                    assert c["name"] and isinstance(c["arguments"], dict), f"{path}: bad tool call"
                    call_ids.add(c["id"])
        if msg["role"] == "toolResult":
            assert msg["toolCallId"] in call_ids, f"{path}: tool result has no matching call"
    return len(body)


# ---------------------------------------------------------------- 6. Main procedure
def main():
    # 6a. Load the tables that hold transcripts, and each run's model
    tables = {config: load_rows(config) for _, config, _ in KINDS}
    columns = {config: find_column(rows, config) for config, rows in tables.items()}
    models = {r["run_id"]: r["model"] for r in load_rows("runs")}

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

    # 6b. Start with an empty output folder
    if OUT.exists():
        shutil.rmtree(OUT)

    # 6c. Write one file per reflection, ablation game and game; games in one folder per run
    for kind, config, folder_name in KINDS:
        for i, row in enumerate(tables[config]):
            run = str(row.get("run_id") or "")
            folder = OUT / folder_name / run if kind == "game" else OUT / folder_name
            folder.mkdir(parents=True, exist_ok=True)
            sid = session_id(row, i, kind)
            header = make_header(sid, session_name(row, kind), models[run], kind)
            write_session(folder / f"{sid}.jsonl", header, as_list(row[columns[config]]))

    # 6d. Check every file
    files = sorted(OUT.rglob("*.jsonl"))
    total = sum(check(p) for p in files)
    thinking = sum('"type": "thinking"' in p.read_text(encoding="utf-8") for p in files)
    print(f"OK: {len(files)} files, {total} messages, all pass the Pi format checks; {thinking} files carry thinking.")
    for folder in sorted((OUT / "games").iterdir()):
        print(f"  traces_{folder.name}: {len(list(folder.glob('*.jsonl')))} games")


if __name__ == "__main__":
    main()
