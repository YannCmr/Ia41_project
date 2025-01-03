from ai.baseIA.MinMax import MinMax

import teeko

from ai.baseIA.heuristiques import evaluate_central_control, evaluate_mobility, evaluate_near_victory
class MiniMax_Facile(MinMax):
    def __init__(self, depth=3):
        self.depth = depth

    def evaluate_board(self, game: teeko.TeekoGame):
        """
        Evaluates the board state for the current player with a more advanced heuristic.

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
            15 * central_control +  # Higher weight for strategic positions
            1.5 * mobility_score +  # Balance mobility and central control
            5 * near_victory_score  # Strongly favor near-victory conditions
        )
        return total_score


    def __str__(self):
        return "MiniMax_Facile"
