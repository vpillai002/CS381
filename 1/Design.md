# CS 381 Project 1: Sliding-Tile Search

## 1. Design Documentation

### 1.1 Overall structure

The program solves a 4x4 sliding-tile puzzle. The value `0` represents the empty square. A search node stores:

- the current board state;
- the move sequence used to reach that state;
- the immediate parent board, so the search does not immediately reverse its previous move;
- the current depth for DLS and IDS.

The program has four layers:

1. Input parsing and validation (`parse_board` and `validate_board`).
2. Board operations (`find_blank`, `is_goal`, and `generate_moves`).
3. Search algorithms (`bfs`, `dls`, and `ids`).
4. Output and command-line interaction (`format_result`, `read_user_board`, and `run_cli`).

The implementation follows the assignment's tree-search requirement. It does not use a global visited set. A child is prevented only from immediately re-entering its parent state.

### 1.2 Data structures

- **Board:** A tuple of four tuples. This makes a state immutable and straightforward to compare.
- **BFS frontier:** `collections.deque`, used as a FIFO queue. `popleft()` removes the oldest node efficiently and `append()` adds new nodes at the back.
- **DLS/IDS frontier:** A Python list used as an explicit LIFO stack. `pop()` removes the most recently added node.
- **Search node:** A tuple containing state information. BFS stores `(state, path, parent)`. DLS stores `(state, path, parent, depth)`.
- **Move sequence:** A string over `U`, `D`, `L`, and `R`.
- **Performance counters:** Integers for expanded nodes and maximum frontier size, plus a floating-point elapsed time.

### 1.3 Libraries

Only Python standard-library modules are used:

- `ast` parses the nested-list board input safely.
- `sys` is used for the exit status after invalid input or interruption.
- `time` provides `time.perf_counter()` for timing.
- `collections.deque` provides the BFS queue.

`pytest` was used only for optional automated tests; the search program itself uses only standard-library modules and requires no downloads.

### 1.4 Move generation

The blank position is found first. For each direction, the code calculates the neighboring tile position, checks that it is inside the 4x4 board, copies the state, and swaps the blank with that tile. The resulting state is discarded if it equals the immediate parent.

The move labels describe the tile's movement. For example, `U` selects the tile below the blank because that tile slides upward into the blank.

### 1.5 `generate_moves` pseudocode

```text
GENERATE_MOVES(state, parent):
    convert state to an immutable board
    locate the blank square at row r and column c
    moves = empty list

    for each move in U, D, L, R:
        calculate the neighboring row and column for that move

        if the neighboring position is inside the board:
            copy the board
            swap the blank with the neighboring tile
            convert the copy to an immutable board

            if the new board is not the parent board:
                add (move, new board) to moves

    return moves
```

This function creates successors but does not place them into a queue or stack. The search algorithm calling it decides how each successor is stored.

### 1.6 BFS pseudocode

```text
BFS(start, goal):
    convert start and goal to immutable board states

    if start equals goal:
        return success with an empty move sequence

    create an empty FIFO queue
    enqueue (start, empty path, no parent)
    expanded = 0
    maximum queue size = 1

    while the queue is not empty:
        remove the oldest node
        expanded = expanded + 1

        if its state equals goal:
            return success and its path

        for each legal (move, child state):
            do not include the immediate parent state
            enqueue (child state, path plus move, current state)
            update maximum queue size

    return failure and the recorded statistics
```

BFS explores states in increasing path depth. Since every move has equal cost, the first solution found is a shortest solution.

### 1.7 DLS pseudocode

```text
DLS(start, goal, limit):
    convert start and goal to immutable board states

    if start equals goal:
        return success with an empty move sequence

    create an empty LIFO stack
    push (start, empty path, no parent, depth 0)
    expanded = 0
    maximum stack size = 1

    while the stack is not empty:
        remove the most recently pushed node
        expanded = expanded + 1

        if its state equals goal:
            return success and its path

        if its depth is equal to or greater than limit:
            do not generate children
            continue

        generate legal children, excluding the immediate parent
        push each child with depth + 1
        update maximum stack size

    return failure and the recorded statistics
```

DLS is depth-first search with a cutoff. A state at the depth limit is still checked for the goal, but it is not expanded further.

### 1.8 IDS pseudocode

```text
IDS(start, goal, max_limit):
    total_expanded = 0
    maximum stack size = 0
    start the timer

    for depth_limit from 0 through max_limit:
        result = DLS(start, goal, depth_limit)
        add result.expanded to total_expanded
        update the maximum stack size

        if result indicates success:
            replace its statistics with the accumulated IDS statistics
            return result

    return failure and the accumulated statistics
```

IDS restarts DLS from the start state with successively larger limits. The first successful limit is the shallowest solution depth, so IDS finds an optimal solution depth while retaining the stack-based frontier behavior of DLS. Its expanded-node count includes work from all previous DLS iterations.

## 2. Code Documentation

All board inputs must represent a valid permutation of the integers `0` through `15`, arranged as four rows of four values. Internally, boards are converted to tuples of tuples.

