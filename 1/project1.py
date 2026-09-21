import ast
import sys
import time
from collections import deque

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
        raise ValueError("Board must be a 4x4 list with numbers 0 through 15 exactly once.")

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


# Search level by level using a queue.
def bfs(start, goal):
    # Normalize both boards before comparing or searching them.
    start = tuple(tuple(row) for row in start)
    goal = tuple(tuple(row) for row in goal)

    # Finish immediately when the start is already the goal.
    if is_goal(start, goal):
        return {
            "found": True,
            "moves": "",
            "expanded": 0,
            "max_queue_size": 1,
            "time_taken": 0.0,
        }

    # Store each state with its move path and parent state.
    queue = deque([(start, "", None)])
    max_queue_size = 1
    expanded = 0
    start_time = time.perf_counter()

    # Repeatedly expand the oldest queued state.
    while queue:
        state, path, parent = queue.popleft()
        expanded += 1

        # Stop as soon as the goal is removed from the queue.
        if is_goal(state, goal):
            return {
                "found": True,
                "moves": path,
                "expanded": expanded,
                "max_queue_size": max_queue_size,
                "time_taken": time.perf_counter() - start_time,
            }

        # Add each valid child to the back of the queue.
        for move, next_state in generate_moves(state, parent):
            queue.append((next_state, path + move, state))
            max_queue_size = max(max_queue_size, len(queue))

    # The queue emptied without finding a solution.
    return {
        "found": False,
        "moves": "",
        "expanded": expanded,
        "max_queue_size": max_queue_size,
        "time_taken": time.perf_counter() - start_time,
    }


# Search depth first while refusing to go past a depth limit.
def dls(start, goal, limit):
    # Normalize both boards before searching them.
    start = tuple(tuple(row) for row in start)
    goal = tuple(tuple(row) for row in goal)

    # Handle the zero move solution immediately.
    if is_goal(start, goal):
        return {
            "found": True,
            "moves": "",
            "expanded": 0,
            "max_stack_size": 1,
            "time_taken": 0.0,
            "limit": limit,
        }

    # Store each state with its path, parent, and current depth.
    stack = [(start, "", None, 0)]
    max_stack_size = 1
    expanded = 0
    start_time = time.perf_counter()

    # Repeatedly expand the most recently added state.
    while stack:
        state, path, parent, depth = stack.pop()
        expanded += 1

        # Stop when this depth first branch reaches the goal.
        if is_goal(state, goal):
            return {
                "found": True,
                "moves": path,
                "expanded": expanded,
                "max_stack_size": max_stack_size,
                "time_taken": time.perf_counter() - start_time,
                "limit": limit,
            }

        # Do not generate children beyond the requested depth.
        if depth >= limit:
            continue

        # Reverse insertion order so the stack follows MOVE_ORDER.
        for move, next_state in reversed(generate_moves(state, parent)):
            stack.append((next_state, path + move, state, depth + 1))
            max_stack_size = max(max_stack_size, len(stack))

    # This depth limit did not contain a solution.
    return {
        "found": False,
        "moves": "",
        "expanded": expanded,
        "max_stack_size": max_stack_size,
        "time_taken": time.perf_counter() - start_time,
        "limit": limit,
    }


# Repeat depth limited search with gradually larger limits.
def ids(start, goal, max_limit=30):
    # Normalize the boards once for all search iterations.
    start = tuple(tuple(row) for row in start)
    goal = tuple(tuple(row) for row in goal)

    total_expanded = 0
    max_stack_size = 0
    start_time = time.perf_counter()

    # Try every depth from zero through the allowed maximum.
    for depth_limit in range(max_limit + 1):
        result = dls(start, goal, depth_limit)
        total_expanded += result["expanded"]
        max_stack_size = max(max_stack_size, result["max_stack_size"])

        # Return the first solution, including totals from all iterations.
        if result["found"]:
            result["expanded"] = total_expanded
            result["max_stack_size"] = max_stack_size
            result["time_taken"] = time.perf_counter() - start_time
            return result

    # No iteration found a solution within max_limit.
    return {
        "found": False,
        "moves": "",
        "expanded": total_expanded,
        "max_stack_size": max_stack_size,
        "time_taken": time.perf_counter() - start_time,
        "limit": max_limit,
    }


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
    # Explain the puzzle and show the expected board format.
    print("Sliding Tile Puzzle Search")
    print("Enter boards as nested 4x4 lists, for example:")
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
