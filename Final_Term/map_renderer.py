import pygame
import math
import random
from config import (
    get_best_font, 
    FONT_FAMILIES, 
    DEFAULT_MAZE, 
    START_CELL, 
    GOAL_CELL, 
    MAZE_ROWS, 
    MAZE_COLS
)
from path_renderer import draw_path

def is_cell_covered(r, c, placed_pacmans, grid):
    """Check if a cell is in the line of sight of any placed Pacman."""
    for pr, pc in placed_pacmans:
        if r == pr:
            # Check if wall in between
            min_c, max_c = min(c, pc), max(c, pc)
            has_wall = False
            for col in range(min_c + 1, max_c):
                if grid[r][col] == 2:
                    has_wall = True
                    break
            if not has_wall:
                return True
        elif c == pc:
            # Check if wall in between
            min_r, max_r = min(r, pr), max(r, pr)
            has_wall = False
            for row in range(min_r + 1, max_r):
                if grid[row][c] == 2:
                    has_wall = True
                    break
            if not has_wall:
                return True
    return False

# --- Drawing Helpers ---

def draw_pacman(screen, x, y, radius, mouth_angle, color=(254, 189, 17), facing_left=False):
    """Draw an animated yellow (or custom colored) Pacman circle with a mouth opening."""
    if mouth_angle <= 0:
        # Draw a full circle if mouth is closed
        pygame.draw.circle(screen, color, (int(x), int(y)), int(radius))
        # Add a small black eye
        eye_x = int(x - radius * 0.1) if facing_left else int(x + radius * 0.1)
        pygame.draw.circle(screen, (0, 0, 0), (eye_x, int(y - radius * 0.5)), 2)
        return

    # Convert angle to radians
    rad = math.radians(mouth_angle)
    
    # Adjust angles based on direction
    if facing_left:
        # Pacman moving left: mouth opens to the left
        start_angle = math.pi + rad
        end_angle = 3 * math.pi - rad
    else:
        # Pacman moving right: mouth opens to the right
        start_angle = rad
        end_angle = 2 * math.pi - rad
        
    # Start with the center point
    points = [(x, y)]
    
    # Generate points along the outer arc
    num_steps = 20
    for i in range(num_steps + 1):
        angle = start_angle + (end_angle - start_angle) * (i / num_steps)
        points.append((x + radius * math.cos(angle), y + radius * math.sin(angle)))
        
    # Close the polygon at the center
    points.append((x, y))
    
    pygame.draw.polygon(screen, color, points)
    # Add a small black eye
    eye_x = int(x - radius * 0.1) if facing_left else int(x + radius * 0.1)
    pygame.draw.circle(screen, (0, 0, 0), (eye_x, int(y - radius * 0.5)), 2)


def draw_cherry(screen, x, y, radius):
    """Draw a nice cherry (goal fruit) with red body and green stem."""
    # Draw red circle
    pygame.draw.circle(screen, (244, 67, 54), (int(x - radius * 0.3), int(y + radius * 0.2)), int(radius * 0.6))
    pygame.draw.circle(screen, (211, 47, 47), (int(x + radius * 0.3), int(y + radius * 0.2)), int(radius * 0.55))
    
    # Draw green stems
    pygame.draw.arc(screen, (76, 175, 80), (x - radius * 0.6, y - radius * 0.8, radius * 1.2, radius), 
                    math.pi * 0.2, math.pi * 0.8, 2)
    # Stem joint
    pygame.draw.circle(screen, (76, 175, 80), (int(x), int(y - radius * 0.7)), 2)


