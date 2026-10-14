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


