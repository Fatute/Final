import pygame
import sys
import time
import math
import random

from ui import Button, Card, ParticleSystem, Transition
from config import (
    get_best_font,
    FONT_FAMILIES,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_TEXT,
    COLOR_MUTED,
    COLOR_RED,
    COLOR_PINK,
    COLOR_CYAN,
    COLOR_ORANGE,
    COLOR_YELLOW,
    COLOR_PURPLE,
    STATE_MAIN_MENU,
    STATE_SUB_MENU,
    STATE_VISUALIZER,
    SPEED_SLOW,
    SPEED_MEDIUM,
    SPEED_FAST,
    SPEED_INSTANT,
    SPEED_MAP,
    ALGO_INFO,
    START_CELL,
    GOAL_CELL,
    get_maze_goal
)
from map_renderer import MazeVisualizer, draw_pacman
import algorithms

# --- Initializations ---
pygame.init()
pygame.display.set_caption("Pacman Algorithm Laboratory")

# Window Dimensions
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Clock
clock = pygame.time.Clock()

# --- Animating Ghost Drawing Helper ---
def draw_ghost_menu(screen, x, y, size, color, scared=False):
    r = size // 2
    # Draw body: semi-circle on top
    pygame.draw.circle(screen, color, (x, y - r // 4), r)
    # Rectangle for the lower part
    pygame.draw.rect(screen, color, (x - r, y - r // 4 + 1, size, r // 2 + 2))
    # Wavy bottom: 3 triangles/legs
    points1 = [(x - r, y + r // 4), (x - r * 0.6, y + r), (x - r * 0.3, y + r // 4)]
    points2 = [(x - r * 0.3, y + r // 4), (x, y + r), (x + r * 0.3, y + r // 4)]
    points3 = [(x + r * 0.3, y + r // 4), (x + r * 0.6, y + r), (x + r, y + r // 4)]
    pygame.draw.polygon(screen, color, points1)
    pygame.draw.polygon(screen, color, points2)
    pygame.draw.polygon(screen, color, points3)
    
    if scared:
        # Scared ghost eyes (White circle, blue pupil)
        pygame.draw.circle(screen, (255, 255, 255), (x - r // 3, y - r // 4), 3)
        pygame.draw.circle(screen, (255, 255, 255), (x + r // 3, y - r // 4), 3)
        # Wiggly mouth
        pygame.draw.line(screen, (255, 255, 255), (x - r // 2, y + r // 6), (x - r // 4, y), 2)
        pygame.draw.line(screen, (255, 255, 255), (x - r // 4, y), (x, y + r // 6), 2)
        pygame.draw.line(screen, (255, 255, 255), (x, y + r // 6), (x + r // 4, y), 2)
        pygame.draw.line(screen, (255, 255, 255), (x + r // 4, y), (x + r // 2, y + r // 6), 2)
    else:
        # Regular eyes looking right
        pygame.draw.circle(screen, (255, 255, 255), (x - r // 2.5, y - r // 4), 5)
        pygame.draw.circle(screen, (33, 150, 243), (x - r // 3.5, y - r // 4), 2)
        pygame.draw.circle(screen, (255, 255, 255), (x + r // 2.5, y - r // 4), 5)
        pygame.draw.circle(screen, (33, 150, 243), (x + r // 2.0, y - r // 4), 2)

class Application:
    def __init__(self):
        self.state = STATE_MAIN_MENU
        self.particles = ParticleSystem(SCREEN_WIDTH, SCREEN_HEIGHT, 40)
        self.transition = Transition(10)
        
        # Menu Selection Variables
        self.selected_group = None
        self.selected_algo = None
        
        # Load fonts
        self.title_font = get_best_font(FONT_FAMILIES, 54, bold=True)
        self.subtitle_font = get_best_font(FONT_FAMILIES, 24)
        self.stats_font = get_best_font(FONT_FAMILIES, 16)
        
        # Animated characters in title
        self.pac_x = 100
        self.pac_mouth_angle = 30
        self.pac_mouth_closing = True
        
        # Initialize submenus
        self.setup_ui()
        
        # Visualizer State
        self.visualizer_maze = MazeVisualizer(30, 150, 32)
        
        # Simulation Running variables
        self.is_running = False
        self.speed = SPEED_MEDIUM
        self.last_step_time = 0
        self.generator = None
        
        # Stats
        self.visited = set()
        self.frontier = []
        self.current_node = None
        self.path = None
        self.found = False
        self.has_run = False
        
        # CSP Stats
        self.csp_backtracks = 0
        self.csp_steps = 0
        
    def setup_ui(self):
        # --- MAIN MENU BUTTONS ---
        # 7 buttons: 6 categories + 1 exit
        self.main_buttons = [
            Button(150, 250, 320, 70, "TÌM KIẾM KHÔNG CÓ THÔNG TIN\n(Uninformed Search)", COLOR_RED, (255, 100, 100)),
            Button(150, 350, 320, 70, "TÌM KIẾM CÓ THÔNG TIN\n(Informed Search)", COLOR_PINK, (255, 120, 180)),
            Button(150, 450, 320, 70, "TÌM KIẾM CỤC BỘ\n(Local Search)", COLOR_CYAN, (150, 230, 255)),
            Button(550, 250, 320, 70, "TÌM KIẾM MÙ\n(Blind Search)", COLOR_ORANGE, (255, 180, 100)),
            Button(550, 350, 320, 70, "TÌM KIẾM RÀNG BUỘC\n(Constraint Satisfaction)", COLOR_YELLOW, (255, 230, 100), text_color=(15, 20, 30)),
            Button(550, 450, 320, 70, "THUẬT TOÁN ĐỐI KHÁNG\n(Adversarial Search)", COLOR_PURPLE, (220, 130, 255)),
            Button(352, 570, 320, 70, "EXIT\n(Thoát)", (60, 70, 90), (140, 160, 180))
        ]
        
        # Map indices to category names
        self.category_names = {
            0: "Tìm kiếm không có thông tin",
            1: "Tìm kiếm có thông tin",
            2: "Tìm kiếm cục bộ",
            3: "Tìm kiếm mù",
            4: "Tìm kiếm ràng buộc",
            5: "Thuật toán đối kháng"
        }
        
        # --- SUBMENU BUTTONS & CARDS ---
        self.sub_buttons = []
        self.sub_card = None
        self.create_submenu_buttons()
        
        # --- VISUALIZER BUTTONS ---
        # Stacked on the right panel
        self.viz_buttons = [
            Button(750, 380, 230, 45, "Chạy / Tạm Dừng", (76, 175, 80), (105, 240, 174)),
            Button(750, 440, 230, 45, "Chạy Từng Bước", (0, 188, 212), (128, 222, 234)),
            Button(750, 500, 230, 45, "Tốc Độ: Vừa", (230, 81, 0), (255, 183, 77)),
            Button(750, 560, 230, 45, "Đặt Lại (Reset)", (21, 101, 192), (100, 181, 246)),
            Button(750, 620, 230, 45, "Trở Lại Menu", (211, 47, 47), (255, 138, 128))
        ]
        
    def create_submenu_buttons(self):
        # We will dynamically recreate these when entering a sub-menu state based on selected_group
        pass
        
    def enter_submenu(self, group_index):
        self.selected_group = group_index
        group_name = self.category_names[group_index]
        
        # Define 3 algorithm names for each group
        if group_index == 0:
            algos = ["BFS", "DFS", "UCS"]
            desc = "Các thuật toán tìm kiếm cơ bản. Chúng không có tri thức bổ sung về mục tiêu mà chỉ mở rộng không gian tìm kiếm một cách hệ thống dựa theo cấu trúc dữ liệu."
            card_color = COLOR_RED
        elif group_index == 1:
            algos = ["Greedy Best-First", "A*", "IDA*"]
            desc = "Sử dụng tri thức bổ sung dưới dạng hàm heuristic h(n) để ước lượng khoảng cách từ trạng thái hiện tại đến Goal, giúp định hướng tìm kiếm thông minh và hiệu quả hơn."
            card_color = COLOR_PINK
        elif group_index == 2:
            algos = ["Hill Climbing", "Beam Search", "Simulated Annealing"]
            desc = "Các giải thuật tối ưu hóa cục bộ. Chúng không lưu vết cây tìm kiếm mà chỉ cập nhật trạng thái hiện tại dựa trên hàng xóm. Phù hợp cho không gian trạng thái cực lớn."
            card_color = COLOR_CYAN
        elif group_index == 3:
            algos = ["Sensorless BFS", "Partial BFS", "AND-OR Search"]
            desc = "Dạng thuật toán tìm kiếm mù (uninformed). Sensorless BFS lập kế hoạch để các trạng thái niềm tin cùng đi tới đích; Partial BFS giải quyết khi chỉ biết 1 phần bản đồ; AND-OR Search dò tìm trong môi trường không tất định."
            card_color = COLOR_ORANGE
        elif group_index == 4:
            algos = ["Simple Backtracking", "Backtracking + AC-3", "Backtracking + Forward Checking"]
            desc = "Ghost Blocking CSP: tìm tập ghost nhỏ nhất để chặn TOÀN BỘ đường đi từ Pacman đến food. Ghost không được đặt trong vòng 1 ô quanh điểm sinh. So sánh 3 chiến lược: Backtracking cơ bản, AC-3 (Arc Consistency) và Forward Checking."
            card_color = COLOR_YELLOW
        else: # 5
            algos = ["Minimax", "Alpha-Beta Pruning", "Expectimax"]
            desc = "Giải thuật đối kháng mô phỏng trò chơi giữa Pacman (MAX) cố gắng ăn Cherry và Ghost (MIN) cố gắng đuổi bắt Pacman trên lưới mê cung đồ thị."
            card_color = COLOR_PURPLE
            
        self.sub_buttons = [
            Button(80, 200, 350, 70, f"{algos[0]}", card_color, (255, 255, 255), text_color=(255, 255, 255)),
            Button(80, 300, 350, 70, f"{algos[1]}", card_color, (255, 255, 255), text_color=(255, 255, 255)),
            Button(80, 400, 350, 70, f"{algos[2]}", card_color, (255, 255, 255), text_color=(255, 255, 255)),
            Button(80, 520, 350, 70, "Trở Lại (Back)", (60, 70, 90), (140, 160, 180))
        ]
        
        # Custom button colors for gold theme to keep black text readable
        if group_index == 4:
            for b in self.sub_buttons[:3]:
                b.text_color = (15, 20, 30)
                
        self.sub_card = Card(480, 200, 460, 390, f"Nhóm: {group_name}", desc, border_color=card_color)
        
        self.state = STATE_SUB_MENU
        self.transition.fade_in()
        
    def enter_visualizer(self, algo_name):
        self.selected_algo = algo_name
        self.is_running = False
        self.reset_simulation()
        
        # Update speed button text
        self.viz_buttons[2].text = f"Tốc Độ: {self.speed}"
        
        self.state = STATE_VISUALIZER
        self.transition.fade_in()
        
    def reset_simulation(self):
        self.visited = set()
        self.frontier = []
        self.current_node = None
        self.path = None
        self.found = False
        self.has_run = False
        self.csp_backtracks = 0
        self.csp_steps = 0
        self.p1_score = 0
        self.p2_score = 0
        self.path_b1 = None
        self.path_b2 = None
        
        # Get active maze based on selected group
        from config import MAZE_0, MAZE_1, MAZE_2, MAZE_3, MAZE_4, MAZE_5, DEFAULT_MAZE
        group = self.selected_group
        if group == 0:
            active_maze = MAZE_0
        elif group == 1:
            active_maze = MAZE_1
        elif group == 2:
            active_maze = MAZE_2
        elif group == 3:
            active_maze = MAZE_3
        elif group == 4:
            active_maze = MAZE_4
        elif group == 5:
            active_maze = MAZE_5
        else:
            active_maze = DEFAULT_MAZE

        active_maze_goal = get_maze_goal(active_maze)

        # Instantiate the correct generator
        algo = self.selected_algo
        if algo == "BFS":
            self.generator = algorithms.bfs(active_maze, START_CELL, active_maze_goal)
        elif algo == "DFS":
            self.generator = algorithms.dfs(active_maze, START_CELL, active_maze_goal)
        elif algo == "UCS":
            self.generator = algorithms.ucs(active_maze, START_CELL, active_maze_goal)
        elif algo == "Greedy Best-First":
            self.generator = algorithms.greedy_best_first(active_maze, START_CELL, active_maze_goal)
        elif algo == "A*":
            self.generator = algorithms.a_star(active_maze, START_CELL, active_maze_goal)
        elif algo == "IDA*":
            self.generator = algorithms.ida_star(active_maze, START_CELL, active_maze_goal)
        elif algo == "Hill Climbing":
            self.generator = algorithms.hill_climbing(active_maze, START_CELL, GOAL_CELL)
        elif algo == "Simulated Annealing":
            self.generator = algorithms.simulated_annealing(active_maze, START_CELL, active_maze_goal)
        elif algo == "Beam Search":
            self.generator = algorithms.beam_search(active_maze, START_CELL, active_maze_goal)
        elif algo == "Sensorless BFS":
            grid_1 = [row.copy() for row in active_maze_goal]
            grid_1[5][7] = 0
            
            grid_2 = [row.copy() for row in active_maze_goal]
            grid_2[5][7] = 0
            grid_2[2][2] = 0 # Break a wall
            grid_2[2][3] = 0 # Break a wall
            grid_2[3][4] = 2 # Add a wall
            
            self.grid_1 = grid_1
            self.grid_2 = grid_2
            self.generator = algorithms.sensorless_bfs(grid_1, grid_2, START_CELL, (1, 3), (5, 7))
        elif algo == "Partial BFS":
            grid_1 = [row.copy() for row in active_maze_goal]
            grid_1[5][7] = 0
            grid_1[3][4] = 2 # Block middle path
            grid_1[1][4] = 2 # Block top path in True Map (so it must go bottom)
            
            grid_2 = [row.copy() for row in active_maze_goal]
            grid_2[5][7] = 0
            grid_2[3][4] = 2 # Block middle path
            grid_2[5][3] = 2 # Block bottom path in Belief 1 (so it must go top)
            
            self.grid_1 = grid_1
            self.grid_2 = grid_2
            
            self.unknown_mask = set()
            for r in range(len(grid_1)):
                for c in range(len(grid_1[0])):
                    if r >= 4 or c >= 4:
                        self.unknown_mask.add((r, c))
                        
            self.generator = algorithms.partial_bfs(grid_1, grid_2, START_CELL, (5, 7))
        elif algo == "AND-OR Search":
            grid_1 = [row.copy() for row in active_maze_goal]
            grid_1[5][7] = 0 # Open exit
            self.grid_1 = grid_1
            self.generator = algorithms.and_or_search(grid_1, START_CELL, (5, 7))
        elif algo == "Simple Backtracking":
            self.generator = algorithms.simple_backtracking(active_maze, START_CELL, GOAL_CELL)
        elif algo == "Backtracking + AC-3":
            self.generator = algorithms.backtracking_ac3(active_maze, START_CELL, GOAL_CELL)
        elif algo == "Backtracking + Forward Checking":
            self.generator = algorithms.backtracking_forward_checking(active_maze, START_CELL, GOAL_CELL)
        elif algo == "Minimax":
            self.generator = algorithms.minimax_search(active_maze, START_CELL, active_maze_goal)
        elif algo == "Alpha-Beta Pruning":
            self.generator = algorithms.alphabeta_search(active_maze, START_CELL, active_maze_goal)
        elif algo == "Expectimax":
            self.generator = algorithms.expectimax_search(active_maze, START_CELL, active_maze_goal)
            
        if algo in ["Sensorless BFS", "Partial BFS", "AND-OR Search"]:
            self.visualizer_maze.grid = self.grid_1
        else:
            self.visualizer_maze.grid = [row.copy() for row in active_maze]
        
        # Calculate dynamic centering offsets based on algorithm
        if algo in ["Sensorless BFS", "Partial BFS"]:  # Multiple maps
            self.visualizer_maze.cell_size = 32
            self.visualizer_maze.x_offset = 30
            self.visualizer_maze.y_offset = 150
        else:  # All other groups: center the maze
            cols = len(active_maze[0])
            rows = len(active_maze)
            # Available display area: width 690 (from x=30 to 720), height 490 (from y=150 to 640)
            max_cell_w = 690 // cols
            max_cell_h = 490 // rows
            cell_size = min(64, min(max_cell_w, max_cell_h))
            
            self.visualizer_maze.cell_size = cell_size
            self.visualizer_maze.x_offset = 30 + (690 - cols * cell_size) // 2
            self.visualizer_maze.y_offset = 150 + (490 - rows * cell_size) // 2
        
    def step_simulation(self):
        """Execute one step of the generator."""
        if not self.generator:
            return False
            
        self.has_run = True
        try:
            val = next(self.generator)
            
            # Save previous path for backtrack counting in CSP
            prev_path = self.path.copy() if self.path else []
            
            # All algorithms yield standard pathfinding structure (visited, frontier, current, path, found)
            if self.selected_algo in ["Sensorless BFS", "Partial BFS"]:
                self.visited, self.frontier, self.current_node, self.path, self.found, self.path_b1, self.path_b2 = val
            elif self.selected_group == 5:
                self.visited, self.frontier, self.current_node, self.path, self.found, self.p1_score, self.p2_score = val
            else:
                self.visited, self.frontier, self.current_node, self.path, self.found = val
            
            if self.selected_group == 4:
                self.csp_steps += 1
                if self.path and len(self.path) < len(prev_path):
                    self.csp_backtracks += 1
                        
            return True
        except StopIteration:
            # Done
            self.is_running = False
            if self.selected_group == 5 and self.path:
                print("Đường đi tốt nhất của Pacman 1:", self.path)
            return False
            
    def update(self):
        self.particles.update()
        self.transition.update()
        
        # Handle automatic simulation stepping
        if self.is_running and self.transition.is_done():
            now = pygame.time.get_ticks()
            delay = SPEED_MAP[self.speed]
            
            if delay == 0:
                # Instant mode: run multiple steps in a single frame to prevent infinite loops but run fast
                steps_per_frame = 50 if self.selected_group == 4 else 5
                for _ in range(steps_per_frame):
                    if not self.step_simulation():
                        break
            elif now - self.last_step_time >= delay:
                self.step_simulation()
                self.last_step_time = now
                
        # Main Menu header Pacman animation
        if self.state == STATE_MAIN_MENU:
            if self.pac_mouth_closing:
                self.pac_mouth_angle -= 3
                if self.pac_mouth_angle <= 5:
                    self.pac_mouth_closing = False
            else:
                self.pac_mouth_angle += 3
                if self.pac_mouth_angle >= 40:
                    self.pac_mouth_closing = True
            # Wrap around
            self.pac_x = (self.pac_x + 3) % (SCREEN_WIDTH + 200)

    def draw(self):
        screen.fill(COLOR_BG)
        self.particles.draw(screen)
        
        if self.state == STATE_MAIN_MENU:
            self.draw_main_menu()
        elif self.state == STATE_SUB_MENU:
            self.draw_submenu()
        elif self.state == STATE_VISUALIZER:
            self.draw_visualizer()
            
        self.transition.draw(screen)
        pygame.display.flip()
        
    def draw_main_menu(self):
        # Draw Pacman lab title (Retro Neon)
        title_surf = self.title_font.render("PAC-MAN AI SEARCH LAB", True, COLOR_YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 70))
        screen.blit(title_surf, title_rect)
        
        subtitle_surf = self.subtitle_font.render("Phòng Thí Nghiệm Giải Thuật Tìm Kiếm", True, COLOR_MUTED)
        sub_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(subtitle_surf, sub_rect)
        
        # Separator Line
        pygame.draw.line(screen, (33, 150, 243), (100, 150), (924, 150), 2)
        
        # Header animated characters
        # Pacman chasing a blue scared ghost, followed by a red ghost chasing Pacman
        px = self.pac_x - 100
        # 1. Scared Ghost (chased by Pacman)
        draw_ghost_menu(screen, int(px + 120), 180, 32, (33, 150, 243), scared=True)
        # 2. Pacman
        pygame.draw.circle(screen, (10, 15, 30), (int(px), 180), 18) # clear background trail
        draw_pacman(screen, px, 180, 18, self.pac_mouth_angle)
        # 3. Blinky Red Ghost (chasing Pacman)
        draw_ghost_menu(screen, int(px - 100), 180, 32, COLOR_RED, scared=False)
        
        # Draw Buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.main_buttons:
            button.update(mouse_pos)
            button.draw(screen)
            
    def draw_submenu(self):
        # Category Title
        title_text = self.category_names[self.selected_group].upper()
        title_surf = self.title_font.render(title_text, True, COLOR_YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(title_surf, title_rect)
        
        sub_surf = self.subtitle_font.render("Chọn một thuật toán để bắt đầu mô phỏng trực quan", True, COLOR_MUTED)
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 110))
        screen.blit(sub_surf, sub_rect)
        
        pygame.draw.line(screen, (33, 150, 243), (100, 140), (924, 140), 2)
        
        # Draw Buttons & Card
        mouse_pos = pygame.mouse.get_pos()
        for button in self.sub_buttons:
            button.update(mouse_pos)
            button.draw(screen)
            
        if self.sub_card:
            self.sub_card.draw(screen)
            
    def draw_visualizer(self):
        # Title
        title_text = f"MÔ PHỎNG: {self.selected_algo.upper()}"
        title_surf = self.title_font.render(title_text, True, COLOR_YELLOW)
        screen.blit(title_surf, (30, 20))
        
        # Back line
        pygame.draw.line(screen, (33, 150, 243), (30, 80), (994, 80), 2)
        
        # Main Visualizer Drawing Area
        if self.selected_algo in ["Sensorless BFS", "Partial BFS"]:
            is_partial = self.selected_algo == "Partial BFS"
            
            if is_partial:
                # Partial Map (Top Left)
                self.visualizer_maze.grid = self.grid_1
                self.visualizer_maze.x_offset = 60
                self.visualizer_maze.y_offset = 120
                self.visualizer_maze.draw(screen, self.visited, self.frontier, self.current_node, self.path, found=self.found, is_sensorless=True, unknown_mask=self.unknown_mask)
                
                # True State Map (Top Right)
                self.visualizer_maze.grid = self.grid_1
                self.visualizer_maze.x_offset = 440
                self.visualizer_maze.y_offset = 120
                self.visualizer_maze.draw(screen, self.visited, self.frontier, self.current_node, self.path, found=self.found, is_sensorless=True)
            else:
                # True State Map (Top Center)
                self.visualizer_maze.grid = self.grid_1
                self.visualizer_maze.x_offset = 250
                self.visualizer_maze.y_offset = 120
                self.visualizer_maze.draw(screen, self.visited, self.frontier, self.current_node, self.path, found=self.found, is_sensorless=True)
            
            # Belief 1 Map (Bottom Left)
            self.visualizer_maze.grid = self.grid_2
            self.visualizer_maze.x_offset = 60
            self.visualizer_maze.y_offset = 380
            curr_b1 = self.path_b2[-1] if self.path_b2 else (START_CELL if is_partial else (1, 3))
            self.visualizer_maze.draw(screen, set(self.path_b2) if self.path_b2 else set(), [], curr_b1, self.path_b2, found=self.found, is_sensorless=True)
            
            # Belief 2 Map (Bottom Right)
            self.visualizer_maze.grid = self.grid_1
            self.visualizer_maze.x_offset = 440
            self.visualizer_maze.y_offset = 380
            curr_b2 = self.path_b1[-1] if self.path_b1 else START_CELL
            self.visualizer_maze.draw(screen, set(self.path_b1) if self.path_b1 else set(), [], curr_b2, self.path_b1, found=self.found, is_sensorless=True)
            
            # Labels
            maze_width = self.visualizer_maze.cell_size * len(self.visualizer_maze.grid[0])
            
            if is_partial:
                lbl_partial = self.stats_font.render("Góc nhìn của Pacman", True, COLOR_TEXT)
                screen.blit(lbl_partial, (60 + maze_width//2 - lbl_partial.get_width()//2, 120 - 30))
                lbl_true = self.stats_font.render("Trạng thái chính xác", True, COLOR_TEXT)
                screen.blit(lbl_true, (440 + maze_width//2 - lbl_true.get_width()//2, 120 - 30))
            else:
                lbl_true = self.stats_font.render("Trạng thái chính xác", True, COLOR_TEXT)
                screen.blit(lbl_true, (250 + maze_width//2 - lbl_true.get_width()//2, 120 - 30))
                
            lbl_b1 = self.stats_font.render("Trạng thái niềm tin 1", True, COLOR_TEXT)
            screen.blit(lbl_b1, (60 + maze_width//2 - lbl_b1.get_width()//2, 380 - 30))
            
            lbl_b2 = self.stats_font.render("Trạng thái niềm tin 2", True, COLOR_TEXT)
            screen.blit(lbl_b2, (440 + maze_width//2 - lbl_b2.get_width()//2, 380 - 30))
            
            # Bottom Info Card
            info = ALGO_INFO.get(self.selected_algo, {"title": self.selected_algo, "desc": ""})
            bottom_card = Card(30, 620, 672, 120, info["title"], info["desc"])
            bottom_card.draw(screen)
            
            # Reset offsets for other algorithms just in case
            self.visualizer_maze.x_offset = 30
            self.visualizer_maze.y_offset = 150
        else:
            self.visualizer_maze.draw(
                screen, self.visited, self.frontier, self.current_node, self.path, 
                is_adversarial=(self.selected_group == 5), 
                is_csp=(self.selected_group == 4), 
                placed_pacmans=self.path if self.path else [], 
                found=self.found
            )
            
            # Bottom Info Card
            info = ALGO_INFO.get(self.selected_algo, {"title": self.selected_algo, "desc": ""})
            bottom_card = Card(30, 645, 672, 110, info["title"], info["desc"])
            bottom_card.draw(screen)
            
        # Draw Control Buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.viz_buttons:
            button.update(mouse_pos)
            button.draw(screen)
            
        # Draw Stats Panel (Right side)
        stats_rect = pygame.Rect(750, 150, 230, 210)
        pygame.draw.rect(screen, (15, 23, 42, 220), stats_rect, border_radius=12)
        pygame.draw.rect(screen, (33, 150, 243), stats_rect, width=2, border_radius=12)
        
        stats_title = self.stats_font.render("TRẠNG THÁI", True, COLOR_YELLOW)
        screen.blit(stats_title, (750 + 20, 150 + 15))
        pygame.draw.line(screen, (40, 60, 80), (750 + 20, 150 + 40), (750 + 210, 150 + 40), 1)
        
        y_offset = 150 + 55
        
        if self.selected_group == 5:
            # Adversarial Stats
            status_text = "Đang chạy..." if self.is_running else ("Đã kết thúc!" if self.found else "Tạm dừng/Chưa chạy")
            stats_list = [
                f"Trạng thái: {status_text}",
                f"Đã duyệt (Visited): {len(self.visited)}",
                f"Pacman 1 ăn: {self.p1_score}",
                f"Pacman 2 ăn: {self.p2_score}"
            ]
        elif self.selected_group != 4:
            # Pathfinding Stats
            status_text = "Đang chạy..." if self.is_running else ("Đã tìm thấy!" if self.found else ("Không tìm thấy!" if self.has_run else "Tạm dừng/Chưa chạy"))
                
            stats_list = [
                f"Trạng thái: {status_text}",
                f"Đã duyệt (Visited): {len(self.visited)}",
                f"Hàng đợi (Frontier): {len(self.frontier)}",
                f"Độ dài đường đi: {len(self.path) if self.path else 0}",
                f"Tổng chi phí: {self.get_path_cost()}"
            ]
        else:
            # Blocking CSP Stats
            status_text = "Đang chạy..." if self.is_running else ("Đã chặn!" if self.found else ("Không thể chặn!" if self.has_run else "Tạm dừng/Chưa chạy"))
            stats_list = [
                f"Trạng thái: {status_text}",
                f"Số bước thử: {self.csp_steps}",
                f"Số lần quay lui: {self.csp_backtracks}",
                f"Số ma đã đặt: {len(self.path) if self.path else 0}",
                f"Ô còn đi được: {len(self.visited)}"
            ]
            
        for line in stats_list:
            lbl = self.stats_font.render(line, True, COLOR_MUTED if "Trạng thái" not in line else COLOR_TEXT)
            screen.blit(lbl, (750 + 20, y_offset))
            y_offset += 25
            
    def get_path_cost(self):
        return len(self.path) - 1 if self.path else 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if self.state == STATE_MAIN_MENU:
                for i, button in enumerate(self.main_buttons):
                    if button.handle_event(event):
                        if i == 6: # Exit
                            return False
                        elif i < 6:
                            self.transition.fade_out()
                            # Wait for fade_out to finish, then go to submenu
                            # To do this cleanly, we can trigger the state change on transition completion,
                            # but for simplicity, we do it and set a small transition trigger
                            self.enter_submenu(i)
                            
            elif self.state == STATE_SUB_MENU:
                for i, button in enumerate(self.sub_buttons):
                    if button.handle_event(event):
                        if i == 3: # Back
                            self.state = STATE_MAIN_MENU
                            self.transition.fade_in()
                        else:
                            # Reconstruct algorithm name
                            group = self.selected_group
                            if group == 0:
                                names = ["BFS", "DFS", "UCS"]
                            elif group == 1:
                                names = ["Greedy Best-First", "A*", "IDA*"]
                            elif group == 2:
                                names = ["Hill Climbing", "Beam Search", "Simulated Annealing"]
                            elif group == 3:
                                names = ["Sensorless BFS", "Partial BFS", "AND-OR Search"]
                            elif group == 4:
                                names = ["Simple Backtracking", "Backtracking + AC-3", "Backtracking + Forward Checking"]
                            else: # group == 5
                                names = ["Minimax", "Alpha-Beta Pruning", "Expectimax"]
                                
                            self.enter_visualizer(names[i])
                            
            elif self.state == STATE_VISUALIZER:
                # Viz buttons: Play/Pause, Step, Speed, Reset, Back
                if self.viz_buttons[0].handle_event(event): # Play/Pause
                    self.is_running = not self.is_running
                    
                elif self.viz_buttons[1].handle_event(event): # Step
                    self.is_running = False
                    self.step_simulation()
                    
                elif self.viz_buttons[2].handle_event(event): # Speed
                    # Toggle speed
                    speeds = [SPEED_SLOW, SPEED_MEDIUM, SPEED_FAST, SPEED_INSTANT]
                    curr_idx = speeds.index(self.speed)
                    self.speed = speeds[(curr_idx + 1) % len(speeds)]
                    self.viz_buttons[2].text = f"Tốc Độ: {self.speed}"
                    
                elif self.viz_buttons[3].handle_event(event): # Reset
                    self.reset_simulation()
                    
                elif self.viz_buttons[4].handle_event(event): # Back
                    self.is_running = False
                    self.enter_submenu(self.selected_group)
                    
        return True

# --- Main Game Loop ---
def main():
    app = Application()
    running = True
    while running:
        app.update()
        app.draw()
        running = app.handle_events()
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
