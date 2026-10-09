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

# NEW PROJECT 2 STUFF WILL GO HERE
# h1()
# h2 setup
# h3()
# best_first_search()

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

    # Let the user select which search algorithm to run.
    choice = input(
        "Choose algorithm: (1) BFS (2) IDS (3) BFS and IDS (4) DLS: "
    ).strip()

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
