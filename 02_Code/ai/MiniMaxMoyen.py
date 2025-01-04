import teeko
from ai.baseIA.heuristiques import (
    evaluate_aligned_pieces,
    evaluate_central_control,
    evaluate_corner_penalty,
    evaluate_defensive_threats,
    evaluate_mobility,
    evaluate_near_victory,
)
from ai.baseIA.MinMax import MinMax


class MiniMaxMoyen(MinMax):
    def __init__(self, depth=3):
        self.depth = depth

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
        aligned_score = evaluate_aligned_pieces(game, current_player)

        # Mobility score: reward having more possible moves 
        mobility_score = evaluate_mobility(game, current_player)

        # Cenral control score: reward central positions
        central_control = evaluate_central_control(game, current_player)

        # Combine all heuristics
        total_score = (
            10 * aligned_score +
            8 * central_control +
            5 * mobility_score 
        )

        
        return total_score
    
    def check_winning_placement(self, game, player):
        """
        Checks if the AI can win during the placement phase by completing a winning configuration.
        Args:
            game (teeko.TeekoGame): Current game state.
            player (str): Current player ('B' or 'W').
        Returns:
            tuple: Coordinates (row, col) to place a winning piece, or None if no winning move is possible.
        This function was not chosen for the final version because it significantly slowed down the AI's moves.
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
            any(MiniMaxMoyen.check_line(board, row, player) for row in range(game.get_rows())) or
            any(MiniMaxMoyen.check_column(board, col, player) for col in range(game.get_columns())) or
            MiniMaxMoyen.check_main_diagonal(board, player) or
            MiniMaxMoyen.check_anti_diagonal(board, player) or
            MiniMaxMoyen.check_squares(board, player)
        )


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
            any(MiniMaxMoyen.check_line(board, row, player) for row in range(game.get_rows())) or
            any(MiniMaxMoyen.check_column(board, col, player) for col in range(game.get_columns())) or
            MiniMaxMoyen.check_main_diagonal(board, player) or
            MiniMaxMoyen.check_anti_diagonal(board, player) or
            MiniMaxMoyen.check_squares(board, player)
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
        return "MiniMaxMoyen"
