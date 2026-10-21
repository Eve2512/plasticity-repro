# Runs inside the sandbox as `python -I -S -c <this file's text>`.
# Protocol: one JSON object per line on stdin/stdout.
import ast
import builtins
import io
import json
import os
import sys
import traceback

_out, _in = sys.stdout, sys.stdin
_SAFE = (
    "abs all any ascii bin bool bytearray bytes callable chr classmethod complex dict "
    "dir divmod enumerate filter float format frozenset getattr hasattr hash hex id int "
    "isinstance issubclass iter len list map max min next object oct ord pow print "
    "property range repr reversed round set setattr slice sorted staticmethod str sum "
    "super tuple type zip Exception BaseException ArithmeticError AssertionError "
    "AttributeError IndexError KeyError LookupError NameError NotImplementedError "
    "RuntimeError StopIteration TypeError ValueError ZeroDivisionError True False None"
).split()
_builtins = {name: getattr(builtins, name) for name in _SAFE if hasattr(builtins, name)}
_builtins["__build_class__"] = builtins.__build_class__
_builtins["__name__"] = "__agent__"


def _deny_import(*args, **kwargs):
    raise ImportError("Python imports are unavailable; use load_python(path) for permitted files")


_builtins["__import__"] = _deny_import


def _send(message):
    _out.write(json.dumps(message) + "\n")
    _out.flush()


def _call(method, *args):
    _send({"op": "api", "method": method, "args": list(args)})
    reply = json.loads(_in.readline())
    if not reply["ok"]:
        raise RuntimeError(reply["error"])
    return reply["value"]


game_api = {
    name: (lambda name: lambda *args: _call(name, *args))(name)
    for name in ("get_state", "get_legal_actions", "apply_action", "undo_action", "current_player", "submit_action")
}
_loadable = []
namespace = {"__builtins__": _builtins, "__name__": "__agent__", "game_api": game_api}


def load_python(path):
    """Execute a permitted .py file in the shared namespace."""
    real = os.path.realpath(path)
    if not any(real == root or real.startswith(root + os.sep) for root in _loadable):
        raise PermissionError(f"load_python may only read under: {', '.join(_loadable)}")
    with open(real) as fh:
        code = compile(fh.read(), real, "exec")
    exec(code, namespace)
    return f"loaded {path}"


namespace["load_python"] = load_python


def _run(code):
    tree = ast.parse(code, "<agent>", "exec")
    last = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        last = ast.Expression(tree.body.pop().value)
    exec(compile(tree, "<agent>", "exec"), namespace)
    if last is not None:
        value = eval(compile(last, "<agent>", "eval"), namespace)
        if value is not None:
            print(repr(value))


for line in _in:
    msg = json.loads(line)
    if msg["op"] == "init":
        _loadable = msg["loadable"]
        _send({"op": "ready"})
    elif msg["op"] == "exec":
        buffer = io.StringIO()
        sys.stdout = buffer
        ok = True
        try:
            _run(msg["code"])
        except BaseException:
            ok = False
            etype, value, tb = sys.exc_info()
            print("".join(traceback.format_exception_only(etype, value)).rstrip())
        finally:
            sys.stdout = _out
        _send({"op": "done", "ok": ok, "output": buffer.getvalue()})
