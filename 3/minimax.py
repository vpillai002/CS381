from dataclasses import dataclass # For creating classes to store data
from itertools import permutations
from time import process_time
from typing import Optional
import ast


SIZE = 4

WINNING_PATTERNS = []

for columns in permutations(range(SIZE)):
    pattern = []

    for row in range(SIZE):
        column = columns[row]
        pattern.append((row, column))

    WINNING_PATTERNS.append(pattern)

EMPTY = 0
PLAYERS = (1, 2)
Board = list[list[int]]
Move = tuple[int, int]  # internal (row, column), both zero-based


def new_board() -> Board:
    """Return a fresh empty 4-by-4 board."""
    board = []

    for row_number in range(SIZE):
        row = []

        for column_number in range(SIZE):
            row.append(EMPTY)

        board.append(row)

    return board

def copy_board(board: Board) -> Board:
    """Make a copy so a hypothetical move does not change the original."""
    copied_board = []

    for row in board:
        copied_row = []

        for value in row:
            copied_row.append(value)

        copied_board.append(copied_row)

    return copied_board

def board_from_rows(rows: list[list[int]]) -> Board:
    """Validate and copy rows supplied by a caller or by the menu."""
    
    if len(rows) != SIZE:
        raise ValueError("A board must have exactly four rows of four values.")

    for row in rows:
        if len(row) != SIZE:
            raise ValueError("A board must have exactly four rows of four values")

    for row in rows:
        for value in row:
            if value not in (EMPTY, 1, 2):
                raise ValueError("Board entries must be 0, 1, or 2.")
    
    return copy_board(rows)

def display_board(board: Board) -> None:
    """Print a board with one based labels that match the assignment."""

    print ("    1 2 3 4")

    row_number = 1

    for row in board:
        print(row_number, end="   ")

        for value in row:
            print(value, end=" ")

        print()
        row_number = row_number + 1

def is_full(board: Board) -> bool:
    """Return True when no square is empty."""

    for row in board:
        for value in row:
            if value == EMPTY:
                return False

    return True

def ordered_moves(board: Board) -> list[Move]:
    """Return empty squares in row-major order for tie-breaking."""

    moves = []

    for row in range(SIZE):
        for column in range(SIZE):
            if board[row][column] == EMPTY:
                moves.append((row, column))

    return moves

def apply_move(board: Board, move: Move, player: int) -> Board:
    """Return a new board with the player's mark added"""
    row = move[0]
    column = move[1]

    if player != 1 and player != 2:
        raise ValueError("Player must be 1 or 2")

    if row < 0 or row >= SIZE:
        raise ValueError("Move is outside the board")

    if column < 0 or column >= SIZE:
        raise ValueError("Move is outside the board")

    if board[row][column] != EMPTY:
        raise ValueError("That square is already taken.")

    result = copy_board(board)
    result[row][column] = player

    return result

def winning_squares(board: Board, player: int) -> list[Move]:
    """Return one winning set, or an empty list if there is no win."""

    for pattern in WINNING_PATTERNS:
        pattern_is_winning = True

        for row, column in pattern:
            if board[row][column] != player:
                pattern_is_winning = False
                break

        if pattern_is_winning:
            return pattern

    return []

def winner(board: Board) -> Optional[int]:
    """Return the winning player, or None when neither player has won."""
    winners = []

    for player in PLAYERS:
        winning_set = winning_squares(board, player)

        if winning_set:
            winners.append(player)

    if len(winners) > 1:
        # The validity checker will report this as invalid
        return None

    if len(winners) == 1:
        return winners[0]

    return None

