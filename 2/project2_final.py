"""CS 381 Project 2: sliding-tile puzzle search.

The main user-facing algorithms are graph-based best-first/A* searches using
h1, h2, or h3.  The h2 pattern database is built with iterative deepening
depth-first search (IDS), as required by the project brief.
"""

import ast
import heapq
import sys
import time
from collections import deque
from functools import lru_cache
from itertools import count
from math import comb


BOARD_SIZE = None
MOVE_ORDER = ("U", "D", "L", "R")


def is_goal(state, goal):
    """Return True when state and goal contain the same board arrangement."""
    return tuple(tuple(row) for row in state) == tuple(tuple(row) for row in goal)


def validate_board(board):
    """Return whether board is a valid BOARD_SIZE by BOARD_SIZE puzzle."""
    if not isinstance(board, (list, tuple)) or len(board) != BOARD_SIZE:
        return False
    flattened = []
    for row in board:
        if not isinstance(row, (list, tuple)) or len(row) != BOARD_SIZE:
            return False
        flattened.extend(row)
    return sorted(flattened) == list(range(BOARD_SIZE * BOARD_SIZE))


def parse_board(raw_text):
    """Parse and validate a nested-list board entered by the user."""
    text = raw_text.strip()
    if not text:
        raise ValueError("Board input cannot be empty.")
    try:
        board = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if line:
                rows.append([int(part) for part in line.replace("[", "").replace("]", "").split()])
        board = rows
    if not validate_board(board):
        raise ValueError(
            f"Board must be a {BOARD_SIZE}x{BOARD_SIZE} board containing "
            f"each value from 0 through {BOARD_SIZE * BOARD_SIZE - 1}."
        )
    return tuple(tuple(row) for row in board)


def find_blank(state):
    """Return the blank tile's (row, column) position."""
    for row_index, row in enumerate(state):
        for column_index, tile in enumerate(row):
            if tile == 0:
                return row_index, column_index
    raise ValueError("State has no blank tile.")


def generate_moves(state, parent=None):
    """Return legal (move, successor) pairs in deterministic move order.

    A supplied parent is excluded so tree-search callers do not immediately
    reverse the preceding move. Graph-search callers can omit parent and use
    their closed/best-cost structures instead.
    """
    state = tuple(tuple(row) for row in state)
    blank_row, blank_column = find_blank(state)
    move_rules = {
        "U": (1, 0),
        "D": (-1, 0),
        "L": (0, 1),
        "R": (0, -1),
    }
    successors = []
    for move in MOVE_ORDER:
        row_delta, column_delta = move_rules[move]
        source_row = blank_row + row_delta
        source_column = blank_column + column_delta
        if not (0 <= source_row < BOARD_SIZE and 0 <= source_column < BOARD_SIZE):
            continue
        next_state = [list(row) for row in state]
        next_state[blank_row][blank_column], next_state[source_row][source_column] = (
            next_state[source_row][source_column],
            next_state[blank_row][blank_column],
        )
        next_state = tuple(tuple(row) for row in next_state)
        if parent is None or next_state != parent:
            successors.append((move, next_state))
    return successors


def h1(state, goal):
    """Return the Manhattan-distance sum, excluding the blank tile."""
    goal_positions = {
        tile: (row_index, column_index)
        for row_index, row in enumerate(goal)
        for column_index, tile in enumerate(row)
    }
    return sum(
        abs(row_index - goal_positions[tile][0])
        + abs(column_index - goal_positions[tile][1])
        for row_index, row in enumerate(state)
        for column_index, tile in enumerate(row)
        if tile != 0
    )


def _abstract_state(state):
    """Map numbered tiles to blank, red, and green categories."""
    red_tile_limit = BOARD_SIZE * BOARD_SIZE // 2
    return tuple(
        0 if tile == 0 else 1 if tile <= red_tile_limit else 2
        for row in state
        for tile in row
    )


def _abstract_neighbors(state, size):
    """Yield abstract states reachable by one blank swap."""
    blank_index = state.index(0)
    row_index, column_index = divmod(blank_index, size)
    neighbor_indices = []
    if row_index + 1 < size:
        neighbor_indices.append(blank_index + size)
    if row_index > 0:
        neighbor_indices.append(blank_index - size)
    if column_index + 1 < size:
        neighbor_indices.append(blank_index + 1)
    if column_index > 0:
        neighbor_indices.append(blank_index - 1)
    for neighbor_index in neighbor_indices:
        next_state = list(state)
        next_state[blank_index], next_state[neighbor_index] = (
            next_state[neighbor_index],
            next_state[blank_index],
        )
        yield tuple(next_state)


