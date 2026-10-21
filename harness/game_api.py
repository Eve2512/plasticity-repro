"""The trusted side of the actor's game API (Appendix I, Hex).

The actor sees game_api with get_state(), get_legal_actions(),
apply_action(action), undo_action(), current_player() and submit_action(action).
The first five work on a reversible analysis board; submit_action commits one
move on the real board, lets the opponent reply, and resets the analysis board
to the new real position. Only `dispatch` is reachable from the sandbox.
"""

from dataclasses import dataclass, field

from envs.hex import HexState
from envs.hex_match import Player
from envs.hex_openings import Opening

API_METHODS = (
    "get_state",
    "get_legal_actions",
    "apply_action",
    "undo_action",
    "current_player",
    "submit_action",
)


@dataclass
class MoveLog:
    before: tuple[str, ...]  # real history before the actor's move
    action: str
    opponent_action: str | None


@dataclass
class HexGameSession:
    opening: Opening
    opponent: Player
    real: HexState = field(init=False)
    analysis: HexState = field(init=False)
    log: list[MoveLog] = field(default_factory=list)
    invalid_submissions: int = 0

    def __post_init__(self):
        self.real = self.opening.state()
        self.analysis = self.real.copy()

    @property
    def actor(self) -> str:
        return self.opening.actor

    @property
    def done(self) -> bool:
        return self.real.is_over()

    def _describe(self, state: HexState) -> dict:
        return {
            "board": state.render(),
            "to_move": state.to_move,
            "you_play": self.actor,
            "moves": [state.name(i) for i in state.history],
            "winner": state.winner(),
            "analysis_depth": len(state.history) - len(self.real.history),
        }

    # --- analysis board ----------------------------------------------------

    def get_state(self) -> dict:
        return self._describe(self.analysis)

    def get_legal_actions(self) -> list[str]:
        return self.analysis.legal_actions()

    def current_player(self) -> str:
        return self.analysis.to_move

    def apply_action(self, action: str) -> dict:
        try:
            self.analysis.play(action)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}
        return {"ok": True, **self._describe(self.analysis)}

    def undo_action(self) -> dict:
        if len(self.analysis.history) <= len(self.real.history):
            return {"ok": False, "error": "analysis board is already at the real position"}
        self.analysis.undo()
        return {"ok": True, **self._describe(self.analysis)}

    # --- real board --------------------------------------------------------

    def submit_action(self, action: str) -> dict:
        if self.done:
            return {"accepted": False, "error": "game is over"}
        if self.real.to_move != self.actor:
            return {"accepted": False, "error": "not your turn"}
        try:
            name = self.real.name(self.real.index(action))
            before = tuple(self.real.name(i) for i in self.real.history)
            self.real.play(name)
        except ValueError as exc:
            self.invalid_submissions += 1
            return {"accepted": False, "error": str(exc)}
        reply = None
        if not self.real.is_over():
            reply = self.opponent(self.real.copy())
            self.real.play(reply)
        self.log.append(MoveLog(before, name, reply))
        self.analysis = self.real.copy()
        return {
            "accepted": True,
            "submitted_action": name,
            "opponent_action": reply,
            **self._describe(self.real),
        }

    # --- sandbox entry point -----------------------------------------------

    def dispatch(self, method: str, args: list) -> object:
        if method not in API_METHODS:
            raise ValueError(f"unknown game_api method: {method}")
        return getattr(self, method)(*args)
