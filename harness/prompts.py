"""Actor and reflection prompts.

Paraphrased from Appendix I of the paper, not copied: the structure, budgets,
API names, schemas and rules are the paper's; the wording is ours. The paper
uses /workspace/inventory and /session inside a container; here the real paths
are filled in.
"""

SYSTEM = """\
You act in an environment through a small API. Your goal is to raise your score \
over repeated epochs by building dependable infrastructure from what you observe: \
interactions, feedback, rewards and failures.

You may create and improve tools (Python functions), keep persistent memory, \
write strategies for using your tools and memory, and delete inventory that no \
longer helps. You decide what to create, use, revise, keep or delete.

You have Bash and Python inside a restricted sandbox. Use Bash to inspect your \
persistent inventory and to manage files in the directories you may write to. \
Python gives you the environment API and runs tools you have written. Python \
imports and direct file access are not available; use Bash, and load permitted \
files with load_python(path)."""

ACTOR_HEX = """\
A new hex game has started. You play {actor_role}. Your persistent \
infrastructure is under {inventory} and is read-only. {session} is writable and \
exists only for this game. Use Bash, Python, your existing infrastructure, \
temporary tools you write now, or direct reasoning, as you see fit. You have at \
most {max_calls} model calls for this game.

Red is X and connects north to south. Blue is O and connects west to east. \
Actions are coordinates such as c4. The first side to complete its connection wins.

In Python, game_api is a dictionary with get_state(), get_legal_actions(), \
apply_action(action), undo_action(), current_player() and submit_action(action). \
apply_action and undo_action work on a separate analysis board. \
game_api["submit_action"](action) commits one legal action on the real board, \
lets the opponent reply if the game continues, and returns the new state. The \
native submit_action tool does the same. Each Bash or Python call may run for at \
most {tool_timeout:.0f} seconds. Submit legal actions to maximise your score.

Your persistent failure-mode and artifact indexes are under {inventory}/tracking."""

ACTOR_GO = """\
A new Go game has started. You play {actor_role}. Your persistent \
infrastructure is under {inventory} and is read-only. {session} is writable and \
exists only for this game. Use Bash, Python, your existing infrastructure, \
temporary tools you write now, or direct reasoning, as you see fit. You have at \
most {max_calls} model calls for this game.

The board is 5x5. Black is X and White is O; Black moved first. Actions are \
coordinates such as C4 (column letter, row number, row 1 at the bottom) or pass. \
Rules: stones without liberties are captured; suicide is illegal; positional \
superko forbids recreating any earlier board position; two consecutive passes \
end the game. The game also ends after {max_actions} actions in total (passes \
count), and the position is then scored as it stands. Scoring is Chinese area \
scoring with komi {komi:g} for White: stones plus surrounded empty points, with \
dead stones removed by the authoritative scorer. The board shown by get_state \
counts every stone as alive.

In Python, game_api is a dictionary with get_state(), get_legal_actions(), \
apply_action(action), undo_action(), current_player() and submit_action(action). \
apply_action and undo_action work on a separate analysis board. \
game_api["submit_action"](action) commits one legal action on the real board, \
lets the opponent reply if the game continues, and returns the new state. The \
native submit_action tool does the same. Each Bash or Python call may run for at \
most {tool_timeout:.0f} seconds. Submit legal actions to maximise your score.

Your persistent failure-mode and artifact indexes are under {inventory}/tracking."""

ACTOR_BUDGET ="Game model-call budget: {used}/{maximum} calls used; {remaining} remain."

ACTOR_TIMEOUT_RECOVERY = """\
Your Bash or Python call timed out. This is your one recovery model call. You \
may only look at the current state, look at the legal actions, and submit one \
legal action with the native tools. Bash, Python and further search are not \
available. Submit a legal action now, or the game is forfeited."""

