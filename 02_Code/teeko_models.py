"""
This file contains the Tkinter classes for the Teeko game. It primarily displays the game state.

    Includes: GameBoard, Player, Turn, and OptionDialog classes.
"""

import os.path
import teeko  # Linking with teeko.py game logic
import tkinter
import glob
import time

# GUI / Tkinter object constants
BACKGROUND_COLOR = '#FFFFFF'
GAME_COLOR =  '#D2B48C' 
PLACE_COLOR = '#8B4513'
FONT = ('Helvetica', 30)
DIALOG_FONT = ('Helvetica', 20)
PLAYERS = {teeko.BLACK: 'Black', teeko.WHITE: 'White'}


class GameBoard:
    def __init__(self, game_state: teeko.TeekoGame, game_width: float, game_height: float, root_window) -> None:
        """ Initialize the game board's settings """
        self._game_state = game_state
        self._rows = self._game_state.get_rows()
        self._cols = self._game_state.get_columns()
        self._board = tkinter.Canvas(master=root_window, width=game_width, height=game_height, background=GAME_COLOR)

    def new_game_settings(self, game_state) -> None:
        """ Update game board settings based on a new game state """
        self._game_state = game_state
        self._rows = self._game_state.get_rows()
        self._cols = self._game_state.get_columns()

    def redraw_board(self) -> None:
        """ Redraws the board """
        self._board.delete(tkinter.ALL)
        self._redraw_grid_with_connections()  # Draw grid with all connections
        self._redraw_cells()

    def _redraw_grid_with_connections(self) -> None:
        """ Draws a grid with dark brown connections (horizontal, vertical, diagonal) """
        cell_width = self.get_cell_width()
        cell_height = self.get_cell_height()
        grid_color = GAME_COLOR

        # Draw lines for connections
        for row in range(self._rows):
            for col in range(self._cols):
                x_center = col * cell_width + cell_width / 2
                y_center = row * cell_height + cell_height / 2

                # Horizontal connections
                if col < self._cols - 1:
                    self._board.create_line(
                        x_center, y_center,
                        x_center + cell_width, y_center,
                        fill=PLACE_COLOR, width=3
                    )
                # Vertical connections
                if row < self._rows - 1:
                    self._board.create_line(
                        x_center, y_center,
                        x_center, y_center + cell_height,
                        fill=PLACE_COLOR, width=3
                    )
                # Diagonal (top-left to bottom-right)
                if row < self._rows - 1 and col < self._cols - 1:
                    self._board.create_line(
                        x_center, y_center,
                        x_center + cell_width, y_center + cell_height,
                        fill=PLACE_COLOR, width=3
                    )
                # Diagonal (top-right to bottom-left)
                if row < self._rows - 1 and col > 0:
                    self._board.create_line(
                        x_center, y_center,
                        x_center - cell_width, y_center + cell_height,
                        fill=PLACE_COLOR, width=3
                    )

                # Draw circle for the grid nodes
                radius = min(cell_width, cell_height) / 6
                self._board.create_oval(
                    x_center - radius, y_center - radius,
                    x_center + radius, y_center + radius,
                    outline="black", width=2, fill=PLACE_COLOR 
                )

    def _redraw_cells(self) -> None:
        """ Draws all placed pieces on the board """
        for row in range(self._rows):
            for col in range(self._cols):
                if self._game_state.get_board()[row][col] != teeko.NONE:
                    self._draw_piece(row, col)

    def _draw_piece(self, row: int, col: int) -> None:
        """ Draws a red or black piece at the specified cell location """
        cell_width = self.get_cell_width()
        cell_height = self.get_cell_height()
        x_center = col * cell_width + cell_width / 2
        y_center = row * cell_height + cell_height / 2
        radius = min(cell_width, cell_height) / 4 # Size of the piece

        color = "black" if self._game_state.get_board()[row][col] == teeko.BLACK else "white"
        self._board.create_oval(
            x_center - radius, y_center - radius,
            x_center + radius, y_center + radius,
            fill=color, outline="black", width=2
        )


    def _redraw_lines(self) -> None:
        """ Draws grid lines for the board """
        row_multiplier = float(self._board.winfo_height()) / self._rows
        col_multiplier = float(self._board.winfo_width()) / self._cols

        for row in range(1, self._rows):
            self._board.create_line(0, row * row_multiplier, self.get_board_width(), row * row_multiplier)
        for col in range(1, self._cols):
            self._board.create_line(col * col_multiplier, 0, col * col_multiplier, self.get_board_height())



    def _draw_cell(self, row: int, col: int) -> None:
        """ Draws a piece at the specified cell location """
        self._board.create_oval(col * self.get_cell_width(),
                                row * self.get_cell_height(),
                                (col + 1) * self.get_cell_width(),
                                (row + 1) * self.get_cell_height(),
                                fill=PLAYERS[self._game_state.get_board()[row][col]])

    def update_game_state(self, game_state: teeko.TeekoGame) -> None:
        """ Updates the game board's state """
        self._game_state = game_state

    def get_cell_width(self) -> float:
        """ Returns a game cell's width """
        return self.get_board_width() / self.get_columns()

    def get_cell_height(self) -> float:
        """ Returns a game cell's height """
        return self.get_board_height() / self.get_rows()

    def get_board_width(self) -> float:
        """ Returns the board canvas's width """
        return float(self._board.winfo_width())

    def get_board_height(self) -> float:
        """ Returns the board canvas's height """
        return float(self._board.winfo_height())

    def get_rows(self) -> int:
        """ Returns the number of rows on the board """
        return self._rows

    def get_columns(self) -> int:
        """ Returns the number of columns on the board """
        return self._cols

    def get_board(self) -> tkinter.Canvas:
        """ Returns the game board """
        return self._board


