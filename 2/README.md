# CS 381 Project 2

## Design

The program solves the fixed 4x4 sliding-tile puzzle with graph-based A* search.
Boards are immutable tuples of row tuples so they can be used as dictionary and
set keys. Each OPEN entry is held in a heap ordered by `g + h`; Manhattan
distance is a secondary tie-breaker, so it does not change A*'s optimality.
The search records the best known path cost and predecessor for each board,
skips stale heap entries, and reopens a state if a less expensive path is found.
The reported expanded count is the number of non-stale boards removed from
OPEN. The maximum queue size counts distinct boards currently in OPEN.

`h1` sums the Manhattan distance of every numbered tile to its goal position.
For `h2`, numbered tiles 1 through 8 are mapped to red and 9 through 15 to
green. A breadth-first traversal from the abstract goal fills a cached table
with exact distances for all 102,960 abstract boards. This is equivalent to
the repeated depth-limited search requested in the handout, but visits each
abstract state once. `h3` is `max(h1, h2)`. The `h2` table is built on first use
and reused for later searches in the same process.

Before searching, a parity test rejects states that cannot reach the supplied
goal. A* uses the goal-relative inversion ordering, so this works for any
valid goal arrangement, not only the standard goal.

## Function Reference

All board arguments below are valid 4x4 boards containing each integer from 0
through 15 exactly once. Search heuristics must be admissible and accept
`(state, goal)`.

| Function | Inputs | Output | Preconditions |
| --- | --- | --- | --- |
| `is_goal(state, goal)` | Two boards | Boolean equality result | Both arguments are board-shaped sequences |
| `validate_board(board)` | Candidate board | Boolean validity result | `BOARD_SIZE` is 4 |
| `parse_board(raw_text)` | Text containing a nested board, or four whitespace-separated rows | Immutable board tuple; raises `ValueError` for invalid input | `BOARD_SIZE` is 4 |
| `find_blank(state)` | Board | `(row, column)` of tile 0 | Board contains exactly one blank |
| `generate_moves(state, parent=None)` | Board and optional parent board | List of `(move, next_board)` pairs; move names the tile's slide direction | `BOARD_SIZE` is 4; state is valid |
| `h1(state, goal)` | Current board and goal | Manhattan-distance integer | Both boards have the same tile set |
| `_abstract_state(state)` | Board | Flat tuple of 0 (blank), 1 (red), and 2 (green) | `BOARD_SIZE` is 4 |
| `_abstract_neighbors(state, size)` | Abstract flat tuple and board width | Iterator of legal abstract neighbors | Abstract state has one blank and `size * size` entries |
| `_build_h2_database(abstract_goal, size)` | Abstract goal and board width | Dictionary mapping every reachable abstract state to its exact distance | Abstract goal is valid; result is cached by goal and size |
| `h2(state, goal)` | Current board and goal | Abstract-distance integer | Both boards are valid 4x4 boards |
| `h3(state, goal)` | Current board and goal | Maximum of `h1` and `h2` | Both boards are valid 4x4 boards |
| `is_solvable(start, goal)` | Two boards | Boolean parity compatibility result | Boards have the same square dimensions and tile set |
| `_failed_result(start_time, max_queue_size=0, expanded=0)` | CPU start timestamp and optional metrics | Standard not-found result dictionary | Timestamp uses `time.process_time()` |
| `best_first_search(start, goal, heuristic)` | Start board, goal board, heuristic callable | Result dictionary: `found`, `moves`, `expanded`, `max_queue_size`, `time_taken` | Valid equal-size boards; heuristic is admissible |
| `format_result(label, result)` | Display label and search result | Formatted output string | Result has the keys returned by `best_first_search` |
| `read_user_board(prompt_text)` | Prompt string | Parsed immutable board | Interactive standard input contains a valid board |
| `run_cli()` | None; reads standard input | Runs selected searches and prints results | Interactive input supplies valid start and goal boards |

## Run

This is Python source and does not need a separate compilation step. From the
repository root, run:

```sh
python3 2/project2.py
```

Enter the start board, goal board, then any combination such as `123`. Enter
`4` (or `5`) to halt. The `h2` abstract-distance table is generated the first
time option 2 or 3 is selected.

## Deep-Board Example

Goal:

```text
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
```

Start:

```text
[[5, 7, 8, 1], [6, 9, 3, 4], [11, 13, 15, 14], [2, 0, 10, 12]]
```

For this start, `h1 = 28`, `h2 = 12`, and `h3 = 28`. A* with `h3` found an
optimal 34-move solution; the verified run was:

```text
Sequence: DRULLDDDLURULURDRDDLURRULDRDLUUULL
States removed: 1061
Maximum OPEN size: 979
```

The `h1` and `h3` runs on this start each removed 1,061 states and reached a
maximum OPEN size of 979. A separate deep-board candidate with `h2 = 34` and
`h1 = 44` exceeded the 30-second check window under `h2`-only search. Use
shorter inputs when benchmarking `h2`, and allow ample runtime for harder
instances. Exact CPU timings vary by machine.

## Remaining Team Submission Items

The team should add the actual role split for both partners and the required
AI-use summary/transcript. Those details cannot be inferred from the source
tree or assignment PDF and should be written by the team accurately.