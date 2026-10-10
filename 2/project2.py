import ast
import heapq
import sys
import time
from collections import deque
from functools import lru_cache
from itertools import count

# Project 2 specifies the 4x4 sliding-tile puzzle.
BOARD_SIZE = 4
MOVE_ORDER = ("U", "D", "L", "R")


# Check whether the current board matches the target board.
def is_goal(state, goal):
    return tuple(tuple(row) for row in state) == tuple(tuple(row) for row in goal)


# Confirm that a board has the expected shape and tile values.
def validate_board(board):
    # First check the outer 4x4 structure.
    if not isinstance(board, (list, tuple)) or len(board) != BOARD_SIZE:
        return False

    # Flatten the rows so all tile values can be checked together.
    flattened = []
    for row in board:
        if not isinstance(row, (list, tuple)) or len(row) != BOARD_SIZE:
            return False
        flattened.extend(row)

    # A valid puzzle uses each number from 0 through 15 once.
    if sorted(flattened) != list(range(BOARD_SIZE * BOARD_SIZE)):
        return False

    return True


# Convert user text into a board and validate.
def parse_board(raw_text):
    # Remove extra whitespace before trying either input format.
    text = raw_text.strip()
    if not text:
        raise ValueError("Board input cannot be empty.")

    # Use Python list input
    try:
        board = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        # If that fails, accept rows of numbers with whitespace.
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            row = [int(part) for part in line.replace("[", "").replace("]", "").split()]
            rows.append(row)
        board = rows

    # Reject bad boards before the search begins.
    if not validate_board(board):
        raise ValueError(
            f"Board must be a {BOARD_SIZE}x{BOARD_SIZE} list with numbers "
            f"0 through {BOARD_SIZE * BOARD_SIZE - 1} exactly once."
        )
    # Store board states in nested tuples.
    return tuple(tuple(row) for row in board)


# Find the row and column containing the blank tile.
def find_blank(state):
    # Scan the board from top left to bottom right.
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if state[r][c] == 0:
                return r, c
    # A valid board should never reach this line.
    raise ValueError("No blank space found in state.")


# Create every legal next board from the current state.
def generate_moves(state, parent=None):
    """Return a list of (move_char, next_state) for valid moves.

    The move character names the direction the tile is sliding. That means the
    blank moves in the opposite direction, because the tile moves into the empty slot.
    """
    # Normalize the state and locate the blank space.
    state = tuple(tuple(row) for row in state)
    r, c = find_blank(state)
    moves = []

    # Each direction identifies where the tile moving into the blank comes from.
    move_rules = {
        "U": (1, 0),
        "D": (-1, 0),
        "L": (0, 1),
        "R": (0, -1),
    }

    # Try moves in the required and consistent order.
    for move in MOVE_ORDER:
        dr, dc = move_rules[move]
        nr = r + dr
        nc = c + dc

        # Ignore directions that would leave the board.
        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
            # Copy the state so the original search node stays unchanged.
            next_state_list = [list(row) for row in state]
            next_state_list[r][c], next_state_list[nr][nc] = next_state_list[nr][nc], next_state_list[r][c]
            next_state = tuple(tuple(row) for row in next_state_list)

            # Avoid immediately reversing the move to the parent state.
            if parent is None or next_state != parent:
                moves.append((move, next_state))

    return moves

def h1(state, goal):
    """Return the Manhattan-distance sum for numbered tiles.

    Inputs: start/search state and goal state as square sequences.
    Output: nonnegative integer distance, excluding the blank tile.
    Preconditions: both states have the same valid square shape and tile set.
    """
    goal_positions = {
        tile: (row_index, column_index)
        for row_index, row in enumerate(goal)
        for column_index, tile in enumerate(row)
    }
    distance = 0
    for row_index, row in enumerate(state):
        for column_index, tile in enumerate(row):
            if tile != 0:
                goal_row, goal_column = goal_positions[tile]
                distance += abs(row_index - goal_row) + abs(column_index - goal_column)
    return distance


def _abstract_state(state):
    """Map tiles to blank, red, or green categories for heuristic 2."""
    red_tile_limit = BOARD_SIZE * BOARD_SIZE // 2
    return tuple(
        0 if tile == 0 else 1 if tile <= red_tile_limit else 2
        for row in state
        for tile in row
    )


def _abstract_neighbors(state, size):
    """Yield abstract boards reachable by one legal blank swap."""
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


@lru_cache(maxsize=4)
def _build_h2_database(abstract_goal, size):
    """Build exact abstract distances from the goal using breadth-first search."""
    distances = {abstract_goal: 0}
    frontier = deque([abstract_goal])
    while frontier:
        state = frontier.popleft()
        next_distance = distances[state] + 1
        for neighbor in _abstract_neighbors(state, size):
            if neighbor not in distances:
                distances[neighbor] = next_distance
                frontier.append(neighbor)
    return distances


def h2(state, goal):
    """Return the exact distance in the red/green abstract puzzle.

    Inputs: start/search state and goal state as square sequences.
    Output: nonnegative integer abstract distance.
    Preconditions: both states are valid boards of the same size.
    """
    abstract_goal = _abstract_state(goal)
    distances = _build_h2_database(abstract_goal, len(goal))
    return distances[_abstract_state(state)]


