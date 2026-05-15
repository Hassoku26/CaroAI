# Thành viên thực hiện
- **Vũ Ngọc Sơn** 
- **Phạm Quang Tiến**
- **Phạm Thành Trung**
# Cờ Caro với Minimax và Alpha-Beta Pruning

Bài tập môn Trí tuệ Nhân tạo: cài đặt AI chơi cờ Caro 9×9 (thắng khi có **4 quân liên tiếp**) bằng thuật toán **Minimax** và **Alpha-Beta Pruning**, sau đó so sánh hai thuật toán bằng thực nghiệm.

## Cấu trúc thư mục

```
caro/
├── caro_game.py         # Module lõi: bàn cờ, đánh giá, Minimax, Alpha-Beta
├── play.py              # Chơi tương tác Người vs Máy (terminal)
├── play_gui.py          # Giao diện đồ họa tkinter (Người vs Máy)
├── experiment.py        # Chạy thực nghiệm Level 3
├── results.json         # Số liệu chi tiết từ lần chạy thực nghiệm
├── experiment_output.txt# Log thô của thực nghiệm
├── report.md            # Báo cáo đầy đủ 16 mục
└── README.md            # File này
```

## Yêu cầu

- **Python 3.8+** (không cần thư viện ngoài; chỉ dùng `time`, `json` trong chuẩn).
- Hệ điều hành: bất kỳ (Linux / macOS / Windows).

## Cách chạy

### 1. Chơi với máy – Giao diện đồ họa (khuyến nghị)

```bash
python play_gui.py
```

Cửa sổ tkinter hiển thị bàn cờ 9×9. Nhấp chuột để đặt quân X, AI tự động đáp lại. Panel bên phải cho phép chọn thuật toán, độ sâu, bật "AI đi trước" và nhận gợi ý nước đi.

### 2. Chơi với máy – Terminal

```bash
python3 play.py
```

Chương trình sẽ hỏi:
- Kích thước bàn cờ (mặc định 9, tối thiểu 9).
- Thuật toán AI: `minimax` hoặc `alphabeta` (mặc định `alphabeta`).
- Độ sâu tìm kiếm (mặc định 3, nên ≤ 3 nếu chọn `minimax` để khỏi chờ lâu).
- Ai đi trước: `human` hay `ai`.

Người chơi nhập nước đi theo dạng `hàng cột`, ví dụ `4 5`.

Mỗi lượt máy đi, chương trình in ra:
- Nước đi đã chọn.
- Giá trị đánh giá.
- Số trạng thái đã xét.
- Thời gian chạy (ms).

### 2. Chạy thực nghiệm Level 3

```bash
python3 experiment.py
```

Script chạy **6 trạng thái** × **3 độ sâu** (1, 2, 3) cho cả Minimax và Alpha-Beta, in bảng tổng hợp ra terminal và lưu chi tiết vào `results.json`.

> Lưu ý: trạng thái S6 với độ sâu 3 dùng Minimax mất khoảng **48 giây** trên CPU thông thường. Nếu muốn nhanh hơn để chấm bài, có thể tạm sửa `DEPTHS = [1, 2, 3]` trong `experiment.py` thành `[1, 2]`.

## Quy ước

| Giá trị | Vai trò | Hiển thị |
|---------|---------|----------|
| 0 | Ô trống | `.` |
| 1 | HUMAN (MIN, người chơi) | `X` |
| 2 | AI (MAX, máy) | `O` |

- Bàn cờ: ma trận `size × size`, mặc định 9×9.
- Điều kiện thắng: 4 quân liên tiếp theo hàng / cột / 2 đường chéo.
- Hàm `get_valid_moves` chỉ sinh các ô trống nằm trong **bán kính 1** quanh các quân đã đặt → giảm branching factor.

## Tóm tắt kết quả thực nghiệm

| Độ sâu | Cắt trạng thái (trung bình) | Speed-up (trung bình) |
|--------|-----------------------------|-----------------------|
| 1 | ~0 % | ~1× |
| 2 | 30 % – 80 % | 1.5× – 6× |
| 3 | **75 % – 91 %** | **4× – 13×** |

**Alpha-Beta luôn chọn cùng nước đi với Minimax** trên cả 18 cặp thử nghiệm (6 trạng thái × 3 độ sâu), khớp với lý thuyết: cắt nhánh không thay đổi giá trị tối ưu của gốc, chỉ giảm chi phí tính toán.

Chi tiết phân tích xem trong `report.md`.

## Các mức (Level) đã hoàn thành

- **Level 1** — Minimax có giới hạn độ sâu: ✓ (xem `minimax` trong `caro_game.py`).
- **Level 2** — Alpha-Beta Pruning dùng cùng `evaluate`: ✓ (xem `alphabeta` trong `caro_game.py`).
- **Level 3** — Thực nghiệm 6 trạng thái × 3 độ sâu, phân tích đầy đủ: ✓ (xem `experiment.py` và `report.md`).

## Hướng cải tiến (nếu phát triển tiếp)

1. Heuristic phân biệt mẫu *mở hai đầu* vs *bị chặn một đầu*.
2. Move ordering: sắp các nước đi theo điểm `evaluate` giảm dần trước khi gọi đệ quy.
3. Iterative deepening + transposition table.
4. Threat-space search (đặc biệt hiệu quả với cờ Caro / Gomoku).
