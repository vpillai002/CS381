# Project 2 - Sliding Tile Puzzle

### Team Members

- Vishnu Pillai
- Will Meyer

### Build & Run Instructions

From the project director, run tests directly with:

```
python3 -c "import test_search; [getattr(test_search, n)() for n in sorted(dir(test_search)) if n.startswith('test_')]; print('All tests passed')"
```

Example Input:

```
Enter board size n: 4
Start state: [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 0, 15]]
Goal state: [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
Choose heuristics: 1
Choose heuristics: 5
```

Choices:

```
- 1 for h1
- 2 for h2
- 3 for h3
- 123 to run all three
- 5 to quit
Choosing 2, 3, or 123 builds the h2 table first.
```

For manual board testing, use this goal state:

```
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
```

and this five-move start state:

```
[[1, 0, 3, 4], [5, 2, 7, 8], [9, 6, 11, 12], [13, 10, 14, 15]]
```



# CS 381 Project 2: Sliding-Tile Search

## 1. Design Documentation

### 1.1 Overall structure

The program solves the sliding-tile puzzle using graph-based A* search. It is
organized into four parts:

1. Board input and validation (`parse_board`, `validate_board`).
2. Board operations and move generation (`is_goal`, `find_blank`, `generate_moves`).
3. Heuristics and graph search (`h1`, `h2`, `h3`, `best_first_search`).
4. Result formatting and command-line interaction (`format_result`, `run_cli`).

The board dimension is requested at runtime. The assignment's required case is
4x4; other square sizes are supported, though large `h2` databases can require
substantial time and memory.

### 1.2 Data structures

- **Board:** A tuple of row tuples. Immutable states can be dictionary keys.
- **OPEN:** A `heapq` priority queue ordered first by `g + h`, then by Manhattan
  distance as a tie-breaker. The tie-breaker does not change the A* priority.
- **CLOSED and best path costs:** Dictionaries record expanded costs and the
  least known cost for each state. Stale queue entries are skipped, and a state
  is reopened if a lower-cost route is found.
- **Predecessors:** A dictionary stores each state's previous state and move;
  the move sequence is reconstructed when the goal is removed from OPEN.
- **Counters:** Integers record expanded states and the largest number of
  distinct states in OPEN. CPU time is measured with `time.process_time()`.

### 1.3 Heuristics

- **`h1`:** Sum of the Manhattan distances from each numbered tile to its
  position in the goal. The blank is excluded.
- **`h2`:** Maps tiles 1 through 8 to red and 9 through 15 to green for the
  required 4x4 board. A breadth-first traversal from the abstract goal caches
  exact distances for all 102,960 abstract states. This computes the same
  distance table as the IDS procedure described in the assignment, but uses
  BFS to visit each abstract state once.
- **`h3`:** `max(h1, h2)`.

The abstract table is generated on the first request for `h2` and reused for
later searches in the process. The implementation generalizes the color split
for other dimensions, but the 4x4 tile grouping above is the assignment's
definition.

Before search, a parity check rejects start/goal pairs that cannot reach each
other. The parity calculation is relative to the supplied goal arrangement.

### 1.4 A* pseudocode

```text
BEST_FIRST_SEARCH(start, goal, heuristic):
    if start and goal have incompatible parity:
        return failure

    put start in OPEN with cost 0 and priority heuristic(start, goal)
    while OPEN is not empty:
        remove the lowest-priority current entry
        skip it if it is stale
        count the state as expanded

        if state is the goal:
            reconstruct moves from predecessor records
            return solution and search statistics

        for each legal successor:
            if this path improves the best known cost:
                update its predecessor and cost
                insert or reopen it in OPEN

    return failure and search statistics
```

### 1.5 Libraries

The solver uses only Python standard-library modules:

- `ast` safely parses nested-list input.
- `heapq` and `itertools.count` implement deterministic priority ordering.
- `collections.deque` builds the abstract `h2` distance table.
- `functools.lru_cache` reuses abstract tables.
- `time` measures CPU time; `sys` reports invalid input through the exit code.

## 2. Code Documentation

Unless stated otherwise, board inputs are valid `n x n` permutations of the
integers from 0 through `n^2 - 1`. Search heuristic functions accept
`(state, goal)` and return an admissible nonnegative integer.

