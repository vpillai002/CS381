<<<<<<< HEAD
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


=======
# CS 381 Project 2: Sliding-Tile Search

Team members: Vishnu Pillai and Will Meyer

## Run the program

From this directory, run:

```bash
python3 project2.py
```

The program asks for the board size, start board, goal board, and heuristic
selection. For the assignment, use board size `4` and enter boards as nested
lists. The menu options are:

- `1` - A* with h1, Manhattan distance
- `2` - A* with h2, the red/green abstraction heuristic
- `3` - A* with h3, `max(h1, h2)`
- `123` - run all three heuristics
- `4` or `5` - halt

Selecting h2 or h3 builds the h2 table on its first use. The table contains
102,960 abstract states, so h2 may take substantially longer than h1 or h3 on
deep boards.

Example input:

```text
4
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 0, 15]]
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
123
5
```

## Run the tests

From this directory, run:

```bash
python3 -c "import unittest, test_project2; result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_project2)); print('All tests passed' if result.wasSuccessful() else 'Tests failed'); raise SystemExit(not result.wasSuccessful())"
```

The test suite contains six tests covering h1, the complete h2 table, all
three heuristics, move labels, parity rejection, and 3x3 support.

## Documentation

The complete design documentation, pseudocode, function documentation, test
results, AI-use statement, and team roles are in
[`docs/design.md`](docs/design.md).
>>>>>>> main
