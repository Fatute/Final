from .node import Node
from .csp import get_reachable_cells
from .uninformed import moves, find_shortest_path, solution

def get_path_to(node):
    path = []
    curr = node
    while curr:
        path.append(curr.state)
        curr = curr.parent
    return path[::-1]

# --- 1. Greedy Best-First Search ---
def greedy_best_first(grid, start, goal):
    reachable = get_reachable_cells(grid, start)
    total_food = sum(1 for r, c in reachable if grid[r][c] == 1)
    
    start_node = Node(start, g=0, h=total_food)
    frontier = [start_node]
    reached_set = set()
    reached_order = []
    
    while frontier:
        frontier.sort(key=lambda x: x.h)
        curr = frontier.pop(0)
        
        if curr.state in reached_set:
            continue
        reached_set.add(curr.state)
        reached_order.append(curr.state)
        
        visited_foods = sum(1 for r, c in reached_set if grid[r][c] == 1)
        if visited_foods == total_food:
            full_path = []
            curr_pos = start
            for target in reached_order:
                sub_path = find_shortest_path(grid, curr_pos, target)
                if sub_path:
                    if full_path:
                        full_path.extend(sub_path[1:])
                    else:
                        full_path.extend(sub_path)
                    curr_pos = target
            return full_path, len(reached_set)
            
        for next_pos in moves(grid, curr.state):
            if next_pos not in reached_set:
                path_so_far = get_path_to(curr) + [next_pos]
                new_g = len(path_so_far) - 1
                new_h = total_food - len(set(path_so_far))
                
                existing = next((n for n in frontier if n.state == next_pos), None)
                if existing:
                    if existing.h > new_h:
                        frontier.remove(existing)
                        frontier.append(Node(next_pos, parent=curr, g=new_g, h=new_h))
                else:
                    frontier.append(Node(next_pos, parent=curr, g=new_g, h=new_h))
                    
    return [], len(reached_set)


# --- 2. A* Search ---
def a_star(grid, start, goal):
    reachable = get_reachable_cells(grid, start)
    total_food = sum(1 for r, c in reachable if grid[r][c] == 1)
    
    start_node = Node(start, g=0, h=total_food)
    frontier = [start_node]
    reached_set = set()
    reached_order = []
    
    while frontier:
        frontier.sort(key=lambda x: x.f)
        curr = frontier.pop(0)
        
        if curr.state in reached_set:
            continue
        reached_set.add(curr.state)
        reached_order.append(curr.state)
        
        visited_foods = sum(1 for r, c in reached_set if grid[r][c] == 1)
        if visited_foods == total_food:
            full_path = []
            curr_pos = start
            for target in reached_order:
                sub_path = find_shortest_path(grid, curr_pos, target)
                if sub_path:
                    if full_path:
                        full_path.extend(sub_path[1:])
                    else:
                        full_path.extend(sub_path)
                    curr_pos = target
            return full_path, len(reached_set)
            
        for next_pos in moves(grid, curr.state):
            if next_pos not in reached_set:
                path_so_far = get_path_to(curr) + [next_pos]
                new_g = len(path_so_far) - 1
                new_h = total_food - len(set(path_so_far))
                
                existing = next((n for n in frontier if n.state == next_pos), None)
                if existing:
                    if existing.g > new_g:
                        frontier.remove(existing)
                        frontier.append(Node(next_pos, parent=curr, g=new_g, h=new_h))
                else:
                    frontier.append(Node(next_pos, parent=curr, g=new_g, h=new_h))
                    
    return [], len(reached_set)


# --- 3. IDA* Search Helper ---
def search_with_threshold(grid, start, total_food, threshold, reached_set, reached_order):
    start_node = Node(start, g=0, h=total_food)
    frontier = [start_node]
    min_threshold = float('inf')
    visited_in_pass = set()
    
    while frontier:
        curr = frontier.pop()
        
        if curr.state in visited_in_pass:
            continue
        visited_in_pass.add(curr.state)
        
        if curr.state not in reached_set:
            reached_set.add(curr.state)
            reached_order.append(curr.state)
            
        visited_foods = sum(1 for r, c in reached_set if grid[r][c] == 1)
        if visited_foods == total_food:
            return curr, threshold
            
        for next_pos in moves(grid, curr.state):
            if next_pos not in visited_in_pass:
                path_so_far = get_path_to(curr) + [next_pos]
                new_g = len(path_so_far) - 1
                new_h = total_food - len(set(path_so_far))
                new_f = new_g + new_h
                
                if new_f > threshold:
                    if new_f < min_threshold:
                        min_threshold = new_f
                    continue
                    
                child = Node(next_pos, parent=curr, g=new_g, h=new_h)
                frontier.append(child)
                
    return None, min_threshold

# --- 4. IDA* Search ---
def ida_star(grid, start, goal):
    reachable = get_reachable_cells(grid, start)
    total_food = sum(1 for r, c in reachable if grid[r][c] == 1)
    threshold = total_food
    
    while True:
        reached_set = set()
        reached_order = []
        
        found_node, next_threshold = search_with_threshold(
            grid, start, total_food, threshold, reached_set, reached_order
        )
        
        if found_node:
            full_path = []
            curr_pos = start
            for target in reached_order:
                sub_path = find_shortest_path(grid, curr_pos, target)
                if sub_path:
                    if full_path:
                        full_path.extend(sub_path[1:])
                    else:
                        full_path.extend(sub_path)
                    curr_pos = target
            return full_path, len(reached_set)
            
        if next_threshold == float('inf'):
            break
        threshold = next_threshold
        
    return [], len(reached_set)
