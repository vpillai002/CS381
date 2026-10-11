import project2


project2.BOARD_SIZE = 4

GOAL = (
    (1, 2, 3, 4),
    (5, 6, 7, 8),
    (9, 10, 11, 12),
    (13, 14, 15, 0),
)

ONE_MOVE = (
    (1, 2, 3, 4),
    (5, 6, 7, 8),
    (9, 10, 11, 12),
    (13, 14, 0, 15),
)


def test_map_board_uses_red_green_abstraction():
    assert project2.map_board(ONE_MOVE) == (
        (1, 1, 1, 1),
        (1, 1, 1, 1),
        (2, 2, 2, 2),
        (2, 2, 0, 2),
    )


def test_h2_table_contains_all_abstract_states():
    table = project2.build_h2_table(GOAL)
    assert len(table) == 102960


def test_h2_goal_and_one_move_values():
    table = project2.build_h2_table(GOAL)
    assert project2.h2(GOAL, GOAL, table) == 0
    assert project2.h2(ONE_MOVE, GOAL, table) == 1


def test_h3_combines_h1_and_h2():
    table = project2.build_h2_table(GOAL)
    assert project2.h3(GOAL, GOAL, table) == 0
    assert project2.h3(ONE_MOVE, GOAL, table) == 1


def test_best_first_search_with_h1_finds_one_move_solution():
    result = project2.best_first_search(
        ONE_MOVE,
        GOAL,
        lambda state: project2.h1(state, GOAL),
    )
    assert result["found"] is True
    assert result["moves"] == "L"
    assert result["expanded"] == 2


def test_best_first_search_with_h2_finds_one_move_solution():
    table = project2.build_h2_table(GOAL)
    result = project2.best_first_search(
        ONE_MOVE,
        GOAL,
        lambda state: project2.h2(state, GOAL, table),
    )
    assert result["found"] is True
    assert result["moves"] == "L"
    assert len(result["moves"]) == 1


def test_best_first_search_with_h3_finds_one_move_solution():
    table = project2.build_h2_table(GOAL)
    result = project2.best_first_search(
        ONE_MOVE,
        GOAL,
        lambda state: project2.h3(state, GOAL, table),
    )
    assert result["found"] is True
    assert result["moves"] == "L"
    assert len(result["moves"]) == 1


def test_best_first_search_handles_already_solved_board():
    result = project2.best_first_search(
        GOAL,
        GOAL,
        lambda state: project2.h1(state, GOAL),
    )
    assert result["found"] is True
    assert result["moves"] == ""
    assert result["expanded"] == 0
