# ─────────────────────────────────────────────
#  Distance helpers
# ─────────────────────────────────────────────

MIN_GHOST_PACMAN_DIST = 1   # ghost không được đứng đúng ô Pacman
MIN_GHOST_GHOST_DIST  = 2   # ghosts must be at least this far from each other

# Safety cap: stop recording steps after this many to avoid memory bloat on large maps
MAX_STEPS = 2000


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
#  Ghost Blocking CSP — shared helpers
# ─────────────────────────────────────────────

def _bfs_reachable(grid, start, blocked):
    """BFS returning cells reachable from start, avoiding blocked cells.

    `blocked` should be a frozenset for hashing / repeated use.
    """
    rows, cols = len(grid), len(grid[0])
    if start in blocked:
        return frozenset()
    reachable = {start}
    queue = [start]
    while queue:
        r, c = queue.pop(0)
        for nr, nc in ((r-1, c), (r+1, c), (r, c-1), (r, c+1)):
            nb = (nr, nc)
            if (0 <= nr < rows and 0 <= nc < cols
                    and grid[nr][nc] != 2
                    and nb not in blocked
                    and nb not in reachable):
                reachable.add(nb)
                queue.append(nb)
    return frozenset(reachable)


def _is_goal_blocked(grid, start, goal, blocked_fs):
    """Return True if Pacman cannot reach goal with the given blocked cells."""
    reach = _bfs_reachable(grid, start, blocked_fs)
    return goal not in reach


def _get_chokepoints(grid, start, goal, forbidden):
    """Cells whose removal prevents Pacman from reaching goal.
    Sorted by distance to goal (ascending) so backtracking tries cells
    close to goal first — gives richer visualisation with more backtracks.
    """
    reachable = get_reachable_cells(grid, start)
    result = []
    for c in reachable:
        if c in forbidden or c == goal:
            continue
        if goal not in _bfs_reachable(grid, start, frozenset({c})):
            result.append(c)
    # Cells closer to goal come first (farther from start)
    result.sort(key=lambda c: _manhattan(c, goal))
    return result


def _setup_blocking(grid, start, goal):
    """Shared setup: forbidden zone and chokepoints for goal-blocking CSP.

    Forbidden zone: only Pacman's own cell (cannot place ghost there).
    Chokepoints: cells whose removal disconnects Pacman from goal.
    """
    forbidden = {start}
    chokepoints = _get_chokepoints(grid, start, goal, forbidden)
    return chokepoints



def _ghosts_too_close(candidate, placed):
    """Return True if candidate is closer than MIN_GHOST_GHOST_DIST to any placed ghost."""
    return any(_manhattan(candidate, g) < MIN_GHOST_GHOST_DIST for g in placed)


# ─────────────────────────────────────────────
#  1. Simple Backtracking Ghost Blocking
# ─────────────────────────────────────────────

def simple_backtracking(grid, start, goal):
    chokepoints = _setup_blocking(grid, start, goal)
    if not chokepoints:
        return None, []

    steps = []
    placed = []
    placed_fs = frozenset()

    def backtrack(idx, k_rem):
        nonlocal placed_fs
        if k_rem == 0:
            return _is_goal_blocked(grid, start, goal, placed_fs)
        if len(chokepoints) - idx < k_rem:
            return False
        for i in range(idx, len(chokepoints)):
            c = chokepoints[i]
            if _ghosts_too_close(c, placed):
                continue
            placed.append(c)
            placed_fs = frozenset(placed)
            reach = _bfs_reachable(grid, start, placed_fs)
            if len(steps) < MAX_STEPS:
                steps.append(('try', c, placed.copy(), reach))
            if backtrack(i + 1, k_rem - 1):
                return True
            placed.pop()
            placed_fs = frozenset(placed)
            reach = _bfs_reachable(grid, start, placed_fs)
            if len(steps) < MAX_STEPS:
                steps.append(('backtrack', c, placed.copy(), reach))
        return False

    solution = None
    for k in range(1, len(chokepoints) + 1):
        placed.clear()
        placed_fs = frozenset()
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
    queue = [(xi, xj) for xi in domains for xj in domains if xi != xj]
    while queue:
        xi, xj = queue.pop(0)
        revised = False
        for v in list(domains[xi]):
            # v is arc-consistent with Dj if ∃ w in Dj satisfying both constraints
            if not any(
                w != v and _manhattan(v, w) >= MIN_GHOST_GHOST_DIST
                for w in domains[xj]
            ):
                domains[xi].discard(v)
                revised = True
        if revised:
            if not domains[xi]:
                return False
            for xk in domains:
                if xk != xi:
                    queue.append((xk, xi))
    return True


