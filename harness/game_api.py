"""The trusted side of the actor's game API (Appendix I, Hex and Go).

The actor sees game_api with get_state(), get_legal_actions(),
apply_action(action), undo_action(), current_player() and submit_action(action).
The first five work on a reversible analysis board; submit_action commits one
move on the real board, lets the opponent reply, and resets the analysis board
to the new real position. Only `dispatch` is reachable from the sandbox.

The session works with any state that has HexState's methods (envs/hex.py,
envs/go.py). A Go analysis board has no adjudicator: GNU Go scores only the
real game.
"""

from dataclasses import dataclass, field

from collections.abc import Callable

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
class GameSession:
    opening: object  # an Opening from envs/hex_openings.py or envs/go_openings.py
    opponent: Callable  # state -> action
    real: object = field(init=False)
    analysis: object = field(init=False)
    log: list[MoveLog] = field(default_factory=list)
    invalid_submissions: int = 0

    def __post_init__(self):
        self.real = self.opening.state()
        self.analysis = self._analysis_board()

    def _analysis_board(self):
        board = self.real.copy()
        if hasattr(board, "adjudicator"):
            board.adjudicator = None
        return board

    @property
    def actor(self) -> str:
        return self.opening.actor

    @property
    def done(self) -> bool:
        return self.real.is_over()

    def _describe(self, state) -> dict:
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
        self.analysis = self._analysis_board()
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


HexGameSession = GameSession  # the name before Go was added
