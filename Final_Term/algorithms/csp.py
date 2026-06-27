def get_reachable_cells(grid, start):
    """Find all path cells reachable from start using BFS."""
    queue = [start]
    visited = {start}
    while queue:
        curr = queue.pop(0)
        r, c = curr
        for nr, nc in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != 2:
                neighbor = (nr, nc)
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
    return visited

def simple_backtracking(grid, start, goal):
    reachable = get_reachable_cells(grid, start)
    
    # Precompute shortest path distances between all reachable cells
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

    # Candidate cells: must be at least 5 steps away from start
    candidates = sorted([c for c in reachable if dist[c][start] >= 5])
    path = []

    def backtrack(cand_idx):
        if len(path) == 5:
            return True
            
        for i in range(cand_idx, len(candidates)):
            c = candidates[i]
            
            # Check constraints (inter-ghost distance >= 3, and no same row/col)
            if all(dist[c][g] >= 3 for g in path) and all(c[0] != g[0] and c[1] != g[1] for g in path):
                path.append(c)
                
                if backtrack(i + 1):
                    return True
                    
                path.pop()
                
        return False

    if backtrack(0):
        return path
    return None


def backtracking_mrv(grid, start, goal):
    reachable = get_reachable_cells(grid, start)
    
    # Precompute shortest path distances
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

    candidates = sorted([c for c in reachable if dist[c][start] >= 5])
    path = []
    
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

    def backtrack(cand_idx):
        if len(path) == 5:
            return True
            
        unsafe = get_unsafe_set(path)
        current_candidates = [c for c in candidates[cand_idx:] if c not in unsafe and all(dist[c][g] >= 3 for g in path) and all(c[0] != g[0] and c[1] != g[1] for g in path)]
        
        # MRV: sort current_candidates by the number of other compatible remaining candidates
        def get_compatible_count(c):
            count = 0
            for other in current_candidates:
                if other != c and dist[c][other] >= 3 and c[0] != other[0] and c[1] != other[1]:
                    count += 1
            return count
            
        current_candidates.sort(key=get_compatible_count)
        
        for c in current_candidates:
            path.append(c)
            idx_in_candidates = candidates.index(c)
            
            if backtrack(idx_in_candidates + 1):
                return True
                
            path.pop()
            
        return False

    if backtrack(0):
        return path
    return None


def backtracking_forward_checking(grid, start, goal):
    reachable = get_reachable_cells(grid, start)
    
    # Precompute shortest path distances
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

    candidates = sorted([c for c in reachable if dist[c][start] >= 5])
    path = []
    
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

    def backtrack(cand_idx):
        if len(path) == 5:
            return True
            
        for i in range(cand_idx, len(candidates)):
            c = candidates[i]
            
            # Check constraints (inter-ghost distance >= 3, and no same row/col)
            if all(dist[c][g] >= 3 for g in path) and all(c[0] != g[0] and c[1] != g[1] for g in path):
                path.append(c)
                
                unsafe = get_unsafe_set(path)
                frontier = [cand for cand in candidates[i+1:] if cand not in unsafe]
                
                # Forward Checking: count remaining compatible candidates
                remaining_ghosts = 5 - len(path)
                compatible_remaining = [cand for cand in frontier if all(dist[cand][g] >= 3 for g in path) and all(cand[0] != g[0] and cand[1] != g[1] for g in path)]
                
                if len(compatible_remaining) < remaining_ghosts:
                    path.pop()
                    continue
                
                if backtrack(i + 1):
                    return True
                    
                path.pop()
                
        return False

    if backtrack(0):
        return path
    return None
