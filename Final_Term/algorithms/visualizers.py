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
    sensorless_bfs as sensorless_bfs_standard,
    partial_bfs as partial_bfs_standard,
    and_or_search as and_or_search_standard,
    bidirectional_search as bidirectional_search_standard
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
            all_food = {(r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] == 1}
            for i in range(len(full_path)):
                path_so_far = full_path[:i+1]
                visited_so_far = set(path_so_far)
                current_node = full_path[i]
                is_found = all_food.issubset(visited_so_far)
                yield visited_so_far, [], current_node, path_so_far, is_found
                
                if is_found:
                    break
        else:
            yield set(), [], start, None, False
    return visualizer

# --- Weight-Constrained Path CSP Visualizer ---
def make_weight_csp_visualizer(csp_func):
    def visualizer(grid, start, goal, *args, **kwargs):
        # We need max_score, get it from config if not passed
        import config
        max_score = config.MAX_SCORE
        
        solution, steps = csp_func(grid, start, goal, max_score, *args, **kwargs)

        # Initial state
        yield set(), [], start, [], False, 'init'

        yielded_any = False
        for step in steps:
            stype = step[0]
            if stype == 'try':
                _, current, path, score, domain = step
                yield set(path), domain, current, path, False, stype
                yielded_any = True
            elif stype == 'backtrack':
                _, current, path, score, domain = step
                yield set(path), domain, current, path, False, stype
                yielded_any = True
            elif stype == 'found':
                _, path = step
                yield set(path), [], path[-1], path, True, stype
                yielded_any = True

        if not solution:
            yield set(), [], start, [], True, 'not_found'

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
        best_path, exec_time = adversarial_func(grid, start, goal, *args, **kwargs)
        
        pacman1_pos = start
        pacman2_pos = GOAL_CELL
        food_set = initial_food
        pacman1_score = 0
        pacman2_score = 0
        path_so_far = [pacman1_pos]
        path_so_far2 = [pacman2_pos]
        
        # Yield initial state
        yield (set(path_so_far) | set(path_so_far2), [pacman2_pos], pacman1_pos, list(path_so_far), False, pacman1_score, pacman2_score, exec_time)
        
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
            yield (set(path_so_far) | set(path_so_far2), [pacman2_pos], pacman1_pos, list(path_so_far), is_last, pacman1_score, pacman2_score, exec_time)
            if not food_set:
                break
    return visualizer

# --- Sensorless Helper Visualizer ---
def make_sensorless_visualizer(algo_func):
    def visualizer(grid_1, grid_2, start_1, start_2, goal, *args, **kwargs):
        actions = algo_func(grid_1, grid_2, start_1, start_2, goal, *args, **kwargs)
        
        def apply_action(r, c, m, action):
            nr, nc = r, c
            if action == 'U': nr -= 1
            elif action == 'D': nr += 1
            elif action == 'L': nc -= 1
            elif action == 'R': nc += 1
            
            grid = grid_1 if m == 1 else grid_2
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != 2:
                return (nr, nc)
            return (r, c)
            
        t_pos, b2_pos = start_1, start_2
        path_t, path_b1, path_b2 = [t_pos], [b2_pos], [t_pos]
        
        # We yield 7 values: visited, frontier, current_node, path, found, path_b1, path_b2
        yield set(), [], t_pos, list(path_t), False, list(path_b1), list(path_b2)
        
        if actions:
            for i, a in enumerate(actions):
                t_pos = apply_action(t_pos[0], t_pos[1], 1, a)
                b2_pos = apply_action(b2_pos[0], b2_pos[1], 2, a)
                
                path_t.append(t_pos)
                path_b1.append(b2_pos)
                path_b2.append(t_pos)
                
                is_last_step = (i == len(actions) - 1)
                yield set(path_t), [], t_pos, list(path_t), is_last_step, list(path_b1), list(path_b2)
        else:
            yield set(), [], start_1, [], True, [], []
            
    return visualizer

# --- Partial Helper Visualizer ---
def make_partial_visualizer(algo_func):
    def visualizer(grid_1, grid_2, start, goal, *args, **kwargs):
        actions = algo_func(grid_1, grid_2, start, goal, *args, **kwargs)
        
        def apply_action(r, c, m, action):
            nr, nc = r, c
            if action == 'U': nr -= 1
            elif action == 'D': nr += 1
            elif action == 'L': nc -= 1
            elif action == 'R': nc += 1
            
            grid = grid_1 if m == 1 else grid_2
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != 2:
                return (nr, nc)
            return (r, c)
            
        t_pos, b2_pos = start, start
        path_t, path_b1, path_b2 = [t_pos], [t_pos], [b2_pos]
        
        # We yield 7 values: visited, frontier, current_node, path, found, path_b1, path_b2
        yield set(), [], t_pos, list(path_t), False, list(path_b1), list(path_b2)
        
        if actions:
            for i, a in enumerate(actions):
                t_pos = apply_action(t_pos[0], t_pos[1], 1, a)
                b2_pos = apply_action(b2_pos[0], b2_pos[1], 2, a)
                
                path_t.append(t_pos)
                path_b1.append(t_pos)
                path_b2.append(b2_pos)
                
                is_last_step = (i == len(actions) - 1)
                yield set(path_t), [], t_pos, list(path_t), is_last_step, list(path_b1), list(path_b2)
        else:
            yield set(), [], start, [], True, [], []
            
    return visualizer

# --- AND-OR Helper Visualizer ---
def make_and_or_visualizer(algo_func):
    def visualizer(grid, start, goal, *args, **kwargs):
        import random
        policy = algo_func(grid, start, goal, *args, **kwargs)
        action_map = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
        
        r, c = start
        path = [(r, c)]
        
        yield set(), [], (r, c), policy, False
        
        steps = 0
        while (r, c) != goal and steps < 150:
            action = policy.get((r, c), 'U')
            
            valid_nbs = []
            for a, (dr, dc) in action_map.items():
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != 2:
                    valid_nbs.append((nr, nc))
                    
            if valid_nbs:
                if random.random() < 0.4: # 40% chance to slip to a random neighbor
                    r, c = random.choice(valid_nbs)
                else:
                    dr, dc = action_map.get(action, (0, 0))
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != 2:
                        r, c = nr, nc
            
            path.append((r, c))
            steps += 1
            yield set(path), [], (r, c), policy, False
            
        yield set(path), [], (r, c), policy, True
        
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

sensorless_bfs = make_sensorless_visualizer(sensorless_bfs_standard)
partial_bfs = make_partial_visualizer(partial_bfs_standard)
and_or_search = make_and_or_visualizer(and_or_search_standard)
bidirectional_search = make_path_visualizer(bidirectional_search_standard)

from .csp import weight_constrained_simple, weight_constrained_forward, weight_constrained_ac3
weight_constrained_simple = make_weight_csp_visualizer(weight_constrained_simple)
weight_constrained_forward = make_weight_csp_visualizer(weight_constrained_forward)
weight_constrained_ac3 = make_weight_csp_visualizer(weight_constrained_ac3)

minimax_search = make_adversarial_visualizer(minimax_search_standard)
alphabeta_search = make_adversarial_visualizer(alphabeta_search_standard)
expectimax_search = make_adversarial_visualizer(expectimax_search_standard)
