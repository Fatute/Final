import pygame

# --- Font Helper ---
def get_best_font(names, size, bold=False, italic=False):
    """Attempt to load system fonts in order of preference, fallback to default Pygame font."""
    for name in names:
        try:
            return pygame.font.SysFont(name, size, bold=bold, italic=italic)
        except:
            continue
    return pygame.font.Font(None, size)

FONT_FAMILIES = ['Times New Roman', 'timesnewroman', 'Times']

# --- Window Dimensions ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# --- Colors ---
COLOR_BG = (10, 15, 30)
COLOR_TEXT = (255, 255, 255)
COLOR_MUTED = (140, 160, 180)

# Ghost Colors
COLOR_RED = (244, 67, 54)       # Blinky
COLOR_PINK = (255, 64, 129)     # Pinky
COLOR_CYAN = (79, 195, 247)     # Inky
COLOR_ORANGE = (255, 145, 0)    # Clyde
COLOR_YELLOW = (244, 189, 17)   # Pacman Yellow
COLOR_PURPLE = (156, 39, 176)   # Adversarial Search Purple

# --- Menu States ---
STATE_MAIN_MENU = "MAIN_MENU"
STATE_SUB_MENU = "SUB_MENU"
STATE_VISUALIZER = "VISUALIZER"

# --- Speed Settings ---
SPEED_SLOW = "Chậm"
SPEED_MEDIUM = "Vừa"
SPEED_FAST = "Nhanh"
SPEED_INSTANT = "Tức thì"

SPEED_MAP = {
    SPEED_SLOW: 400,     # ms per step
    SPEED_MEDIUM: 100,   # ms per step
    SPEED_FAST: 16,      # ms per step (60fps)
    SPEED_INSTANT: 0     # run loop instantly
}

# --- Predefined Pacman Maze (15 rows, 21 columns) ---
DEFAULT_MAZE = [
    [2, 2, 2, 2, 2, 2, 2, 2],
    [2, 1, 1, 0, 0, 1, 1, 2],
    [2, 1, 2, 2, 1, 2, 1, 2],
    [2, 1, 1, 0, 1, 1, 1, 2],
    [2, 2, 1, 2, 2, 1, 2, 2],
    [2, 1, 1, 0, 0, 1, 1, 2],
    [2, 2, 2, 2, 2, 2, 2, 2]
]

MAZE_0 = DEFAULT_MAZE
MAZE_1 = DEFAULT_MAZE
MAZE_2 = DEFAULT_MAZE
MAZE_3 = DEFAULT_MAZE
MAZE_4 = DEFAULT_MAZE
MAZE_5 = [
    [2, 2, 2, 2, 2, 2, 2, 2],
    [2, 1, 1, 1, 1, 0, 1, 2],
    [2, 1, 2, 2, 0, 2, 1, 2],
    [2, 1, 1, 2, 1, 1, 1, 2],
    [2, 2, 1, 0, 2, 2, 1, 2],
    [2, 1, 0, 1, 1, 1, 1, 2],
    [2, 2, 2, 2, 2, 2, 2, 2]
]

MAZE_COLS = len(DEFAULT_MAZE[0])
MAZE_ROWS = len(DEFAULT_MAZE)

START_CELL = (1, 1)
GOAL_CELL = (5, 6)

def get_maze_goal(maze):
    """Return a copy of the maze with all food cells (1) set to 0."""
    return [[0 if cell == 1 else cell for cell in row] for row in maze]

DEFAULT_MAZE_GOAL = get_maze_goal(DEFAULT_MAZE)
MAZE_0_GOAL = get_maze_goal(MAZE_0)
MAZE_1_GOAL = get_maze_goal(MAZE_1)
MAZE_2_GOAL = get_maze_goal(MAZE_2)
MAZE_3_GOAL = get_maze_goal(MAZE_3)
MAZE_4_GOAL = get_maze_goal(MAZE_4)
MAZE_5_GOAL = get_maze_goal(MAZE_5)

# --- Path Rendering Configuration ---
SHOW_PATH = False  # Set to True to enable path drawing

