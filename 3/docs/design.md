# Project 2

## Minimax

### Team Members

- Vishnu Pillai
- Will Meyer

### Build & Run Instructions

From the project directory, run tests directly with:

`python3 minimax.py`

The program displays a menu. Options 1-3 ask for a board entered as one bracketed list containing four rows, for example:

[[1, 0, 0, 0], [2, 0, 0, 0], [0, 2, 1, 0], [0, 0, 0, 0]]

Option 0 starts a new game.

Option 4 reads an existing board and continues the game. 

The search options as for a cutoff depth when one is needed.

# CS 381 Project 3: Minimax

## 1. Design Documentation

### 1.1 Overall structure

The program implements a two player game on a 4X4 board and uses Minimax search to select moves. A player wins by marking four squares that use four different rows and four different columns. 

The program is organized into these parts:

1. Board input and validation: Reads a board and checks its dimensions, values, mark counts, and winning player conditions.
2. Board operations and move generation: Creates and copies boards, displays them, finds empty squares, and appies a move to a copy of the board.
3. Win detection and evaluation: Checks the possible winning patterns and scores a nonterminal board for depth limited search.
4. Search Algorithms: Provides a complete Minimax, depth limited Minimax, and depth limited Minimax with alpha-beta pruning.
5. User Interaction: Provides the menu, board entry, human vs. computer version of the game and formats the search results.

### 1.2 Data structures

- **Board:** A list of four lists. Each inner list is a row and each value is 0 for an empty square, 1 for Player 1 or 2 for Player 2.
- **Move:** A pair of zero based row and column numbers. The program converts moves to one based labels when displaying them to the user.
- **Winning Pattern:** A list of four board coordinates, one in each row and one in each column. The program builds the 24 patterns once using permutations of the four column numbers.
- **SearchResult:** A dataclass that stores the search value, chosen move, number of expanded nodes and CPU time in seconds.

### 1.3 Heuristics

The complete Minimax search uses exxact game outcomes, meaning, a win for the root player scores 1 and a loss scores -1 and a draw scores 0.

The depth limited searches use the same exact scores for finished games. If the search reaches its depth limit before the game ends, it uses the following:

```
score = number of possible winning patterns for the root player - number of possible winning patterns for the opponent.
```

A pattern is possible for a player when every square in it is either epty or already marked by that player.

### 1.4 Minimax and Alpha-beta Pseudocode

```text
MINIMAX(board, current_player, root_player):
    if board is a win, loss or draw:
        return its exact score

    if current_player is root_player:
        best_value = negative infinity
    else:
        best_value = positive infinity

    for each legal move:
        make the move on a child board
        switch to the other player
        child_value = MINIMAX(child board)

        if current_player is root_player:
            keep the larger value
        else:
            keep the smaller value
    return best_value and the move that produced it
``` 

For depth limited Minimax, the same search stops when the depth limit is reacher. At that point, it returns the heuristic evaluation instead of searching further.

Alpha-beta Minimax keeps two additional values:

- Alpha is the best value found so far for the maximizing player
- Beta is the best value found so far for the minimizing player

After updating alpha or beta, the search stops examinging the current node's remaining moves when alpha is greater than or equal to beta. Those moves cannot change the final choice.

### 1.5 Libraries

The solver uses only Python standard-library modules:

- dataclasses: Defines the SearchResult dataclass.
- itertools.permutations: Builds the 24 possible winning patterns.
- time.process_time: Measures CPU time used by a search.
- typing.Optional: indicates that a search result may have no move, such as at a terminal board.
- ast.literal_eval: Reads a bracketed board as Python literal data.

## 2. Code Documentation

**Board and move functions**

- new_board: Creates an empty 4X4 board.
- copy_board: Makes an independent copy of a board.
- board_from_rows: Checks board dimensions and values, then returns a copy.
- display_board: Printsthe board with one based row and column labels.
- is_full: Checks whether every square is occupied.
- ordered_moves: Returns empty squares in "row-major" order, which determines tie breaking order.
- apply_move: Checks a move and returns a new board with the mark added.

**Validation, wins, and evaluation**

- winning_squares: Checks whether a player occupies all four squares in any winning pattern.
- winner: REturns the winning player, or None if there is no single winner.
- check_valid: Checks board dimensions, values, mark counts, and winner conditions.
- count_winning_sets: Counts patterns that a player could still complete.
- evaluate: Subtracts the opponent's possible winning pattern count from the root player's count.

**Search and user interface functions**

- SearchResult: Stores the value, move, node count, and CPU time returned by a search.
- minimx: Searches the complete game tree.
- minimax_cutoff: Searches to a selected depth and evaluates boards at the cutoff.
- minimax_alpha_beta_cufoff: Performs the depth limited search with alpha-beta pruning.
- read_board: Reads a bracketed board and validates its dimensions and values.
- print_result: Displays the value, selected move, node count, and CPU time.
- run_game: Runs the human vs computer turn loop.
- player_new_game: Sets up a game from an empty board.
- play_existing_game: Sets up a game from a user entered board.
- main: Displays the menu and calls the selected option.

## 3. Compiling and Running

Run the program from the project directory with:

```bash
python3 minimax.py
```

Use the menu to select and option. For board search optinos, enter all four rows on one line as a bracketed list. Each board value most be a 0, 1 or 2. For depth limited searches, enter positive cutoff values when prompted.

## 4. Test Effort



### Performance Comparison



### File Structure

The project files are organized as follows:

```text
3/
├──/docs
    ├── design.md
    ├── ai_transcript.md
    ├── cs381-project3-Fa26.pdf
    ├── CS_381_Project_3_test_cases_Fall_2026.pdf
├── minimax.py
└── test_project2.py
```

### AI Support

The submitted Python project was primarily developed with AI assistance.

AI assistance was used to explain Pythong and the search algorithms, discuss implementation choices, and help review/debug the program.

The transcript for the AI input and assistance on building the project is included at docs/ai_transcript.md.

- `docs/ai_transcript.md`

### Team Member Roles

**Will Meyer**

- Built ...

**Vishnu Pillai**

- Responsible for...


