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


# ─────────────────────────────────────────────
#  Ghost Blocking CSP — shared helpers
# ─────────────────────────────────────────────

def _bfs_reachable(grid, start, blocked):
    """BFS returning cells reachable from start, avoiding blocked cells."""
    if start in blocked:
        return set()
    reachable = {start}
    queue = [start]
    while queue:
        r, c = queue.pop(0)
        for nr, nc in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
            nb = (nr, nc)
            if (0 <= nr < len(grid) and 0 <= nc < len(grid[0])
                    and grid[nr][nc] != 2 and nb not in blocked and nb not in reachable):
                reachable.add(nb)
                queue.append(nb)
    return reachable


def _neighbors(grid, pos):
    r, c = pos
    result = []
    for nr, nc in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != 2:
            result.append((nr, nc))
    return result


def _is_all_blocked(grid, start, food_cells, ghosts):
    reach = _bfs_reachable(grid, start, set(ghosts))
    return not (food_cells & reach)


def _get_chokepoints(grid, start, food_cells, forbidden):
    """Cells whose removal reduces reachable food count."""
    reachable = get_reachable_cells(grid, start)
    result = []
    for c in sorted(reachable):
        if c in forbidden:
            continue
        if len(food_cells & _bfs_reachable(grid, start, {c})) < len(food_cells):
            result.append(c)
    return result


def _setup_blocking(grid, start):
    """Shared setup: food cells, forbidden zone, chokepoints."""
    reachable = get_reachable_cells(grid, start)
    # Forbidden: only the Pacman spawn cell itself (ghost cannot overlap with Pacman)
    forbidden = {start}
    food_cells = frozenset(
        (r, c) for r, c in reachable if grid[r][c] == 1 and (r, c) != start
    )
    chokepoints = _get_chokepoints(grid, start, food_cells, forbidden)
    return food_cells, forbidden, chokepoints


# ─────────────────────────────────────────────
#  1. Simple Backtracking Ghost Blocking
# ─────────────────────────────────────────────

def simple_backtracking(grid, start, goal):
    food_cells, _, chokepoints = _setup_blocking(grid, start)
    if not food_cells or not chokepoints:
        return None, []

    steps = []
    placed = []

    def backtrack(idx, k_rem):
        if k_rem == 0:
            return _is_all_blocked(grid, start, food_cells, placed)
        if len(chokepoints) - idx < k_rem:
            return False
        for i in range(idx, len(chokepoints)):
            c = chokepoints[i]
            placed.append(c)
            reach = _bfs_reachable(grid, start, set(placed))
            steps.append(('try', c, placed.copy(), reach))
            if backtrack(i + 1, k_rem - 1):
                return True
            placed.pop()
            reach = _bfs_reachable(grid, start, set(placed))
            steps.append(('backtrack', c, placed.copy(), reach))
        return False

    solution = None
    for k in range(1, len(chokepoints) + 1):
        placed.clear()
        steps.clear()
        if backtrack(0, k):
            solution = placed.copy()
            steps.append(('found', solution))
            break

    return solution, steps

# ─────────────────────────────────────────────
#  2. Backtracking + AC-3 Ghost Blocking
# ─────────────────────────────────────────────

def _ac3(domains):
    """
    AC-3 algorithm: enforce arc consistency for Xi ≠ Xj constraints.
    domains: dict {variable_id: set of candidate cells}
    Modifies domains in-place.
    Returns False if any domain becomes empty (no solution possible).
    """
    queue = [(xi, xj) for xi in domains for xj in domains if xi != xj]
    while queue:
        xi, xj = queue.pop(0)
        revised = False
        for v in list(domains[xi]):
            # v is arc-consistent with Dj if ∃ w in Dj: w ≠ v
            if not any(w != v for w in domains[xj]):
                domains[xi].discard(v)
                revised = True
        if revised:
            if not domains[xi]:
                return False   # Domain wiped out → no solution
            # Re-check all arcs pointing to xi
            for xk in domains:
                if xk != xi:
                    queue.append((xk, xi))
    return True


def backtracking_ac3(grid, start, goal):
    food_cells, _, chokepoints = _setup_blocking(grid, start)
    if not food_cells or not chokepoints:
        return None, []

    steps = []
    placed = []

    def effective_domain(curr_reach):
        """Keep only chokepoints that still block some remaining reachable food."""
        remaining_food = food_cells & curr_reach
        result = set()
        for c in chokepoints:
            if c in placed:
                continue
            test_reach = _bfs_reachable(grid, start, set(placed) | {c})
            if len(remaining_food & test_reach) < len(remaining_food):
                result.add(c)
        return result

    def backtrack(k_rem, curr_reach):
        if k_rem == 0:
            return not bool(food_cells & curr_reach)

        # Build k_rem identical domains from effective candidates
        base = effective_domain(curr_reach)
        if not base:
            return False

        domains = {i: set(base) for i in range(k_rem)}

        # ── AC-3: enforce xi ≠ xj arc consistency ──
        if not _ac3(domains):
            return False

        # Use domain[0] (may have been reduced by AC-3)
        candidates = sorted(domains[0])

        for c in candidates:
            placed.append(c)
            new_reach = _bfs_reachable(grid, start, set(placed))
            steps.append(('try', c, placed.copy(), new_reach))

            if backtrack(k_rem - 1, new_reach):
                return True

            placed.pop()
            prev_reach = _bfs_reachable(grid, start, set(placed))
            steps.append(('backtrack', c, placed.copy(), prev_reach))

        return False

    initial_reach = _bfs_reachable(grid, start, set())
    solution = None
    for k in range(1, len(chokepoints) + 1):
        placed.clear()
        steps.clear()
        if backtrack(k, initial_reach):
            solution = placed.copy()
            steps.append(('found', solution))
            break

    return solution, steps


# ─────────────────────────────────────────────
#  3. Backtracking + Forward Checking Ghost Blocking
# ─────────────────────────────────────────────

def backtracking_forward_checking(grid, start, goal):
    food_cells, _, chokepoints = _setup_blocking(grid, start)
    if not food_cells or not chokepoints:
        return None, []

    steps = []
    placed = []

    def can_still_block(remaining_cands, k_rem):
        """Forward check: can remaining candidates block all remaining reachable food?"""
        curr_reach = _bfs_reachable(grid, start, set(placed))
        remaining_food = food_cells & curr_reach
        if not remaining_food:
            return True
        if k_rem == 0:
            return False
        # Each remaining food must be blockable by at least one remaining candidate
        for food in remaining_food:
            if not any(
                food not in _bfs_reachable(grid, start, set(placed) | {c})
                for c in remaining_cands
            ):
                return False
        return True

    def backtrack(idx, k_rem):
        if k_rem == 0:
            return _is_all_blocked(grid, start, food_cells, placed)
        if len(chokepoints) - idx < k_rem:
            return False
        for i in range(idx, len(chokepoints)):
            c = chokepoints[i]
            placed.append(c)
            reach = _bfs_reachable(grid, start, set(placed))
            steps.append(('try', c, placed.copy(), reach))
            remaining = chokepoints[i + 1:]
            if can_still_block(remaining, k_rem - 1) and backtrack(i + 1, k_rem - 1):
                return True
            placed.pop()
            reach = _bfs_reachable(grid, start, set(placed))
            steps.append(('backtrack', c, placed.copy(), reach))
        return False

    solution = None
    for k in range(1, len(chokepoints) + 1):
        placed.clear()
        steps.clear()
        if backtrack(0, k):
            solution = placed.copy()
            steps.append(('found', solution))
            break

    return solution, steps
