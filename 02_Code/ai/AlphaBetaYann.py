import tekko
import functools


class AlphaBetaYann:
    def __init__(self, depth=5):
        """
        Initialize the AlphaBeta AI with a specified search depth.

        Args:
            depth (int): How deep the AI will search in the game tree.
        """
        self.depth = depth
        self.corners = [(0, 0), (0, 8), (6, 0), (6, 8)]
        self.directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
        self.cache = {}  # Cache in order to speed up the evaluation

    def next_move(self, board: othello.OthelloGame) -> tuple[int, int]:
        """
        Determine the AI's next move using the AlphaBeta pruning algorithm.

        Args:
            board (othello.OthelloGame): The current game state.

        Returns:
            tuple[int, int]: The coordinates (row, col) of the best move.
        """
        possible_moves = board.get_possible_move()
        sorted_moves = self.sort_moves(board, possible_moves)
        _, move = self.alphabeta(
            board, self.depth, float("-inf"), float("inf"), 1, tuple(sorted_moves)
        )
        return move

    @functools.lru_cache(maxsize=None)
    def alphabeta(
        self,
        board: othello.OthelloGame,
        depth: int,
        alpha: float,
        beta: float,
        min_or_max: int,
        moves: tuple[tuple[int, int]],
    ):
        """
        The AlphaBeta pruning algorithm to find the best move.

        Args:
            board (othello.OthelloGame): The current game state.
            depth (int): The current depth in the game tree.
            alpha (float): The current alpha value for pruning.
            beta (float): The current beta value for pruning.
            min_or_max (int): 1 if the current player is maximizing, -1 if the current player is minimizing.
            moves (tuple[tuple[int, int]]): The current possible moves.

        Returns:
            tuple[float, tuple[int, int] | None]: A tuple containing the evaluation score and the best move coordinates.
        """
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board), None

        optimal_value = min_or_max * -float("inf")
        optimal_move = None

        for move in moves:
            new_board = board.copy_game()
            new_board.move(*move)
            next_moves = new_board.get_possible_move()
            next_sorted_moves = self.sort_moves(new_board, next_moves)
            eval, _ = self.alphabeta(
                new_board, depth - 1, alpha, beta, -min_or_max, tuple(next_sorted_moves)
            )

            if eval * min_or_max > optimal_value * min_or_max:
                optimal_value, optimal_move = eval, move

            if min_or_max == 1:
                alpha = max(alpha, optimal_value)
            else:
                beta = min(beta, optimal_value)

            if beta <= alpha:
                break

        return optimal_value, optimal_move

    def __str__(self):
        """
        Return the name of the AI.

        Returns:
            str: The name of the AI.
        """
        return "AlphaBetaYann"

    def evaluate_board(self, board: othello.OthelloGame) -> float:
        """
        Evaluate the board to get a score based on the current game state.

        Args:
            board (othello.OthelloGame): The current game state.

        Returns:
            float: The evaluated score of the board.
        """
        # use for optimisation of the evaluation
        # check if there is already a value in the cache
        # if yes, return the value
        # else, calculate the value and store it in the cache
        board_state_key = str(board.get_board())
        if board_state_key in self.cache:
            return self.cache[board_state_key]

        # instantiate the value of the different parameters
        corner_value, dangerous_moves_value = 250, -100
        mobility_value, stable_value = 2, 2

        my_color = "B" if board.get_turn() == "W" else "W"
        black_score, white_score = board.get_scores()
        black_corners, white_corners = 0, 0
        black_mobility, white_mobility = 0, 0
        black_stable, white_stable = 0, 0
        black_dangerous_moves, white_dangerous_moves = 0, 0

        # corner evaluation
        for corner in self.corners:
            corner_color = board.get_board()[corner[0]][corner[1]]
            if corner_color == "B":
                black_corners += corner_value
            elif corner_color == "W":
                white_corners += corner_value

        # mobility evaluation
        current_moves = len(board.get_possible_move())
        board.switch_turn()
        next_moves = len(board.get_possible_move())
        board.switch_turn()

        if my_color == "B":
            black_mobility = current_moves
            white_mobility = next_moves
        else:
            white_mobility = current_moves
            black_mobility = next_moves

        # dangerous moves evaluation and stable evaluation
        for row in range(board.get_rows()):
            for col in range(board.get_columns()):
                if self.is_dangerous_move(board, (row, col)):
                    if board.get_board()[row][col] == my_color:
                        if my_color == "B":
                            black_dangerous_moves += dangerous_moves_value
                        else:
                            white_dangerous_moves += dangerous_moves_value
                if self.is_stable(board, row, col):
                    if board.get_board()[row][col] == "B":
                        black_stable += stable_value
                    elif board.get_board()[row][col] == "W":
                        white_stable += stable_value

        # Final evaluation
        black_score += (
            black_corners
            + black_mobility * mobility_value
            + black_stable * stable_value
            + black_dangerous_moves
        )
        white_score += (
            white_corners
            + white_mobility * mobility_value
            + white_stable * stable_value
            + white_dangerous_moves
        )

        return (
            black_score - white_score if my_color == "B" else white_score - black_score
        )

    def get_all_possible_moves(
        self, board: othello.OthelloGame
    ) -> list[tuple[int, int]]:
        """
        Get all possible moves for the current player.

        Args:
            board (othello.OthelloGame): The current game state.

        Returns:
            List[Tuple[int, int]]: A list of all possible move coordinates.
        """
        return board.get_possible_move()

    def is_stable(self, board: othello.OthelloGame, row: int, col: int) -> bool:
        """
        Determine if a pawn is stable, i.e., it cannot be flipped.

        Args:
            board (othello.OthelloGame): The current game state.
            row (int): The row of the pawn.
            col (int): The column of the pawn.

        Returns:
            bool: True if the pawn is stable, False otherwise.
        """
        cell_color = board.get_board()[row][col]

        # for some optimization, we check some specific cases before checking all the directions
        # gain some time
        if cell_color in self.corners:
            return True

        if cell_color == othello.NONE:
            return False

        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]

        for d_row, d_col in directions:
            if not self.check_direction_stable(
                board, row, col, d_row, d_col, cell_color
            ):
                return False
        return True

    def check_direction_stable(
        self,
        board: othello.OthelloGame,
        row: int,
        col: int,
        d_row: int,
        d_col: int,
        color: str,
    ) -> bool:
        """
        Check if a pawn is stable in a specific direction.

        Args:
            board (othello.OthelloGame): The current game state.
            row (int): The row of the pawn.
            col (int): The column of the pawn.
            d_row (int): The direction in the row.
            d_col (int): The direction in the column.
            color (str): The color of the pawn.

        Returns:
            bool: True if the pawn is stable in the direction, False otherwise.
        """
        while 0 <= row < board.get_rows() and 0 <= col < board.get_columns():
            if board.get_board()[row][col] != color:
                return False
            row += d_row
            col += d_col
        return True

    def get_corners(self, board: othello.OthelloGame):
        """
        Get all corners value.

        Args:
            board (othello.OthelloGame): The current game state.

        Returns:
            List[int]: A list of coordinates for all corners.

        """
        return [
            (0, 0),
            (0, board.get_columns() - 1),
            (board.get_rows() - 1, 0),
            (board.get_rows() - 1, board.get_columns() - 1),
        ]

    def sort_moves(
        self, board: othello.OthelloGame, moves: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        """
        Sort the moves in order to optimize the evaluation.

        Args:
            board (othello.OthelloGame): The current game state.
            moves (list[tuple[int, int]]): A list of all possible moves.

        Returns:
            List[Tuple[int, int]]: A list of all possible moves sorted.
        """
        corners = self.get_corners(board)
        corner_moves = [move for move in moves if move in corners]
        dangerous_moves = self.get_dangerous_moves(board, moves)
        other_moves = [
            move
            for move in moves
            if move not in corners and move not in dangerous_moves
        ]
        return corner_moves + other_moves + dangerous_moves

    def get_dangerous_moves(
        self, board: othello.OthelloGame, moves: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        """
        Get all dangerous moves. A dangerous move is a move that is next to an empty corner.

        Args:
            board (othello.OthelloGame): The current game state.
            moves (list[tuple[int, int]]): A list of all possible moves.

        Returns:
            List[Tuple[int, int]]: A list of all dangerous moves.
        """
        dangerous_moves = []
        possible_moves = self.get_all_possible_moves(board)
        for move in moves:
            if move in possible_moves and self.is_dangerous_move(board, move):
                dangerous_moves.append(move)
        return dangerous_moves

    def is_dangerous_move(
        self, board: othello.OthelloGame, move: tuple[int, int]
    ) -> bool:
        """
        Determine if a move is dangerous, i.e., it is next to an empty corner.

        Args:
            board (othello.OthelloGame): The current game state.
            move (tuple[int, int]): The move to check.

        Returns:
            bool: True if the move is dangerous, False otherwise.
        """
        row, col = move
        for d_row in [-1, 0, 1]:
            for d_col in [-1, 0, 1]:
                if d_row == 0 and d_col == 0:
                    continue
                adj_row, adj_col = row + d_row, col + d_col
                if (adj_row, adj_col) in self.get_corners(board) and board.get_board()[
                    adj_row
                ][adj_col] == othello.NONE:
                    return True
        return False
