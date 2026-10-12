import ast
import sys
import time
from collections import deque
import heapq
from itertools import count

# make n, and prompt user for board size value
BOARD_SIZE = None
MOVE_ORDER = ("U", "D", "L", "R")


# Check whether the current board matches the target board.
def is_goal(state, goal):
    return tuple(tuple(row) for row in state) == tuple(tuple(row) for row in goal)


# Confirm that a board has the expected shape and tile values.
def validate_board(board):
    # First check the outer n x n structure.
    if not isinstance(board, (list, tuple)) or len(board) != BOARD_SIZE:
        return False

    # Flatten the rows so all tile values can be checked together.
    flattened = []
    for row in board:
        if not isinstance(row, (list, tuple)) or len(row) != BOARD_SIZE:
            return False
        flattened.extend(row)

    # A valid puzzle uses each number from 0 through n*n - 1 once.
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

# Calculate h1 as the sum of Manhattan distances for all nonblank tiles.
def h1(state, goal):
    total = 0

    for r in range(len(state)):
        for c in range(len(state[r])):

            tile = state[r][c]

            if tile == 0:
                continue

            for goal_r in range(len(goal)):
                for goal_c in range(len(goal[goal_r])):

                    if tile == goal[goal_r][goal_c]:

                        # Calculate Manhattan distance
                        # between (r, c) and (goal_r, goal_c).
                        distance = abs(r - goal_r) + abs(c - goal_c)

                        # Add distance to total.
                        total += distance

    return total





