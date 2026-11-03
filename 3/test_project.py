import unittest
import minimax


class MinimaxTests(unittest.TestCase):

    def assert_valid_result(self, result):
        self.assertIsInstance(result.value, (int, float))
        self.assertIsInstance(result.nodes_expanded, int)
        self.assertGreater(result.nodes_expanded, 0)
        self.assertGreaterEqual(result.cpu_time, 0)

    def test_case_1_minimax_finds_player_1_win(self):
        board = [
            [1, 2, 1, 2],
            [2, 1, 2, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 0],
        ]

        valid, message = minimax.check_valid(board)
        self.assertTrue(valid, message)

        result = minimax.minimax(board, 1, 1)

        self.assert_valid_result(result)
        self.assertEqual(result.value, 1)
        self.assertIn(result.move, minimax.ordered_moves(board))

    def test_case_2_alpha_beta_on_empty_board(self):
        board = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]

        result = minimax.minimax_alpha_beta_cutoff(
            board, 1, 1, 8
        )

        self.assert_valid_result(result)
        self.assertEqual(result.value, 0)
        self.assertEqual(result.move, (0, 0))

    def test_case_3_alpha_beta_finds_draw(self):
        board = [
            [0, 1, 0, 0],
            [0, 0, 2, 0],
            [0, 0, 0, 0],
            [0, 1, 0, 2],
        ]

        result = minimax.minimax_alpha_beta_cutoff(
            board, 1, 1, 8
        )

        self.assert_valid_result(result)
        self.assertEqual(result.value, 0)

    def test_case_4_minimax_finds_player_1_win(self):
        board = [
            [2, 1, 2, 1],
            [1, 0, 0, 0],
            [2, 0, 0, 0],
            [1, 0, 0, 0],
        ]

        valid, message = minimax.check_valid(board)
        self.assertTrue(valid, message)

        result = minimax.minimax(board, 2, 1)

        self.assert_valid_result(result)
        self.assertEqual(result.value, 1)
        self.assertIn(result.move, minimax.ordered_moves(board))

    def test_case_5_cutoff_and_alpha_beta_agree(self):
        board = [
            [1, 2, 1, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 1, 0],
        ]

        valid, message = minimax.check_valid(board)
        self.assertTrue(valid, message)

        cutoff_result = minimax.minimax_cutoff(
            board, 2, 2, 6
        )

        alpha_beta_result = minimax.minimax_alpha_beta_cutoff(
            board, 2, 2, 6
        )

        self.assert_valid_result(cutoff_result)
        self.assert_valid_result(alpha_beta_result)

        self.assertEqual(cutoff_result.value, alpha_beta_result.value)
        self.assertEqual(cutoff_result.move, alpha_beta_result.move)

        # Alpha-beta should search no more nodes than ordinary cutoff minimax.
        self.assertLessEqual(
            alpha_beta_result.nodes_expanded,
            cutoff_result.nodes_expanded
        )


if __name__ == "__main__":
    unittest.main()