
from .BaseIA import BaseAI
import teeko
from abc import ABC, abstractmethod
class AlphaBeta(BaseAI):
    def alpha_beta(self, game: teeko.TeekoGame, depth: int, alpha: float, beta: float, is_maximizing: bool):
        """
        Alpha-Beta pruning algorithm.

        Args:
            game (teeko.TeekoGame): Current game state.
            depth (int): Remaining depth to evaluate.
            alpha (float): Best value for the maximizing player.
            beta (float): Best value for the minimizing player.
            is_maximizing (bool): Whether the current player is maximizing.

        Returns:
            tuple[int, tuple]: Best evaluation score and the best move.
        """
        if depth == 0 or game.is_game_over():
            return self.evaluate_board(game), None

        best_move = None

        if is_maximizing:
            max_eval = float('-inf')
            for move in self.get_all_possible_moves(game):
                simulated_game = game.copy_game()
                self.apply_move(simulated_game, move)

                eval, _ = self.alpha_beta(simulated_game, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in self.get_all_possible_moves(game):
                simulated_game = game.copy_game()
                self.apply_move(simulated_game, move)

                eval, _ = self.alpha_beta(simulated_game, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move

                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval, best_move

    def next_move(self, board):
        """
        Determines the next move for the AI using Alpha-Beta pruning.

        Args:
            board (teeko.TeekoGame): Current game state.

        Returns:
            tuple[int, int, int, int]: The next move (row, col, new_row, new_col) or
                                        (row, col, None, None) for placement phase.
        """
        _, move = self.alpha_beta(board, self.depth, float('-inf'), float('inf'), True)
        return move
    
    def apply_move(self, game: teeko.TeekoGame, move):
            """Applies a move to the game state."""
            row, col, new_row, new_col = move
            if new_row is None and new_col is None:
                game.move(row, col)
            else:
                game.move(row, col, new_row, new_col)

    @abstractmethod
    def evaluate_board(self, game: teeko.TeekoGame):
        """
        Evaluates the board state for the current player.

        Args:
            game (teeko.TeekoGame): Current game state.

        Returns:
            int: Evaluation score.
        """
        raise NotImplementedError("evaluate_board method must be implemented in the subclass")