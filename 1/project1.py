import ast
import sys
import time
from collections import deque

BOARD_SIZE = 4
MOVE_ORDER = ("U", "D", "L", "R")


def is_goal(state, goal):
    return tuple(tuple(row) for row in state) == tuple(tuple(row) for row in goal)


def validate_board(board):
    if not isinstance(board, (list, tuple)) or len(board) != BOARD_SIZE:
        return False

    flattened = []
    for row in board:
        if not isinstance(row, (list, tuple)) or len(row) != BOARD_SIZE:
            return False
        flattened.extend(row)

    if sorted(flattened) != list(range(BOARD_SIZE * BOARD_SIZE)):
        return False

    return True


def parse_board(raw_text):
    text = raw_text.strip()
    if not text:
        raise ValueError("Board input cannot be empty.")

    try:
        board = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            row = [int(part) for part in line.replace("[", "").replace("]", "").split()]
            rows.append(row)
        board = rows

    if not validate_board(board):
        raise ValueError("Board must be a 4x4 list with numbers 0 through 15 exactly once.")

    return tuple(tuple(row) for row in board)


def find_blank(state):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if state[r][c] == 0:
                return r, c
    raise ValueError("No blank space found in state.")


def generate_moves(state, parent=None):
    """Return a list of (move_char, next_state) for valid moves.

    The move character names the direction the tile is sliding. That means the
    blank moves in the opposite direction, because the tile moves into the empty slot.
    """
    state = tuple(tuple(row) for row in state)
    r, c = find_blank(state)
    moves = []

    move_rules = {
        "U": (1, 0),
        "D": (-1, 0),
        "L": (0, 1),
        "R": (0, -1),
    }

    for move in MOVE_ORDER:
        dr, dc = move_rules[move]
        nr = r + dr
        nc = c + dc

        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
            next_state_list = [list(row) for row in state]
            next_state_list[r][c], next_state_list[nr][nc] = next_state_list[nr][nc], next_state_list[r][c]
            next_state = tuple(tuple(row) for row in next_state_list)
            if parent is None or next_state != parent:
                moves.append((move, next_state))

    return moves


def bfs(start, goal):
    start = tuple(tuple(row) for row in start)
    goal = tuple(tuple(row) for row in goal)

    if is_goal(start, goal):
        return {
            "found": True,
            "moves": "",
            "expanded": 0,
            "max_queue_size": 1,
            "time_taken": 0.0,
        }

    queue = deque([(start, "", None)])
    max_queue_size = 1
    expanded = 0
    start_time = time.perf_counter()

    while queue:
        state, path, parent = queue.popleft()
        expanded += 1

        if is_goal(state, goal):
            return {
                "found": True,
                "moves": path,
                "expanded": expanded,
                "max_queue_size": max_queue_size,
                "time_taken": time.perf_counter() - start_time,
            }

        for move, next_state in generate_moves(state, parent):
            queue.append((next_state, path + move, state))
            max_queue_size = max(max_queue_size, len(queue))

    return {
        "found": False,
        "moves": "",
        "expanded": expanded,
        "max_queue_size": max_queue_size,
        "time_taken": time.perf_counter() - start_time,
    }


def dls(start, goal, limit):
    start = tuple(tuple(row) for row in start)
    goal = tuple(tuple(row) for row in goal)

    if is_goal(start, goal):
        return {
            "found": True,
            "moves": "",
            "expanded": 0,
            "max_stack_size": 1,
            "time_taken": 0.0,
            "limit": limit,
        }

    stack = [(start, "", None, 0)]
    max_stack_size = 1
    expanded = 0
    start_time = time.perf_counter()

    while stack:
        state, path, parent, depth = stack.pop()
        expanded += 1

        if is_goal(state, goal):
            return {
                "found": True,
                "moves": path,
                "expanded": expanded,
                "max_stack_size": max_stack_size,
                "time_taken": time.perf_counter() - start_time,
                "limit": limit,
            }

        if depth >= limit:
            continue

        for move, next_state in reversed(generate_moves(state, parent)):
            stack.append((next_state, path + move, state, depth + 1))
            max_stack_size = max(max_stack_size, len(stack))

    return {
        "found": False,
        "moves": "",
        "expanded": expanded,
        "max_stack_size": max_stack_size,
        "time_taken": time.perf_counter() - start_time,
        "limit": limit,
    }


def ids(start, goal, max_limit=30):
    start = tuple(tuple(row) for row in start)
    goal = tuple(tuple(row) for row in goal)

    total_expanded = 0
    max_stack_size = 0
    start_time = time.perf_counter()

    for depth_limit in range(max_limit + 1):
        result = dls(start, goal, depth_limit)
        total_expanded += result["expanded"]
        max_stack_size = max(max_stack_size, result["max_stack_size"])

        if result["found"]:
            result["expanded"] = total_expanded
            result["max_stack_size"] = max_stack_size
            result["time_taken"] = time.perf_counter() - start_time
            return result

    return {
        "found": False,
        "moves": "",
        "expanded": total_expanded,
        "max_stack_size": max_stack_size,
        "time_taken": time.perf_counter() - start_time,
        "limit": max_limit,
    }


def format_result(label, result):
    if result["found"]:
        status = "Solution found."
    else:
        status = "Solution not found."

    lines = [
        f"{label}: {status}",
        f"Number of moves: {len(result['moves'])}",
        f"Sequence of moves: {result['moves']}",
        f"Number of states removed: {result['expanded']}",
    ]

    if "max_queue_size" in result:
        lines.append(f"Maximum size of queue: {result['max_queue_size']}")
    if "max_stack_size" in result:
        lines.append(f"Maximum size of stack: {result['max_stack_size']}")

    lines.append(f"CPU time: {result['time_taken']:.6f} seconds")
    return "\n".join(lines)


def read_user_board(prompt_text):
    raw = input(prompt_text)
    return parse_board(raw)


def run_cli():
    print("Sliding Tile Puzzle Search")
    print("Enter boards as nested 4x4 lists, for example:")
    print("[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]")

    start = read_user_board("Start state: ")
    goal = read_user_board("Goal state: ")

    choice = input(
        "Choose algorithm: (1) BFS (2) IDS (3) BFS and IDS (4) DLS: "
    ).strip()

    if choice == "1":
        result = bfs(start, goal)
        print(format_result("BFS", result))
    elif choice == "2":
        result = ids(start, goal)
        print(format_result("IDS", result))
    elif choice == "3":
        bfs_result = bfs(start, goal)
        print(format_result("BFS", bfs_result))
        print()
        ids_result = ids(start, goal)
        print(format_result("IDS", ids_result))
    elif choice == "4":
        depth = int(input("Enter DLS depth limit: "))
        result = dls(start, goal, depth)
        print(format_result("DLS", result))
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
