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