# Map tiles to Red/Green. For n>4, use one red tile to keep h2 feasible.
# The assignment specifically defines eight red tiles for n=4.
def map_tile(tile):
    if tile == 0:
        return 0
    elif 1 <= tile <= (BOARD_SIZE * BOARD_SIZE // 2 if BOARD_SIZE <= 4 else 1):
        return 1 # red
    else:
        return 2 # green

# Map the board to hashable abstract Red/Green states.
def map_board(state):
    mapped = []

    for row in state:
        new_row = []

        for tile in row:
            mapped_tile = map_tile(tile)

            # Append mapped_tile to new_row.
            new_row.append(mapped_tile)

        # Append the completed new_row to mapped.
        mapped.append(new_row)

    return tuple(tuple(row) for row in mapped)

# Build exact abstract distances using reverse BFS (unit-cost shortest paths).
# The brief specifies IDS; BFS produces the same distances more efficiently.
def build_h2_table(goal):
    abstract_goal = map_board(goal)

    distances = {abstract_goal: 0}
    queue = deque([abstract_goal])

    while queue:
        current_state = queue.popleft()

        for move, next_state in generate_moves(current_state):
            if next_state not in distances:
                distances[next_state] = distances[current_state] + 1
                queue.append(next_state)

    return distances

# IDS Implementation - takes hours to days for 4 X 4 board
# def collect_depth_limited(state, depth, depth_limit, path, distances):

#     # Record the shortest distance when first discovered.
#     if state not in distances:
#         distances[state] = depth

#     # Stop exploring this branch at the depth limit.
#     if depth == depth_limit:
#         return

#     # Explore successors in the existing move order.
#     for move, next_state in generate_moves(state):

#         # Prevent cycles along the current DFS path.
#         if next_state in path:
#             continue

#         path.add(next_state)

#         collect_depth_limited(
#             next_state,
#             depth + 1,
#             depth_limit,
#             path,
#             distances
#         )

#         # Backtrack before exploring the next branch.
#         path.remove(next_state)

# def build_h2_table_ids(goal):
#     abstract_goal = map_board(goal)

#     distances = {}
#     depth_limit = 0

#     # Number of possible abstract states for this board.
#     from math import comb

#     total_positions = BOARD_SIZE * BOARD_SIZE
#     red_tiles = total_positions // 2 if BOARD_SIZE <= 4 else 1

#     expected_states = (
#         total_positions * comb(total_positions - 1, red_tiles)
#     )

#     # Increase the depth limit until all states are discovered.
#     while len(distances) < expected_states:

#         path = {abstract_goal}

#         collect_depth_limited(
#             abstract_goal,
#             depth=0,
#             depth_limit=depth_limit,
#             path=path,
#             distances=distances
#         )

#         depth_limit += 1

#     return distances

# Return the abstract-board distance for state using the precomputed table.
def h2(state, goal, h2_table):
    abstract_state = map_board(state)
    distance = h2_table[abstract_state]
    return distance

# Combine h1 and h2 by returning the larger admissible heuristic value.
def h3(state, goal, h2_table):
    return max(h1(state, goal), h2(state, goal, h2_table))

# Search the board graph by heuristic priority while tracking visited states and solution paths.
# Prioritize OPEN by heuristic value and preserve U, D, L, R order for deterministic ties.
# Track removed states, maximum OPEN size, and CPU time for formatted search results.
def best_first_search(start, goal, heuristic):
    """Graph-based A*: OPEN prioritized by g+h; reopen improved CLOSED states."""
    start_time = time.process_time()
    start = tuple(tuple(row) for row in start)
    goal = tuple(tuple(row) for row in goal)

    if not is_solvable(start, goal):
        return {"found": False, "moves": "", "expanded": 0,
                "max_queue_size": 0, "time_taken": time.process_time() - start_time}

    if is_goal(start, goal):
        return {"found": True, "moves": "", "expanded": 0,
                "max_queue_size": 1, "time_taken": time.process_time() - start_time}

    counter = count()
    open_queue = []
    open_costs = {start: 0}
    best_costs = {start: 0}
    closed = set()
    parents = {}
    heapq.heappush(open_queue, (heuristic(start), next(counter), 0, start))
    expanded = 0
    max_queue_size = 1

    while open_queue:
        priority, _, cost, current = heapq.heappop(open_queue)
        # Ignore outdated heap entries for states improved in the meantime.
        if open_costs.get(current) != cost:
            continue
        del open_costs[current]
        closed.add(current)
        expanded += 1

        if is_goal(current, goal):
            path = []
            while current != start:
                current, move = parents[current]
                path.append(move)
            return {"found": True, "moves": "".join(reversed(path)),
                    "expanded": expanded, "max_queue_size": max_queue_size,
                    "time_taken": time.process_time() - start_time}

        for move, next_state in generate_moves(current):
            new_cost = cost + 1
            if new_cost >= best_costs.get(next_state, float("inf")):
                continue
            best_costs[next_state] = new_cost
            parents[next_state] = (current, move)
            if next_state in closed:
                closed.remove(next_state)
            open_costs[next_state] = new_cost
            heapq.heappush(open_queue, (
                new_cost + heuristic(next_state), next(counter), new_cost, next_state
            ))
            max_queue_size = max(max_queue_size, len(open_costs))

    return {"found": False, "moves": "", "expanded": expanded,
            "max_queue_size": max_queue_size,
            "time_taken": time.process_time() - start_time}


def is_solvable(start, goal):
    """Check inversion/blank-row parity relative to an arbitrary goal."""
    n = len(start)
    order = {tile: i for i, tile in enumerate(
        tile for row in goal for tile in row if tile != 0)}

    def parity(board):
        values = [order[tile] for row in board for tile in row if tile != 0]
        inversions = sum(values[i] > values[j]
                         for i in range(len(values)) for j in range(i + 1, len(values)))
        if n % 2 == 0:
            blank_row = next(i for i, row in enumerate(board) if 0 in row)
            inversions += n - blank_row
        return inversions % 2

    return parity(start) == parity(goal)


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
    BOARD_SIZE = int(input("Enter board size n: "))
    if BOARD_SIZE < 2:
        raise ValueError("Board size must be at least 2.")

    # Explain the puzzle and show the expected board format.
    print("Sliding Tile Puzzle Search")
    print(f"Enter boards as nested {BOARD_SIZE}x{BOARD_SIZE} lists.")
    example = list(range(1, BOARD_SIZE * BOARD_SIZE)) + [0]
    print("Example:", [example[i:i + BOARD_SIZE] for i in range(0, len(example), BOARD_SIZE)])

    # Read and validate both boards before choosing a search method.
    start = read_user_board("Start state: ")
    goal = read_user_board("Goal state: ")

    # Rebuild the h2 table whenever the mapped goal changes.
    h2_table = None

    while True:
        choice = input(
            "Choose heuristics: (1) h1 (2) h2 (3) h3 "
            "(4 or 5) quit: "
        ).strip()

        if choice in {"4", "5"}:
            break

        valid = (
            choice
            and all(option in "123" for option in choice)
            and len(set(choice)) == len(choice)
        )

        if not valid:
            print("Invalid choice. Enter a combination of 1, 2, 3, or 4/5 to quit.")
            continue

        if ("2" in choice or "3" in choice) and h2_table is None:
            print("Building h2 table...")
            if BOARD_SIZE > 4:
                print("For n>4, h2 groups only tile 1 as red to keep the table manageable.")
            h2_table = build_h2_table_ids(goal)

        for option in choice:
            if option == "1":
                result = best_first_search(
                    start,
                    goal,
                    lambda state: h1(state, goal),
                )
                print(format_result("h1", result))

            elif option == "2":
                result = best_first_search(
                    start,
                    goal,
                    lambda state: h2(state, goal, h2_table),
                )
                print(format_result("h2", result))

            elif option == "3":
                result = best_first_search(
                    start,
                    goal,
                    lambda state: h3(state, goal, h2_table),
                )
                print(format_result("h3", result))

            print()

# BOARD_SIZE = 4

# goal = (
#     (1, 2, 3, 4),
#     (5, 6, 7, 8),
#     (9, 10, 11, 12),
#     (13, 14, 15, 0),
# )

# one_move = (
#     (1, 2, 3, 4),
#     (5, 6, 7, 8),
#     (9, 10, 11, 12),
#     (13, 14, 0, 15),
# )
# h2_table = build_h2_table(goal)

# print(len(h2_table))
# print(h2(goal, goal, h2_table))
# print(h2(one_move, goal, h2_table))

# print(h3(goal, goal, h2_table))
# print(h3(one_move, goal, h2_table))

# result = best_first_search(
#     one_move,
#     goal,
#     lambda state: h2(state, goal, h2_table)
# )

# print(result)

# h1_search = best_first_search(
#     one_move,
#     goal,
#     lambda state: h1(state, goal)
# )

# h2_search = best_first_search(
#     one_move,
#     goal,
#     lambda state: h2(state, goal, h2_table)
# )

# h3_search = best_first_search(
#     one_move,
#     goal,
#     lambda state: h3(state, goal, h2_table)
# )

# print(h1_search)
# print(h2_search)
# print(h3_search)


if __name__ == "__main__":
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    except ValueError as exc:
        print(f"Input error: {exc}")
        sys.exit(1)


# TODO Project 2 submission checklist:
# Document each function's inputs, outputs, and preconditions.
# Explain the board representation, priority queue, CLOSED structure, and h2 table.
# Add compilation and execution instructions to the design documentation.
# Include a start/goal pair whose solution requires at least 30 moves.
# Run that pair with options 123 and record the required output.
# Describe which code was produced with AI and include the complete transcript.
# Record each teammate's role.
