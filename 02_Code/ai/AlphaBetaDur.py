from ai.baseIA.AlphaBeta import AlphaBeta

import teeko


class AlphaBetaDur(AlphaBeta):
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
        central_control = self.evaluate_central_control(game, current_player)

        # Mobility: reward having more possible moves
        mobility_score = self.evaluate_mobility(game, current_player) - self.evaluate_mobility(game, opponent)

        # Proximity to victory: reward near-winning configurations
        near_victory_score = self.evaluate_near_victory(game, current_player)

        # Combine all heuristics
        total_score = (
            2 * central_control +  # Higher weight for strategic positions
            5.5 * mobility_score +  # Balance mobility and central control
            15 * near_victory_score  # Strongly favor near-victory conditions
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

        # Add square detection
        near_victory_count += self.check_square_winning(game, player)
        return near_victory_count

    def check_square_winning(self, game, player):
        """
        Checks for 2x2 squares of the player's pieces.

        Args:
            game (teeko.TeekoGame): Current game state.
            player (str): Current player ('B' or 'W').

        Returns:
            int: Number of 2x2 square configurations.
        """
        board = game.get_board()
        rows, cols = game.get_rows(), game.get_columns()
        square_count = 0

        for row in range(rows - 1):  # Stop 1 row before the edge
            for col in range(cols - 1):  # Stop 1 column before the edge
                # Check if the 2x2 square is entirely occupied by the player's pieces
                if (board[row][col] == player and
                    board[row][col + 1] == player and
                    board[row + 1][col] == player and
                    board[row + 1][col + 1] == player):
                    square_count += 1

        return square_count

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


