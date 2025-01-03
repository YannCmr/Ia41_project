from abc import ABC, abstractmethod
import teeko 
class BaseAI(ABC):
    def __init__(self, depth=4):
        self.depth = depth

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

    def get_adjacent_cells(self, game, row, col):
        """Returns a list of adjacent cells for movement."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        adjacent_cells = []
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            if game._is_valid_cell(new_row, new_col) and game.get_board()[new_row][new_col] == teeko.NONE:
                adjacent_cells.append((new_row, new_col))
        return adjacent_cells

    @abstractmethod
    def next_move(self, board):
        pass