class Player:
    def __init__(self, name: str, root_window) -> None:
        """ Initializes a player label for display """
        self._name = name
        self._player_label = tkinter.Label(master=root_window, text=self._name, background=BACKGROUND_COLOR,
                                           fg="Black", font=FONT)

    def get_name(self) -> str:
        """ Returns the player's name """
        return self._name

    def get_player_label(self) -> tkinter.Label:
        """ Returns the player's name label """
        return self._player_label

    def update_name(self, name: str) -> None:
        """ Updates the player's displayed name """
        self._name = name
        self._change_player_name_label()

    def _change_player_name_label(self) -> None:
        """ Updates the player label text """
        self._player_label['text'] = self._name


class Turn:
    def __init__(self, game_state: teeko.TeekoGame, root_window) -> None:
        """ Initializes the player's turn label """
        self._player = game_state.get_turn()
        self._timer = time.time()  # Playing time for the current move
        self._total_time_BLACK = 0
        self._total_time_WHITE = 0
        self._turn_label = tkinter.Label(master=root_window,
                                         text=self._turn_text(),
                                         background=BACKGROUND_COLOR,
                                         fg="Black",
                                         font=FONT)

    def display_winner(self, winner: str) -> None:
        """ Displays the game winner """
        if winner is None:
            victory_text = 'Tie game. Nobody wins!'
        else:
            victory_text = PLAYERS[winner] + ' wins!'
            victory_text += f'\n Players Time (B|W): {int(self._total_time_BLACK)}s|{int(self._total_time_WHITE)}s'
        self._turn_label['text'] = victory_text

    def switch_turn(self, game_state: teeko.TeekoGame) -> None:
        """ Switches the turn between players """
        self._player = game_state.get_turn()
        self.update_turn(self._player)

    def update_turn_text(self) -> None:
        """ Update the turn label's text """
        self._update_total_time()
        self._turn_label['text'] = self._turn_text()

    def get_turn_label(self) -> tkinter.Label:
        """ Returns the turn label """
        return self._turn_label

    def update_turn(self, turn: str) -> None:
        """ Updates the turn to the current game state's turn """
        self._player = turn
        self.update_turn_text()
        self._restart_timer()

    def _turn_text(self) -> str:
        """ Returns the turn text """
        time_elapsed = self._total_time_BLACK if self._player == teeko.BLACK else self._total_time_WHITE
        return PLAYERS[self._player] + f"'s turn [{int(time_elapsed)}s]"

    def _opposite_turn(self) -> str:
        """ Returns the opposite turn """
        return {teeko.BLACK: teeko.WHITE, teeko.WHITE: teeko.BLACK}[self._player]

    def _restart_timer(self):
        self._timer = time.time()

    def reset_total_times(self):
        self._timer = time.time()
        self._total_time_BLACK = 0
        self._total_time_WHITE = 0

    def _get_elapsed_time(self) -> float:
        return time.time() - self._timer

    def _update_total_time(self):
        elapsed = self._get_elapsed_time()
        if self._player == teeko.BLACK:
            self._total_time_BLACK += elapsed
        elif self._player == teeko.WHITE:
            self._total_time_WHITE += elapsed
        self._restart_timer()