| Function | Inputs and output | Preconditions |
| --- | --- | --- |
| `is_goal(state, goal)` | Two boards; returns a boolean | Both arguments are board-shaped sequences |
| `validate_board(board)` | Candidate board; returns a boolean | `BOARD_SIZE` is a positive integer |
| `parse_board(raw_text)` | Board text; returns an immutable board or raises `ValueError` | `BOARD_SIZE` has been set |
| `find_blank(state)` | Board; returns the blank's `(row, column)` | The board contains one blank |
| `generate_moves(state, parent=None)` | Board and optional parent; returns `(move, next_state)` pairs | State matches `BOARD_SIZE` and is valid |
| `h1(state, goal)` | Current and goal boards; returns Manhattan distance | Boards have the same tile set |
| `_abstract_state(state)` | Board; returns a flat red/green/blank tuple | Board matches `BOARD_SIZE` |
| `_abstract_neighbors(state, size)` | Abstract state and dimension; yields legal abstract neighbors | State has `size * size` entries and one blank |
| `_build_h2_database(abstract_goal, size)` | Abstract goal and dimension; returns abstract-state distances | Abstract goal is valid; table may be large |
| `h2(state, goal)` | Current and goal boards; returns abstract distance | Boards are valid and have equal dimensions |
| `h3(state, goal)` | Current and goal boards; returns `max(h1, h2)` | Boards are valid and have equal dimensions |
| `is_solvable(start, goal)` | Two boards; returns parity compatibility | Boards have equal square dimensions and tile sets |
| `best_first_search(start, goal, heuristic)` | Start, goal, and heuristic; returns result dictionary | Valid equal-size boards and admissible heuristic |
| `format_result(label, result)` | Label and result dictionary; returns formatted text | Result comes from the search function |
| `read_user_board(prompt_text)` | Prompt; returns parsed board | Standard input contains a valid board |
| `run_cli()` | Reads input and prints results; returns `None` | User supplies valid dimension and boards |

The search result dictionary contains `found`, `moves`, `expanded`,
`max_queue_size`, and `time_taken`. A not-found result has an empty move string.

## 3. Compiling and Running

Python is interpreted; no separate compilation step is needed. From the
repository root, run:

```bash
python3 2/project2.py
```

Enter the board dimension, start board, and goal board. At the menu, enter any
combination of `1`, `2`, and `3`, such as `123`. Enter `4` or `5` to halt.
For the assignment, use dimension `4`.

Example one-move input:

```text
4
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 0, 15]]
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
123
4
```

## 4. Test Effort

The automated tests cover Manhattan distance, the complete 4x4 abstract table,
optimal path length for all three heuristics, move labels, parity rejection,
and a 3x3 board. Run them from this directory with:

```bash
pytest -q
```

The current test run reports six passing tests. A verified deep-board `h3`
case is included below; its optimal solution has 34 moves. `h2` can require
many more expansions on some deep boards, so a complete deep-board `123` run
has not been verified.

Goal:

```text
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
```

Start:

```text
[[5, 7, 8, 1], [6, 9, 3, 4], [11, 13, 15, 14], [2, 0, 10, 12]]
```

Verified `h3` result:

```text
Sequence of moves: DRULLDDDLURULURDRDDLURRULDRDLUUULL
Number of moves: 34
States removed: 1061
Maximum OPEN size: 979
```

### File Structure

The project files are organized as follows:

```text
1/
├──/docs
    ├── design.md
    ├── ai_transcript.md
    ├── cs381-project2-Fa26-final.pdf
    ├── Sliding_Puzzle_Astar_Test_Results.pdf
├── project2.py
└── test_search.py
```

### AI Support

The submitted Python project was primarily developed by Vishnu Pillai without
AI assistance.

Will Meyer also developed a separate Python version for learning and to practice
in another language, but that version is not being submitted for grading. Python is not
Will's primary programming language. Will used AI in an interactive mode to provide
tutoring while developing his separate version. The AI asked questions and provided 
explanations and gave feedback on Will's answers. This helped him to write his own
version that used the project 1 implementation as a template for the remaining program.
The interactive process helped him work through the A* implementation. 

AI assistance was not used to for the final submitted Python implementation.

The transcript of that AI supported practice project is included in:

- `docs/ai_transcript.md`

### Team Member Roles

**Vishnu Pillai**

- Responsible for the design and implementation of extending project 1 to use the A* algorithm in Python.
- Wrote the design and pseudocode sections of the final project documentation.

**Will Meyer**

- Built his own version of the project in Python with the support of AI as an interactive tutor.
- Final organization before submission, ensuring the brief checkpoints were achieved.
