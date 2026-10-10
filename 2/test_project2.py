import unittest

import project2


GOAL = (
    (1, 2, 3, 4),
    (5, 6, 7, 8),
    (9, 10, 11, 12),
    (13, 14, 15, 0),
)


class Project2Tests(unittest.TestCase):
    def setUp(self):
        project2.BOARD_SIZE = 4

    def test_h1_counts_tile_manhattan_distance(self):
        start = (
            (1, 2, 3, 4),
            (5, 6, 7, 8),
            (9, 10, 11, 12),
            (13, 14, 0, 15),
        )

        self.assertEqual(project2.h1(start, GOAL), 1)

    def test_h2_builds_complete_abstract_distance_table(self):
        start = (
            (1, 2, 3, 4),
            (5, 6, 7, 8),
            (9, 10, 11, 12),
            (13, 14, 0, 15),
        )
        abstract_goal = project2._abstract_state(GOAL)

        self.assertEqual(project2.h2(start, GOAL), 1)
        self.assertEqual(len(project2._build_h2_database(abstract_goal, 4)), 102960)

    def test_all_heuristics_find_the_five_move_optimum(self):
        start = (
            (1, 0, 3, 4),
            (5, 2, 7, 8),
            (9, 6, 11, 12),
            (13, 10, 14, 15),
        )

        for heuristic in (project2.h1, project2.h2, project2.h3):
            result = project2.best_first_search(start, GOAL, heuristic)
            self.assertTrue(result["found"])
            self.assertEqual(len(result["moves"]), 5)
            self.assertGreater(result["expanded"], 0)
            self.assertGreater(result["max_queue_size"], 0)

    def test_search_keeps_tile_slide_move_labels(self):
        start = (
            (1, 2, 3, 4),
            (5, 6, 7, 8),
            (9, 10, 11, 12),
            (13, 14, 0, 15),
        )

        result = project2.best_first_search(start, GOAL, project2.h1)

        self.assertEqual(result["moves"], "L")

    def test_search_rejects_parity_impossible_board(self):
        impossible = (
            (1, 2, 3, 4),
            (5, 6, 7, 8),
            (9, 10, 11, 12),
            (13, 15, 14, 0),
        )

        result = project2.best_first_search(impossible, GOAL, project2.h1)

        self.assertFalse(result["found"])
        self.assertEqual(result["expanded"], 0)


if __name__ == "__main__":
    unittest.main()

def test_search_rejects_parity_impossible_board():
    impossible = (
        (1, 2, 3, 4),
        (5, 6, 7, 8),
        (9, 10, 11, 12),
        (13, 15, 14, 0),
    )

    result = project2.best_first_search(impossible, GOAL, project2.h1)

    assert result["found"] is False
    assert result["expanded"] == 0