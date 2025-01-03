import teeko
from ai.baseIA.AlphaBeta import AlphaBeta
from ai.baseIA.heuristiques import (
    evaluate_central_control,
    evaluate_connectivity,
    evaluate_defense,
    evaluate_mobility,
    evaluate_near_victory,
)


class AlphaBetaAI(AlphaBeta):
    def __init__(self, depth=4):
        self.depth = depth

    def evaluate_board(self, game: teeko.TeekoGame):
        current_player = game.get_turn()
        opponent = teeko.BLACK if current_player == teeko.WHITE else teeko.WHITE

        base_score = 0#game.get_scores(current_player) - game.get_scores(opponent)
        central_control = evaluate_central_control(game, current_player)
        mobility_score = evaluate_mobility(game, current_player) - evaluate_mobility(game, opponent)
        near_victory_score = evaluate_near_victory(game, current_player)
        defense_score = evaluate_defense(game, current_player)
        connectivity_score = evaluate_connectivity(game, current_player)

        total_score = (
            1.0 * base_score +
            2.5 * central_control +
            6.0 * mobility_score +
            17.0 * near_victory_score +
            11.0 * defense_score +
            4.0 * connectivity_score
        )
        return total_score

    def __str__(self):
        return "AlphaBetaAI"