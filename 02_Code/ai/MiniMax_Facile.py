import math
import teeko

class MiniMax_Facile:
    def __init__(self, depth=4):
        self.depth = depth

    def next_move(self, board: teeko.TeekoGame) -> tuple[int, int, int, int]:
        """
        Determines the next move for the AI.

        Args:
            board (teeko.TeekoGame): Current game state.

        Returns:
            tuple[int, int, int, int]: The next move (row, col, new_row, new_col) or
                                        (row, col, None, None) for placement phase.
        """
        _, move = self.minimax(board, self.depth, 1)  # 1 for maximizing AI, -1 for opponent
        return move

    def minimax(self, game: teeko.TeekoGame, depth, is_maximizing):
        if depth == 0 or game.is_game_over():
            return self.evaluate_board(game), None

        if is_maximizing:
            max_eval = float('-inf')
            best_move = None
            for move in self.get_all_possible_moves(game):
                simulated_game = game.copy_game()
                self.apply_move(simulated_game, move)
                evaluation, _ = self.minimax(simulated_game, depth - 1, False)
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in self.get_all_possible_moves(game):
                simulated_game = game.copy_game()
                self.apply_move(simulated_game, move)
                evaluation, _ = self.minimax(simulated_game, depth - 1, True)
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = move
            return min_eval, best_move

    def get_all_possible_moves(self, game):
        """
        Generates all possible moves for the current player.

        Args:
            game (teeko.TeekoGame): Current game state.

        Returns:
            list[tuple[int, int, int, int]]: List of moves. Each move is
                                              (row, col, new_row, new_col) or
                                              (row, col, None, None) during placement phase.
        """
        possible_moves = []
        board = game.get_board()
        if game.placement_phase:
            for row in range(game.get_rows()):
                for col in range(game.get_columns()):
                    if board[row][col] == teeko.NONE:
                        possible_moves.append((row, col, None, None))
        else:
            for row in range(game.get_rows()):
                for col in range(game.get_columns()):
                    if board[row][col] == game.get_turn():
                        for new_row, new_col in self.get_adjacent_cells(game, row, col):
                            if board[new_row][new_col] == teeko.NONE:
                                possible_moves.append((row, col, new_row, new_col))
        return possible_moves

    def get_adjacent_cells(self, game:teeko.TeekoGame, row, col):
        """Returns a list of adjacent cells for movement."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        adjacent_cells = []
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            if game._is_valid_cell(new_row, new_col) and game.get_board()[new_row][new_col] == teeko.NONE:
                adjacent_cells.append((new_row, new_col))
        return adjacent_cells

    def apply_move(self, game:teeko.TeekoGame, move):
        """Applies a move to the game state."""
        row, col, new_row, new_col = move
        if new_row is None and new_col is None:
            game.move(row, col)
        else:
            game.move(row, col, new_row, new_col)

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
        central_control = self.evaluate_central_control(game, current_player)

        # Mobility: reward having more possible moves
        mobility_score = self.evaluate_mobility(game, current_player) - self.evaluate_mobility(game, opponent)

        # Proximity to victory: reward near-winning configurations
        near_victory_score = self.evaluate_near_victory(game, current_player)

        # Combine all heuristics
        total_score = (
            15 * central_control +  # Higher weight for strategic positions
            1.5 * mobility_score +  # Balance mobility and central control
            5 * near_victory_score  # Strongly favor near-victory conditions
        )
        return total_score

    def evaluate_central_control(self, game, player):
        """
        Evaluate how well the player controls the central part of the board.

        Args:
            game (teeko.TeekoGame): Current game state.
            player (str): Current player ('B' or 'W').

        Returns:
            int: Central control score.
        """
        rows, cols = game.get_rows(), game.get_columns()
        board = game.get_board()

        score = 0
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == player:
                    # Reward central positions
                    distance_to_center = abs(row - rows // 2) + abs(col - cols // 2)
                    score += max(0, 3 - distance_to_center)  # Closer to the center = higher score
        return score

    def evaluate_mobility(self, game, player):
        """
        Evaluate the mobility of the player (number of possible moves).

        Args:
            game (teeko.TeekoGame): Current game state.
            player (str): Current player ('B' or 'W').

        Returns:
            int: Mobility score.
        """
        possible_moves = 0
        board = game.get_board()
        for row in range(game.get_rows()):
            for col in range(game.get_columns()):
                if board[row][col] == player:
                    # Count all valid moves for this piece
                    for new_row, new_col in self.get_adjacent_cells(game, row, col):
                        if board[new_row][new_col] == teeko.NONE:
                            possible_moves += 1
        return possible_moves

    def evaluate_near_victory(self, game, player):
        """
        Evaluate how close the player is to winning.

        Args:
            game (teeko.TeekoGame): Current game state.
            player (str): Current player ('B' or 'W').

        Returns:
            int: Near-victory score.
        """
        # Count configurations close to winning
        near_victory_count = 0
        for row in range(game.get_rows()):
            for col in range(game.get_columns()):
                if game.get_board()[row][col] == player:
                    # Check rows, columns, and diagonals for near-complete lines
                    near_victory_count += self.check_almost_winning(game, row, col, player)
        return near_victory_count

    def check_almost_winning(self, game, row, col, player):
        """
        Checks if the player is close to winning from a given position.

        Args:
            game (teeko.TeekoGame): Current game state.
            row (int): Row index.
            col (int): Column index.
            player (str): Current player ('B' or 'W').

        Returns:
            int: Number of near-winning configurations.
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Horizontal, vertical, and both diagonals
        board = game.get_board()
        count = 0

        for dr, dc in directions:
            line_pieces = 0
            empty_spaces = 0
            for i in range(4):  # Check 4 cells in each direction
                r, c = row + i * dr, col + i * dc
                if 0 <= r < game.get_rows() and 0 <= c < game.get_columns():
                    if board[r][c] == player:
                        line_pieces += 1
                    elif board[r][c] == teeko.NONE:
                        empty_spaces += 1
                else:
                    break
            # Near-victory: 3 pieces and 1 empty space
            if line_pieces == 3 and empty_spaces == 1:
                count += 1
        return count


    def __str__(self):
        return "TeekoMinimaxAI"
