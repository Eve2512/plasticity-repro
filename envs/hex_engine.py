"""Alpha-beta Hex opponent with a node budget per move.

The paper's opponent is a "native alpha-beta" engine at 10k-1M nodes per move
(10M for OOD); its evaluation is not described. This one scores a position by
connection distance: the fewest empty cells each side still needs to connect
its edges (own stones cost 0, empty cells 1, opponent stones block).
It is deterministic: the same position and budget always give the same move.
"""

from collections import deque

from envs.hex import BLUE, EMPTY, RED, HexState, other

WIN = 10_000
INF = 10**6


def connection_distance(state: HexState, player: str) -> int:
    """Empty cells `player` still needs to connect its two edges (0-1 BFS)."""
    n = state.size
    cells = state.cells
    blocked = other(player)
    dist = [INF] * (n * n)
    queue = deque()
    starts = range(n) if player == RED else range(0, n * n, n)
    for i in starts:
        if cells[i] == blocked:
            continue
        d = 0 if cells[i] == player else 1
        if d < dist[i]:
            dist[i] = d
            (queue.appendleft if d == 0 else queue.append)(i)
    while queue:
        i = queue.popleft()
        for j in state.neighbours(i):
            if cells[j] == blocked:
                continue
            d = dist[i] + (0 if cells[j] == player else 1)
            if d < dist[j]:
                dist[j] = d
                (queue.appendleft if cells[j] == player else queue.append)(j)
    ends = range(n * (n - 1), n * n) if player == RED else range(n - 1, n * n, n)
    return min(dist[i] for i in ends)


def evaluate(state: HexState) -> int:
    """Score for the side to move: opponent's distance minus own distance."""
    me = state.to_move
    return connection_distance(state, other(me)) - connection_distance(state, me)


class _OutOfNodes(Exception):
    pass


class AlphaBetaEngine:
    def __init__(self, max_nodes: int, max_depth: int = 64):
        self.max_nodes = max_nodes
        self.max_depth = max_depth
        self.nodes = 0
        self.last_depth = 0

    def choose(self, state: HexState) -> str:
        if state.is_over():
            raise ValueError("game is over")
        work = state.copy()
        root_moves = self._ordered(work)
        best = root_moves[0]
        self.nodes = 0
        self.last_depth = 0
        for depth in range(1, self.max_depth + 1):
            try:
                scored = []
                alpha = -INF
                for move in root_moves:
                    work.play(move)
                    score = -self._negamax(work, depth - 1, -INF, -alpha, enforce=depth > 1)
                    work.undo()
                    scored.append((score, move))
                    alpha = max(alpha, score)
            except _OutOfNodes:
                break
            # Stable sort keeps the previous order among equal scores: deterministic.
            scored.sort(key=lambda sm: -sm[0])
            root_moves = [m for _, m in scored]
            best = root_moves[0]
            self.last_depth = depth
            if scored[0][0] >= WIN or depth >= len(root_moves):
                break
        return state.name(best)

    def _negamax(self, state: HexState, depth: int, alpha: int, beta: int, enforce: bool) -> int:
        self.nodes += 1
        if enforce and self.nodes > self.max_nodes:
            raise _OutOfNodes
        if state.is_over():
            return -(WIN + depth)  # the side to move has lost; sooner losses score lower
        if depth == 0:
            return evaluate(state)
        best = -INF
        for move in self._ordered(state):
            state.play(move)
            score = -self._negamax(state, depth - 1, -beta, -alpha, enforce)
            state.undo()
            if score > best:
                best = score
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break
        return best

    @staticmethod
    def _ordered(state: HexState) -> list[int]:
        """Moves next to more stones first, then nearer the centre."""
        n = state.size
        centre = (n - 1) / 2
        cells = state.cells

        def key(i):
            row, col = divmod(i, n)
            touching = sum(cells[j] != EMPTY for j in state.neighbours(i))
            return (-touching, abs(row - centre) + abs(col - centre), i)

        return sorted(state.legal_indices(), key=key)


__all__ = ["AlphaBetaEngine", "connection_distance", "evaluate", "RED", "BLUE"]
