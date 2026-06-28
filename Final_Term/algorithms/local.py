import random
import math
from .node import Node
from .uninformed import moves, solution

def heuristic(state, visited_set, grid):
    # Remaining food count after visiting state
    new_visited = visited_set | {state}
    count = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 1 and (r, c) not in new_visited:
                count += 1
    return count

def get_node_visited(node):
    visited = set()
    curr = node
    while curr:
        visited.add(curr.state)
        curr = curr.parent
    return visited

# --- 1. Hill Climbing đơn giản (Leo Đồi) ---
def hill_climbing(grid, start, goal):

    curr = start
    path = [curr]
    visited = {curr}

    while heuristic(curr, visited, grid) > 0:
        neighbors = moves(grid, curr)
        if not neighbors:
            break

        best = min(neighbors, key=lambda pos: heuristic(pos, visited, grid))

        # Nếu hàng xóm tốt nhất không làm giảm số lượng thức ăn còn lại so với hiện tại
        # thì dừng lại (kẹt cực trị cục bộ)
        if heuristic(best, visited, grid) >= heuristic(curr, visited, grid):
            break

        curr = best
        path.append(curr)
        visited.add(curr)

    return path


# --- 2. Beam Search ---
def beam_search(grid, start, goal, k=2):
    start_node = Node(start, g=0, h=heuristic(start, set(), grid))
    start_node.food_eaten = {start} if grid[start[0]][start[1]] == 1 else set()
    
    if heuristic(start, set(), grid) == 0:
        return [start]
        
    beam = [start_node]
    visited = {start}
    best_node_so_far = start_node
    
    found_node = None
    level = 0
    while beam and level < 150:
        level += 1
        candidates = []
        for node in beam:
            node_visited = get_node_visited(node)
            for next_state in moves(grid, node.state):
                new_g = node.g + 1
                new_h = heuristic(next_state, node_visited, grid)
                child = Node(next_state, parent=node, g=new_g, h=new_h)
                child.food_eaten = node.food_eaten.copy()
                if grid[next_state[0]][next_state[1]] == 1:
                    child.food_eaten.add(next_state)
                
                if new_h == 0:
                    found_node = child
                    break
                candidates.append(child)
            if found_node:
                break
        if found_node:
            break
            
        if not candidates:
            break
            
        candidates.sort(key=lambda n: n.f)

        seen = set()
        new_beam = []
        for cand in candidates:
            if cand.state not in seen:
                seen.add(cand.state)
                new_beam.append(cand)
                if len(new_beam) == k:
                    break
        beam = new_beam
        
        for node in beam:
            visited.add(node.state)
            if node.h < best_node_so_far.h:
                best_node_so_far = node
            
    if found_node:
        return solution(found_node)
    else:
        return solution(best_node_so_far)


# --- 3. Simulated Annealing (Giả Lập Luyện Kim) ---
def simulated_annealing(grid, start, goal):
    T = 1000
    T_min = 0.1
    alpha = 0.95
    
    curr = start
    path = [curr]
    visited = {curr}
    
    while T > T_min and heuristic(curr, visited, grid) > 0:
        neighbors = moves(grid, curr)
        if not neighbors:
            break
            
        neighbor = random.choice(neighbors)
        
        delta = heuristic(neighbor, visited, grid) - heuristic(curr, visited, grid)
        accept = False
        
        if delta < 0:
            accept = True
        else:
            p = math.exp(-delta / T)
            if random.random() < p:
                accept = True
                
        if accept:
            curr = neighbor
            path.append(curr)
            visited.add(curr)
            
        T *= alpha
        
    return path
