# Board setup and moves
- new_board() — Creates an empty 4×4 board.
- copy_board(board) — Makes a separate copy of a board.
- board_from_rows(rows) — Checks that entered rows have the right size and values, then returns a copy.
- display_board(board) — Prints the board with row and column labels.
- is_full(board) — Checks whether every square is occupied.
- legal_moves(board) — Lists the empty squares where a player could move.
- apply_move(board, move, player) — Returns a new board with a player’s mark placed in the chosen square.

# Win and board checks
- winning_squares(board, player) — Looks for a set of four of that player’s marks in four different rows and columns.
- winner(board) — Returns the winning player’s number, or None if there’s no single winner.
- check_valid(board) — Checks whether a board has the right shape, values, mark counts, and winner status.
- ordered_moves(board) — Lists legal moves in row-and-column order, which supports the tie-breaking rule.

# Scoring and search
- count_winning_sets(board, mark) — Counts the winning patterns that a player could still complete.
- evaluate(board, player) — Scores a board by subtracting the opponent’s available winning patterns from the player’s.
- minimax(board, current_player, root_player) — Searches the complete game tree and returns the best score and move.
- minimax_cutoff(...) — Searches only to the requested depth, using evaluate() at the cutoff.
- minimax_alpha_beta_cutoff(...) — Does the same depth-limited search, while pruning branches that cannot affect the result.

# Input, output, and game flow
- read_board() — Reads four rows from the user and passes them for validation.
- print_result(result) — Prints the score, best move, node count, and search time.
- play_game() — Handles a human-versus-computer game. This part is still in progress.
- main() — Shows the menu, calls the selected function, and repeats until the user chooses to exit.

SearchResult is a class, not a function. It bundles the search score, move, node count, and CPU time into one result.