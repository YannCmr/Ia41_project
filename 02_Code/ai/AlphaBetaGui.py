import math 
import tekko 

class AlphaBetaGui:
    def __init__(self, depth=8):
        self.depth = depth 
        
    def next_move(self, board: tekko.TekkoGame) -> tuple [int, int, int, int]:
        _, move = self.alpha_beta(board, self.depth, float('-inf'), float('inf'), True)
        return move
    
    def alpha_beta(self, game: tekko.TekkoGame, depth: int, alpha: float, beta: float, is_maximizing: bool ):
        if depth == 0 or game.is_game_over(): 
            return self.evaluate_board(game), None
        
        best_move = None
    
    
        if is_maximizing: 
            max_eval = float('-inf')
            for move in self.get_all_possible_moves(game):
                simulated_game = game.copy_game()
                self.apply_move(simulated_game, move)
                
                eval, _ = self.alpha_beta(simulated_game, depth-1, alpha, beta, False)
                if eval > max_eval: 
                    max_eval = eval
                    best_move = move
                    
                alpha = max(alpha, eval)
                if beta <= alpha: 
                    break
            return max_eval, best_move
        else: 
            min_eval = float('inf')
            for move in self.get_all_possible_moves(game):
                simulated_game = game.copy_game()
                self.apply_move(simulated_game, move)
                
                eval, _ = self.alpha_beta(simulated_game, depth-1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move
        
    def get_all_possible_moves(self, game):
        possible_moves = []
        board = game.get_board()
        if game.placement_phase:
            for row in range(game.get_rows()):
                for col in range(game.get_columns()):
                    if board[row][col] == tekko.NONE: 
                        possible_moves.append((row, col, None, None))
        else:
            for row in range(game.get_rows()):
                for col in range(game.get_columns()):
                    if board[row][col] == game.get_turn():
                        for new_row, new_col in self.get_adjacent_cells(game, row, col):
                            if board[new_row][new_col] == tekko.NONE :
                                possible_moves.append((row, col, new_row, new_col))
        return possible_moves
    
    def get_adjacent_cells(self, game: tekko.TekkoGame, row, col):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]    
        adjacent_cells = []
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol 
            if game._is_valid_cell(new_row, new_col) and game.get_board()[new_row][new_col] == tekko.NONE:
                adjacent_cells.append((new_row, new_col))
        return adjacent_cells
    
    def apply_move(self, game: tekko.TekkoGame, move):
        row, col, new_row, new_col = move
        if new_row is None and new_col is None:
            game.move(row, col)
        else:
            game.move(row, col, new_row, new_col)
            
    def evaluate_board(self, game: tekko.TekkoGame):
        current_player = game.get_turn()
        opponent = tekko.BLACK if current_player == tekko.WHITE else tekko.WHITE
        
        # Base score: difference in the number of pieces
        base_score = game.get_scores(current_player) - game.get_scores(opponent)

        # Control the board: reward central positions
        central_control = self.evaluate_central_control(game, current_player)

        # Mobility: reward having more possible moves
        mobility_score = self.evaluate_mobility(game, current_player) - self.evaluate_mobility(game, opponent)

        # Proximity to victory: reward near-winning configurations
        near_victory_score = self.evaluate_near_victory(game, current_player)
        
        # Check the defensives moves
        defense_score = self.evaluate_defense(game, current_player)
        
        # Check the connectivity
        connectivity_score = self.evaluate_connectivity(game, current_player)
        
        # Combine all heuristics
        total_score = (
            #base_score +
            #2 * central_control +  # Higher weight for strategic positions
            #5.5 * mobility_score +  # Balance mobility and central control
            #15 * near_victory_score  # Strongly favor near-victory conditions
            #10 * defense_score +  # Wheigt for defensie
            #3 * connectivity_score  # Wheigt for connectivity
            
            1.0 * base_score +
            2.5 * central_control +
            6.0 * mobility_score +
            17.0 * near_victory_score +
            11.0 * defense_score +
            4.0 * connectivity_score
        )
        return total_score
    
    def evaluate_central_control(self, game, player):
        rows, cols = game.get_rows(), game.get_columns()
        board = game.get_board()
        
        score = 0
        
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == player:
                    distance_to_center = abs(row - rows // 2) + abs(col - cols // 2)
                    score += max(0, 3 - distance_to_center)
        return score  
    
    def evaluate_mobility(self, game, player):
        possible_moves = 0
        board = game.get_board()
        for row in range(game.get_rows()):
            for col in range(game.get_columns()):
                if board[row][col] == player:
                    for new_row, new_col in self.get_adjacent_cells(game, row, col):
                        possible_moves += 1
        return possible_moves
    
    def evaluate_near_victory(self, game, player):
        near_victory_count = 0
        for row in range(game.get_rows()):
            for col in range(game.get_columns()):
                if game.get_board()[row][col]==player:
                    near_victory_count += self.check_almost_winning(game, row, col, player)
                    
        near_victory_count += self.check_square_winning(game, player)
        return near_victory_count
    
    def check_square_winning(self, game, player):
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
                    elif board[r][c] == tekko.NONE:
                        empty_spaces += 1
                else:
                    break
            # Near-victory: 3 pieces and 1 empty space
            if line_pieces == 3 and empty_spaces == 1:
                count += 1
        return count
    
    def evaluate_defense(self, game: tekko.TekkoGame, player):
        opponent = tekko.BLACK if player == tekko.WHITE else tekko.WHITE
        defensive_score = 0

        # Bloquage des configurations gagnantes de l'adversaire
        defensive_score += self.block_near_winning_configurations(game, opponent)

        # Protection contre les carrés gagnants potentiels
        defensive_score += self.prevent_opponent_squares(game, player, opponent)

        return defensive_score
    
        
    def block_near_winning_configurations(self, game: tekko.TekkoGame, opponent):
        block_score = 0
        board = game.get_board()
        
        # Détection des lignes presque gagnantes de l'adversaire
        for row in range(game.get_rows()):
            for col in range(game.get_columns()):
                if board[row][col] == opponent:
                    # Vérifie et pénalise les lignes presque gagnantes de l'adversaire
                    block_score += self.check_blockable_near_winning(game, row, col, opponent)
        
        return block_score

    def check_blockable_near_winning(self, game, row, col, opponent):
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
                    elif game.get_board()[r][c] == tekko.NONE:
                        blockable_spaces += 1
                else:
                    break
            
            # Score élevé si l'adversaire a 3 pièces avec un espace bloquable
            if line_pieces == 3 and blockable_spaces == 1:
                block_potential += 10
        
        return block_potential

    def prevent_opponent_squares(self, game: tekko.TekkoGame, player, opponent):
        prevention_score = 0
        board = game.get_board()
        rows, cols = game.get_rows(), game.get_columns()

        for row in range(rows - 1):
            for col in range(cols - 1):
                # Détecte un carré potentiel de l'adversaire
                opponent_square_potential = self.detect_potential_square(game, row, col, opponent)
                
                # Bonus pour bloquer les carrés potentiels de l'adversaire
                if opponent_square_potential:
                    prevention_score += 15
        
        return prevention_score

    def detect_potential_square(self, game, row, col, opponent):
        board = game.get_board()
        
        # Compte les pièces de l'adversaire dans le carré potentiel
        square_pieces = sum([
            board[row][col] == opponent,
            board[row][col + 1] == opponent,
            board[row + 1][col] == opponent,
            board[row + 1][col + 1] == opponent
        ])
        
        # Retourne True si 3 des 4 cases sont occupées par l'adversaire
        return square_pieces >= 3

    def evaluate_connectivity(self, game: tekko.TekkoGame, player):
        connectivity_score = 0
        board = game.get_board()
        
        # Bonus pour les groupes de pièces connectées
        connectivity_score += self.count_connected_groups(game, player)
        
        return connectivity_score

    def count_connected_groups(self, game: tekko.TekkoGame, player):
        board = game.get_board()
        visited = set()
        groups = 0

        def dfs(row, col):
            if (row, col) in visited or board[row][col] != player:
                return 0
            
            visited.add((row, col))
            group_size = 1
            
            # Directions de vérification (8 directions)
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
