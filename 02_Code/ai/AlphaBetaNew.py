import teeko

class AlphaBetaNew:
    def __init__(self, depth=4):
        self.depth = depth

    def next_move(self, game: teeko.TeekoGame):
        """
        Calculates the next move using Alpha-Beta pruning.

        Args:
            game (teeko.TeekoGame): The current game state.

        Returns:
            tuple[int, int, int, int]: The best move as (row, col, new_row, new_col).
        """
        _, best_move = self.alpha_beta(game, self.depth, float('-inf'), float('inf'), True)
        return best_move

    def alpha_beta(self, game, depth, alpha, beta, is_maximizing):
        """
        Implements the Alpha-Beta pruning algorithm.

        Args:
            game (teeko.TeekoGame): The current game state.
            depth (int): The current depth.
            alpha (float): Alpha value for pruning.
            beta (float): Beta value for pruning.
            is_maximizing (bool): True if maximizing player.

        Returns:
            tuple[float, tuple]: Best score and corresponding move.
        """
        if depth == 0 or game.is_game_over():
            return self.evaluate_board(game), None

        best_move = None

        if is_maximizing:
            max_eval = float('-inf')
            for move in self.get_all_moves(game):
                simulated_game = game.copy_game()
                self.apply_move(simulated_game, move)

                eval_score, _ = self.alpha_beta(simulated_game, depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in self.get_all_moves(game):
                simulated_game = game.copy_game()
                self.apply_move(simulated_game, move)

                eval_score, _ = self.alpha_beta(simulated_game, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_all_moves(self, game):
        """
        Generates all possible moves for the current player.

        Args:
            game (teeko.TeekoGame): The current game state.

        Returns:
            list[tuple]: List of all possible moves.
        """
        moves = []
        if game.placement_phase:
            for row in range(game.get_rows()):
                for col in range(game.get_columns()):
                    if game.get_board()[row][col] == teeko.NONE:
                        moves.append((row, col, None, None))
        else:
            for row in range(game.get_rows()):
                for col in range(game.get_columns()):
                    if game.get_board()[row][col] == game.get_turn():
                        for new_row, new_col in self.get_adjacent_cells(game, row, col):
                            if game.get_board()[new_row][new_col] == teeko.NONE:
                                moves.append((row, col, new_row, new_col))
        return moves

    def get_adjacent_cells(self, game, row, col):
        """
        Gets all adjacent cells for the current piece.

        Args:
            game (teeko.TeekoGame): The current game state.
            row (int): Row index.
            col (int): Column index.

        Returns:
            list[tuple]: List of adjacent cell coordinates.
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        adjacent_cells = []
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if game._is_valid_cell(new_row, new_col):
                adjacent_cells.append((new_row, new_col))
        return adjacent_cells

    def apply_move(self, game, move):
        """
        Applies a move to the game state.

        Args:
            game (teeko.TeekoGame): The current game state.
            move (tuple): The move to apply.
        """
        row, col, new_row, new_col = move
        if new_row is None and new_col is None:
            game.move(row, col)
        else:
            game.move(row, col, new_row, new_col)

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

        central_control = self.evaluate_central_control(game, current_player)
        mobility_score = self.evaluate_mobility(game, current_player) - self.evaluate_mobility(game, opponent)
        near_victory_score = self.evaluate_near_victory(game, current_player)

        total_score = (
            3 * central_control +
            5 * mobility_score +
            15 * near_victory_score
        )
        return total_score

    def evaluate_central_control(self, game, player):
        """
        Evaluates the control over the center of the board.

        Args:
            game (teeko.TeekoGame): The current game state.
            player (str): The current player.

        Returns:
            int: Score based on central control.
        """
        rows, cols = game.get_rows(), game.get_columns()
        board = game.get_board()
        score = 0

        for row in range(rows):
            for col in range(cols):
                if board[row][col] == player:
                    distance_to_center = abs(row - rows // 2) + abs(col - cols // 2)
                    score += max(0, 3 - distance_to_center)
        return score

    def evaluate_mobility(self, game, player):
        """
        Evaluates the mobility of the player's pieces.

        Args:
            game (teeko.TeekoGame): The current game state.
            player (str): The current player.

        Returns:
            int: Mobility score.
        """
        moves = 0
        for row in range(game.get_rows()):
            for col in range(game.get_columns()):
                if game.get_board()[row][col] == player:
                    moves += len(self.get_adjacent_cells(game, row, col))
        return moves

    def evaluate_near_victory(self, game, player):
        """
        Evaluates near-victory conditions.

        Args:
            game (teeko.TeekoGame): The current game state.
            player (str): The current player.

        Returns:
            int: Near-victory score.
        """
        return sum(
            self.check_line_victory(game, player, row, col)
            for row in range(game.get_rows())
            for col in range(game.get_columns())
            if game.get_board()[row][col] == player
        )

    def check_line_victory(self, game, player, row, col):
        """
        Checks for near-victory in lines and squares.

        Args:
            game (teeko.TeekoGame): The current game state.
            player (str): The current player.
            row (int): Row index.
            col (int): Column index.

        Returns:
            int: Score for near-victory.
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        count = 0
        for dr, dc in directions:
            line_pieces = 0
            empty_spaces = 0
            for i in range(4):
                r, c = row + i * dr, col + i * dc
                if 0 <= r < game.get_rows() and 0 <= c < game.get_columns():
                    if game.get_board()[r][c] == player:
                        line_pieces += 1
                    elif game.get_board()[r][c] == teeko.NONE:
                        empty_spaces += 1
                else:
                    break
            if line_pieces == 3 and empty_spaces == 1:
                count += 1
        return count