REFLECTION = """\
The transcripts of your training games, their annotations and failures, \
per-game scratch files, feedback on earlier attempts, and your current \
infrastructure are under {workspace}. Your persistent infrastructure is under \
{workspace}/inventory. On a retry, logs of earlier attempts are under \
{workspace}/feedback/reflection_attempts. Improve the infrastructure for future games.

You may create or change Python tools, persistent memory and strategies for \
using them, and delete inventory that no longer helps. Use the Bash tool to \
inspect and edit {workspace}/inventory; call Bash directly instead of describing \
or printing a tool call. Each Bash call may run for at most {bash_timeout:.0f} \
seconds. You have at most {max_calls} reflection model calls and will be told \
how many remain. Stop early when the work is done. The inventory is validated \
after your final call.

Keep tracking/failure_modes.json and tracking/artifacts.json in the inventory up \
to date while you study the training trajectories under {workspace}/feedback. \
Reuse a failure-mode ID when the cause is the same problem; create a new ID only \
for a materially different problem. Map each failure to the exact training game \
IDs. A trajectory with no failure need not be mapped. Keep mitigated and merged \
modes; do not delete them.

Keep artifact IDs stable for persistent tools, memory, strategies, instructions \
and other infrastructure. Keep the ID when you revise the same capability; use a \
new ID for a materially different capability instead of reusing an old one. \
Record paths, executable entrypoints, the failure modes addressed, and active or \
retired status. Every functional file you create, change or retire must belong to \
an artifact that addresses at least one failure mode. Retired artifacts must not \
leave files in the active inventory.

Use exactly these JSON shapes. failure_modes.json: \
{{"schema_version":"failure_modes.v1","failure_modes":[{{"id":"FM-0001","description":"...",\
"status":"active","trajectory_ids":["checkpoint_000_train_g01_red"]}}]}}. Status is \
active, mitigated or merged; only a merged entry adds "merged_into":"FM-....". \
artifacts.json: {{"schema_version":"artifacts.v1","artifacts":[{{"id":"AR-0001",\
"description":"...","kind":"tool","paths":["tools/example.py"],\
"entrypoints":["tools/example.py:choose_move"],"failure_mode_ids":["FM-0001"],\
"status":"active"}}]}}. Kind is tool, memory, strategy, instruction or other; status \
is active or retired; non-executable artifacts use an empty entrypoints list. The \
same rules are in {workspace}/feedback/protocol/SCHEMA.md.

Before you finish, run the validator ({validate_command}) and fix any structural \
errors before your final response."""

REFLECTION_BUDGET = "Reflection budget: {used}/{maximum} calls used; {remaining} remain."

REFLECTION_FINAL = """\
Reflection budget: {used}/{maximum} calls used; {remaining} remains. Final \
reflection call {turn}/{maximum}. With the evidence so far, make your best \
persistent infrastructure edits now. Call the Bash tool directly for edits under \
{workspace}/inventory instead of describing a tool call. The inventory is \
validated after this call. Bring failure_modes.json and artifacts.json in line \
with the final inventory, then run the validator before finishing."""

REFLECTION_RETRY = """\
This is a retry after a rejected reflection attempt. Before editing, read \
{workspace}/feedback/reflection_retry_history.json and the earlier logs under \
{workspace}/feedback/reflection_attempts. Fix the recorded validation error \
instead of repeating the rejected change.

Latest rejection: {latest_error}"""

SCHEMA_MD = """\
# Inventory tracking schema

failure_modes.json
  schema_version: "failure_modes.v1"
  failure_modes: list of {id: "FM-0001", description, status, trajectory_ids: [game ids]}
  status: active | mitigated | merged (merged entries add merged_into: "FM-....")
  Never delete a failure mode; mark it mitigated or merged.

artifacts.json
  schema_version: "artifacts.v1"
  artifacts: list of {id: "AR-0001", description, kind, paths, entrypoints,
                      failure_mode_ids, status}
  kind: tool | memory | strategy | instruction | other
  status: active | retired
  paths: relative to the inventory, outside tracking/
  entrypoints: "<path>:<function>" for tools; [] for every other kind
  failure_mode_ids: at least one existing failure mode
  Never delete an artifact ID; retire it and remove its files.

Every file in the inventory (outside tracking/) must belong to an active artifact.
Every Python file must load with load_python, without imports.
"""