def check_valid(board: Board) -> tuple[bool, str]:
    """Check whether the board has valid dimensions, values, and mark counts."""

    try:
        board_from_rows(board)
    except ValueError as error:
        return False, str(error)

    count_1 = 0
    count_2 = 0

    for row in board:
        for value in row:
            if value == 1:
                count_1 = count_1 + 1
            elif value == 2:
                count_2 = count_2 + 1

    # Player 1 moves first, so the counts must be equal,
    # or Player 1 may have exactly one extra mark.
    if count_1 < count_2 or count_1 > count_2 + 1:
        return False, "Player 1 must have the same number of marks as Player 2 or one more."

    player_1_wins = winning_squares(board, 1)
    player_2_wins = winning_squares(board, 2)

    if player_1_wins and player_2_wins:
        return False, "Both players cannot have winning sets on a valid board."

    # The winner must be the player who made the most recent move.
    # Player 1 moves first, so Player 1 wins only with one extra mark,
    # while Player 2 wins only when both players have the same count.
    if player_1_wins and count_1 != count_2 + 1:
        return False, "Player 1 can only win after making one more move than Player 2."

    if player_2_wins and count_1 != count_2:
        return False, "Player 2 can only win when both players have the same number of marks."

    return True, "valid"

def count_winning_sets(board: Board, mark: int) -> int:
    number_of_sets = 0

    for pattern in WINNING_PATTERNS:
        possible = True

        for row, column in pattern:
            if board[row][column] not in (EMPTY, mark):
                possible = False
                break

        if possible:
            number_of_sets += 1

    return number_of_sets

def evaluate(board: Board, player: int) -> int:
    """Score the board fromt he given player's point of view"""
    opponent = 3 - player

    player_sets = count_winning_sets(board, player)
    opponent_sets = count_winning_sets(board, opponent)

    return player_sets - opponent_sets   

@dataclass
class SearchResult:
    value: int
    move: Optional[Move]
    nodes_expanded: int
    cpu_time: float

def minimax(board, current_player, root_player):
    start = process_time()

    # Store board states so we don't have to compute them again.
    cache = {}

    value, move, nodes_expanded = minimax_search(
        board,
        current_player,
        root_player,
        cache
    )

    return SearchResult(
        value,
        move,
        nodes_expanded,
        process_time() - start
    )

def minimax_search(board, current_player, root_player, cache):
    board_key = tuple(tuple(row) for row in board)
    key = (board_key, current_player, root_player)

    # Return the saved answer if this position was already searched.
    if key in cache:
        value, move = cache[key]

        # No new node was expanded during this cache lookup.
        return value, move, 0

    winner_found = winner(board)

    if winner_found == root_player:
        result = (1, None)
        cache[key] = result
        return 1, None, 0

    if winner_found is not None:
        result = (-1, None)
        cache[key] = result
        return -1, None, 0

    if is_full(board):
        result = (0, None)
        cache[key] = result
        return 0, None, 0

    if current_player == root_player:
        value = float("-inf")
    else:
        value = float("inf")

    best_move = None
    nodes_expanded = 1

    for move in ordered_moves(board):
        child = apply_move(board, move, current_player)

        child_value, unused_move, child_nodes = minimax_search(
            child,
            3 - current_player,
            root_player,
            cache
        )

        nodes_expanded += child_nodes

        if current_player == root_player:
            if child_value > value:
                value = child_value
                best_move = move
        else:
            if child_value < value:
                value = child_value
                best_move = move

    # Cache only the value and move.
    # The node count belongs to this particular search execution.
    cache[key] = (value, best_move)

    return value, best_move, nodes_expanded

def minimax_cutoff(
    board: Board,
    current_player: int,
    root_player: int,
    depth: int,
    current_depth: int = 0
) -> SearchResult:
    """Start the search and return its result with the total CPU time."""

    if depth <= 0:
        raise ValueError("Cutoff depth must be a positive integer.")

    start = process_time()

    value, move, nodes = cutoff_search(
        board, current_player, root_player, depth, current_depth
    )

    return SearchResult(
        value,
        move,
        nodes,
        process_time() - start
    )

