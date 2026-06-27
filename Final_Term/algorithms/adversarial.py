import random
import sys
from .uninformed import moves
from .csp import get_reachable_cells
from config import GOAL_CELL

sys.setrecursionlimit(20000)

def dist_to_nearest_food(pos, food_set):
    if not food_set:
        return 0
    return min(abs(pos[0] - f[0]) + abs(pos[1] - f[1]) for f in food_set)

def find_blank(board, grid):
    p1, p2, f_set, s1, s2, turn = board
    if turn == 'X':
        return moves(grid, p1)
    else:
        return moves(grid, p2)
        
def check_winner(board):
    p1, p2, f_set, s1, s2, turn = board
    if not f_set:
        if s1 > s2:
            return 'X'
        elif s2 > s1:
            return 'O'
        else:
            return 'Draw'
    return False
    
def utility(board, depth=0):
    p1, p2, f_set, s1, s2, turn = board
    winner = check_winner(board)
    if winner == 'X':
        return 1
    if winner == 'O':
        return -1
    if winner == 'Draw':
        return 0
        
    total = s1 + s2 + len(f_set)
    if total == 0:
        return 0
    score = (s1 - s2) / total
    score -= dist_to_nearest_food(p1, f_set) / 1000.0 if f_set else 0
    score += dist_to_nearest_food(p2, f_set) / 1000.0 if f_set else 0
    return max(-0.99, min(0.99, score))
    
def current_player(board):
    p1, p2, f_set, s1, s2, turn = board
    return turn
    
def result(board, row, col, sign):
    p1, p2, f_set, s1, s2, turn = board
    move = (row, col)
    
    new_f_set = f_set
    new_s1 = s1
    new_s2 = s2
    
    if move in f_set:
        new_f_set = f_set - {move}
        if sign == 'X':
            new_s1 += 1
        else:
            new_s2 += 1
            
    if sign == 'X':
        return (move, p2, new_f_set, new_s1, new_s2, 'O')
    else:
        return (p1, move, new_f_set, new_s1, new_s2, 'X')


def minimax_search(grid, start, goal):
    reachable = get_reachable_cells(grid, start)
    initial_food = frozenset(
        (r, c) for r, c in reachable if grid[r][c] == 1
    )
    
    pacman1_pos = start
    pacman2_pos = GOAL_CELL
    food_set = initial_food
    pacman1_score = 0
    pacman2_score = 0
    
    path_so_far = [pacman1_pos]
    path_so_far2 = [pacman2_pos]
    
    visited_p1 = {pacman1_pos}
    visited_p2 = {pacman2_pos}
    
    def get_best_move(board, depth):
        def search(b, d):
            if d == 0 or len(find_blank(b, grid)) == 0 or check_winner(b) is not False:
                return utility(b), []
                
            turn = current_player(b)
            if turn == 'X':
                value = -float('inf')
                best_path = []
                for move in find_blank(b, grid):
                    child = result(b, move[0], move[1], 'X')
                    score, path = search(child, d - 1)
                    if move in visited_p1: score -= 100
                    if score > value:
                        value = score
                        best_path = [move] + path
                return value, best_path
            else:
                value = float('inf')
                best_path = []
                for move in find_blank(b, grid):
                    child = result(b, move[0], move[1], 'O')
                    score, path = search(child, d - 1)
                    if move in visited_p2: score += 100
                    if score < value:
                        value = score
                        best_path = [move] + path
                return value, best_path

        value, path = search(board, depth)
        return path[0] if path else None

    board = (pacman1_pos, pacman2_pos, food_set, pacman1_score, pacman2_score, 'X')
    best_path = []
    step = 0
    while board[2] and step < 100:
        step += 1
        turn = current_player(board)
        prev_food_count = len(board[2])
        if turn == 'X':
            move = get_best_move(board, depth=10)
            if not move:
                break
            board = result(board, move[0], move[1], 'X')
            best_path.append(move)
            if len(board[2]) < prev_food_count:
                visited_p1.clear()
                visited_p2.clear()
            visited_p1.add(move)
        else:
            move = get_best_move(board, depth=1)
            if not move:
                break
            board = result(board, move[0], move[1], 'O')
            best_path.append(move)
            if len(board[2]) < prev_food_count:
                visited_p1.clear()
                visited_p2.clear()
            visited_p2.add(move)

    print(f"\n--- Minimax Adversarial Search ---")
    p1_path = [best_path[i] for i in range(0, len(best_path), 2)]
    print(f"Final Score -> Pacman 1: {board[3]}, Pacman 2: {board[4]}")
    print(f"Best Path of Pacman 1: {p1_path}")
    return best_path


