import teeko
from ai.baseIA.AlphaBeta import AlphaBeta
from ai.baseIA.heuristiques import (
    evaluate_central_control,
    evaluate_mobility,
    evaluate_near_victory,
)


class AlphaBetaMoyen(AlphaBeta):
    def evaluate_board(self, game: teeko.TeekoGame):
        """
        Evaluates the board state for the current player.

        Args:
            game (teeko.TeekoGame): Current game state.

        Returns:
            int: Evaluation score.
        """
        current_player = game.get_turn()
        opponent = teeko.BLACK if current_player == teeko.WHITE else teeko.WHITE


        # Control the board: reward central positions
        central_control = evaluate_central_control(game, current_player)

        # Mobility: reward having more possible moves
        mobility_score = evaluate_mobility(game, current_player) - evaluate_mobility(game, opponent)

        # Proximity to victory: reward near-winning configurations
        near_victory_score = evaluate_near_victory(game, current_player)

        # Combine all heuristics
        total_score = (
            2 * central_control +  # Higher weight for strategic positions
            5.5 * mobility_score +  # Balance mobility and central control
            15 * near_victory_score  # Strongly favor near-victory conditions
        )
        return total_score

    def __str__(self):
        return "AlphaBetaDur"    