def cutoff_search(board, current_player, root_player, depth, current_depth):
    """Recursively search to the cutoff depth."""

    winner_found = winner(board)

    if winner_found == root_player:
        return 1, None, 0

    if winner_found is not None:
        return -1, None, 0

    if is_full(board):
        return 0, None, 0

    if current_depth >= depth:
        return evaluate(board, root_player), None, 0

    if current_player == root_player:
        value = float("-inf")
    else:
        value = float("inf")

    best_move = None
    nodes_expanded = 1

    for move in ordered_moves(board):
        child_board = apply_move(board, move, current_player)
        next_player = 3 - current_player
        child_depth = current_depth + 1

        child_value, unused_move, child_nodes = cutoff_search(
            child_board,
            next_player,
            root_player,
            depth,
            child_depth
        )

        nodes_expanded = nodes_expanded + child_nodes

        if current_player == root_player:
            # MAX keeps the larger score.
            if child_value > value:
                value = child_value
                best_move = move
        else:
            # MIN keeps the smaller score.
            if child_value < value:
                value = child_value
                best_move = move

    return value, best_move, nodes_expanded

def minimax_alpha_beta_cutoff(
    board: Board,
    current_player: int,
    root_player: int,
    depth: int,
    current_depth: int = 0,
    alpha: float = float("-inf"),
    beta: float = float("inf")
) -> SearchResult:
    """Start the alpha-beta search and return its result and CPU time."""

    if depth <= 0:
        raise ValueError("Cutoff depth must be a positive integer.")

    start = process_time()

    value, move, nodes = alpha_beta_search(
        board,
        current_player,
        root_player,
        depth,
        current_depth,
        alpha,
        beta
    )

    return SearchResult(
        value,
        move,
        nodes,
        process_time() - start
    )

def alpha_beta_search(
    board,
    current_player,
    root_player,
    depth,
    current_depth,
    alpha,
    beta
):
    """Recursively search to the cutoff depth using alpha-beta pruning."""

    winner_found = winner(board)

    if winner_found == root_player:
        return 1, None, 0

    if winner_found is not None:
        return -1, None, 0

    if is_full(board):
        return 0, None, 0

    if current_depth >= depth:
        return evaluate(board, root_player), None, 0

    if current_player == root_player:
        value = float("-inf")
    else:
        value = float("inf")

    best_move = None
    nodes_expanded = 1

    for move in ordered_moves(board):
        child_board = apply_move(board, move, current_player)
        next_player = 3 - current_player
        child_depth = current_depth + 1

        child_value, unused_move, child_nodes = alpha_beta_search(
            child_board,
            next_player,
            root_player,
            depth,
            child_depth,
            alpha,
            beta
        )

        nodes_expanded = nodes_expanded + child_nodes

        if current_player == root_player:
            # MAX keeps the largest score.
            if child_value > value:
                value = child_value
                best_move = move

            # Alpha is MAX's best score so far.
            if value > alpha:
                alpha = value

        else:
            # MIN keeps the smallest score.
            if child_value < value:
                value = child_value
                best_move = move

            # Beta is MIN's best score so far.
            if value < beta:
                beta = value

        if alpha >= beta:
            break

    return value, best_move, nodes_expanded

def read_board() -> Board:
    """Read a whole board entered as a list of rows."""
    text = input("Enter the board, for example [[1, 0, 0, 0], ...]: ")

    rows = ast.literal_eval(text)

    return board_from_rows(rows)

def print_result(result: SearchResult) -> None:
    """Print the search results"""

    if result.move is None:
        move_text = "none"
    else:
        row = result.move[0] + 1
        column = result.move[1] + 1
        move_text = (row, column)

    print(f"Value: {result.value}")
    print(f"Best move (row, column): {move_text}")
    print(f"Nodes expanded: {result.nodes_expanded}")
    print(f"CPU time: {result.cpu_time:.6f} seconds")

