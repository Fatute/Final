# Pacman AI Search Algorithms

## Giới thiệu Dự án (Project Introduction)
Dự án này là một phiên bản mô phỏng trực quan của trò chơi Pacman, được xây dựng bằng Python. Mục tiêu chính của dự án là triển khai và trực quan hóa các thuật toán Tìm kiếm và Trí tuệ Nhân tạo (AI Search Algorithms) khác nhau. Thay vì được điều khiển bởi người chơi, Pacman sẽ tự động tìm đường đi tối ưu đến các mục tiêu (thức ăn) hoặc tránh/ăn ma dựa trên các thuật toán được lập trình sẵn.

Giao diện đồ họa (GUI) cung cấp cái nhìn trực quan, giúp người xem dễ dàng hiểu được cách mỗi thuật toán hoạt động, duyệt qua các trạng thái (node) và tìm ra giải pháp.

## Các nhóm thuật toán được triển khai
Dự án bao gồm 6 nhóm thuật toán tìm kiếm chính, được phân chia cụ thể như sau:

### 1. Uninformed Search (Tìm kiếm mù / Không có thông tin)
Các thuật toán duyệt không gian trạng thái mà không có bất kỳ thông tin heuristic nào về khoảng cách đến mục tiêu.
*   **BFS (Breadth-First Search):** Tìm kiếm theo chiều rộng.
*   **DFS (Depth-First Search):** Tìm kiếm theo chiều sâu.
*   **UCS (Uniform Cost Search):** Tìm kiếm chi phí cực tiểu.

### 2. Informed Search (Tìm kiếm có thông tin / Heuristic)
Sử dụng hàm heuristic để ước lượng khoảng cách đến đích, giúp tập trung tìm kiếm và tăng tốc độ tìm đường đi tối ưu.
*   **Greedy Best-First Search:** Tìm kiếm tham lam tốt nhất đầu tiên.
*   **A* (A-Star) Search:** Tìm kiếm A* (kết hợp chi phí thực tế và heuristic).
*   **IDA* (Iterative Deepening A*):** Tìm kiếm A* sâu dần lặp.

### 3. Local Search (Tìm kiếm cục bộ)
Tập trung tối ưu hóa trạng thái hiện tại thay vì duyệt toàn bộ không gian, thích hợp cho các bài toán tối ưu hóa.
*   **Hill Climbing:** Thuật toán leo đồi.
*   **Beam Search:** Tìm kiếm chùm.
*   **Simulated Annealing:** Luyện kim (Mô phỏng ủ thép).

### 4. Adversarial Search (Tìm kiếm đối kháng)
Được sử dụng khi có nhiều tác nhân (Pacman và Ghosts) cạnh tranh với nhau trong môi trường.
*   **Minimax:** Cây trò chơi tối đa / tối thiểu.
*   **Alpha-Beta Pruning:** Cắt tỉa Alpha-Beta để tăng tốc tối ưu hóa Minimax.

### 5. Constraint Satisfaction Problems (CSP - Bài toán thỏa mãn ràng buộc)
Giải quyết các bài toán dựa trên các ràng buộc cụ thể của môi trường (ví dụ: Pacman bị giới hạn trọng lượng điểm số khi đi tìm đường).
*   **Simple Backtracking (Weight Constrained):** Quay lui đơn giản có ràng buộc.
*   **Forward Checking:** Kiểm tra tiến.
*   **AC-3 (Arc Consistency):** Nhất quán cung.

### 6. Blind Search / Partial Observability (Tìm kiếm trong môi trường mù/quan sát một phần)
Áp dụng cho môi trường nơi Pacman không biết chính xác vị trí ban đầu của mình (Sensorless) hoặc môi trường có tính không chắc chắn.
*   **Sensorless BFS:** Tìm kiếm không có cảm biến.
*   **Partial BFS:** Tìm kiếm với thông tin quan sát một phần.
*   **AND-OR Search:** Tìm kiếm đồ thị AND-OR.

---

## Demo
Dưới đây là các minh họa quá trình hoạt động của các nhóm thuật toán:

### Demo 1: Uninformed Search (BFS/DFS/UCS)


### Demo 2: Informed Search (A* / Greedy)
![Demo Informed Search](./assets/informed_demo.gif)
*(Thay thế bằng đường dẫn tới file GIF demo tìm kiếm có thông tin của bạn)*

### Demo 3: Local Search
![Demo Local Search](./assets/local_demo.gif)
*(Thay thế bằng đường dẫn tới file GIF demo tìm kiếm cục bộ của bạn)*

### Demo 4: Adversarial Search (Pacman vs Ghosts)
![Demo Adversarial Search](./assets/adversarial_demo.gif)
*(Thay thế bằng đường dẫn tới file GIF demo thuật toán đối kháng của bạn)*

### Demo 5: Constraint Satisfaction Problem (CSP)
![Demo CSP](./assets/csp_demo.gif)
*(Thay thế bằng đường dẫn tới file GIF demo bài toán ràng buộc của bạn)*

### Demo 6: Blind / Partial Observability Search
![Demo Blind Search](./assets/blind_demo.gif)
*(Thay thế bằng đường dẫn tới file GIF demo thuật toán quan sát một phần của bạn)*

---

## 🛠 Hướng dẫn cài đặt và chạy dự án

1. Clone repository này về máy của bạn.
2. Đảm bảo bạn đã cài đặt Python.
3. Chạy lệnh sau trong terminal để khởi động giao diện Pacman:
   ```bash
   python pacman_gui.py
   ```
