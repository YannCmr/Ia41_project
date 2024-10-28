# Tekko specific GUI adjustments based on Othello's interface

import importlib
import tekko  # Assuming `tekko.py` has Tekko game logic similar to `othello.py`
import tekko_models  # Reusing the GUI components from `tekko_models.py`
import tkinter

# Update GUI constants for Tekko, if any changes required
GAME_HEIGHT = 400
GAME_WIDTH = 400
WAITING_TIME = 500
DEFAULT_ROWS = 5
DEFAULT_COLUMNS = 5


class TekkoGUI:
    def __init__(self, black_name="Human", white_name="Human"):
        # Initial Game Settings
        self._rows = DEFAULT_ROWS
        self._columns = DEFAULT_COLUMNS
        self._black_name = black_name
        self._white_name = white_name
        self._black_ai = None
        self._white_ai = None

        # Initialize TekkoGame with an empty board for Tekko
        self._game_state = tekko.TekkoGame(self._rows, self._columns, tekko.BLACK)

        # Set up GUI elements as in Othello
        self._root_window = tkinter.Tk()
        self._root_window.configure(background=tekko_models.BACKGROUND_COLOR)
        self._black_player = tekko_models.Player(self._black_name, self._root_window)
        self._white_player = tekko_models.Player(self._white_name, self._root_window)
        self._board = tekko_models.GameBoard(
            self._game_state, GAME_WIDTH, GAME_HEIGHT, self._root_window
        )
        self._black_score = tekko_models.Score(
            tekko.BLACK, self._game_state, self._root_window
        )
        self._white_score = tekko_models.Score(
            tekko.WHITE, self._game_state, self._root_window
        )
        self._player_turn = tekko_models.Turn(self._game_state, self._root_window)

        # Bind the game board
        self._board.get_board().bind("<Configure>", self._on_board_resized)
        self._board.get_board().bind("<Button-1>", self._on_board_clicked)

        # Menu setup (same as in Othello)
        self._menu_bar = tkinter.Menu(self._root_window)
        self._game_menu = tkinter.Menu(self._menu_bar, tearoff=0)
        self._game_menu.add_command(label="New Game", command=self._new_game)
        self._game_menu.add_command(
            label="Game Settings", command=self._configure_game_settings
        )
        self._game_menu.add_separator()
        self._game_menu.add_command(label="Exit", command=self._root_window.destroy)
        self._menu_bar.add_cascade(label="Game", menu=self._game_menu)

        # Layout adjustments
        self._root_window.config(menu=self._menu_bar)
        self._black_player.get_player_label().grid(row=0, column=0, sticky=tkinter.S)
        self._white_player.get_player_label().grid(row=0, column=1, sticky=tkinter.S)
        self._black_score.get_score_label().grid(row=1, column=0, sticky=tkinter.S)
        self._white_score.get_score_label().grid(row=1, column=1, sticky=tkinter.S)
        self._board.get_board().grid(
            row=2,
            column=0,
            columnspan=2,
            padx=50,
            pady=10,
            sticky=tkinter.N + tkinter.E + tkinter.S + tkinter.W,
        )
        self._player_turn.get_turn_label().grid(
            row=3, column=0, columnspan=2, padx=10, pady=10
        )

        # Window row/column weight configuration
        self._root_window.rowconfigure(0, weight=1)
        self._root_window.rowconfigure(1, weight=1)
        self._root_window.rowconfigure(2, weight=1)
        self._root_window.columnconfigure(0, weight=1)
        self._root_window.columnconfigure(1, weight=1)
        self.cb_timer_idx = []
        self.update_timer()

    def start(self) -> None:
        """Runs the mainloop of the root window"""
        self._root_window.mainloop()

    def run_auto(self) -> None:
        """Runs the game automatically for testing"""
        print(f"Run_auto: {self._black_name} vs {self._white_name}")
        self._root_window.after(200, self._new_game)
        self.start()

    def _configure_game_settings(self) -> None:
        """Game settings configuration window"""
        dialog = tekko_models.OptionDialog(
            self._rows, self._columns, self._black_name, self._white_name
        )
        dialog.show()
        if dialog.was_ok_clicked():
            self._rows = dialog.get_rows()
            self._columns = dialog.get_columns()
            self._black_name = dialog.get_black_name()
            self._white_name = dialog.get_white_name()
            self._black_ai = None
            self._white_ai = None
            self._new_game()

    def _new_game(self) -> None:
        """Initialize a new game with empty board and free placement"""
        self._game_state = tekko.TekkoGame(self._rows, self._columns, tekko.BLACK)
        self._board.new_game_settings(self._game_state)
        self._board.redraw_board()
        self._player_turn.reset_total_times()
        self._black_player.update_name(self._black_name)
        self._white_player.update_name(self._white_name)
        self._black_score.update_score(self._game_state)
        self._white_score.update_score(self._game_state)

        # Set initial player turn to BLACK and reset any timers
        self._player_turn.update_turn(tekko.BLACK)

        [self._root_window.after_cancel(idx) for idx in self.cb_timer_idx]
        self.cb_timer_idx = []
        self.update_timer()

        if self._white_name != "Human":
            self._white_ai = getattr(
                importlib.import_module(f"ai.{self._white_name}"), f"{self._white_name}"
            )()
        if self._black_name != "Human":
            self._black_ai = getattr(
                importlib.import_module(f"ai.{self._black_name}"), f"{self._black_name}"
            )()
            self._play_ai()

    def update_timer(self):
        self.cb_timer_idx.append(self._root_window.after(500, self.update_timer))
        self._player_turn.update_turn_text()

    def _on_board_clicked(self, event: tkinter.Event) -> None:
        """Handle move on the board for Tekko"""
        move = self._convert_point_coord_to_move(event.x, event.y)
        row, col = move
        if self._game_state.placement_phase:
            self._play(row, col)  # Place phase
        else:
            if self._selected_piece:
                self._move_selected_piece(row, col)  # Move selected piece
            elif self._game_state.get_board()[row][col] == self._game_state.get_turn():
                self._selected_piece = (row, col)  # Select piece for modification


    def _move_selected_piece(self, row, col):
        """Move the selected piece if adjacent and valid"""
        if self._selected_piece:
            old_row, old_col = self._selected_piece
            try:
                self._game_state.move(old_row, old_col, row, col)
                self._board.update_game_state(self._game_state)
                self._board.redraw_board()
                self._player_turn.switch_turn(self._game_state)
                self._selected_piece = None
            except tekko.InvalidMoveException:
                self._selected_piece = None

    def _play(self, row, col):
        try:
            self._game_state.move(row, col)
            self._board.update_game_state(self._game_state)
            self._board.redraw_board()
            self._black_score.update_score(self._game_state)
            self._white_score.update_score(self._game_state)

            if self._game_state.is_game_over():
                self._player_turn.display_winner(self._game_state.return_winner())
                [self._root_window.after_cancel(idx) for idx in self.cb_timer_idx]
                self.cb_timer_idx = []
            else:
                self._player_turn.switch_turn(self._game_state)
                self._root_window.after(WAITING_TIME, self._play_ai)

        except tekko.InvalidMoveException:
            pass
        except tekko.InvalidTypeException:
            pass

    def _convert_point_coord_to_move(self, pointx: int, pointy: int):
        row = int(pointy // self._board.get_cell_height())
        col = int(pointx // self._board.get_cell_width())
        return row, col

    def _on_board_resized(self, event: tkinter.Event) -> None:
        self._board.redraw_board()

    def _play_ai(self):
        if self._game_state.get_turn() == tekko.BLACK and self._black_ai is not None:
            move = self._black_ai.next_move(self._game_state.copy_game())
            self._play(move[0], move[1])
        elif (
            self._game_state.get_turn() == tekko.WHITE and self._white_ai is not None
        ):
            move = self._white_ai.next_move(self._game_state.copy_game())
            self._play(move[0], move[1])

if __name__ == "__main__":
    TekkoGUI().start()
