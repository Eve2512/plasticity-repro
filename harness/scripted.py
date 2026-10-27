"""A scripted stand-in for a model: no API calls, picklable for worker processes."""

import functools
import itertools

from harness.model import ModelTurn, ScriptedModel, ToolCall

_ids = itertools.count()


def first_legal(system, messages, tools):
    """Plays the first legal action in one Python call; reflects by doing nothing."""
    if messages[0]["content"].startswith("A new ") and " game has started." in messages[0]["content"]:
        if any(m["role"] == "assistant" for m in messages):
            return ModelTurn("done")
        code = ("s = game_api['get_state']()\nwhile not s['winner']:\n"
                "    s = game_api['submit_action'](game_api['get_legal_actions']()[0])")
        return ModelTurn("", (ToolCall(f"d{next(_ids)}", "python", {"code": code}),))
    return ModelTurn("No changes.")


def first_legal_factory(name: str = "scripted"):
    """A picklable callable that builds the scripted model (for cfg.workers > 1)."""
    return functools.partial(ScriptedModel, first_legal, name=name)