| Function | Inputs | Output | Preconditions |
|---|---|---|---|
| `is_goal` | `state`, `goal`: board-like values | Boolean indicating whether the boards are equal | Both values must be comparable as 4x4 boards. |
| `validate_board` | `board`: candidate list or tuple | Boolean | No special precondition; invalid shapes and values return `False`. |
| `parse_board` | `raw_text`: string containing a board | Immutable tuple-of-tuples board | Text must describe a valid 4x4 permutation of `0` through `15`; otherwise it raises `ValueError`. |
| `find_blank` | `state`: board | `(row, column)` pair for the blank | The state must contain exactly one `0`. |
| `generate_moves` | `state`: board; optional `parent`: board | List of `(move, next_state)` pairs | `state` must be a valid board. `parent` is either `None` or a board. |
| `bfs` | `start`, `goal`: boards | Result dictionary with `found`, `moves`, `expanded`, `max_queue_size`, and `time_taken` | Both boards must be valid and solvable if success is expected. |
| `dls` | `start`, `goal`: boards; `limit`: nonnegative depth bound | Result dictionary with `found`, `moves`, `expanded`, `max_stack_size`, `time_taken`, and `limit` | Both boards must be valid; `limit` should be a nonnegative integer. |
| `ids` | `start`, `goal`: boards; optional `max_limit`: maximum nonnegative depth | Result dictionary with the accumulated IDS statistics | Both boards must be valid; `max_limit` should be a nonnegative integer. |
| `format_result` | `label`: algorithm name; `result`: search result dictionary | Formatted output string | `result` must have the fields returned by the selected search function. |
| `read_user_board` | `prompt_text`: prompt string | Parsed immutable board | User input must describe a valid board. |
| `run_cli` | None; reads from standard input | None; prints prompts and results | The user must enter valid board data and a valid algorithm choice. |

### Result dictionary fields

- `found`: `True` or `False`.
- `moves`: solution string, or an empty string when no solution is found.
- `expanded`: number of nodes removed from the queue or stack.
- `max_queue_size`: maximum BFS queue size, when BFS is used.
- `max_stack_size`: maximum DLS/IDS stack size, when stack search is used.
- `time_taken`: elapsed time in seconds.
- `limit`: the DLS limit or IDS maximum limit when applicable.

## 3. Compiling and Running

After extracting the submission, open a terminal in the extracted folder. Python is interpreted, so no separate compilation step is required:

```bash
python project1.py
```

The program uses only Python standard-library modules, so no package installation or Linux-specific directory is required. The command works from any operating system with a compatible Python 3 installation, as long as the terminal's current directory contains `project1.py`.

The program requests:

1. a start state;
2. a goal state;
3. an algorithm choice: `1` for BFS, `2` for IDS, `3` for BFS and IDS, or `4` for DLS.

For DLS, it also requests a depth limit.

Example input:

```text
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 0, 15]]
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
1
```

The program prints whether a solution was found, the number and sequence of moves, states removed, maximum queue/stack size, and CPU time.

## 4. Test Effort

The goal board for the following tests was:

```text
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
```

The start board was one move away:

```text
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 0, 15]]
```

CPU times vary slightly between runs, so the important correctness checks are the found status, move sequence, and depth behavior.

### Test 1: BFS

Command choice: `1`

Observed output:

```text
BFS: Solution found.
Number of moves: 1
Sequence of moves: L
Number of states removed: 3
Maximum size of queue: 5
CPU time: approximately 0.000042 seconds
```

The output is correct because moving tile `15` left produces the goal, so the shortest sequence is `L`.

### Test 2: DLS with an insufficient limit

Command choice: `4`, depth limit `0`

Observed output:

```text
DLS limit 0: Solution not found.
Number of moves: 0
Sequence of moves:
Number of states removed: 1
Maximum size of stack: 1
CPU time: approximately 0.000002 seconds
```

The output is correct because the start board is not the goal and DLS is not allowed to expand beyond depth 0.

### Test 3: DLS with a sufficient limit

Command choice: `4`, depth limit `1`

Observed output:

```text
DLS limit 1: Solution found.
Number of moves: 1
Sequence of moves: L
Number of states removed: 3
Maximum size of stack: 3
CPU time: approximately 0.000016 seconds
```

The output is correct because the goal is exactly one move away and the limit allows depth 1.

### Test 4: IDS

Command choice: `2`

Observed output:

```text
IDS: Solution found.
Number of moves: 1
Sequence of moves: L
Number of states removed: 4
Maximum size of stack: 3
CPU time: approximately 0.000024 seconds
```

The output is correct because IDS tries limits 0 and 1. The limit-0 attempt fails, the limit-1 attempt finds `L`, and the reported expanded count includes both attempts.

### Automated tests

The project also includes `test_search.py` as an optional automated test file. If `pytest` is installed, run this command from the extracted submission folder:

```bash
python -m pytest -q
```

The main program does not require pytest. If pytest is unavailable, the program can still be run normally with `python project1.py`, and the manual test cases above can be entered through the interactive interface.

The current result is:

```text
8 passed in 0.05s
```

The automated suite contains both focused unit tests and deeper behavioral tests:

- one-move BFS, DLS, and IDS checks;
- parent-reentry prevention in `generate_moves`;
- a five-move BFS solution (`UUULL`);
- an eight-move comparison showing BFS and IDS find solutions at the same depth;
- DLS failure when its limit is below the solution depth;
- the already-solved input for BFS, DLS, and IDS.

The deeper cases are useful because they exercise multiple search levels and compare the algorithms, while the small cases make individual failures easier to diagnose. The 8-move board is a meaningful test without making the required tree-search implementation excessively expensive.
