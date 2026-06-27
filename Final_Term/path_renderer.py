import pygame
from config import SHOW_PATH

def draw_path(screen, path, cell_size, x_offset, y_offset, color=(255, 255, 0), force=False):
    """
    Draws the reconstructed path connecting cells on the screen.
    Visualizes if SHOW_PATH is enabled in config, or if force is True.
    """
    if not force and not SHOW_PATH:
        return
    if not path or len(path) < 2:
        return
        
    points = []
    for r, c in path:
        x = x_offset + c * cell_size + cell_size // 2
        y = y_offset + r * cell_size + cell_size // 2
        points.append((x, y))
        
    # Draw path connecting lines
    pygame.draw.lines(screen, color, False, points, 3)
    
    # Draw smaller dots on path vertices to make it look smooth and premium
    for pt in points:
        pygame.draw.circle(screen, color, pt, 4)
