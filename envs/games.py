"""What the harness needs to know about each game.

The runner, episode and reflection code look a game up here by name ("hex" or
"go"): its opening banks per checkpoint, its opponent, its actor prompt, its
reflection diagnostics, and how to name the actor's colour.
"""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Game:
    name: str
    title: str  # for reports, e.g. "6x6 Hex"
    roles: dict  # actor stone -> role text for the prompt
    colours: dict  # actor stone -> colour word for game ids
    train_id_levels: tuple
    ood_levels: tuple
    openings: tuple  # opening sources; the first is the default
    banks: Callable  # (games, source, checkpoint) -> {split: [opening]}
    opponent: Callable  # (level, opening) -> Player
    diagnose: Callable  # [(history before, action)] -> [diagnostics]

    @property
    def prompt(self) -> str:
        from harness import prompts

        return {"hex": prompts.ACTOR_HEX, "go": prompts.ACTOR_GO}[self.name]


def _hex_banks(games, source, checkpoint):
    from envs.hex_openings import split_banks

    return split_banks(games, source=source)


def _hex_opponent(level, opening):
    from envs.hex_engine import AlphaBetaEngine

    return AlphaBetaEngine(level).choose


def _hex_diagnose(moves):
    from envs.hex_feedback import diagnose_game

    return diagnose_game(moves)


def _go_banks(games, source, checkpoint):
    from envs.go_openings import split_banks

    if source != "pooled":
        raise ValueError(f"Go has only pooled openings, not {source!r}")
    return split_banks(games, checkpoint=checkpoint)


def _go_opponent(level, opening):
    from envs.go_engine import GnuGoEngine

    return GnuGoEngine(level, opening.seed).choose


def _go_diagnose(moves):
    from envs.go_feedback import diagnose_game

    return diagnose_game(moves)


HEX = Game(
    name="hex", title="6x6 Hex",
    roles={"X": "red (X)", "O": "blue (O)"}, colours={"X": "red", "O": "blue"},
    train_id_levels=(3_000, 10_000, 30_000, 100_000), ood_levels=(1_000_000,),  # envs/hex_openings.py
    openings=("pooled", "contested", "legacy"),
    banks=_hex_banks, opponent=_hex_opponent, diagnose=_hex_diagnose,
)

GO = Game(
    name="go", title="5x5 Go",
    roles={"X": "Black (X)", "O": "White (O)"}, colours={"X": "black", "O": "white"},
    train_id_levels=(5, 6, 7, 8, 9), ood_levels=(10,),  # envs/go_openings.py
    openings=("pooled",),
    banks=_go_banks, opponent=_go_opponent, diagnose=_go_diagnose,
)

GAMES = {g.name: g for g in (HEX, GO)}