# OptionDialog for configuring game settings
class OptionDialog:
    def __init__(self, current_rows, current_columns, current_black_name, current_white_name):
        self._dialog_window = tkinter.Toplevel()
        # Searches for modules in the ai folder
        self._player_option_list = ["Human"] + [os.path.basename(path).split(".")[0] for path in glob.glob("ai/*.py")]

        # Game attributes
        self._black = current_black_name
        self._white = current_white_name

        # Row and column settings
        self._setup_options()
        self._ok_clicked = False

    def _setup_options(self):
        """ player options in the dialog """
                # Black player option
        self._setup_player_option("Black", self._black, 0, 0)
        # White player option
        self._setup_player_option("White", self._white, 0, 1)

        # OK and Cancel Buttons
        self._button_frame = tkinter.Frame(master=self._dialog_window)
        self._button_frame.grid(row=2, column=1, sticky=tkinter.E, padx=10, pady=10)
        self._ok_button = tkinter.Button(master=self._button_frame, text='OK', font=DIALOG_FONT, command=self._on_ok)
        self._ok_button.grid(row=0, column=0, padx=10, pady=10)
        self._cancel_button = tkinter.Button(master=self._button_frame, text='Cancel', font=DIALOG_FONT,
                                             command=self._on_cancel)
        self._cancel_button.grid(row=0, column=1, padx=10, pady=10)

    def _setup_player_option(self, color, current_name, row, col):
        """ Helper to set up the player options for a given color """
        frame = tkinter.Frame(master=self._dialog_window)
        label = tkinter.Label(master=frame, text=f'{color} :', font=DIALOG_FONT)
        label.grid(row=0, column=0, sticky=tkinter.E, padx=10, pady=10)
        var = tkinter.StringVar(value=current_name)
        option_menu = tkinter.OptionMenu(frame, var, *self._player_option_list)
        option_menu.grid(row=0, column=1, sticky=tkinter.W, padx=10, pady=10)
        frame.grid(row=row, column=col, sticky=tkinter.W, padx=10, pady=10)
        setattr(self, f"_{color.lower()}", var)

    def show(self) -> None:
        self._dialog_window.grab_set()
        self._dialog_window.wait_window()

    def was_ok_clicked(self) -> bool:
        return self._ok_clicked

    def get_rows(self):
        """Fixed rows value for the board."""
        return 5

    def get_columns(self):
        """Fixed columns value for the board."""
        return 5

    def get_black_name(self):
        return self._black.get()

    def get_white_name(self):
        return self._white.get()

    def _on_ok(self):
        self._ok_clicked = True
        self._dialog_window.destroy()

    def _on_cancel(self):
        self._dialog_window.destroy()
