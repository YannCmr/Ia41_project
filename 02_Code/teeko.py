"""
This file contains the Teeko game logic, modified according to the new game rules.
"""

import copy

# Game Constants
NONE = '.'
BLACK = 'B'
WHITE = 'W'
BOARD_SIZE = 5
MAX_PIECES = 4  # Maximum pieces each player can place

class InvalidMoveException(Exception):
    """ Raised whenever an exception arises from an invalid move """
    pass


class InvalidTypeException(Exception):
    """ Raised whenever an exception arises from an invalid type """
    pass


class TeekoGame:
    """
    Class that creates the Teeko game and manages all game logic.
    """

    def __init__(self, rows=BOARD_SIZE, cols=BOARD_SIZE, turn=BLACK):
        """ Initialize all game settings and creates an empty board. """
        self.rows = rows
        self.cols = cols
        self.turn = turn
        self.current_board = self._new_game_board(rows, cols)
        self.black_pieces = 0
        self.white_pieces = 0
        self.placement_phase = True  # Tracks if we are still placing pieces
        self.winner = None  # Tracks the winner

    def _new_game_board(self, rows, cols):
        """ Creates an empty board for the game. """
        return [[NONE for _ in range(cols)] for _ in range(rows)]

    def move(self, row, col, new_row=None, new_col=None):
        """ Handles placing and moving/modifying pieces based on the game phase. """
        if not self._is_valid_cell(row, col):
            raise InvalidMoveException("Invalid cell selected.")
        
        if self.placement_phase:
            self._place_piece(row, col)
        elif new_row is None and new_col is None:
            self._prepare_piece_for_modification(row, col)
        else:
            self._move_piece(row, col, new_row, new_col)
        
        if self.check_winner():
            self.winner = self.turn
            return True  # Game won
        self.switch_turn()

    def _place_piece(self, row, col):
        """ Places a piece during the placement phase. """
        if self.current_board[row][col] != NONE:
            raise InvalidMoveException("Cell is already occupied.")
        if self.turn == BLACK and self.black_pieces >= MAX_PIECES:
            raise InvalidMoveException("Black has placed all pieces.")
        if self.turn == WHITE and self.white_pieces >= MAX_PIECES:
            raise InvalidMoveException("White has placed all pieces.")
        
        # Place the piece
        self.current_board[row][col] = self.turn
        if self.turn == BLACK:
            self.black_pieces += 1
        else:
            self.white_pieces += 1

        # Transition to modification phase after initial placements
        if self.black_pieces == MAX_PIECES and self.white_pieces == MAX_PIECES:
            self.placement_phase = False

    def _prepare_piece_for_modification(self, row, col):
        """ Sets up a piece for modification after placement phase. """
        if self.current_board[row][col] != self.turn:
            raise InvalidMoveException("You can only modify your own pieces.")
        # No action needed here as GUI handles moving to adjacent cells

    def _move_piece(self, row, col, new_row, new_col):
        """ Moves a piece to an adjacent cell after the placement phase. """
        if not self._is_valid_cell(new_row, new_col):
            raise InvalidMoveException("The destination cell is invalid.")
        if self.current_board[row][col] != self.turn:
            raise InvalidMoveException("You can only move your own pieces.")
        if self.current_board[new_row][new_col] != NONE:
            raise InvalidMoveException("The destination cell is already occupied.")
        if not self._is_adjacent(row, col, new_row, new_col):
            raise InvalidMoveException("The destination cell is not adjacent.")

        # Do the movement
        self.current_board[row][col] = NONE
        self.current_board[new_row][new_col] = self.turn

        # Check immediately for a winner
        if self.check_winner():
            self.winner = self.turn  # Define the winner
            return True  # Return True to indicate a win

        return False  # Return False to indicate no win



    def _is_adjacent(self, row, col, new_row, new_col):
        """Checks if the new cell is adjacent (horizontally, vertically, or diagonally) to the original cell."""
        return max(abs(row - new_row), abs(col - new_col)) == 1

    def check_winner(self):
        """ Checks for a winning configuration on the board. """
        return self._check_line_win() or self._check_square_win()

    def _check_line_win(self):
        """ Checks for 4 pieces in a row horizontally, vertically, or diagonally. """
        for row in range(self.rows):
            for col in range(self.cols):
                if self.current_board[row][col] == self.turn:
                    if (
                        self._check_direction(row, col, 1, 0) or  # Horizontal
                        self._check_direction(row, col, 0, 1) or  # Vertical
                        self._check_direction(row, col, 1, 1) or  # Diagonal /
                        self._check_direction(row, col, 1, -1)    # Diagonal \
                    ):
                        return True
        return False

    def _check_direction(self, row, col, row_delta, col_delta):
        """ Checks if there are 4 consecutive pieces in a specified direction. """
        count = 0
        for i in range(4):
            r, c = row + i * row_delta, col + i * col_delta
            if 0 <= r < self.rows and 0 <= c < self.cols and self.current_board[r][c] == self.turn:
                count += 1
            else:
                break
        return count == 4

    def _check_square_win(self):
        """ Checks for a 2x2 square of the current player's pieces. """
        for row in range(self.rows - 1):
            for col in range(self.cols - 1):
                if (
                    self.current_board[row][col] == self.turn and
                    self.current_board[row][col + 1] == self.turn and
                    self.current_board[row + 1][col] == self.turn and
                    self.current_board[row + 1][col + 1] == self.turn
                ):
                    return True
        return False

    def return_winner(self):
        """ Returns the winner if there is one; otherwise, None. """
        return self.winner

    def switch_turn(self):
        """ Switches the turn between BLACK and WHITE. """
        self.turn = WHITE if self.turn == BLACK else BLACK

    def is_game_over(self):
        """ Determines if the game is over (a player has won). """
        return self.check_winner()

    def get_board(self):
        """ Returns the current game board. """
        return self.current_board

    def get_rows(self):
        """ Returns the number of rows in the game board. """
        return self.rows

    def get_columns(self):
        """ Returns the number of columns in the game board. """
        return self.cols

    def get_turn(self):
        """ Returns the current player's turn. """
        return self.turn

    def _is_valid_cell(self, row, col):
        """ Checks if a cell position is within the board's boundaries. """
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def get_scores(self, player):
        """Calculates the score for the specified player."""
        return sum(row.count(player) for row in self.current_board)
    

    def copy_game(self):
        """Creates a deep copy of the current game state."""
        new_game = TeekoGame(self.rows, self.cols, self.turn)
        new_game.current_board = [row[:] for row in self.current_board]
        new_game.black_pieces = self.black_pieces
        new_game.white_pieces = self.white_pieces
        new_game.placement_phase = self.placement_phase
        new_game.winner = self.winner
        return new_game
