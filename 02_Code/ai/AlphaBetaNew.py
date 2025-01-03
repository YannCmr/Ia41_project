import teeko
from ai.baseIA.AlphaBeta import AlphaBeta
from ai.baseIA.heuristiques import (
    evaluate_block_opponent,
    evaluate_central_control,
    evaluate_mobility,
    evaluate_near_victory,
)


class AlphaBetaNew(AlphaBeta):
    def __init__(self, depth=4):
        self.depth = depth

    def evaluate_board(self, game):
        """
        Evaluates the current board state.

        Args:
            game (teeko.TeekoGame): The current game state.

        Returns:
            int: Evaluation score for the board.
        """
        current_player = game.get_turn()
        opponent = teeko.BLACK if current_player == teeko.WHITE else teeko.WHITE

        central_control = evaluate_central_control(game, current_player)
        mobility_score = evaluate_mobility(game, current_player) - evaluate_mobility(game, opponent)
        near_victory_score = evaluate_near_victory(game, current_player)
        block_opponent_score = evaluate_block_opponent(game, opponent)

        total_score = (
            3 * central_control +
            5 * mobility_score +
            15 * near_victory_score +
            10 * block_opponent_score
        )
        return total_score
    
    def __str__(self):
        return "AlphaBetaNew"

    
