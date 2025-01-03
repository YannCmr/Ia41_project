from BaseIA import BaseAI


class MinMax(BaseAI):
    def minimax(self, game, depth, is_maximizing):
        if depth == 0 or game.is_game_over():
            return self.evaluate_board(game), None

        best_move = None
        if is_maximizing:
            max_eval = float('-inf')
            for move in self.get_all_possible_moves(game):
                simulated_game = game.copy_game()
                self.apply_move(simulated_game, move)
                eval, _ = self.minimax(simulated_game, depth - 1, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in self.get_all_possible_moves(game):
                simulated_game = game.copy_game()
                self.apply_move(simulated_game, move)
                eval, _ = self.minimax(simulated_game, depth - 1, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
            return min_eval, best_move

    def next_move(self, board):
        _, move = self.minimax(board, self.depth, True)
        return move