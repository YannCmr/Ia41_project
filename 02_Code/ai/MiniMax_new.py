import math
import teeko
import time

class MiniMax_new:
    def __init__(self, depth=3):
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
        _, move = self.minimax(board, self.depth, True)
        return move

    def minimax(self, game: teeko.TeekoGame, depth, is_maximizing):
        if depth == 0 or game.is_game_over():
            return self.evaluate_board(game), None

        possible_moves = self.get_all_possible_moves(game)
        if not possible_moves:
            return self.evaluate_board(game), None

        if is_maximizing:
            max_eval = float('-inf')
            best_move = None
            for move in possible_moves:
                simulated_game = game.copy_game()
                self.apply_move(simulated_game, move)
                if simulated_game.is_game_over():  # Check for winning move
                    return float('inf'), move
                evaluation, _ = self.minimax(simulated_game, depth - 1, False)
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in possible_moves:
                simulated_game = game.copy_game()
                self.apply_move(simulated_game, move)
                if simulated_game.is_game_over():  # Block opponent's winning move
                    return float('-inf'), move
                evaluation, _ = self.minimax(simulated_game, depth - 1, True)
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = move
            # Prevent AI from "freezing" by choosing the best available move when no blocking is possible
            return min_eval if best_move else self.evaluate_board(game), best_move

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
                    if board[row][col] == teeko.NONE: #and not self.is_corner(row, col, game):
                        possible_moves.append((row, col, None, None))
        else:
            for row in range(game.get_rows()):
                for col in range(game.get_columns()):
                    if board[row][col] == game.get_turn():
                        for new_row, new_col in self.get_adjacent_cells(game, row, col):
                            if board[new_row][new_col] == teeko.NONE:
                                possible_moves.append((row, col, new_row, new_col))
        return possible_moves
    
    def is_corner(self, row, col, game):
        """
        Checks if a position is a corner of the board.
        """
        rows, cols = game.get_rows(), game.get_columns()
        return (row, col) in [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]

    def get_adjacent_cells(self, game: teeko.TeekoGame, row, col):
        """Returns a list of adjacent cells for movement."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        adjacent_cells = []
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            if game._is_valid_cell(new_row, new_col) and game.get_board()[new_row][new_col] == teeko.NONE:
                adjacent_cells.append((new_row, new_col))
        return adjacent_cells

    def apply_move(self, game: teeko.TeekoGame, move):
        """Applies a move to the game state."""
        row, col, new_row, new_col = move
        if new_row is None and new_col is None:
            game.move(row, col)
        else:
            game.move(row, col, new_row, new_col)

    def evaluate_board(self, game: teeko.TeekoGame):
        """
        Simplified board evaluation function with 3-4 heuristics.

        Args:
            game (teeko.TeekoGame): Current game state.

        Returns:
            int: Evaluation score.
        """
        current_player = game.get_turn()
        opponent = teeko.BLACK if current_player == teeko.WHITE else teeko.WHITE

        # Aligned pieces : reward having more aligned pieces
        aligned_score = self.evaluate_aligned_pieces(game, current_player)

        # Mobility score: reward having more possible moves 
        mobility_score = self.evaluate_mobility(game, current_player)

        # Near victory score: Proximity to victory
        #near_victory_score = self.evaluate_near_victory(game, current_player)

        # Cenral control score: reward central positions
        central_control = self.evaluate_central_control(game, current_player)

        # Defensive score : reward mitigating opponent threats
        #defensive_threats_score = self.evaluate_defensive_threats(game, opponent)

        # Winning move: prioritize immediate winning opportunities
        #winning_move = self.check_winning_placement(game, current_player)
        #winning_move_score = 100 if winning_move else 0  # Large weight for immediate victory

        # Penalty corner
        #corner_penalty = self.evaluate_corner_penalty(game, current_player)

        # Combine all heuristics
        total_score = (
            #12 * defensive_threats_score +
            10 * aligned_score +
            8 * central_control +
            5 * mobility_score 
            #50 * corner_penalty
            #10 * near_victory_score 
            # winning_move_score
            
        )

        """
        print(f"central cont = {central_control}")
        print(f"mobility score = {mobility_score}")
        print(f"near victory = {near_victory_score}")
        print(f"total = {total_score}")
        time.sleep(5)

        """
        
        return total_score

    def evaluate_mobility(self, game, player):
        """
        Evaluate the mobility of the player (number of possible moves).

        Args:
            game (teeko.TeekoGame): Current game state.
            player (str): Current player ('B' or 'W').

        Returns:
            int: Mobility score.
        
        Pros: 
            encourages flexible positions with lots of options
            works well with heuristic evaluate_central_control

        Cons:
            does not consider the strategic quality of moves
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

    def evaluate_aligned_pieces(self, game, player):
        """
        Counts the number of aligned pieces for the player, including squares (2x2).
        """
        board = game.get_board()
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Horizontal, vertical, diagonals
        aligned_count = 0

        for row in range(game.get_rows()):
            for col in range(game.get_columns()):
                if board[row][col] == player:
                    # Check strict alignments
                    for dr, dc in directions:
                        line_pieces = 1
                        for i in range(1, 4):
                            r, c = row + dr * i, col + dc * i
                            if 0 <= r < game.get_rows() and 0 <= c < game.get_columns() and board[r][c] == player:
                                line_pieces += 1
                            else:
                                break
                        # Reward based on the length of the alignment
                        if line_pieces >= 2:
                            aligned_count += line_pieces - 1  # Reward 2 = +1, 3 = +2, 4 = +3

                    # Check for square formations
                    if (
                        row + 1 < game.get_rows() and col + 1 < game.get_columns() and
                        board[row][col] == player and
                        board[row + 1][col] == player and
                        board[row][col + 1] == player and
                        board[row + 1][col + 1] == player
                    ):
                        aligned_count += 3  # Reward for square formation
        return aligned_count


    def evaluate_near_victory(self, game, player):
        """
        Evaluates how close the player is to winning.

        Args:
            game (teeko.TeekoGame): Current game state.
            player (str): Current player ('B' or 'W').

        Returns:
            int: Near Victory score.

        Pros: 
            works well with heuristics evaluate_aligned_pieces and evluate_mobility
        
        Cons:
            lets 
        """
        near_victory_count = 0
        for row in range(game.get_rows()):
            for col in range(game.get_columns()):
                if game.get_board()[row][col] == player:
                    near_victory_count += self.check_almost_winning(game, row, col, player)
        return near_victory_count

    def check_almost_winning(self, game, row, col, player):
        """
        Checks if the player is close to winning from a given position.
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
            if line_pieces == 3 and empty_spaces >= 1:
                count += 1
        
        # Check 2x2 squares
        square_offsets = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for dr, dc in [(0, 0), (0, -1), (-1, 0), (-1, -1)]:  # Potential origines of a 2x2 square
            square_pieces = 0
            empty_spaces = 0
            for offset_r, offset_c in square_offsets:
                r, c = row + dr + offset_r, col + dc + offset_c
                if 0 <= r < game.get_rows() and 0 <= c < game.get_columns():
                    if board[r][c] == player:
                        square_pieces += 1
                    elif board[r][c] == teeko.NONE:
                        empty_spaces += 1
            # Near-victory: 3 pieces and 1 empty space in a square
            if square_pieces == 3 and empty_spaces == 1:
                count += 1

        return count
    
    def evaluate_aligned_pieces(self, game: teeko.TeekoGame, player: str):
        """
        Evaluates the number of aligned pieces for the current player, including squares and diagonals.
        The higher the number of aligned pieces, the higher the score.

        Args:
            game (teeko.TeekoGame): The current game state.
            player (str): The current player ('B' or 'W').

        Returns:
            int: Heuristic score based on the number of aligned pieces.

        Pros: 
            good with heuristics evaluate_central_control and evaluate mobility
        
        Cons:
            does not prevent the alignement of the opponent pieces
            When the opponent has 3 pieces aligned but no pieces that allow him to win immediately, 
            the AI ​​will do nothing to prevent the opponent from getting closer to the winning configuration
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Horizontal, Vertical, Diagonals
        board = game.get_board()
        score = 0
        
        # Traverse each cell on the board
        for row in range(game.get_rows()):
            for col in range(game.get_columns()):
                if board[row][col] == player:
                    # Check in each direction
                    for dr, dc in directions:
                        line_pieces = 1  # The current piece is counted
                        
                        # Check alignment in each direction
                        for i in range(1, 4):  # Check up to 3 cells in each direction
                            r, c = row + i * dr, col + i * dc
                            if 0 <= r < game.get_rows() and 0 <= c < game.get_columns() and board[r][c] == player:
                                line_pieces += 1
                            else:
                                break
                        
                        # Add score based on the number of aligned pieces
                        if line_pieces == 2:
                            score += 1  # 2 aligned pieces
                        elif line_pieces == 3:
                            score += 5  # 3 aligned pieces
                        elif line_pieces == 4:
                            score += 10  # 4 aligned pieces (winning condition)

                    # Check for squares (2 pieces on a line + 1 perpendicular piece)
                    for dr, dc in directions[:2]:  # Horizontal and Vertical
                        # Check for squares formed on a line
                        if 0 <= row + dr < game.get_rows() and 0 <= col + dc < game.get_columns():
                            if board[row + dr][col + dc] == player:  # 2 aligned pieces
                                # Check perpendicular (square formation)
                                for perp_dr, perp_dc in directions[2:]:
                                    if 0 <= row + perp_dr < game.get_rows() and 0 <= col + perp_dc < game.get_columns():
                                        if board[row + perp_dr][col + perp_dc] == player:
                                            score += 3  # Square formed
                        # Check squares in the opposite direction
                        if 0 <= row + dr < game.get_rows() and 0 <= col + dc < game.get_columns():
                            if board[row + dr][col + dc] == player:  # 2 aligned pieces
                                # Check perpendicular (square formation)
                                for perp_dr, perp_dc in directions[2:]:
                                    if 0 <= row + perp_dr < game.get_rows() and 0 <= col + perp_dc < game.get_columns():
                                        if board[row + perp_dr][col + perp_dc] == player:
                                            score += 3  # Square formed
        
        return score


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

        # Define the central position for a 5x5 board
        center_row, center_col = rows // 2, cols // 2

        score = 0
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == player:
                    # Calculate Manhattan distance to the center
                    distance_to_center = abs(row - center_row) + abs(col - center_col)
                    # Reward inversely proportional to distance (closer = higher score)
                    score += max(0, (rows + cols) // 2 - distance_to_center)  # Adjust weight
        return score
    
    def evaluate_corner_penalty(self, game, player) -> int:
        """
        Penalizes moves in the corners of the board.
        """
        rows, cols = game.get_rows(), game.get_columns()
        board = game.get_board()

        # Define the four corners
        corners = [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]
        penalty = 0

        for r, c in corners:
            if board[r][c] == player:
                penalty -= 5  

        return penalty

    
    def evaluate_defensive_threats(self, game, opponent):
        """
        Evaluates the opponent's near-victory threats and penalizes them to ensure a defensive response.
        """
        threat_score = 0
        for row in range(game.get_rows()):
            for col in range(game.get_columns()):
                if game.get_board()[row][col] == opponent:
                    threat_score += self.check_almost_winning(game, row, col, opponent)
        return -5 * threat_score  # Negative weight to penalize opponent's advantage.

    def check_winning_placement(self, game, player):
        """
        Checks if the AI can win during the placement phase by completing a winning configuration.
        Args:
            game (teeko.TeekoGame): Current game state.
            player (str): Current player ('B' or 'W').
        Returns:
            tuple: Coordinates (row, col) to place a winning piece, or None if no winning move is possible.
        """
        board = game.get_board()

        for row in range(game.get_rows()):
            for col in range(game.get_columns()):
                if board[row][col] == teeko.NONE:  # Check empty cell
                    board[row][col] = player  # Simulate placement
                    if self.is_winning_position(self, game, player):
                        board[row][col] = teeko.NONE  # Reset the board
                        return row, col
                    board[row][col] = teeko.NONE  # Reset the board
        return None

    
    @staticmethod
    def is_winning_position(self, game, player):
        """
        Checks if a given board position is a winning configuration for the player.

        Args:
            game (teeko.TeekoGame): The current game state.
            player (str): The player's symbol (e.g., 'B' or 'W').

        Returns:
            bool: True if the player has a winning configuration, False otherwise.
        """
        board = game.get_board()  # Get the current board state
        return (
            any(MiniMax_new.check_line(board, row, player) for row in range(game.get_rows())) or
            any(MiniMax_new.check_column(board, col, player) for col in range(game.get_columns())) or
            MiniMax_new.check_main_diagonal(board, player) or
            MiniMax_new.check_anti_diagonal(board, player) or
            MiniMax_new.check_squares(board, player)
        )


    @staticmethod
    def check_line(board, row, player):
        """
        Checks if there are 4 consecutive pieces of the player in the given row.

        Args:
            board (list): The game board as a 2D list.
            row (int): The row index to check.
            player (str): The player's symbol (e.g., 'B' or 'W').

        Returns:
            bool: True if there are 4 consecutive pieces of the player in the row, False otherwise.
        """
        for col in range(len(board[row]) - 3):  # Iterate only up to the last possible starting position
            if all(board[row][col + i] == player for i in range(4)):  # Check 4 consecutive cells
                return True
        return False

    @staticmethod
    def check_column(board, col, player):
        """
        Checks if there are 4 consecutive pieces of the player in the given column.

        Args:
            board (list): The game board as a 2D list.
            col (int): The column index to check.
            player (str): The player's symbol (e.g., 'B' or 'W').

        Returns:
            bool: True if there are 4 consecutive pieces of the player in the column, False otherwise.
        """
        for row in range(len(board) - 3):  # Iterate only up to the last possible starting position
            if all(board[row + i][col] == player for i in range(4)):  # Check 4 consecutive cells
                return True
        return False


    @staticmethod
    def check_main_diagonal(board, player):
        """
        Checks if there are 4 consecutive pieces of the player on any main diagonal.

        Args:
            board (list): The game board as a 2D list.
            player (str): The player's symbol (e.g., 'B' or 'W').

        Returns:
            bool: True if there are 4 consecutive pieces of the player on a main diagonal, False otherwise.
        """
        for row in range(len(board) - 3):  # Iterate over possible starting rows
            for col in range(len(board[row]) - 3):  # Iterate over possible starting columns
                if all(board[row + i][col + i] == player for i in range(4)):  # Check 4 consecutive cells
                    return True
        return False

    @staticmethod
    def check_anti_diagonal(board, player):
        """
        Checks if there are 4 consecutive pieces of the player on any anti-diagonal.

        Args:
            board (list): The game board as a 2D list.
            player (str): The player's symbol (e.g., 'B' or 'W').

        Returns:
            bool: True if there are 4 consecutive pieces of the player on an anti-diagonal, False otherwise.
        """
        for row in range(len(board) - 3):  # Iterate over possible starting rows
            for col in range(3, len(board[row])):  # Iterate over possible starting columns
                if all(board[row + i][col - i] == player for i in range(4)):  # Check 4 consecutive cells
                    return True
        return False

    @staticmethod
    def check_squares(board, player):
        """
        Checks if there is a 2x2 square of the player's pieces on the board.

        Args:
            board (list): The game board as a 2D list.
            player (str): The player's symbol (e.g., 'B' or 'W').

        Returns:
            bool: True if a 2x2 square of the player's pieces exists, False otherwise.
        """
        for row in range(len(board) - 1):  # Iterate over possible starting rows
            for col in range(len(board[row]) - 1):  # Iterate over possible starting columns
                if (
                    board[row][col] == player and
                    board[row + 1][col] == player and
                    board[row][col + 1] == player and
                    board[row + 1][col + 1] == player
                ):
                    return True
        return False


    def __str__(self):
        return "TeekoMinimaxAISimple"
