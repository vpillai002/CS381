"""Starter framework for CS 381 Project 3.

This file is intentionally NOT a complete submission.  The program structure,
board helpers, menu, and measurement scaffolding are provided so that the
remaining search logic can be implemented and explained by the student.

Board convention:
    * A board is a list of four lists, each containing four integers.
    * 0 means empty; 1 and 2 are the players.
    * User-facing row and column numbers start at 1.
    * Internally, Python indexes start at 0.

The assignment's duplicate descriptions of Options 0 and 4, and its reference
to both MinimaxAlphaBeta and MinimaxAlphaBetaCutOff, are documented in the menu
comments below.  This framework treats Option 0 and Option 4 as aliases for a
human-vs-computer game, and uses the cutoff alpha-beta function for Options 2
and 3.
"""

from dataclasses import dataclass # For creating classes to store data
from itertools import combinations # 
from time import perf_counter
from typing import Optional


SIZE = 4
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
    
    # TODO Make and return an independent copy of rows:
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


def legal_moves(board: Board) -> list[Move]:
    """Return all currently empty squares in row major order."""

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

# Test function:
# board = new_board()

# updated = apply_move(board, (1, 2), 1)

# print(board[1][2])    # should print 0
# print(updated[1][2])  # should print 1

# display_board(board)
# display_board(updated)


def winning_squares(board: Board, player: int) -> list[Move]:
    """Return one winning set, or an empty list if player has no win.

    A win is four marked squares with four distinct rows and four distinct
    columns.  This is not limited to the usual Tic-tac-toe lines.
    """
    # Collect the coordinates of every square owned by this player.
    owned = []

    for row in range(SIZE):
        for column in range(SIZE):
            if board[row][column] == player:
                owned.append((row, column))


    # Try every possible group of four owned squares.
    for candidate in combinations(owned, SIZE):
        rows = set()
        columns = set()

        for square in candidate:
            row = square[0]
            column = square[1]

            rows.add(row)
            columns.add(column)

        # TODO: Check that the group uses all four rows
        # and all four columns.
        if len(rows) == SIZE and len(columns) == SIZE:
            return list(candidate)

    # No winning group was found.
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
    """Check basic reachability conditions required by the assignment.

    Player 1 moves first, so player 1 has either the same number of marks as
    player 2 or exactly one more.  A board with both players winning is not
    valid.  The win-detection TODO above must be completed for the win checks
    here to be meaningful.
    """
    try:
        board_from_rows(board)
    except ValueError as error:
        return False, str(error)

    # Count Player 1's marks on the board
    count_1 = 0
    for row in board:
        for value in row:
            if value == 1:
                count_1 = count_2 + 1

    # Count Player 2's marks on the board
    count_2 = 0
    for row in board:
        for value in row:
            if value == 2:
                count_2 = count_2 + 1

    # Player 1 goes first so their count must match Player 2's
    # or be exactly one higher

    if count_1 < count_2:
        return False, "Player 2 cannot have must have more marks than player 1."

    if count_1 > count_2:
        return False, "Player 1 cannot have more than one extra mark."
    
    # A valid game cannot have both players winning
    player_1_wins = winning_squares(board, 1)
    player_2_wins = winning_squares(board, 2)

    if player_1_wins and player_2_wins:
        return False, "Both players cannot have winning sets on a valid board"

    if player_1_wins:
        return True, "valid"
        
    return True, "valid"


def ordered_moves(board: Board) -> list[Move]:
    """Return legal moves in the tie-breaking order required by the project."""
    moves = legal_moves(board)

    # TODO (move-ordering learning line): choose an ordering that is useful for
    # alpha-beta pruning while preserving row/column tie-breaking.  The simple
    # row-major ordering below is intentionally only a safe starting point.

    # Sort by row, then by column,
    moves.sort()
    return moves


def count_winning_sets(board: Board, mark: int) -> int:
    # Count the possible winning sets for mark
    available_squares = []

    for row in range(SIZE):
        for column in range(SIZE):
            if board[row][column] == EMPTY or board[row][column] == mark:
                available_squares.append((row, column))

    number_of_sets = 0

    # Try every group of four squares the player could use.
    for candidate in combinations(available_squares, SIZE):
        rows_used = set()
        columns_used = set()

        # Record which rows and columns this group uses.
        for square in candidate:
            row = square[0]
            column = square[1]

            rows_used.add(row)
            columns_used.add(column)

        # It is a possible winning set if all rows and columns differ.
        if len(rows_used) == SIZE and len(columns_used) == SIZE:
            number_of_sets = number_of_sets + 1

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

def minimax(board: Board, current_player: int, root_player: int) -> SearchResult:
    """Search the game tree."""

    start = perf_counter()

    # If the game is over, return its exact result.
    winner_found = winner(board)

    if winner_found == root_player:
        return SearchResult(1, None, 0, perf_counter() - start)

    if winner_found is not None:
        return SearchResult(-1, None, 0, perf_counter() - start)

    if is_full(board):
        return SearchResult(0, None, 0, perf_counter() - start)

    # Initialize the value for a MAX or MIN node position.
    if current_player == root_player:
        value = float("-inf")
    else:
        value = float("inf")

    best_move = None
    nodes_expanded = 1

    # Search each child position
    for move in ordered_moves(board):
        child_position = apply_move(board, move, current_player)
        next_player = 3 - current_player

        child_result = minimax(child_position, next_player, root_player)

        # MAX keeps the larger value. MIN keeps the smaller value.
        if current_player == root_player:
            if child_result.value > value:
                value = child_result.value
                best_move = move
        else:
            if child_result.value < value:
                value = child_result.value
                best_move = move

    return SearchResult(
        value,
        best_move,
        nodes_expanded,
        perf_counter() - start
    )