def run_game(board, human_player, depth):
    """Play a game from the given board."""

    computer_player = 3 - human_player

    # Count the marks to find whose turn is next.
    count_1 = 0
    count_2 = 0

    for row in board:
        for value in row:
            if value == 1:
                count_1 = count_1 + 1
            elif value == 2:
                count_2 = count_2 + 1

    if count_1 == count_2:
        current_player = 1
    else:
        current_player = 2

    display_board(board)

    while winner(board) is None and not is_full(board):
        if current_player == human_player:
            row = int(input("Choose a row (1-4): ")) - 1
            column = int(input("Choose a column (1-4): ")) - 1
            move = (row, column)
        else:
            result = minimax_alpha_beta_cutoff(
                board,
                current_player,
                computer_player,
                depth
            )
            move = result.move

        board = apply_move(board, move, current_player)
        display_board(board)

        current_player = 3 - current_player

    winner_found = winner(board)

    if winner_found is None:
        print("The game is a draw.")
    else:
        print(f"The winner is {winner_found}")

def play_new_game() -> None:

    board = new_board()
    answer = input("Do you want to play first? (y/n): ")

    if answer.lower() == "y":
        human_player = 1
    else:
        human_player = 2

    if human_player != 1 and human_player != 2:
        print("Please choose Player 1 or Player 2.")
        return

    depth = int(input("How many moves ahead should the computer search?"))

    if depth <= 0:
        print("Search depth must be greater than 0.")
        return
    
    run_game(board, human_player, depth)

def play_existing_game() -> None:
    board = read_board()

    valid, message = check_valid(board)

    if not valid:
        print(f"Invalid board: {message}")
        return

    human_player = int(input("Do you want to be Player 1 or Player 2? "))

    if human_player != 1 and human_player != 2:
        print("Please choose Player 1 or Player 2.")
        return

    depth = int(input("How many moves ahead should the computer search? "))

    if depth <= 0:
        print("Search depth must be greater than 0.")
        return

    run_game(board, human_player, depth)

def main() -> None:
    """Run the menu until the user chooses Option 5."""

    while True:
        print("\n0: play against computer - New game")
        print("1: complete minimax")
        print("2: cutoff alpha-beta")
        print("3: compare cutoff minimax and alpha-beta")
        print("4: play against the computer with a user entered board")
        print("5: exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "0":
                play_new_game()

            elif choice == "4":
                play_existing_game()

            elif choice in ("1", "2", "3"):
                board = read_board()
                valid, message = check_valid(board)

                if not valid:
                    print(f"Invalid board: {message}")
                    continue

                count_1 = 0
                count_2 = 0

                for row in board:
                    for value in row:
                        if value == 1:
                            count_1 += 1
                        elif value == 2:
                            count_2 += 1

                if count_1 == count_2:
                    current_player = 1
                else:
                    current_player = 2

                if choice == "1":
                    # Complete minimax reports the value from Player 1's perspective.
                    result = minimax(board, current_player, 1)
                    print_result(result)

                else:
                    depth = int(input("Cutoff depth k: "))

                    if choice == "2":
                        # Cutoff alpha-beta reports the value for the current player.
                        result = minimax_alpha_beta_cutoff(
                            board,
                            current_player,
                            current_player,
                            depth
                        )
                        print_result(result)

                    else:
                        print("Minimax cutoff:")
                        result = minimax_cutoff(
                            board,
                            current_player,
                            current_player,
                            depth
                        )
                        print_result(result)

                        print("Alpha-beta cutoff:")
                        result = minimax_alpha_beta_cutoff(
                            board,
                            current_player,
                            current_player,
                            depth
                        )
                        print_result(result)

            elif choice == "5":
                print("Goodbye.")
                return

            else:
                print("Please choose one of the listed options.")

        except (ValueError, SyntaxError, EOFError) as error:
            print(f"Input error: {error}")


if __name__ == "__main__":
    main()
