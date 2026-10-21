"""6x6 Hex (Table 2, Appendix I of the paper).

Red (X) moves first and connects north (row 1) to south (row 6). Blue (O)
connects west (column a) to east (column f). Actions are coordinates such as
"c4": column letter, then row number. The first completed connection wins;
Hex cannot end in a draw. There is no swap rule.
"""

from collections import deque

RED, BLUE, EMPTY = "X", "O", "."
COLUMNS = "abcdefghijklmnopqrstuvwxyz"


def other(player: str) -> str:
    return BLUE if player == RED else RED


class HexState:
    def __init__(self, size: int = 6):
        if not 2 <= size <= len(COLUMNS):
            raise ValueError("unsupported board size")
        self.size = size
        self.cells = [EMPTY] * (size * size)
        self.to_move = RED
        self.history: list[int] = []
        self._winner: str | None = None
        self._neighbours = [self._compute_neighbours(i) for i in range(size * size)]

    # --- coordinates -------------------------------------------------------

    def index(self, action: str) -> int:
        action = action.strip().lower()
        if len(action) < 2 or action[0] not in COLUMNS[: self.size] or not action[1:].isdigit():
            raise ValueError(f"not a coordinate: {action!r}")
        col, row = COLUMNS.index(action[0]), int(action[1:]) - 1
        if not 0 <= row < self.size:
            raise ValueError(f"not a coordinate: {action!r}")
        return row * self.size + col

    def name(self, index: int) -> str:
        row, col = divmod(index, self.size)
        return f"{COLUMNS[col]}{row + 1}"

    def _compute_neighbours(self, index: int) -> tuple[int, ...]:
        n = self.size
        row, col = divmod(index, n)
        steps = ((-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0))
        return tuple(
            (row + dr) * n + (col + dc)
            for dr, dc in steps
            if 0 <= row + dr < n and 0 <= col + dc < n
        )

    def neighbours(self, index: int) -> tuple[int, ...]:
        return self._neighbours[index]

    # --- play --------------------------------------------------------------

    def winner(self) -> str | None:
        return self._winner

    def is_over(self) -> bool:
        return self._winner is not None

    def legal_indices(self) -> list[int]:
        if self._winner:
            return []
        return [i for i, cell in enumerate(self.cells) if cell == EMPTY]

    def legal_actions(self) -> list[str]:
        return [self.name(i) for i in self.legal_indices()]

    def play(self, action: str | int) -> None:
        index = self.index(action) if isinstance(action, str) else action
        if self._winner:
            raise ValueError("game is over")
        if not 0 <= index < len(self.cells) or self.cells[index] != EMPTY:
            raise ValueError(f"illegal action: {self.name(index) if 0 <= index < len(self.cells) else index}")
        player = self.to_move
        self.cells[index] = player
        self.history.append(index)
        if self._connects(index, player):
            self._winner = player
        self.to_move = other(player)

    def undo(self) -> None:
        if not self.history:
            raise ValueError("nothing to undo")
        index = self.history.pop()
        self.cells[index] = EMPTY
        self.to_move = other(self.to_move)
        self._winner = None  # play() refuses moves after a win, so the previous state had none

    def copy(self) -> "HexState":
        new = HexState.__new__(HexState)
        new.size = self.size
        new.cells = self.cells.copy()
        new.to_move = self.to_move
        new.history = self.history.copy()
        new._winner = self._winner
        new._neighbours = self._neighbours
        return new

    def _connects(self, start: int, player: str) -> bool:
        """Does the group containing `start` touch both of `player`'s edges?"""
        n = self.size
        seen, queue = {start}, deque([start])
        first = second = False
        while queue:
            i = queue.popleft()
            row, col = divmod(i, n)
            line = row if player == RED else col
            first |= line == 0
            second |= line == n - 1
            if first and second:
                return True
            for j in self._neighbours[i]:
                if j not in seen and self.cells[j] == player:
                    seen.add(j)
                    queue.append(j)
        return False

    # --- display -----------------------------------------------------------

    def render(self) -> str:
        """ASCII board with each row shifted right, the usual Hex rhombus."""
        n = self.size
        lines = ["  " + " ".join(COLUMNS[:n])]
        for row in range(n):
            cells = " ".join(self.cells[row * n : (row + 1) * n])
            lines.append(f"{' ' * row}{row + 1:>2} {cells}")
        return "\n".join(lines)