def minimax_cutoff(board: Board, current_player: int, root_player: int, depth: int, 
                   current_depth: int = 0) -> SearchResult:
    """Search to depth plies using evaluate at the cutoff depth."""

    if depth <= 0:
        raise ValueError("Cutoff depth must be a positive integer.")
    
    start = perf_counter()

    winner_found = winner(board)

    if winner_found == root_player:
        return SearchResult(1, None, 0, perf_counter() - start)

    if winner_found is not None:
        return SearchResult(-1, None, 0, perf_counter() - start)

    if is_full(board):
        return SearchResult(0, None, 0, perf_counter() - start)

    if current_depth >= depth:
        return SearchResult(
            evaluate(board, root_player),
            None,
            0,
            perf_counter() - start
        )

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

        child_result = minimax_cutoff(
            child_board,
            next_player,
            root_player,
            depth,
            child_depth
        )

        nodes_expanded = nodes_expanded + child_result.nodes_expanded

        if current_player == root_player:
            # MAX keeps the larger score.
            if child_result.value > value:
                value = child_result.value
                best_move = move
        else:
            # MIN keeps the smaller score.
            if child_result.value < value:
                value = child_result.value
                best_move = move

    return SearchResult(
        value,
        best_move,
        nodes_expanded,
        perf_counter() - start
    )


def minimax_alpha_beta_cutoff(
    board: Board,
    current_player: int,
    root_player: int,
    depth: int,
    current_depth: int = 0,
    alpha: float = float("-inf"),
    beta: float = float("inf")
) -> SearchResult:
    
    """Search to depth plies using alpha-beta pruning."""

    if depth <= 0:
        raise ValueError("Cutoff depth must be a positive integer.")
    
    start = perf_counter()

    winner_found = winner(board)

    if winner_found == root_player:
        return SearchResult(1, None, 0, perf_counter() - start)

    if winner_found is not None:
        return SearchResult(-1, None, 0, perf_counter() - start)

    if is_full(board):
        return SearchResult(0, None, 0, perf_counter() - start)

    if current_depth >= depth:
        return SearchResult(
            evaluate(board, root_player),
            None,
            0,
            perf_counter() - start
        )

    if current_player == root_player:
        value = float("-inf")
    else:
        value = float('inf')

    best_move = None
    nodes_expanded = 1

    for move in ordered_moves(board):
        child_board = apply_move(board, move, current_player)
        next_player = 3 - current_player
        child_depth = current_depth + 1

        child_result = minimax_alpha_beta_cutoff(
            child_board,
            next_player,
            root_player,
            depth,
            child_depth,
            alpha,
            beta
        )

        nodes_expanded = nodes_expanded + child_result.nodes_expanded

        if current_player == root_player:
            # MAX keeps the largest child score.
            if child_result.value > value:
                value = child_result.value
                best_move = move

            # Alpha remembers MAX's best score so far.
            if value > alpha:
                alpha = value

        else:
            # MIN keeps the smallest child score.
            if child_result.value < value:
                value = child_result.value
                best_move = move

            # Beta remembers MIN's best score so far.
            if value < beta:
                beta = value
        
        if alpha >= beta:
            break

    return SearchResult(
        value,
        best_move,
        nodes_expanded,
        perf_counter() - start
    )


def read_board() -> Board:
    """Read four rows of four integers from the user."""

    print("Enter four rows, each containing four values (0, 1, or 2).")
    rows = []

    for row_number in range(1, SIZE + 1):
        row_text = input(f"Row {row_number}: ")
        values = row_text.split()

        if len(values) != SIZE:
            raise ValueError("Each row must contain exactly four integers.")

        row = []
        for value in value:
            number = int(value)
            row.append(number)

        rows.append(row)

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


def play_game() -> None:
    """Menu placeholder for the human vs computer game loop."""

    print("Game-loop framework selected.")
    print("TODO: ask who moves first, alternate turns, and stop at win/draw.")


def main() -> None:
    """Run the assignment's menu until Option 5 is selected."""
    while True:
        print("\n0/4: play against computer")
        print("1: complete minimax")
        print("2: cutoff alpha-beta")
        print("3: compare cutoff minimax and alpha-beta")
        print("5: exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice in ("0", "4"):
                play_game()
            elif choice == "1":
                board = read_board()
                valid, message = check_valid(board)
                if not valid:
                    print(f"Invalid board: {message}")
                else:
                    print_result(minimax(board, 1))
            elif choice == "2":
                board = read_board()
                depth = int(input("Cutoff depth k: "))
                print_result(minimax_alpha_beta_cutoff(board, 1, depth))
            elif choice == "3":
                board = read_board()
                depth = int(input("Cutoff depth k: "))
                print("Minimax cutoff:")
                print_result(minimax_cutoff(board, 1, depth))
                print("Alpha-beta cutoff:")
                print_result(minimax_alpha_beta_cutoff(board, 1, depth))
            elif choice == "5":
                print("Goodbye.")
                return
            else:
                print("Please choose one of the listed options.")
        except (ValueError, EOFError) as error:
            print(f"Input error: {error}")



if __name__ == "__main__":
    main()
