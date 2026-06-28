# ─────────────────────────────────────────────
#  Distance helpers
# ─────────────────────────────────────────────

def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_reachable_cells(grid, start):
    """Find all path cells reachable from start using BFS."""
    rows, cols = len(grid), len(grid[0])
    queue = [start]
    visited = {start}
    while queue:
        r, c = queue.pop(0)
        for nr, nc in ((r-1, c), (r+1, c), (r, c-1), (r, c+1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 2:
                nb = (nr, nc)
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)
    return visited

# ─────────────────────────────────────────────
#  Weight-Constrained Path CSP Variations
# ─────────────────────────────────────────────

def _get_coin_score(r, c):
    """Deterministic pseudo-random coin score between 1 and 5"""
    return (r * 3 + c * 7) % 5 + 1


# 1. Simple Backtracking
def weight_constrained_simple(grid, start, goal, max_score):
    """
    1. Simple Backtracking: Does not check max_score until AFTER stepping.
    """
    rows, cols = len(grid), len(grid[0])
    steps = []
    current_path = [start]
    
    def backtrack(current_score):
        current_node = current_path[-1]
        
        if current_node == goal:
            return True
            
        if current_score > max_score:
            return False # Backtrack after stepping
            
        r, c = current_node
        neighbors = []
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 2:
                if (nr, nc) not in current_path:
                    neighbors.append((nr, nc))
                    
        # Sort heuristically
        neighbors.sort(key=lambda n: _manhattan(n, goal))
        
        # Domain visually shows all geometric neighbors
        domain = neighbors.copy()
        
        for n in neighbors:
            score = _get_coin_score(n[0], n[1]) if n != goal else 0
            new_score = current_score + score
            
            steps.append(('try', n, current_path.copy(), new_score, domain))
            
            current_path.append(n)
            if backtrack(new_score):
                return True
            current_path.pop()
            
            steps.append(('backtrack', n, current_path.copy(), current_score, domain))
            
        return False
        
    if backtrack(0):
        steps.append(('found', current_path.copy()))
        return current_path, steps
    
    return None, steps


# 2. Forward Checking
def weight_constrained_forward(grid, start, goal, max_score):
    """
    2. Forward Checking: Checks new_score <= max_score BEFORE stepping.
    Prunes neighbors from domain.
    """
    rows, cols = len(grid), len(grid[0])
    steps = []
    current_path = [start]
    
    def backtrack(current_score):
        current_node = current_path[-1]
        if current_node == goal:
            return True
            
        r, c = current_node
        neighbors = []
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 2:
                if (nr, nc) not in current_path:
                    score = _get_coin_score(nr, nc) if (nr, nc) != goal else 0
                    if current_score + score <= max_score:
                        neighbors.append((nr, nc))
                    
        neighbors.sort(key=lambda n: _manhattan(n, goal))
        domain = neighbors.copy()
        
        for n in neighbors:
            score = _get_coin_score(n[0], n[1]) if n != goal else 0
            new_score = current_score + score
            
            steps.append(('try', n, current_path.copy(), new_score, domain))
            
            current_path.append(n)
            if backtrack(new_score):
                return True
            current_path.pop()
            
            steps.append(('backtrack', n, current_path.copy(), current_score, domain))
            
        return False
        
    if backtrack(0):
        steps.append(('found', current_path.copy()))
        return current_path, steps
    
    return None, steps


# 3. AC-3 (Arc Consistency / Lookahead)
def weight_constrained_ac3(grid, start, goal, max_score):
    """
    3. AC-3: Uses lookahead with Manhattan distance.
    Prunes if current_score + score + manhattan > max_score.
    """
    rows, cols = len(grid), len(grid[0])
    steps = []
    current_path = [start]
    
    def backtrack(current_score):
        current_node = current_path[-1]
        if current_node == goal:
            return True
            
        r, c = current_node
        neighbors = []
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 2:
                if (nr, nc) not in current_path:
                    score = _get_coin_score(nr, nc) if (nr, nc) != goal else 0
                    # The goal cell costs 0, so we subtract 1 from manhattan distance
                    min_future_cost = max(0, _manhattan((nr, nc), goal) - 1)
                    # AC-3 strict pruning
                    if current_score + score + min_future_cost <= max_score:
                        neighbors.append((nr, nc))
                    
        neighbors.sort(key=lambda n: _manhattan(n, goal))
        domain = neighbors.copy()
        
        for n in neighbors:
            score = _get_coin_score(n[0], n[1]) if n != goal else 0
            new_score = current_score + score
            
            steps.append(('try', n, current_path.copy(), new_score, domain))
            
            current_path.append(n)
            if backtrack(new_score):
                return True
            current_path.pop()
            
            steps.append(('backtrack', n, current_path.copy(), current_score, domain))
            
        return False
        
    if backtrack(0):
        steps.append(('found', current_path.copy()))
        return current_path, steps
    
    return None, steps
