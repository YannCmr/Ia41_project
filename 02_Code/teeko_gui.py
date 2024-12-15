# Teeko specific GUI adjustments based on Othello's interface

import importlib
import teeko  
import teeko_models 
import tkinter
import time

# Update GUI constants for Teeko, if any changes required
GAME_HEIGHT = 400
GAME_WIDTH = 400
WAITING_TIME = 500
DEFAULT_ROWS = 5
DEFAULT_COLUMNS = 5


class TeekoGUI:
    def __init__(self, black_name="Human", white_name="Human"):
        # Initial Game Settings
        self._rows = DEFAULT_ROWS
        self._columns = DEFAULT_COLUMNS
        self._black_name = black_name
        self._white_name = white_name
        self._black_ai = None
        self._white_ai = None

        self._selected_piece = None  # Initialize selected piece tracking

        # Initialize TeekoGame with an empty board for Teeko
        self._game_state = teeko.TeekoGame(self._rows, self._columns, teeko.BLACK)

        # Set up GUI elements
        self._root_window = tkinter.Tk()
        self._root_window.configure(background=teeko_models.BACKGROUND_COLOR)
        self._black_player = teeko_models.Player(self._black_name, self._root_window)
        self._white_player = teeko_models.Player(self._white_name, self._root_window)
        self._board = teeko_models.GameBoard(
            self._game_state, GAME_WIDTH, GAME_HEIGHT, self._root_window
        )

        self._player_turn = teeko_models.Turn(self._game_state, self._root_window)

        # for highlighting moves and the current selected piece
        self._selected_piece = None  # Tracks the currently selected piece
        self._highlighted_moves = []  # Tracks available moves for the selected piece


        # Bind the game board
        self._board.get_board().bind("<Configure>", self._on_board_resized)
        self._board.get_board().bind("<Button-1>", self._on_board_clicked)

        # Menu setup
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

        # For the notification to the user
        self._status_label = tkinter.Label(self._root_window, text="", font=("Helvetica", 12), fg="red")
        self._status_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))


        # Window row/column weight configuration
        self._root_window.rowconfigure(0, weight=1)
        self._root_window.rowconfigure(1, weight=1)
        self._root_window.rowconfigure(2, weight=1)
        self._root_window.columnconfigure(0, weight=1)
        self._root_window.columnconfigure(1, weight=1)
        self.cb_timer_idx = []
        self.update_timer()




    def highlight_piece(self, row, col):
        """Highlight the selected piece with a yellow border."""
        cell_width = self._board.get_cell_width()
        cell_height = self._board.get_cell_height()
        x_center = col * cell_width + cell_width / 2
        y_center = row * cell_height + cell_height / 2
        radius = min(cell_width, cell_height) / 3
        self._board.get_board().create_oval(
            x_center - radius, y_center - radius,
            x_center + radius, y_center + radius,
            outline="yellow", width=4
        )

    def highlight_available_moves(self, moves):
        """Highlight available moves with green circles."""
        cell_width = self._board.get_cell_width()
        cell_height = self._board.get_cell_height()
        for row, col in moves:
            x_center = col * cell_width + cell_width / 2
            y_center = row * cell_height + cell_height / 2
            radius = min(cell_width, cell_height) / 4
            self._board.get_board().create_oval(
                x_center - radius, y_center - radius,
                x_center + radius, y_center + radius,
                fill="lightgreen", outline=""
            )

    def clear_highlights(self):
        """Clear all highlights from the board."""
        self._board.redraw_board()  # Redraws the board to clear previous highlights


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
        dialog = teeko_models.OptionDialog(
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
        self._game_state = teeko.TeekoGame(self._rows, self._columns, teeko.BLACK)
        self._board.new_game_settings(self._game_state)
        self._board.redraw_board()
        self._player_turn.reset_total_times()
        self._black_player.update_name(self._black_name)
        self._white_player.update_name(self._white_name)

        # Set initial player turn to BLACK and reset any timers
        self._player_turn.update_turn(teeko.BLACK)

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
        """Handles board click events for piece selection and highlights moves only in movement phase."""
        row, col = self._convert_point_coord_to_move(event.x, event.y)


        # Clear any existing highlights
        self.clear_highlights()

        # Only allow highlighting if in movement phase (placement phase is over)
        if not self._game_state.placement_phase:
            if self._selected_piece:
                if (row, col) in self._highlighted_moves:
                    # Move to the selected available cell
                    try:
                        self._play(*self._selected_piece, row, col)  # Use _play to handle the move
                    except teeko.InvalidMoveException as e:
                        self.show_message(str(e))
                    self._selected_piece = None  # Clear selection after move
                    return
                else:
                    self.show_message("Invalid move. Please select a valid target cell.")
                    self._selected_piece = None

            # If no piece is selected, check if the cell has the current player's piece
            if self._game_state.get_board()[row][col] == self._game_state.get_turn():
                self._selected_piece = (row, col)

                # Highlight the selected piece
                self.highlight_piece(row, col)

                # Find available moves and highlight them
                self._highlighted_moves = self._find_available_moves(row, col)
                self.highlight_available_moves(self._highlighted_moves)
            else:
                # Clear selected piece if click is invalid
                self.show_message("Invalid selection. Please select your own piece.")
                self._selected_piece = None
        else:
            # If still in placement phase, handle placement instead
            try:
                self._play(row, col)
            except teeko.InvalidMoveException as e:
                self.show_message(str(e))


    def show_message(self, message):
        """Displays a message in the status label and clears it after a delay."""
        self._status_label.config(text=message)
        self._root_window.after(3000, self.clear_message)  # Clear message after 3 seconds


    def clear_message(self):
        """Clears the status label message."""
        self._status_label.config(text="")

    def _find_available_moves(self, row, col):
        """Return a list of available moves (adjacent empty cells) for the selected piece."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # All 8 directions
        available_moves = []
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            if self._game_state._is_valid_cell(new_row, new_col) and self._game_state.get_board()[new_row][new_col] == teeko.NONE:
                available_moves.append((new_row, new_col))
        return available_moves

    def _play(self, row, col, new_row=None, new_col=None):
        """
        Handles the game logic for placing and moving pieces based on the game phase.

        Args:
            row (int): Row of the selected cell.
            col (int): Column of the selected cell.
            new_row (int): Row of the destination cell for movement phase.
            new_col (int): Column of the destination cell for movement phase.

        Raises:
            teeko.InvalidMoveException: If the move is invalid.
        """
        try:
            if new_row is None and new_col is None:
                # Phase of placement
                self._game_state.move(row, col)
            else:
                # Phase of movement
                self._game_state.move(row, col, new_row, new_col)
            


            #  Update the game state and redraw the board
            self._board.update_game_state(self._game_state)
            self._board.redraw_board()

            if self._game_state.is_game_over():
                self._player_turn.display_winner(self._game_state.return_winner())
                [self._root_window.after_cancel(idx) for idx in self.cb_timer_idx]
                self.cb_timer_idx = []
            else:
                self._player_turn.switch_turn(self._game_state)
                self._root_window.after(WAITING_TIME, self._play_ai)

        except teeko.InvalidMoveException as e:
            self.show_message(str(e))
        except teeko.InvalidTypeException as e:
            self.show_message(str(e))

    def _convert_point_coord_to_move(self, pointx: int, pointy: int):
        row = int(pointy // self._board.get_cell_height())
        col = int(pointx // self._board.get_cell_width())
        return row, col

    def _on_board_resized(self, event: tkinter.Event) -> None:
        self._board.redraw_board()

    def _play_ai(self):
        """
        Function to play the AI move based on the current turn.
        """
        current_turn = self._game_state.get_turn()
        ai_start_time = time.time()

        if current_turn == teeko.BLACK and self._black_ai is not None:
            move = self._black_ai.next_move(self._game_state.copy_game())
            ai_elapsed_time = time.time() - ai_start_time 
            self._player_turn.add_time_to_player(teeko.BLACK, ai_elapsed_time)
            self._player_turn.add_time_to_player(teeko.WHITE, -ai_elapsed_time)   #Because of a bug in the timer when the IA is playing, this time is add to the player not the IA
            self._play(move[0], move[1], move[2], move[3])
            self._board.redraw_board() 
        elif current_turn == teeko.WHITE and self._white_ai is not None:
            move = self._white_ai.next_move(self._game_state.copy_game())
            ai_elapsed_time = time.time() - ai_start_time 
            self._player_turn.add_time_to_player(teeko.WHITE, ai_elapsed_time)
            self._player_turn.add_time_to_player(teeko.BLACK, -ai_elapsed_time)#Because of a bug in the timer when the IA is playing, this time is add to the player not the IA
            self._play(move[0], move[1], move[2], move[3])
            self._board.redraw_board()

if __name__ == "__main__":
    TeekoGUI().start()