def backtracking_ac3(grid, start, goal):
    chokepoints = _setup_blocking(grid, start, goal)
    if not chokepoints:
        return None, []

    steps = []
    placed = []
    placed_fs = frozenset()

    def effective_domain(curr_reach):
        result = set()
        placed_set = set(placed)
        for c in chokepoints:
            if c in placed_set:
                continue
            # c is useful if blocking it (on top of already placed) cuts off goal
            test_reach = _bfs_reachable(grid, start, placed_fs | frozenset({c}))
            if goal not in test_reach:
                result.add(c)
            # Also include c if it reduces the reachable area toward goal
            elif goal in curr_reach and goal not in test_reach:
                result.add(c)
        # Broader: any chokepoint still on a path from start to goal in curr_reach
        if not result:
            for c in chokepoints:
                if c in placed_set:
                    continue
                test_reach = _bfs_reachable(grid, start, placed_fs | frozenset({c}))
                if len(test_reach) < len(curr_reach):
                    result.add(c)
        return result

    def backtrack(k_rem, curr_reach):
        nonlocal placed_fs
        if k_rem == 0:
            return goal not in curr_reach

        base = set(chokepoints) - set(placed)
        if not base:
            return False

        domains = {i: set(base) for i in range(k_rem)}
        if not _ac3(domains):
            return False

        candidates = sorted(domains[0])

        for c in candidates:
            if _ghosts_too_close(c, placed):
                continue
            placed.append(c)
            placed_fs = frozenset(placed)
            new_reach = _bfs_reachable(grid, start, placed_fs)
            if len(steps) < MAX_STEPS:
                steps.append(('try', c, placed.copy(), new_reach))

            if backtrack(k_rem - 1, new_reach):
                return True

            placed.pop()
            placed_fs = frozenset(placed)
            prev_reach = _bfs_reachable(grid, start, placed_fs)
            if len(steps) < MAX_STEPS:
                steps.append(('backtrack', c, placed.copy(), prev_reach))

        return False

    initial_reach = _bfs_reachable(grid, start, frozenset())
    solution = None
    for k in range(1, len(chokepoints) + 1):
        placed.clear()
        placed_fs = frozenset()
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
    chokepoints = _setup_blocking(grid, start, goal)
    if not chokepoints:
        return None, []

    steps = []
    placed = []
    placed_fs = frozenset()

    def can_still_block(remaining_cands, k_rem, curr_reach):
        if goal not in curr_reach:
            return True  # Already blocked!
        if k_rem == 0:
            return False
        valid_cands = [c for c in remaining_cands if not _ghosts_too_close(c, placed)]
        # There must be at least one candidate that, if placed, cuts off goal
        return any(
            goal not in _bfs_reachable(grid, start, placed_fs | frozenset({c}))
            for c in valid_cands
        )

    def backtrack(idx, k_rem, curr_reach):
        nonlocal placed_fs
        if k_rem == 0:
            return _is_goal_blocked(grid, start, goal, placed_fs)
        if len(chokepoints) - idx < k_rem:
            return False
        for i in range(idx, len(chokepoints)):
            c = chokepoints[i]
            if _ghosts_too_close(c, placed):
                continue
            placed.append(c)
            placed_fs = frozenset(placed)
            reach = _bfs_reachable(grid, start, placed_fs)
            if len(steps) < MAX_STEPS:
                steps.append(('try', c, placed.copy(), reach))
            remaining = chokepoints[i + 1:]
            if can_still_block(remaining, k_rem - 1, reach) and backtrack(i + 1, k_rem - 1, reach):
                return True
            placed.pop()
            placed_fs = frozenset(placed)
            reach = _bfs_reachable(grid, start, placed_fs)
            if len(steps) < MAX_STEPS:
                steps.append(('backtrack', c, placed.copy(), reach))
        return False

    initial_reach = _bfs_reachable(grid, start, frozenset())
    solution = None
    for k in range(1, len(chokepoints) + 1):
        placed.clear()
        placed_fs = frozenset()
        steps.clear()
        if backtrack(0, k, initial_reach):
            solution = placed.copy()
            steps.append(('found', solution))
            break

    return solution, steps
