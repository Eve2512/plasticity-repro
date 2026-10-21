"""Play one Hex game from an opening between two move-choosing functions."""

from collections.abc import Callable
from dataclasses import dataclass

from envs.hex import HexState
from envs.hex_openings import Opening

Player = Callable[[HexState], str]


@dataclass(frozen=True)
class GameRecord:
    opening: tuple[str, ...]
    moves: tuple[str, ...]  # moves after the opening
    winner: str


def play_from(opening: Opening, actor: Player, opponent: Player) -> GameRecord:
    state = opening.state()
    start = len(state.history)
    while not state.is_over():
        mover = actor if state.to_move == opening.actor else opponent
        state.play(mover(state.copy()))
    moves = tuple(state.name(i) for i in state.history[start:])
    return GameRecord(opening.moves, moves, state.winner())
