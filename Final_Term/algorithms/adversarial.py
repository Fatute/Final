import random
import sys
from .uninformed import moves
from .csp import get_reachable_cells
from config import GOAL_CELL

sys.setrecursionlimit(20000)

# --- Board helpers ---

def get_center_score(r, c, rows=7, cols=8):
    center_r = rows / 2.0 - 0.5
    center_c = cols / 2.0 - 0.5
    dist = abs(r - center_r) + abs(c - center_c)
    return max(1, 10 - int(dist))

def find_blank(board, grid):
    p1, p2, f_set, s1, s2, turn = board
    return moves(grid, p1) if turn == 'X' else moves(grid, p2)

def check_winner(board):
    p1, p2, f_set, s1, s2, turn = board
    if not f_set:
        if s1 > s2:   return 'X'
        if s2 > s1:   return 'O'
        return 'Draw'
    return False

def current_player(board):
    return board[5]

def result(board, row, col, sign):
    p1, p2, f_set, s1, s2, turn = board
    move = (row, col)
    score_val = get_center_score(row, col)
    new_f_set = f_set - {move} if move in f_set else f_set
    new_s1 = s1 + (score_val if sign == 'X' and move in f_set else 0)
    new_s2 = s2 + (score_val if sign == 'O' and move in f_set else 0)
    if sign == 'X':
        return (move, p2, new_f_set, new_s1, new_s2, 'O')
    else:
        return (p1, move, new_f_set, new_s1, new_s2, 'X')

def utility(board):
    p1, p2, f_set, s1, s2, turn = board
    return s1 - s2


# --- Search algorithms ---

def minimax(board, grid, d, visited_p1, visited_p2):
    if d == 0 or not find_blank(board, grid) or check_winner(board) is not False:
        return utility(board), []

    turn = current_player(board)
    if turn == 'X':
        value, best_path = -float('inf'), []
        for move in find_blank(board, grid):
            score, path = minimax(result(board, move[0], move[1], 'X'), grid, d - 1, visited_p1, visited_p2)
            if move in visited_p1: score -= 100
            if score > value:
                value, best_path = score, [move] + path
        return value, best_path
    else:
        value, best_path = float('inf'), []
        for move in find_blank(board, grid):
            score, path = minimax(result(board, move[0], move[1], 'O'), grid, d - 1, visited_p1, visited_p2)
            if move in visited_p2: score += 100
            if score < value:
                value, best_path = score, [move] + path
        return value, best_path


def alphabeta(board, grid, alpha, beta, d, visited_p1, visited_p2):
    if d == 0 or not find_blank(board, grid) or check_winner(board) is not False:
        return utility(board), []

    turn = current_player(board)
    if turn == 'X':
        value, best_path = -float('inf'), []
        for move in find_blank(board, grid):
            score, path = alphabeta(result(board, move[0], move[1], 'X'), grid, alpha, beta, d - 1, visited_p1, visited_p2)
            if move in visited_p1: score -= 100
            if score > value:
                value, best_path = score, [move] + path
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value, best_path
    else:
        value, best_path = float('inf'), []
        for move in find_blank(board, grid):
            score, path = alphabeta(result(board, move[0], move[1], 'O'), grid, alpha, beta, d - 1, visited_p1, visited_p2)
            if move in visited_p2: score += 100
            if score < value:
                value, best_path = score, [move] + path
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value, best_path


def expectimax(board, grid, d, visited_p1, visited_p2):
    if d == 0 or not find_blank(board, grid) or check_winner(board) is not False:
        return utility(board), []

    turn = current_player(board)
    if turn == 'X':
        value, best_path = -float('inf'), []
        for move in find_blank(board, grid):
            score, path = expectimax(result(board, move[0], move[1], 'X'), grid, d - 1, visited_p1, visited_p2)
            if move in visited_p1: score -= 100
            if score > value:
                value, best_path = score, [move] + path
        return value, best_path
    else:
        blanks = find_blank(board, grid)
        if not blanks:
            return utility(board), []
        rate = 1 / len(blanks)
        value = sum(
            rate * (expectimax(result(board, m[0], m[1], 'O'), grid, d - 1, visited_p1, visited_p2)[0]
                    + (100 if m in visited_p2 else 0))
            for m in blanks
        )
        return value, []


# --- Shared game loop ---

def _run_game_loop(grid, start, search_fn, label):
    import time
    start_time = time.time()
    
    reachable = get_reachable_cells(grid, start)
    food_set  = frozenset((r, c) for r, c in reachable if grid[r][c] == 1)

    board      = (start, GOAL_CELL, food_set, 0, 0, 'X')
    visited_p1 = {start}
    visited_p2 = {GOAL_CELL}
    best_path  = []
    step       = 0

    while board[2] and step < 100:
        step += 1
        prev_food = len(board[2])
        turn = current_player(board)

        _, path = search_fn(board, grid, visited_p1, visited_p2)
        move = path[0] if path else None
        if not move:
            break

        board = result(board, move[0], move[1], turn)
        best_path.append(move)

        if len(board[2]) < prev_food:
            visited_p1.clear()
            visited_p2.clear()

        if turn == 'X':
            visited_p1.add(move)
        else:
            visited_p2.add(move)

    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\n--- {label} ---")
    p1_path = [best_path[i] for i in range(0, len(best_path), 2)]
    print(f"Execution Time: {execution_time:.4f} seconds")
    print(f"Final Score -> Pacman 1: {board[3]}, Pacman 2: {board[4]}")
    print(f"Best Path of Pacman 1: {p1_path}")
    return best_path, execution_time


# --- Public entry points ---

def minimax_search(grid, start, goal):
    def search_fn(board, grid, vp1, vp2):
        return minimax(board, grid, 3, vp1, vp2)
    return _run_game_loop(grid, start, search_fn, "Minimax Adversarial Search")


def alphabeta_search(grid, start, goal):
    def search_fn(board, grid, vp1, vp2):
        return alphabeta(board, grid, -float('inf'), float('inf'), 3, vp1, vp2)
    return _run_game_loop(grid, start, search_fn, "Alpha-Beta Pruning Search")


def expectimax_search(grid, start, goal):
    def search_fn(board, grid, vp1, vp2):
        turn = current_player(board)
        if turn == 'X':
            return expectimax(board, grid, 3, vp1, vp2)
        else:
            # Ghost moves randomly in Expectimax (by definition of the algorithm)
            p2_moves = moves(grid, board[1])
            if not p2_moves:
                return utility(board), []
            move = random.choice(p2_moves)
            return utility(board), [move]
    return _run_game_loop(grid, start, search_fn, "Expectimax Search")
