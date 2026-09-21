from project1 import bfs, dls, ids, is_goal, generate_moves


def test_bfs_shortest_solution_for_one_move_board():
    start = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 0, 15))
    goal = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 0))

    result = bfs(start, goal)
    assert result["found"] is True
    assert result["moves"] == "L"
    assert result["expanded"] >= 1


def test_dls_finds_solution_if_depth_allows():
    start = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 0, 15))
    goal = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 0))

    result = dls(start, goal, limit=1)
    assert result["found"] is True
    assert result["moves"] == "L"


def test_ids_finds_shortest_solution():
    start = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 0, 15))
    goal = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 0))

    result = ids(start, goal)
    assert result["found"] is True
    assert result["moves"] == "L"


def test_generate_moves_keeps_parent_reentry_out():
    state = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 0, 15))
    parent = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 0))

    moves = generate_moves(state, parent)
    assert isinstance(moves, list)
    assert all(next_state != parent for _, next_state in moves)


def test_bfs_finds_five_move_solution():
    start = ((1, 0, 3, 4), (5, 2, 7, 8), (9, 6, 11, 12), (13, 10, 14, 15))
    goal = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 0))

    result = bfs(start, goal)
    assert result["found"] is True
    assert result["moves"] == "UUULL"
    assert len(result["moves"]) == 5


def test_bfs_and_ids_find_same_eight_move_depth():
    start = ((5, 1, 3, 4), (2, 0, 7, 8), (9, 6, 11, 12), (13, 10, 14, 15))
    goal = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 0))

    bfs_result = bfs(start, goal)
    ids_result = ids(start, goal)
    assert bfs_result["found"] is True
    assert ids_result["found"] is True
    assert len(bfs_result["moves"]) == 8
    assert len(ids_result["moves"]) == len(bfs_result["moves"])


def test_dls_fails_below_solution_depth():
    start = ((1, 0, 3, 4), (5, 2, 7, 8), (9, 6, 11, 12), (13, 10, 14, 15))
    goal = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 0))

    result = dls(start, goal, limit=4)
    assert result["found"] is False


def test_all_searches_handle_already_solved_board():
    goal = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 0))

    for search_result in (bfs(goal, goal), dls(goal, goal, 0), ids(goal, goal)):
        assert search_result["found"] is True
        assert search_result["moves"] == ""
        assert search_result["expanded"] == 0