def draw_crown(screen, x, y, size):
    """Draw a golden crown representing a Chess Queen."""
    cx, cy = x + size // 2, y + size // 2
    r = size // 3
    # Draw crown polygon
    points = [
        (cx - r, cy + r),          # Bottom Left
        (cx - r, cy - r * 0.5),    # Left peak start
        (cx - r * 0.6, cy - r),    # Left tip
        (cx - r * 0.2, cy - r * 0.2), # Inner dip left
        (cx, cy - r * 1.1),        # Center tip (highest)
        (cx + r * 0.2, cy - r * 0.2), # Inner dip right
        (cx + r * 0.6, cy - r),    # Right tip
        (cx + r, cy - r * 0.5),    # Right peak start
        (cx + r, cy + r),          # Bottom Right
    ]
    pygame.draw.polygon(screen, (255, 215, 0), points) # Gold fill
    pygame.draw.polygon(screen, (255, 165, 0), points, 2) # Orange outline
    # Bottom band decoration
    pygame.draw.line(screen, (244, 67, 54), (cx - r * 0.8, cy + r * 0.7), (cx + r * 0.8, cy + r * 0.7), 2)


def draw_ghost(screen, x, y, size, color):
    r = size // 2
    # Body: semi-circle on top
    pygame.draw.circle(screen, color, (x, y - r // 4), r)
    # Rectangle for lower part
    pygame.draw.rect(screen, color, (x - r, y - r // 4 + 1, size, r // 2 + 2))
    # Wavy bottom: 3 triangles
    points1 = [(x - r, y + r // 4), (x - r * 0.6, y + r), (x - r * 0.3, y + r // 4)]
    points2 = [(x - r * 0.3, y + r // 4), (x, y + r), (x + r * 0.3, y + r // 4)]
    points3 = [(x + r * 0.3, y + r // 4), (x + r * 0.6, y + r), (x + r, y + r // 4)]
    pygame.draw.polygon(screen, color, points1)
    pygame.draw.polygon(screen, color, points2)
    pygame.draw.polygon(screen, color, points3)
    # Eyes (white circle, blue pupil looking right)
    pygame.draw.circle(screen, (255, 255, 255), (x - r // 2.5, y - r // 4), 4)
    pygame.draw.circle(screen, (33, 150, 243), (x - r // 3.5, y - r // 4), 2)
    pygame.draw.circle(screen, (255, 255, 255), (x + r // 2.5, y - r // 4), 4)
    pygame.draw.circle(screen, (33, 150, 243), (x + r // 2.0, y - r // 4), 2)


# --- Maze Renderer Class ---

class MazeVisualizer:
    def __init__(self, x_offset, y_offset, cell_size=32):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.cell_size = cell_size
        self.grid = [row.copy() for row in DEFAULT_MAZE]
        self.pacman_mouth_angle = 30
        self.mouth_closing = True
        
    def reset(self):
        self.grid = [row.copy() for row in DEFAULT_MAZE]
        
    def draw(self, screen, visited, frontier, current, path, is_adversarial=False, is_csp=False, placed_pacmans=[], found=False, is_sensorless=False, unknown_mask=None):
        # Update Pacman mouth animation
        if self.mouth_closing:
            self.pacman_mouth_angle -= 2
            if self.pacman_mouth_angle <= 5:
                self.mouth_closing = False
        else:
            self.pacman_mouth_angle += 2
            if self.pacman_mouth_angle >= 40:
                self.mouth_closing = True
                
        # Draw Walls and Paths
        for r in range(len(self.grid)):
            for c in range(len(self.grid[0])):
                cell_x = self.x_offset + c * self.cell_size
                cell_y = self.y_offset + r * self.cell_size
                
                val = self.grid[r][c]
                # Treat visited cells as empty path (0)
                if (r, c) in visited:
                    val = 0
                    
                if val == 2:
                    # Draw a nice double-wall styled like retro Pacman
                    # Dark blue block background
                    pygame.draw.rect(screen, (10, 20, 50), (cell_x, cell_y, self.cell_size, self.cell_size))
                    # Neon blue outline
                    pygame.draw.rect(screen, (33, 150, 243), (cell_x + 2, cell_y + 2, self.cell_size - 4, self.cell_size - 4), 1)
                else:
                    # Path background
                    pygame.draw.rect(screen, (10, 15, 30), (cell_x, cell_y, self.cell_size, self.cell_size))
                    
                    # Pac-dot in the center (only draw if it is food (1) and not special/covered)
                    is_special_cell = (r, c) == START_CELL or (is_adversarial and (r, c) == GOAL_CELL) or (is_csp and (r, c) in placed_pacmans)
                    is_covered = False
                    if val == 1 and not is_special_cell and not is_covered:
                        pygame.draw.circle(screen, (248, 187, 208), (cell_x + self.cell_size // 2, cell_y + self.cell_size // 2), 3)
                        
                    if is_sensorless and (r, c) == (5, 7):
                        pygame.draw.rect(screen, (76, 175, 80), (cell_x + 2, cell_y + 2, self.cell_size - 4, self.cell_size - 4))
                        font = get_best_font(FONT_FAMILIES, 12, bold=True)
                        lbl_exit = font.render("OUT", True, (255, 255, 255))
                        screen.blit(lbl_exit, (cell_x + self.cell_size//2 - lbl_exit.get_width()//2, cell_y + self.cell_size//2 - lbl_exit.get_height()//2))
                        
                if unknown_mask and (r, c) in unknown_mask:
                    pygame.draw.rect(screen, (0, 0, 0), (cell_x, cell_y, self.cell_size, self.cell_size))
                        
        if is_csp:
            # Draw placed Ghosts
            for pr, pc in placed_pacmans:
                px = self.x_offset + pc * self.cell_size + self.cell_size // 2
                py = self.y_offset + pr * self.cell_size + self.cell_size // 2
                draw_ghost(screen, px, py, self.cell_size - 4, (244, 67, 54))
            # Draw current active placement cell candidate (cyan block)
            if current:
                curr_x = self.x_offset + current[1] * self.cell_size
                curr_y = self.y_offset + current[0] * self.cell_size
                pygame.draw.rect(screen, (0, 229, 255), (curr_x + 1, curr_y + 1, self.cell_size - 2, self.cell_size - 2), 2)
        else:
            # Draw Visited Cells (Semi-transparent cyan)
            visited_surf = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            pygame.draw.rect(visited_surf, (0, 229, 255, 60), (1, 1, self.cell_size - 2, self.cell_size - 2))
            for r, c in visited:
                if (r, c) != START_CELL and (r, c) != GOAL_CELL:
                    screen.blit(visited_surf, (self.x_offset + c * self.cell_size, self.y_offset + r * self.cell_size))
                    
            # Draw Frontier Cells (Semi-transparent pink/orange)
            if not is_adversarial:
                frontier_surf = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                pygame.draw.rect(frontier_surf, (255, 64, 129, 80), (1, 1, self.cell_size - 2, self.cell_size - 2))
                for item in frontier:
                    # item might be coordinate tuple or a heap element, handle both
                    r, c = item if isinstance(item, tuple) else item
                    if (r, c) != START_CELL and (r, c) != GOAL_CELL:
                        screen.blit(frontier_surf, (self.x_offset + c * self.cell_size, self.y_offset + r * self.cell_size))
                    
            # Draw current active node being expanded (Green square border)
            if current and current != START_CELL and current != GOAL_CELL:
                curr_x = self.x_offset + current[1] * self.cell_size
                curr_y = self.y_offset + current[0] * self.cell_size
                pygame.draw.rect(screen, (0, 230, 118), (curr_x + 1, curr_y + 1, self.cell_size - 2, self.cell_size - 2), 2)
                
            # Reconstructed Path drawing
            draw_path(screen, path, self.cell_size, self.x_offset, self.y_offset)
                
            # Draw Start (Pacman)
            pacman_cell = current if current else START_CELL
            start_cx = self.x_offset + pacman_cell[1] * self.cell_size + self.cell_size // 2
            start_cy = self.y_offset + pacman_cell[0] * self.cell_size + self.cell_size // 2
            # Animate rotation if moving
            draw_pacman(screen, start_cx, start_cy, self.cell_size // 2 - 2, self.pacman_mouth_angle)
    
            # Draw Adversarial Opponent Pacman at GOAL_CELL or dynamic position from frontier
            if is_adversarial:
                opp_pos = frontier[0] if (frontier and isinstance(frontier, list) and len(frontier) > 0) else GOAL_CELL
                goal_cx = self.x_offset + opp_pos[1] * self.cell_size + self.cell_size // 2
                goal_cy = self.y_offset + opp_pos[0] * self.cell_size + self.cell_size // 2
                # Draw as Red Pacman facing left
                draw_pacman(screen, goal_cx, goal_cy, self.cell_size // 2 - 2, self.pacman_mouth_angle, color=(244, 67, 54), facing_left=True)



# --- N-Queens Chessboard Renderer Class ---

class ChessboardVisualizer:
    def __init__(self, x_offset, y_offset, board_size=8, cell_size=55):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.board_size = board_size
        self.cell_size = cell_size
        self.label_font = get_best_font(FONT_FAMILIES, 18, bold=True)
        
    def draw(self, screen, board, current_col):
        # Draw Chessboard grid (alternate light and dark cells)
        for r in range(self.board_size):
            for c in range(self.board_size):
                cell_x = self.x_offset + c * self.cell_size
                cell_y = self.y_offset + r * self.cell_size
                
                # Checkered pattern color
                if (r + c) % 2 == 0:
                    bg_color = (25, 35, 60) # Dark cell
                else:
                    bg_color = (40, 55, 85) # Light cell
                    
                pygame.draw.rect(screen, bg_color, (cell_x, cell_y, self.cell_size, self.cell_size))
                # Soft grid border
                pygame.draw.rect(screen, (10, 15, 25), (cell_x, cell_y, self.cell_size, self.cell_size), 1)
                
        # Draw Labels (Row indices 1-8, Col indices A-H)
        for i in range(self.board_size):
            # Row labels (left side)
            lbl_r = self.label_font.render(str(i + 1), True, (120, 140, 180))
            screen.blit(lbl_r, (self.x_offset - 20, self.y_offset + i * self.cell_size + self.cell_size // 2 - lbl_r.get_height() // 2))
            
            # Column labels (bottom side)
            lbl_c = self.label_font.render(chr(65 + i), True, (120, 140, 180))
            screen.blit(lbl_c, (self.x_offset + i * self.cell_size + self.cell_size // 2 - lbl_c.get_width() // 2, 
                               self.y_offset + self.board_size * self.cell_size + 8))
            
        # Draw placed Queens and highlight conflicts
        # Keep track of conflict rows and diagonals
        conflict_positions = set()
        for c1 in range(self.board_size):
            r1 = board[c1]
            if r1 == -1:
                continue
            for c2 in range(c1 + 1, self.board_size):
                r2 = board[c2]
                if r2 == -1:
                    continue
                # Conflict check
                if r1 == r2 or abs(r1 - r2) == abs(c1 - c2):
                    conflict_positions.add(c1)
                    conflict_positions.add(c2)
                    
        # Render cell overlays and Queens
        for col in range(self.board_size):
            row = board[col]
            if row != -1:
                cell_x = self.x_offset + col * self.cell_size
                cell_y = self.y_offset + row * self.cell_size
                
                # If in conflict, highlight in semi-transparent red
                if col in conflict_positions:
                    red_overlay = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    red_overlay.fill((244, 67, 54, 100)) # Transparent red
                    screen.blit(red_overlay, (cell_x, cell_y))
                    pygame.draw.rect(screen, (244, 67, 54), (cell_x, cell_y, self.cell_size, self.cell_size), 2)
                elif col == current_col:
                    # Highlight active column in green
                    green_overlay = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    green_overlay.fill((76, 175, 80, 80))
                    screen.blit(green_overlay, (cell_x, cell_y))
                    pygame.draw.rect(screen, (76, 175, 80), (cell_x, cell_y, self.cell_size, self.cell_size), 2)
                    
                # Draw Pacman instead of Queen
                cx = cell_x + self.cell_size // 2
                cy = cell_y + self.cell_size // 2
                draw_pacman(screen, cx, cy, self.cell_size // 2 - 4, 30)
                
        # Draw red border on current column if it has no placed queen yet
        if current_col != -1 and current_col < self.board_size and board[current_col] == -1:
            col_x = self.x_offset + current_col * self.cell_size
            pygame.draw.rect(screen, (0, 229, 255), (col_x, self.y_offset, self.cell_size, self.board_size * self.cell_size), 2)