# --- Algorithm Info Dictionary ---
ALGO_INFO = {
    "BFS": {
        "title": "Breadth-First Search (BFS)",
        "desc": "Tìm kiếm theo chiều rộng. Mở rộng các nút nông nhất trước. Đảm bảo tìm thấy đường đi ngắn nhất (về số bước) trên đồ thị không trọng số. Sử dụng hàng đợi (Queue) FIFO."
    },
    "DFS": {
        "title": "Depth-First Search (DFS)",
        "desc": "Tìm kiếm theo chiều sâu. Đi theo một nhánh sâu nhất có thể trước khi quay lui. Sử dụng ngăn xếp (Stack) LIFO. Không đảm bảo tối ưu và có thể bị lặp vô hạn."
    },
    "UCS": {
        "title": "Uniform Cost Search (UCS)",
        "desc": "Tìm kiếm chi phí đồng nhất. Mở rộng nút có chi phí đường đi g(n) thấp nhất từ Start. Sử dụng hàng đợi ưu tiên. Đảm bảo tìm thấy đường đi tối ưu nhất về mặt chi phí (tránh vùng bùn lầy)."
    },
    "Greedy Best-First": {
        "title": "Greedy Best-First Search",
        "desc": "Tìm kiếm tham lam. Mở rộng nút có ước lượng khoảng cách h(n) đến Goal gần nhất (Manhattan). Chạy rất nhanh nhưng không đảm bảo tìm thấy đường đi ngắn nhất."
    },
    "A*": {
        "title": "A* Search",
        "desc": "Thuật toán A*. Mở rộng nút dựa trên f(n) = g(n) + h(n), kết hợp chi phí thực tế và khoảng cách ước lượng đến Goal. Là thuật toán tìm kiếm tối ưu và đầy đủ nhất."
    },
    "IDA*": {
        "title": "IDA* Search",
        "desc": "Thuật toán A* sâu dần (Iterative Deepening A*). Kết hợp thuật toán DFS giới hạn bởi ngưỡng f(n) tăng dần, giúp tối ưu hóa dung lượng bộ nhớ."
    },
    "Hill Climbing": {
        "title": "Hill Climbing (Leo Đồi)",
        "desc": "Thuật toán leo đồi. Luôn di chuyển tới ô lân cận có khoảng cách ngắn nhất tới Goal. Không giữ hàng đợi hay quay lui, do đó rất dễ bị kẹt ở các ngõ cụt (cực đại địa phương)."
    },
    "Simulated Annealing": {
        "title": "Simulated Annealing (Luyện Kim)",
        "desc": "Mô phỏng luyện kim. Tương tự Leo Đồi nhưng chấp nhận bước đi tệ hơn với xác suất phụ thuộc nhiệt độ T. Nhiệt độ giảm dần giúp giải thuật thoát khỏi ngõ cụt ban đầu."
    },
    "Beam Search": {
        "title": "Beam Search",
        "desc": "Thuật toán tìm kiếm chùm (Beam Search). Chỉ giữ lại k trạng thái tốt nhất ở mỗi bước tìm kiếm để hạn chế không gian bộ nhớ."
    },
    "Sensorless BFS": {
        "title": "Sensorless BFS (Conformant Planning)",
        "desc": "Tìm kiếm không cần cảm biến. Khởi đầu với một tập hợp các trạng thái niềm tin (belief state). Tìm chuỗi hành động để mọi trạng thái có thể đều đi đến Goal."
    },
    "Partial BFS": {
        "title": "Partial BFS (Unknown Map)",
        "desc": "Tìm kiếm khi chỉ biết một phần bản đồ. Lập kế hoạch sao cho dù cấu trúc phần chưa biết (bóng tối) có ra sao, Pacman vẫn đến đích."
    },
    "Bidirectional BFS": {
        "title": "Bidirectional Search",
        "desc": "Tìm kiếm hai chiều. Chạy hai luồng BFS đồng thời từ Start và từ Goal. Khi hai đường biên gặp nhau, ta ghép đường đi. Giảm lũy thừa không gian tìm kiếm."
    },
    "Simple Backtracking": {
        "title": "Ghost Placement Backtracking",
        "desc": "Quay lui cơ bản xếp 5 con ma. Tìm kiếm đệ quy đặt các con ma cách Pacman >= 5 ô, cách nhau >= 3 ô, và không chung hàng/cột."
    },
    "Backtracking + MRV": {
        "title": "Ghost Placement Backtracking + MRV",
        "desc": "Quay lui + MRV. Chọn các ô ứng viên bị ràng buộc nhiều nhất (có ít ô hàng, cột và ô lân cận an toàn hơn) đặt trước để tối ưu hóa không gian tìm kiếm."
    },
    "Backtracking + Forward Checking": {
        "title": "Ghost Placement + Forward Checking",
        "desc": "Quay lui + Kiểm tra trước. Dự đoán trước số lượng ô trống an toàn còn lại ở các hàng/cột tiếp theo, nếu không đủ chỗ cho số ma còn lại sẽ quay lui sớm."
    },
    "Minimax": {
        "title": "Minimax Adversarial Search",
        "desc": "Thuật toán đối kháng Minimax. Pacman (MAX) chọn bước đi tối đa hóa điểm số dự kiến, giả định Ghost (MIN) chọn bước đi giảm điểm số của Pacman tối đa."
    },
    "Alpha-Beta Pruning": {
        "title": "Alpha-Beta Pruning Search",
        "desc": "Thuật toán cắt tỉa Alpha-Beta. Cải tiến Minimax bằng cách bỏ qua các nhánh tìm kiếm không ảnh hưởng đến quyết định cuối cùng, giúp tăng tốc vượt bậc."
    },
    "Expectimax": {
        "title": "Expectimax Search",
        "desc": "Thuật toán Expectimax. Dùng khi đối thủ (Ghost) không chơi tối ưu mà di chuyển ngẫu nhiên (chance node), tính giá trị trung bình có trọng số của các trạng thái tương lai."
    }
}
