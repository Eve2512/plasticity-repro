"""5×5 Go (Table 2, Appendix I of the paper).

Black (X) moves first. Rules: captures, no suicide, positional superko (no move
may recreate an earlier whole-board position), two consecutive passes end the
game, and so does the 75-action cap (passes count). Chinese area scoring with
komi 9.5, so there are no draws. Actions are GTP coordinates such as "C4"
(column letter, row number, row 1 at the bottom) or "pass".

`area_margin` counts every stone as alive. The paper adjudicates dead stones
with "the authoritative scorer"; a state can carry an `adjudicator` (GNU Go's
final_score, see envs/go_engine.py) that decides the winner of a finished game.
Without one the plain area count decides.
"""

from collections.abc import Callable

BLACK, WHITE, EMPTY = "X", "O", "."
COLUMNS = "ABCDEFGHJKLMNOPQRST"  # GTP skips I
KOMI = 9.5
MAX_ACTIONS = 75


def other(player: str) -> str:
    return WHITE if player == BLACK else BLACK


class GoState:
    def __init__(self, size: int = 5, komi: float = KOMI, max_actions: int = MAX_ACTIONS,
                 adjudicator: Callable[["GoState"], float] | None = None):
        if not 2 <= size <= len(COLUMNS):
            raise ValueError("unsupported board size")
        self.size = size
        self.komi = komi
        self.max_actions = max_actions
        self.adjudicator = adjudicator  # finished state -> black's margin after komi
        self.cells = [EMPTY] * (size * size)
        self.to_move = BLACK
        self.history: list[int] = []
        self.passes = 0  # consecutive passes at the end of history
        self.captures = {BLACK: 0, WHITE: 0}  # stones each side has captured
        self._undo: list[tuple] = []
        self._seen: dict[tuple, int] = {tuple(self.cells): 1}
        self._final: float | None = None
        self._neighbours = [self._compute_neighbours(i) for i in range(size * size)]

    @property
    def pass_index(self) -> int:
        return self.size * self.size

    # --- coordinates -------------------------------------------------------

    def index(self, action: str) -> int:
        action = action.strip().upper()
        if action == "PASS":
            return self.pass_index
        if len(action) < 2 or action[0] not in COLUMNS[: self.size] or not action[1:].isdigit():
            raise ValueError(f"not a coordinate: {action!r}")
        col, row = COLUMNS.index(action[0]), int(action[1:]) - 1
        if not 0 <= row < self.size:
            raise ValueError(f"not a coordinate: {action!r}")
        return row * self.size + col

    def name(self, index: int) -> str:
        if index == self.pass_index:
            return "pass"
        row, col = divmod(index, self.size)
        return f"{COLUMNS[col]}{row + 1}"

    def _compute_neighbours(self, index: int) -> tuple[int, ...]:
        n = self.size
        row, col = divmod(index, n)
        steps = ((-1, 0), (1, 0), (0, -1), (0, 1))
        return tuple(
            (row + dr) * n + (col + dc)
            for dr, dc in steps
            if 0 <= row + dr < n and 0 <= col + dc < n
        )

    def neighbours(self, index: int) -> tuple[int, ...]:
        return self._neighbours[index]

    # --- groups ------------------------------------------------------------

    def group(self, index: int, cells: list[str] | None = None) -> tuple[set[int], set[int]]:
        """(stones, liberties) of the group at `index`."""
        cells = self.cells if cells is None else cells
        colour = cells[index]
        stones, libs, stack = {index}, set(), [index]
        while stack:
            i = stack.pop()
            for j in self._neighbours[i]:
                if cells[j] == EMPTY:
                    libs.add(j)
                elif cells[j] == colour and j not in stones:
                    stones.add(j)
                    stack.append(j)
        return stones, libs

    def _place(self, index: int, player: str) -> tuple[list[str], int] | None:
        """Board after `player` plays `index` and the stones it captures; None if illegal."""
        if self.cells[index] != EMPTY:
            return None
        cells = self.cells.copy()
        cells[index] = player
        captured = 0
        for j in self._neighbours[index]:
            if cells[j] == other(player):
                stones, libs = self.group(j, cells)
                if not libs:
                    for s in stones:
                        cells[s] = EMPTY
                    captured += len(stones)
        if not self.group(index, cells)[1]:
            return None  # suicide
        if tuple(cells) in self._seen:
            return None  # positional superko
        return cells, captured

    # --- play --------------------------------------------------------------

    def is_over(self) -> bool:
        return self.passes >= 2 or len(self.history) >= self.max_actions

    def legal_indices(self) -> list[int]:
        """Board points first (A1, B1, ...), then pass."""
        if self.is_over():
            return []
        return [i for i in range(self.size * self.size) if self._place(i, self.to_move)] + [self.pass_index]

    def legal_actions(self) -> list[str]:
        return [self.name(i) for i in self.legal_indices()]

    def play(self, action: str | int) -> None:
        index = self.index(action) if isinstance(action, str) else action
        if self.is_over():
            raise ValueError("game is over")
        player = self.to_move
        if index == self.pass_index:
            self._undo.append((self.cells, self.passes, 0))
            self.passes += 1
        else:
            placed = self._place(index, player) if 0 <= index < self.pass_index else None
            if placed is None:
                bad = self.name(index) if 0 <= index < self.pass_index else index
                raise ValueError(f"illegal action: {bad}")
            cells, captured = placed
            self._undo.append((self.cells, self.passes, captured))
            self.cells, self.passes = cells, 0
            self.captures[player] += captured
            key = tuple(cells)
            self._seen[key] = self._seen.get(key, 0) + 1
        self.history.append(index)
        self.to_move = other(player)

    def undo(self) -> None:
        if not self.history:
            raise ValueError("nothing to undo")
        index = self.history.pop()
        self.to_move = other(self.to_move)
        if index != self.pass_index:
            key = tuple(self.cells)
            self._seen[key] -= 1
            if not self._seen[key]:
                del self._seen[key]
        self.cells, self.passes, captured = self._undo.pop()
        self.captures[self.to_move] -= captured
        self._final = None

    def copy(self) -> "GoState":
        new = GoState.__new__(GoState)
        new.__dict__.update(self.__dict__)
        new.cells = self.cells.copy()
        new.history = self.history.copy()
        new.captures = dict(self.captures)
        new._undo = self._undo.copy()
        new._seen = dict(self._seen)
        return new

    # --- scoring -----------------------------------------------------------

    def area(self) -> dict[str, int]:
        """Stones plus empty regions that touch only one colour (every stone alive)."""
        score = {BLACK: self.cells.count(BLACK), WHITE: self.cells.count(WHITE)}
        seen: set[int] = set()
        for i, c in enumerate(self.cells):
            if c != EMPTY or i in seen:
                continue
            region, borders, stack = {i}, set(), [i]
            while stack:
                k = stack.pop()
                for j in self._neighbours[k]:
                    if self.cells[j] == EMPTY and j not in region:
                        region.add(j)
                        stack.append(j)
                    elif self.cells[j] != EMPTY:
                        borders.add(self.cells[j])
            seen |= region
            if len(borders) == 1:
                score[borders.pop()] += len(region)
        return score

    def area_margin(self, player: str = BLACK) -> float:
        """`player`'s area lead after komi, every stone counted alive."""
        a = self.area()
        black = a[BLACK] - a[WHITE] - self.komi
        return black if player == BLACK else -black

    def final_margin(self) -> float | None:
        """Black's margin after komi for a finished game (adjudicated when possible)."""
        if not self.is_over():
            return None
        if self._final is None:
            self._final = self.adjudicator(self) if self.adjudicator else self.area_margin(BLACK)
        return self._final

    def winner(self) -> str | None:
        margin = self.final_margin()
        if margin is None:
            return None
        return BLACK if margin > 0 else WHITE

    # --- display -----------------------------------------------------------

    def render(self) -> str:
        n = self.size
        lines = ["   " + " ".join(COLUMNS[:n])]
        for row in range(n - 1, -1, -1):
            lines.append(f"{row + 1:>2} " + " ".join(self.cells[row * n : (row + 1) * n]))
        lines.append(f"captures: X {self.captures[BLACK]}, O {self.captures[WHITE]}; "
                     f"komi {self.komi:g}; actions {len(self.history)}/{self.max_actions}")
        return "\n".join(lines)