def breadth_first_search(start, goal):
    """Return a shortest path using tree-search BFS.

    This is included as the brief's uninformed-search reference algorithm.
    The main project interface uses graph-based best_first_search instead.
    """
    start = tuple(tuple(row) for row in start)
    goal = tuple(tuple(row) for row in goal)
    if not is_solvable(start, goal):
        return None
    queue = deque([(start, "", None)])
    while queue:
        state, path, parent = queue.popleft()
        if is_goal(state, goal):
            return path
        for move, neighbor in generate_moves(state, parent):
            queue.append((neighbor, path + move, state))
    return None


def depth_limited_search(start, goal, depth_limit):
    """Return a path found by depth-limited tree-search DFS, or None."""
    start = tuple(tuple(row) for row in start)
    goal = tuple(tuple(row) for row in goal)

    def visit(state, depth, parent, path):
        if is_goal(state, goal):
            return path
        if depth == depth_limit:
            return None
        for move, neighbor in generate_moves(state, parent):
            result = visit(neighbor, depth + 1, state, path + move)
            if result is not None:
                return result
        return None

    return visit(start, 0, None, "")


def iterative_deepening_search(start, goal):
    """Return a shortest path by calling DLS at limits 0, 1, 2, ... ."""
    depth_limit = 0
    while True:
        result = depth_limited_search(start, goal, depth_limit)
        if result is not None:
            return result
        depth_limit += 1


def _collect_depth_limited(state, depth, depth_limit, path, distances, seen_depths):
    """Expand one IDS iteration of the abstract h2 state graph.

    `seen_depths` is reset at every iteration. It safely avoids expanding a
    transposition already reached at an equal or shallower depth while still
    preserving the shortest distances recorded in `distances`.
    """
    previous_depth = seen_depths.get(state)
    if previous_depth is not None and previous_depth <= depth:
        return
    seen_depths[state] = depth

    if state not in distances:
        distances[state] = depth
    if depth == depth_limit:
        return

    for neighbor in _abstract_neighbors(state, BOARD_SIZE):
        if neighbor in path:
            continue
        path.add(neighbor)
        _collect_depth_limited(
            neighbor, depth + 1, depth_limit, path, distances, seen_depths
        )
        path.remove(neighbor)


@lru_cache(maxsize=4)
def build_h2_table_ids(abstract_goal, size):
    """Build the complete h2 table with iterative deepening DFS.

    Inputs are an immutable abstract goal and board size. The returned table
    maps every reachable abstract board to its exact distance from the goal.
    For a 4x4 board, the expected table size is 102,960 states.
    """
    global BOARD_SIZE
    old_board_size = BOARD_SIZE
    BOARD_SIZE = size
    try:
        total_positions = size * size
        red_tiles = total_positions // 2
        expected_states = total_positions * comb(total_positions - 1, red_tiles)
        distances = {}
        depth_limit = 0
        while len(distances) < expected_states:
            _collect_depth_limited(
                abstract_goal,
                0,
                depth_limit,
                {abstract_goal},
                distances,
                {},
            )
            depth_limit += 1
        return distances
    finally:
        BOARD_SIZE = old_board_size


def h2(state, goal):
    """Return the IDS-computed exact distance in the red/green abstraction."""
    abstract_goal = _abstract_state(goal)
    table = build_h2_table_ids(abstract_goal, len(goal))
    return table[_abstract_state(state)]


def h3(state, goal):
    """Return the stronger admissible heuristic max(h1(state), h2(state))."""
    return max(h1(state, goal), h2(state, goal))


def is_solvable(start, goal):
    """Return whether start and goal have the same puzzle parity."""
    size = len(start)
    goal_order = {
        tile: rank
        for rank, tile in enumerate(tile for row in goal for tile in row if tile != 0)
    }

    def inversion_parity(state):
        values = [goal_order[tile] for row in state for tile in row if tile != 0]
        inversions = sum(
            values[left] > values[right]
            for left in range(len(values))
            for right in range(left + 1, len(values))
        )
        return inversions % 2

    if size % 2:
        return inversion_parity(start) == inversion_parity(goal)

    def blank_row_from_bottom(state):
        row = next(index for index, values in enumerate(state) if 0 in values)
        return size - row

    return (
        (inversion_parity(start) + blank_row_from_bottom(start)) % 2
        == (inversion_parity(goal) + blank_row_from_bottom(goal)) % 2
    )


