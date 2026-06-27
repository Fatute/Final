from algorithms.visualizers import simple_backtracking, backtracking_ac3, backtracking_forward_checking
from config import MAZE_4, START_CELL, get_maze_goal

goal = get_maze_goal(MAZE_4)

for name, viz_fn in [
    ("Simple Backtracking", simple_backtracking),
    ("Backtracking + AC-3", backtracking_ac3),
    ("Backtracking + Forward Checking", backtracking_forward_checking)
]:
    print(f"Testing viz for: {name}")
    gen = viz_fn(MAZE_4, START_CELL, goal)
    steps_count = 0
    try:
        while True:
            val = next(gen)
            # In GUI, we unpack:
            # visited, frontier, current_node, path, found = val
            visited, frontier, current, path, found = val
            steps_count += 1
            if found:
                print(f"  -> Found solution: {path} at step {steps_count}")
    except StopIteration:
        print(f"  -> Finished generator. Total steps yielded: {steps_count}")
    except Exception as e:
        print(f"  -> ERROR in {name}: {e}")
        import traceback
        traceback.print_exc()