def alphabeta_search(grid, start, goal):
    reachable = get_reachable_cells(grid, start)
    initial_food = frozenset(
        (r, c) for r, c in reachable if grid[r][c] == 1
    )
    
    pacman1_pos = start
    pacman2_pos = GOAL_CELL
    food_set = initial_food
    pacman1_score = 0
    pacman2_score = 0
    
    path_so_far = [pacman1_pos]
    path_so_far2 = [pacman2_pos]
    
    visited_p1 = {pacman1_pos}
    visited_p2 = {pacman2_pos}
    
    def get_best_move(board, depth):
        def alphabeta(b, alpha, beta, d):
            if d == 0 or len(find_blank(b, grid)) == 0 or check_winner(b) is not False:
                return utility(b), []
                
            turn = current_player(b)
            if turn == 'X':
                value = -float('inf')
                best_path = []
                for move in find_blank(b, grid):
                    child = result(b, move[0], move[1], 'X')
                    score, path = alphabeta(child, alpha, beta, d - 1)
                    if move in visited_p1: score -= 100
                    if score > value:
                        value = score
                        best_path = [move] + path
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break
                return value, best_path
            else:
                value = float('inf')
                best_path = []
                for move in find_blank(b, grid):
                    child = result(b, move[0], move[1], 'O')
                    score, path = alphabeta(child, alpha, beta, d - 1)
                    if move in visited_p2: score += 100
                    if score < value:
                        value = score
                        best_path = [move] + path
                    beta = min(beta, value)
                    if alpha >= beta:
                        break
                return value, best_path

        value, path = alphabeta(board, -float('inf'), float('inf'), depth)
        return path[0] if path else None

    board = (pacman1_pos, pacman2_pos, food_set, pacman1_score, pacman2_score, 'X')
    best_path = []
    step = 0
    while board[2] and step < 100:
        step += 1
        turn = current_player(board)
        prev_food_count = len(board[2])
        if turn == 'X':
            move = get_best_move(board, depth=10)
            if not move:
                break
            board = result(board, move[0], move[1], 'X')
            best_path.append(move)
            if len(board[2]) < prev_food_count:
                visited_p1.clear()
                visited_p2.clear()
            visited_p1.add(move)
        else:
            move = get_best_move(board, depth=1)
            if not move:
                break
            board = result(board, move[0], move[1], 'O')
            best_path.append(move)
            if len(board[2]) < prev_food_count:
                visited_p1.clear()
                visited_p2.clear()
            visited_p2.add(move)

    print(f"\n--- Alpha-Beta Pruning Search ---")
    p1_path = [best_path[i] for i in range(0, len(best_path), 2)]
    print(f"Final Score -> Pacman 1: {board[3]}, Pacman 2: {board[4]}")
    print(f"Best Path of Pacman 1: {p1_path}")
    return best_path


def expectimax_search(grid, start, goal):
    reachable = get_reachable_cells(grid, start)
    initial_food = frozenset(
        (r, c) for r, c in reachable if grid[r][c] == 1
    )
    
    pacman1_pos = start
    pacman2_pos = GOAL_CELL
    food_set = initial_food
    pacman1_score = 0
    pacman2_score = 0
    
    path_so_far = [pacman1_pos]
    path_so_far2 = [pacman2_pos]
    
    visited_p1 = {pacman1_pos}
    visited_p2 = {pacman2_pos}
    
    def get_best_move(board, depth):
        def expectimax(b, d):
            if d == 0 or len(find_blank(b, grid)) == 0 or check_winner(b) is not False:
                return utility(b), []
                
            turn = current_player(b)
            if turn == 'X':
                value = -float('inf')
                best_path = []
                for move in find_blank(b, grid):
                    child = result(b, move[0], move[1], 'X')
                    score, path = expectimax(child, d - 1)
                    if move in visited_p1: score -= 100
                    if score > value:
                        value = score
                        best_path = [move] + path
                return value, best_path
            else:
                blank_position = find_blank(b, grid)
                if not blank_position:
                    return utility(b), []
                value = 0
                rate = 1 / len(blank_position)
                for move in blank_position:
                    child = result(b, move[0], move[1], 'O')
                    score, path = expectimax(child, d - 1)
                    if move in visited_p2: score += 100
                    value += rate * score
                return value, []

        value, path = expectimax(board, depth)
        return path[0] if path else None

    board = (pacman1_pos, pacman2_pos, food_set, pacman1_score, pacman2_score, 'X')
    best_path = []
    step = 0
    while board[2] and step < 100:
        step += 1
        turn = current_player(board)
        prev_food_count = len(board[2])
        if turn == 'X':
            move = get_best_move(board, depth=8)
            if not move:
                break
            board = result(board, move[0], move[1], 'X')
            best_path.append(move)
            if len(board[2]) < prev_food_count:
                visited_p1.clear()
                visited_p2.clear()
            visited_p1.add(move)
        else:
            p2_moves = moves(grid, board[1])
            if not p2_moves:
                break
            move = random.choice(p2_moves)
            board = result(board, move[0], move[1], 'O')
            best_path.append(move)
            if len(board[2]) < prev_food_count:
                visited_p1.clear()
                visited_p2.clear()
            visited_p2.add(move)

    print(f"\n--- Expectimax Search ---")
    p1_path = [best_path[i] for i in range(0, len(best_path), 2)]
    print(f"Final Score -> Pacman 1: {board[3]}, Pacman 2: {board[4]}")
    print(f"Best Path of Pacman 1: {p1_path}")
    return best_path