def _failed_result(start_time, max_queue_size=0, expanded=0):
    return {
        "found": False,
        "moves": "",
        "expanded": expanded,
        "max_queue_size": max_queue_size,
        "time_taken": time.process_time() - start_time,
    }


def best_first_search(start, goal, heuristic):
    """Run graph-based A* using priority g+h and return search metrics."""
    start = tuple(tuple(row) for row in start)
    goal = tuple(tuple(row) for row in goal)
    start_time = time.process_time()

    if not is_solvable(start, goal):
        return _failed_result(start_time)
    if is_goal(start, goal):
        return {
            "found": True,
            "moves": "",
            "expanded": 0,
            "max_queue_size": 1,
            "time_taken": time.process_time() - start_time,
        }

    insertion_order = count()
    frontier = []
    start_cost = 0
    heapq.heappush(
        frontier,
        (heuristic(start, goal), h1(start, goal), next(insertion_order), start_cost, start),
    )
    open_costs = {start: start_cost}
    best_cost = {start: start_cost}
    closed_costs = {}
    parents = {}
    expanded = 0
    max_queue_size = 1

    while frontier:
        _, _, _, path_cost, state = heapq.heappop(frontier)
        if open_costs.get(state) != path_cost:
            continue
        del open_costs[state]
        closed_costs[state] = path_cost
        expanded += 1

        if is_goal(state, goal):
            moves = []
            while state != start:
                state, move = parents[state]
                moves.append(move)
            return {
                "found": True,
                "moves": "".join(reversed(moves)),
                "expanded": expanded,
                "max_queue_size": max_queue_size,
                "time_taken": time.process_time() - start_time,
            }

        for move, neighbor in generate_moves(state):
            new_cost = path_cost + 1
            if new_cost >= best_cost.get(neighbor, float("inf")):
                continue
            best_cost[neighbor] = new_cost
            parents[neighbor] = (state, move)
            closed_costs.pop(neighbor, None)
            open_costs[neighbor] = new_cost
            heapq.heappush(
                frontier,
                (
                    new_cost + heuristic(neighbor, goal),
                    h1(neighbor, goal),
                    next(insertion_order),
                    new_cost,
                    neighbor,
                ),
            )
            max_queue_size = max(max_queue_size, len(open_costs))

    return _failed_result(start_time, max_queue_size, expanded)


def format_result(label, result):
    """Format a search result using the output labels from the brief."""
    status = "Solution found." if result["found"] else "Solution not found."
    return "\n".join(
        [
            f"{label}: {status}",
            f"Number of moves: {len(result['moves'])}",
            f"Sequence of moves: {result['moves']}",
            f"Number of states removed: {result['expanded']}",
            f"Maximum size of queue: {result['max_queue_size']}",
            f"CPU time: {result['time_taken']:.6f} seconds",
        ]
    )


def read_user_board(prompt):
    """Read one validated board from standard input."""
    return parse_board(input(prompt))


def run_cli():
    """Run the required interactive best-first-search interface."""
    global BOARD_SIZE
    try:
        BOARD_SIZE = int(input("Enter board size n: "))
    except ValueError as exc:
        raise ValueError("Board size must be an integer.") from exc
    if BOARD_SIZE < 2:
        raise ValueError("Board size must be at least 2.")

    start = read_user_board("Start state: ")
    goal = read_user_board("Goal state: ")
    heuristics = {"1": h1, "2": h2, "3": h3}

    while True:
        choice = input(
            "Choose heuristic(s): 1=h1, 2=h2, 3=h3; enter 4 or 5 to halt: "
        ).strip()
        if choice in {"4", "5"}:
            return
        if not choice or any(option not in heuristics for option in choice):
            print("Invalid choice. Enter any combination of 1, 2, and 3.")
            continue
        if len(set(choice)) != len(choice):
            print("Invalid choice. Do not repeat a heuristic.")
            continue

        for option in choice:
            result = best_first_search(start, goal, heuristics[option])
            print(format_result(f"Best-first search (h{option})", result))
            print()


if __name__ == "__main__":
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    except ValueError as exc:
        print(f"Input error: {exc}")
        sys.exit(1)
