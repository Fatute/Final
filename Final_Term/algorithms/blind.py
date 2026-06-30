def sensorless_bfs(grid_1, grid_2, start_1, start_2, goal):
    rows = len(grid_1)
    cols = len(grid_1[0]) if rows > 0 else 0
    
    def apply_action(r, c, m, action):
        nr, nc = r, c
        if action == 'U': nr -= 1
        elif action == 'D': nr += 1
        elif action == 'L': nc -= 1
        elif action == 'R': nc += 1
        
        grid = grid_1 if m == 1 else grid_2
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 2:
            return (nr, nc, m)
        return (r, c, m)
        
    initial_belief = frozenset([(start_1[0], start_1[1], 1), (start_2[0], start_2[1], 2)])
    visited = set([initial_belief])
    
    # Check if already at goal
    def is_goal(belief):
        return all((r, c) == goal for r, c, m in belief)
        
    if is_goal(initial_belief):
        return [], len(visited)
        
    queue = [(initial_belief, [])]
    actions = ['U', 'D', 'L', 'R']
    
    while queue:
        current_belief, current_actions = queue.pop(0)
        
        for action in actions:
            new_belief = frozenset([apply_action(r, c, m, action) for r, c, m in current_belief])
            
            if new_belief not in visited:
                new_actions = current_actions + [action]
                
                if is_goal(new_belief):
                    return new_actions, len(visited)
                    
                visited.add(new_belief)
                queue.append((new_belief, new_actions))
                
    return [], len(visited)

def partial_bfs(grid_1, grid_2, start, goal):
    rows = len(grid_1)
    cols = len(grid_1[0]) if rows > 0 else 0
    
    def apply_action(r, c, m, action):
        nr, nc = r, c
        if action == 'U': nr -= 1
        elif action == 'D': nr += 1
        elif action == 'L': nc -= 1
        elif action == 'R': nc += 1
        
        grid = grid_1 if m == 1 else grid_2
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 2:
            return (nr, nc, m)
        return (r, c, m)
        
    initial_belief = frozenset([(start[0], start[1], 1), (start[0], start[1], 2)])
    visited = set([initial_belief])
    
    def is_goal(belief):
        return all((r, c) == goal for r, c, m in belief)
        
    if is_goal(initial_belief):
        return [], len(visited)
        
    queue = [(initial_belief, [])]
    actions = ['U', 'D', 'L', 'R']
    
    while queue:
        current_belief, current_actions = queue.pop(0)
        
        for action in actions:
            new_belief = frozenset([apply_action(r, c, m, action) for r, c, m in current_belief])
            
            if new_belief not in visited:
                new_actions = current_actions + [action]
                
                if is_goal(new_belief):
                    return new_actions, len(visited)
                    
                visited.add(new_belief)
                queue.append((new_belief, new_actions))
                
    return [], len(visited)

def and_or_search(grid, start, goal, max_depth=15):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    action_map = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
    
    def get_valid_neighbors(r, c):
        nbs = {}
        for a, (dr, dc) in action_map.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 2:
                nbs[a] = (nr, nc)
        return nbs

    policy = {}
    
    def or_search(state, path, depth):
        if state == goal:
            return True
        if state in path:
            return False
        if depth <= 0:
            return False
            
        nbs = get_valid_neighbors(state[0], state[1])
        if not nbs:
            return False
            
        for action, intended_state in nbs.items():
            outcomes = list(nbs.values())
            plan = and_search(outcomes, path + [state], depth - 1)
            if plan:
                policy[state] = action
                return True
        return False

    def and_search(states, path, depth):
        for state in states:
            plan_i = or_search(state, path, depth)
            if not plan_i:
                return False
        return True

    or_search(start, [], max_depth)
    
    from collections import deque
    q = deque([(goal[0], goal[1])])
    visited = {goal: 0}
    
    while q:
        curr = q.popleft()
        for a, (dr, dc) in action_map.items():
            nr, nc = curr[0] - dr, curr[1] - dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 2:
                if (nr, nc) not in visited:
                    visited[(nr, nc)] = visited[curr] + 1
                    q.append((nr, nc))
                    if (nr, nc) not in policy:
                        policy[(nr, nc)] = a
                        
    return policy, len(policy)
def bidirectional_search(grid, start, goal):
    if start == goal:
        return [start], 1
    
    fw_queue = [start]
    fw_parent = {start: None}
    
    bw_queue = [goal]
    bw_parent = {goal: None}
    
    def get_neighbors(pos):
        r, c = pos
        res = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != 2:
                res.append((nr, nc))
        return res

    intersect = None
    while fw_queue and bw_queue:
        # Step forward
        curr_fw = fw_queue.pop(0)
        if curr_fw in bw_parent:
            intersect = curr_fw
            break
        for nxt in get_neighbors(curr_fw):
            if nxt not in fw_parent:
                fw_parent[nxt] = curr_fw
                fw_queue.append(nxt)
                
        # Step backward
        curr_bw = bw_queue.pop(0)
        if curr_bw in fw_parent:
            intersect = curr_bw
            break
        for nxt in get_neighbors(curr_bw):
            if nxt not in bw_parent:
                bw_parent[nxt] = curr_bw
                bw_queue.append(nxt)

    if intersect is None:
        return [], len(fw_parent) + len(bw_parent)

    # Reconstruct path
    path = []
    # Forward path (from start to intersect)
    curr = intersect
    while curr is not None:
        path.append(curr)
        curr = fw_parent[curr]
    path.reverse()
    
    # Backward path (from intersect's parent in backward tree to goal)
    curr = bw_parent[intersect]
    while curr is not None:
        path.append(curr)
        curr = bw_parent[curr]
        
    return path, len(fw_parent) + len(bw_parent)
