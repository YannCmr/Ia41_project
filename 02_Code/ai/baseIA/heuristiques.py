import teeko


def evaluate_central_control(game, player):
    """
    Évalue le contrôle central du joueur sur le plateau.
    """
    rows, cols = game.get_rows(), game.get_columns()
    board = game.get_board()
    score = 0
    for row in range(rows):
        for col in range(cols):
            if board[row][col] == player:
                distance_to_center = abs(row - rows // 2) + abs(col - cols // 2)
                score += max(0, 3 - distance_to_center)
    return score


def evaluate_mobility(game, player):
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
                for new_row, new_col in game.get_adjacent_cells(row, col):
                    if board[new_row][new_col] == teeko.NONE:
                        possible_moves += 1
    return possible_moves


def evaluate_near_victory(game, player):
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
    # Count configurations close to winning
    near_victory_count = 0
    for row in range(game.get_rows()):
        for col in range(game.get_columns()):
            if game.get_board()[row][col] == player:
                # Check rows, columns, and diagonals for near-complete lines
                near_victory_count += check_almost_winning(game, row, col, player)

    return near_victory_count




def evaluate_defense( game: teeko.TeekoGame, player):
    """
    Evaluates the defensive capabilities of the player.

    Args:
        game (teeko.TeekoGame): The current game state.
        player (str): The current player.

    Returns:
        int: Defensive score.
    """
    opponent = teeko.BLACK if player == teeko.WHITE else teeko.WHITE
    defensive_score = 0
    defensive_score += block_near_winning_configurations(game, opponent)
    defensive_score += prevent_opponent_squares(game, player, opponent)
    return defensive_score

def block_near_winning_configurations( game: teeko.TeekoGame, opponent):
    """
    Function to block near-winning configurations for the opponent.

    Args:
        game (teeko.TeekoGame): The current game state.
        opponent (str): The opponent player.

    Returns:
        int: Block score.
    """
    block_score = 0
    board = game.get_board()
    for row in range(game.get_rows()):
        for col in range(game.get_columns()):
            if board[row][col] == opponent:
                block_score += check_blockable_near_winning(game, row, col, opponent)
    return block_score

def check_blockable_near_winning( game, row, col, opponent):
    """
    Function to check for blockable near-winning configurations.

    Args:
        game (teeko.TeekoGame): The current game state.
        row (int): Row index.
        col (int): Column index.
        opponent (str): The opponent player.

    Returns:
        int: Block score.
    """
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    block_potential = 0

    for dr, dc in directions:
        line_pieces = 0
        blockable_spaces = 0

        for i in range(4):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < game.get_rows() and 0 <= c < game.get_columns():
                if game.get_board()[r][c] == opponent:
                    line_pieces += 1
                elif game.get_board()[r][c] == teeko.NONE:
                    blockable_spaces += 1
            else:
                break

        if line_pieces == 3 and blockable_spaces == 1:
            block_potential += 10

    return block_potential

def prevent_opponent_squares( game: teeko.TeekoGame, player, opponent):
    """
    Evaluates the ability to prevent the opponent from forming squares.

    Args:
        game (teeko.TeekoGame): The current game state.
        player (str): The current player.
        opponent (str): The opponent player.

    Returns:
        int: Prevention score.
    """
    prevention_score = 0
    board = game.get_board()
    rows, cols = game.get_rows(), game.get_columns()

    for row in range(rows - 1):
        for col in range(cols - 1):
            opponent_square_potential = detect_potential_square(game, row, col, opponent)
            if opponent_square_potential:
                prevention_score += 15

    return prevention_score

def detect_potential_square( game, row, col, opponent):
    board = game.get_board()
    square_pieces = sum([
        board[row][col] == opponent,
        board[row][col + 1] == opponent,
        board[row + 1][col] == opponent,
        board[row + 1][col + 1] == opponent
    ])
    return square_pieces >= 3

def evaluate_connectivity( game: teeko.TeekoGame, player):
    """
    Evaluates the connectivity of the player's pieces on the board. The connectivity is defined as the number of connected groups of pieces.

    Args:
        game (teeko.TeekoGame): The current game state.
        player (str): The current player.

    Returns:
        int: Connectivity score.
    """
    connectivity_score = 0
    board = game.get_board()
    connectivity_score += count_connected_groups(game, player)
    return connectivity_score

def count_connected_groups( game: teeko.TeekoGame, player):
    """
    Function to count the number of connected groups of pieces for the player.
    """
    board = game.get_board()
    visited = set()
    groups = 0

    def dfs(row, col):
        if (row, col) in visited or board[row][col] != player:
            return 0

        visited.add((row, col))
        group_size = 1

        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1), 
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < game.get_rows() and 
                0 <= new_col < game.get_columns()):
                group_size += dfs(new_row, new_col)

        return group_size

    for row in range(game.get_rows()):
        for col in range(game.get_columns()):
            if board[row][col] == player and (row, col) not in visited:
                group_size = dfs(row, col)
                if group_size > 1:
                    groups += group_size

    return groups



def evaluate_block_opponent( game, opponent):
    """
    Evaluates the ability to block the opponent's potential winning moves.

    Args:
        game (teeko.TeekoGame): The current game state.
        opponent (str): The opponent player.

    Returns:
        int: Blocking score.
    """
    return sum(
        check_line_victory(game, opponent, row, col)
        for row in range(game.get_rows())
        for col in range(game.get_columns())
        if game.get_board()[row][col] == opponent
    ) * -1  # Negative score to penalize opponent's near victories

def check_line_victory( game, player, row, col):
    """
    Checks for near-victory in lines and squares.

    Args:
        game (teeko.TeekoGame): The current game state.
        player (str): The current player.
        row (int): Row index.
        col (int): Column index.

    Returns:
        int: Score for near-victory.
    """
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    count = 0
    for dr, dc in directions:
        line_pieces = 0
        empty_spaces = 0
        for i in range(4):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < game.get_rows() and 0 <= c < game.get_columns():
                if game.get_board()[r][c] == player:
                    line_pieces += 1
                elif game.get_board()[r][c] == teeko.NONE:
                    empty_spaces += 1
            else:
                break
        if line_pieces == 3 and empty_spaces == 1:
            count += 1
    return count



def is_corner( row, col, game):
        """
        Checks if a position is a corner of the board.
        """
        rows, cols = game.get_rows(), game.get_columns()
        return (row, col) in [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]


def check_almost_winning(game, row, col, player):
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

def evaluate_aligned_pieces( game: teeko.TeekoGame, player: str):
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



def evaluate_corner_penalty( game, player) -> int:
    """
    Penalizes moves in the corners of the board.
    Even with a high weight for this penalty, the AI still plays in the corners.
    This heuristic was not chosen for the final version because it does not improve the AI's gameplay.
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


def evaluate_defensive_threats( game, opponent):
    """
    Evaluates the opponent's near-victory threats and penalizes them to ensure a defensive response.
    """
    threat_score = 0
    for row in range(game.get_rows()):
        for col in range(game.get_columns()):
            if game.get_board()[row][col] == opponent:
                threat_score += check_almost_winning(game, row, col, opponent)
    return -5 * threat_score  # Negative weight to penalize opponent's advantage.



