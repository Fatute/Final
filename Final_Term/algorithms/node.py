class Node:
    def __init__(self, state, parent=None, g=0, h=0):
        self.state = state      # Coordinate tuple (row, col)
        self.parent = parent    # Pointer to parent Node
        self.g = g              # Cost from start to this node
        self.h = h              # Heuristic cost to goal
        self.f = g + h          # Total cost (g + h)
        
    def __lt__(self, other):
        return self.f < other.f
