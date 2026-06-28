from .node import Node
from .csp import get_reachable_cells

def solution(node):
    path = []
    curr = node
    while curr is not None:
        path.append(curr.state)
        curr = curr.parent
    return path[::-1]


#Valid move of state
def moves(grid, state):
    r, c = state
    directions = [
        [0, 1],   # Right
        [0, -1],  # Left
        [1, 0],   # Down
        [-1, 0]   # Up
    ]
    valid_move = []
    for x, y in directions:
        new_row = r + x
        new_col = c + y
        if 0 <= new_row < len(grid) and 0 <= new_col < len(grid[0]):
            if grid[new_row][new_col] != 2:
                valid_move.append((new_row, new_col))
    return valid_move

#Evaluate g(n)
def count_food(grid):
    count = 0
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if grid[x][y] == 1:
                count += 1
    return count

def priority_queue(frontier):
    frontier.sort(key = lambda x : x.g)
    return frontier[0]

#Back to old road
def find_shortest_path(grid, start, end):
    """BFS helper to find the shortest continuous path between two cells."""
    if start == end:
        return [start]
    queue = [[start]]
    visited = {start}
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node == end:
            return path
        for neighbor in moves(grid, node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return []

# BFS
def bfs(grid, start, goal):
    node = Node(start)
    frontier = [node]
    reached_set = set()
    reached_order = []
    
    reachable = get_reachable_cells(grid, start)
    total_food = sum(1 for r, c in reachable if grid[r][c] == 1)
    
    while len(frontier) != 0:
        node = frontier.pop(0)
        
        if node.state in reached_set:
            continue
        reached_set.add(node.state)
        reached_order.append(node.state)
        
        visited_foods = sum(1 for r, c in reached_set if grid[r][c] == 1)
        if visited_foods == total_food:
            full_path = []
            curr = start
            for target in reached_order:
                sub_path = find_shortest_path(grid, curr, target)
                if sub_path:
                    if full_path:
                        full_path.extend(sub_path[1:])
                    else:
                        full_path.extend(sub_path)
                    curr = target
            return full_path
            
        actions = moves(grid, node.state)
        for state in actions:
            if state not in reached_set and not any(n.state == state for n in frontier):
                child = Node(state, parent=node)
                frontier.append(child)
                    
    return []

#DFS
def dfs(grid, start, goal):
    node = Node(start)
    frontier = [node]
    reached_set = set()
    reached_order = []
    
    reachable = get_reachable_cells(grid, start)
    total_food = sum(1 for r, c in reachable if grid[r][c] == 1)
    
    while len(frontier) != 0:
        node = frontier.pop()
        
        if node.state in reached_set:
            continue
        reached_set.add(node.state)
        reached_order.append(node.state)
        
        visited_foods = sum(1 for r, c in reached_set if grid[r][c] == 1)
        if visited_foods == total_food:
            full_path = []
            curr = start
            for target in reached_order:
                sub_path = find_shortest_path(grid, curr, target)
                if sub_path:
                    if full_path:
                        full_path.extend(sub_path[1:])
                    else:
                        full_path.extend(sub_path)
                    curr = target
            return full_path
            
        actions = moves(grid, node.state)
        for state in actions:
            if state not in reached_set and not any(n.state == state for n in frontier):
                child = Node(state, parent=node)
                frontier.append(child)
                    
    return []

#UCS
def ucs(grid, start, goal):
    reachable = get_reachable_cells(grid, start)
    total_food = sum(1 for r, c in reachable if grid[r][c] == 1)
    node = Node(start, g=0)
    frontier = [node]
    reached_set = set()
    reached_order = []

    while len(frontier) != 0:
        node = priority_queue(frontier)
        frontier.remove(node)

        if node.state in reached_set:
            continue
        reached_set.add(node.state)
        reached_order.append(node.state)

        visited_foods = sum(1 for r, c in reached_set if grid[r][c] == 1)
        if visited_foods == total_food:
            full_path = []
            curr = start
            for target in reached_order:
                sub_path = find_shortest_path(grid, curr, target)
                if sub_path:
                    if full_path:
                        full_path.extend(sub_path[1:])
                    else:
                        full_path.extend(sub_path)
                    curr = target
            return full_path

        for state in moves(grid, node.state):
            if state not in reached_set:
                child = Node(state, parent=node, g=node.g + 1)
                # If there's an existing node with the same state in frontier,
                # we update it if the new cost is smaller
                existing = next((n for n in frontier if n.state == state), None)
                if existing:
                    if child.g < existing.g:
                        frontier.remove(existing)
                        frontier.append(child)
                else:
                    frontier.append(child)

    return []
