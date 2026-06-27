import random
from .uninformed import (
    bfs as bfs_standard,
    dfs as dfs_standard,
    ucs as ucs_standard
)
from .informed import (
    greedy_best_first as greedy_best_first_standard,
    a_star as a_star_standard,
    ida_star as ida_star_standard
)
from .local import (
    hill_climbing as hill_climbing_standard,
    simulated_annealing as simulated_annealing_standard,
    beam_search as beam_search_standard
)
from .blind import (
    dls as dls_standard,
    ids as ids_standard,
    bidirectional_search as bidirectional_search_standard
)
from .csp import (
    simple_backtracking as simple_backtracking_standard,
    backtracking_mrv as backtracking_mrv_standard,
    backtracking_forward_checking as backtracking_forward_checking_standard
)
from .adversarial import (
    minimax_search as minimax_search_standard,
    alphabeta_search as alphabeta_search_standard,
    expectimax_search as expectimax_search_standard
)

# --- Pathfinding Helper Visualizer ---
def make_path_visualizer(algo_func):
    def visualizer(grid, start, goal, *args, **kwargs):
        # Run standard search algorithm
        full_path = algo_func(grid, start, goal, *args, **kwargs)
        
        # Yield initial state
        yield set(), [], start, None, False
        
        if full_path:
            for i in range(len(full_path)):
                path_so_far = full_path[:i+1]
                visited_so_far = set(path_so_far)
                current_node = full_path[i]
                is_last_step = (i == len(full_path) - 1)
                yield visited_so_far, [], current_node, path_so_far, is_last_step
        else:
            yield set(), [], start, None, True
    return visualizer

# --- CSP Helper Visualizer ---
def make_csp_visualizer(csp_func):
    def visualizer(grid, start, goal, *args, **kwargs):
        from .csp import get_reachable_cells
        reachable = get_reachable_cells(grid, start)
        
        # Compute distances for get_unsafe_set
        dist = {}
        for s in reachable:
            dist[s] = {s: 0}
            q = [s]
            while q:
                curr = q.pop(0)
                r, c = curr
                d = dist[s][curr]
                for nr, nc in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
                    if (nr, nc) in reachable:
                        if (nr, nc) not in dist[s]:
                            dist[s][(nr, nc)] = d + 1
                            q.append((nr, nc))

        def get_unsafe_set(placed):
            unsafe = set()
            for c in reachable:
                if dist[c][start] < 5:
                    unsafe.add(c)
            placed_rows = {g[0] for g in placed}
            placed_cols = {g[1] for g in placed}
            for c in reachable:
                if c[0] in placed_rows or c[1] in placed_cols:
                    unsafe.add(c)
                    continue
                for g in placed:
                    if dist[c][g] < 3:
                        unsafe.add(c)
                        break
            return unsafe

        # Run standard CSP solver
        solution = csp_func(grid, start, goal, *args, **kwargs)
        
        # Yield initial state
        yield get_unsafe_set([]), [], start, [], False
        
        if solution:
            # Yield final state with 5 ghosts
            yield get_unsafe_set(solution), [], solution[-1] if solution else start, list(solution), True
        else:
            yield get_unsafe_set([]), [], start, [], True
    return visualizer

# --- Adversarial Helper Visualizer ---
def make_adversarial_visualizer(adversarial_func):
    def visualizer(grid, start, goal, *args, **kwargs):
        from .adversarial import get_reachable_cells, GOAL_CELL
        reachable = get_reachable_cells(grid, start)
        initial_food = frozenset(
            (r, c) for r, c in reachable if grid[r][c] == 1
        )
        
        # Run standard adversarial search to get the path
        best_path = adversarial_func(grid, start, goal, *args, **kwargs)
        
        pacman1_pos = start
        pacman2_pos = GOAL_CELL
        food_set = initial_food
        pacman1_score = 0
        pacman2_score = 0
        path_so_far = [pacman1_pos]
        path_so_far2 = [pacman2_pos]
        
        # Yield initial state
        yield (set(path_so_far) | set(path_so_far2), [pacman2_pos], pacman1_pos, list(path_so_far), False, pacman1_score, pacman2_score)
        
        for idx, move in enumerate(best_path):
            if idx % 2 == 0:
                pacman1_pos = move
                path_so_far.append(pacman1_pos)
                if pacman1_pos in food_set:
                    food_set = food_set - {pacman1_pos}
                    pacman1_score += 1
            else:
                pacman2_pos = move
                path_so_far2.append(pacman2_pos)
                if pacman2_pos in food_set:
                    food_set = food_set - {pacman2_pos}
                    pacman2_score += 1
                    
            is_last = (idx == len(best_path) - 1) or not food_set
            yield (set(path_so_far) | set(path_so_far2), [pacman2_pos], pacman1_pos, list(path_so_far), is_last, pacman1_score, pacman2_score)
            if not food_set:
                break
    return visualizer

# --- Instantiate Visualizers ---
bfs = make_path_visualizer(bfs_standard)
dfs = make_path_visualizer(dfs_standard)
ucs = make_path_visualizer(ucs_standard)

greedy_best_first = make_path_visualizer(greedy_best_first_standard)
a_star = make_path_visualizer(a_star_standard)
ida_star = make_path_visualizer(ida_star_standard)

hill_climbing = make_path_visualizer(hill_climbing_standard)
simulated_annealing = make_path_visualizer(simulated_annealing_standard)
beam_search = make_path_visualizer(beam_search_standard)

dls = make_path_visualizer(dls_standard)
ids = make_path_visualizer(ids_standard)
bidirectional_search = make_path_visualizer(bidirectional_search_standard)

simple_backtracking = make_csp_visualizer(simple_backtracking_standard)
backtracking_mrv = make_csp_visualizer(backtracking_mrv_standard)
backtracking_forward_checking = make_csp_visualizer(backtracking_forward_checking_standard)

minimax_search = make_adversarial_visualizer(minimax_search_standard)
alphabeta_search = make_adversarial_visualizer(alphabeta_search_standard)
expectimax_search = make_adversarial_visualizer(expectimax_search_standard)