def h3(state, goal):
    """Return the maximum of Manhattan distance and abstract distance."""
    return max(h1(state, goal), h2(state, goal))


def is_solvable(start, goal):
    """Return whether start and goal share the sliding puzzle's parity class."""
    size = len(start)
    goal_order = {
        tile: rank
        for rank, tile in enumerate(tile for row in goal for tile in row if tile != 0)
    }

    def inversion_parity(state):
        ordered_tiles = [goal_order[tile] for row in state for tile in row if tile != 0]
        inversions = sum(
            ordered_tiles[left] > ordered_tiles[right]
            for left in range(len(ordered_tiles))
            for right in range(left + 1, len(ordered_tiles))
        )
        return inversions % 2

    if size % 2:
        return inversion_parity(start) == inversion_parity(goal)

    def blank_row_from_bottom(state):
        blank_row = next(row_index for row_index, row in enumerate(state) if 0 in row)
        return size - blank_row

    start_parity = (inversion_parity(start) + blank_row_from_bottom(start)) % 2
    goal_parity = (inversion_parity(goal) + blank_row_from_bottom(goal)) % 2
    return start_parity == goal_parity


def _failed_result(start_time, max_queue_size=0, expanded=0):
    return {
        "found": False,
        "moves": "",
        "expanded": expanded,
        "max_queue_size": max_queue_size,
        "time_taken": time.process_time() - start_time,
    }


def best_first_search(start, goal, heuristic):
    """Run graph-based A* and return the optimal move sequence and metrics.

    Inputs: start board, goal board, and a heuristic callable(state, goal).
    Output: result dictionary with found, moves, expanded, max_queue_size,
    and time_taken keys. Each move names the direction its tile slides.
    Preconditions: start and goal are valid boards of equal square size;
    heuristic is admissible for unit-cost moves.
    """
    start = tuple(tuple(row) for row in start)
    goal = tuple(tuple(row) for row in goal)
    start_time = time.process_time()

    if not is_solvable(start, goal):
        return _failed_result(start_time)

    insertion_order = count()
    start_h = heuristic(start, goal)
    start_tie_breaker = h1(start, goal)
    frontier = [(start_h, start_tie_breaker, next(insertion_order), 0, start)]
    open_costs = {start: 0}
    closed_costs = {}
    parent = {}
    best_cost = {start: 0}
    max_queue_size = 1
    expanded = 0

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
                state, move = parent[state]
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
            parent[neighbor] = (state, move)
            if neighbor in closed_costs:
                del closed_costs[neighbor]

            neighbor_h = heuristic(neighbor, goal)
            tie_breaker = h1(neighbor, goal)
            open_costs[neighbor] = new_cost
            heapq.heappush(
                frontier,
                (
                    new_cost + neighbor_h,
                    tie_breaker,
                    next(insertion_order),
                    new_cost,
                    neighbor,
                ),
            )
            max_queue_size = max(max_queue_size, len(open_costs))

    return _failed_result(start_time, max_queue_size, expanded)

# Turn a search result dictionary into readable output.
def format_result(label, result):
    # Choose a short status message based on the search outcome.
    if result["found"]:
        status = "Solution found."
    else:
        status = "Solution not found."

    # Build the common result lines first.
    lines = [
        f"{label}: {status}",
        f"Number of moves: {len(result['moves'])}",
        f"Sequence of moves: {result['moves']}",
        f"Number of states removed: {result['expanded']}",
    ]

    # Add the data structure metric used by this search.
    if "max_queue_size" in result:
        lines.append(f"Maximum size of queue: {result['max_queue_size']}")
    if "max_stack_size" in result:
        lines.append(f"Maximum size of stack: {result['max_stack_size']}")

    # Finish with timing and join all lines for display.
    lines.append(f"CPU time: {result['time_taken']:.6f} seconds")
    return "\n".join(lines)


# Read one board from the user and pass it through the parser.
def read_user_board(prompt_text):
    # Input handling and validation are kept in separate functions.
    raw = input(prompt_text)
    return parse_board(raw)


# Run the interactive program from input prompts to search results.
def run_cli():
    global BOARD_SIZE
    BOARD_SIZE = 4

    print("Sliding Tile Puzzle Search")
    print("Enter boards as nested 4x4 lists.")
    print("[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]")

    start = read_user_board("Start state: ")
    goal = read_user_board("Goal state: ")

    heuristics = {"1": h1, "2": h2, "3": h3}
    while True:
        choice = input(
            "Choose heuristic(s): 1=h1, 2=h2, 3=h3; enter 4 or 5 to halt: "
        ).strip()
        if choice in {"4", "5"}:
            break
        if not choice or any(option not in heuristics for option in choice):
            print("Invalid choice. Enter any combination of 1, 2, and 3, or 4 to halt.")
            continue

        for option in choice:
            label = f"Best-first search (h{option})"
            result = best_first_search(start, goal, heuristics[option])
            print(format_result(label, result))


if __name__ == "__main__":
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    except ValueError as exc:
        print(f"Input error: {exc}")
        sys.exit(1)
