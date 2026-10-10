import ast
import sys
import time
from collections import deque

# make n, and prompt user for board size value
BOARD_SIZE = None
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

# TODO Project 2: add a function for heuristic h1.
# For every numbered tile, find its row and column in the goal state.
# Add the Manhattan distance from the tile's current position to that goal
# position. Do not include the blank tile in the sum.
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

                        # TODO 1: Calculate Manhattan distance
                        # between (r, c) and (goal_r, goal_c).
                        distance = abs(r - goal_r) + abs(c - goal_c)

                        # TODO 2: Add distance to total.
                        total += distance

    return total





# TODO Project 2: add the red/green abstraction used by heuristic h2.
# Map tiles 1 through 8 to one value, tiles 9 through 15 to another value,
# and keep the blank as its own value. Return the mapped board in a hashable
# form so it can be used as a dictionary key.

# TODO Project 2: build the h2 lookup table once for the selected goal.
# Map the goal board, then search outward from that mapped goal until every
# reachable red/green board has a distance. Store each distance in a table.
# The table should contain distances for all 102,960 abstract board states.

# TODO Project 2: add h2(state, goal, h2_table).
# Map the original state in the same way as the goal and read its distance
# from the precomputed table. Build the table before the first h2 search.

# TODO Project 2: add h3(state, goal, h2_table).
# Return the larger of h1(state, goal) and h2(state, goal, h2_table).

# TODO Project 2: add a generic best_first_search(start, goal, heuristic).
# Use a priority queue for OPEN and a set or dictionary for CLOSED so each
# board state is handled as a graph-search state rather than a tree node.
# Each queue entry should retain enough parent or path information to rebuild
# the move string when the goal is found.

# TODO Project 2: define the priority and tie-breaking rules for OPEN.
# Rank a state by its heuristic value and keep move generation in U, D, L, R
# order so equal-priority results are deterministic.

# TODO Project 2: record the required search statistics.
# Count states when they are removed from OPEN, track the largest OPEN size,
# and measure CPU time around the search. Return the same keys used by
# format_result.

# TODO Project 2: decide how the h2 table is cached when the goal changes.
# A table is valid only for the mapped goal currently being searched.

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
    if BOARD_SIZE < 1:
        raise ValueError("Board size must be at least 1.")

    # Explain the puzzle and show the expected board format.
    print("Sliding Tile Puzzle Search")
    print("Enter boards as nested {BOARD_SIZE}x{BOARD_SIZE} lists.")
    print("[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]")

    # Read and validate both boards before choosing a search method.
    start = read_user_board("Start state: ")
    goal = read_user_board("Goal state: ")

    # TODO Project 2: replace the Project 1 menu with options 1, 2, 3, and 5.
    # Options 1, 2, and 3 run best-first search with h1, h2, and h3.
    # Accept combinations such as 123, and keep prompting until the user
    # enters 5 to halt. Avoid running the same option twice in one choice.
    choice = input(
        "Choose algorithm: (1) BFS (2) IDS (3) BFS and IDS (4) DLS: "
    ).strip()

    # TODO Project 2: replace these Project 1 branches with the new loop.
    # Prepare h2's abstraction table only when h2 or h3 is requested, then
    # call best_first_search with the selected heuristic for each digit.
    # Print each result with a label that identifies h1, h2, or h3.
    # The final menu should offer 1, 2, 3, and 5, and accept combinations
    # such as 123 before prompting again until the user chooses 5.

    # TODO Project 2: validate menu input before searching.
    # Reject letters, repeated digits, and digits outside 1, 2, 3, and 5.

    # Run BFS and display its formatted result.
    if choice == "1":
        result = bfs(start, goal)
        print(format_result("BFS", result))
    # Run IDS and display its formatted result.
    elif choice == "2":
        result = ids(start, goal)
        print(format_result("IDS", result))
    # Run both searches so their results can be compared.
    elif choice == "3":
        bfs_result = bfs(start, goal)
        print(format_result("BFS", bfs_result))
        print()
        ids_result = ids(start, goal)
        print(format_result("IDS", ids_result))
    # Read a depth limit, then run depth-limited search.
    elif choice == "4":
        depth = int(input("Enter DLS depth limit: "))
        result = dls(start, goal, depth)
        print(format_result("DLS", result))
    # Handle choices outside the four supported options.
    else:
        print("Invalid choice. Please enter 1, 2, 3, or 4.")


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
