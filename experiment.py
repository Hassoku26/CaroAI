"""
experiment.py
-------------
Thực nghiệm Level 3.

- Chuẩn bị 6 trạng thái bàn cờ khác nhau (đại diện các giai đoạn / tình huống
  điển hình của ván cờ).
- Chạy Minimax và Alpha-Beta với cùng độ sâu, cùng hàm đánh giá, cùng cách
  sinh nước đi.
- Thử 3 độ sâu (1, 2, 3) để so sánh ảnh hưởng của độ sâu.
- In bảng kết quả + lưu ra file JSON để dùng trong báo cáo.
"""

import json
from caro_game import (
    CaroGame, EMPTY, HUMAN, AI,
    find_move_minimax, find_move_alphabeta,
)


# ---------------------------------------------------------------------
# 1. ĐỊNH NGHĨA CÁC TRẠNG THÁI THỬ NGHIỆM
# ---------------------------------------------------------------------
# Dùng ký tự '.' = trống, 'X' = HUMAN, 'O' = AI.
# Tất cả bàn cờ đều 9x9 để bảo đảm đồng nhất.
CHAR_TO_CODE = {'.': EMPTY, 'X': HUMAN, 'O': AI}


def board_from_strings(rows):
    """Chuyển danh sách chuỗi 9 ký tự thành ma trận bàn cờ."""
    size = len(rows)
    board = [[CHAR_TO_CODE[ch] for ch in row] for row in rows]
    return board, size


TEST_STATES = [
    # (1) Đầu ván: hai bên vừa đi 1-2 nước, không gian còn rất rộng
    {
        "name": "S1 - Đầu ván",
        "desc": "Hai bên mới đi vài nước, nhiều khả năng đối xứng",
        "rows": [
            ".........",
            ".........",
            ".........",
            ".........",
            "....OX...",
            ".....O...",
            ".........",
            ".........",
            ".........",
        ],
    },
    # (2) Giữa ván: nhiều quân trên bàn, cần tính toán nhiều nhánh
    {
        "name": "S2 - Giữa ván",
        "desc": "Đã có nhiều quân, AI cần cân nhắc cả tấn công và phòng thủ",
        "rows": [
            ".........",
            ".........",
            "...X.....",
            "....OX...",
            "...OOX...",
            "....OX...",
            ".........",
            ".........",
            ".........",
        ],
    },
    # (3) AI có thể thắng ngay (đã có 3 quân liên tiếp mở hai đầu)
    {
        "name": "S3 - AI thắng ngay",
        "desc": "AI có 3 quân liên tiếp mở, đi thêm 1 nước là thắng",
        "rows": [
            ".........",
            ".........",
            ".........",
            "...XX....",
            "...OOO...",
            "....X....",
            ".........",
            ".........",
            ".........",
        ],
    },
    # (4) Người chơi sắp thắng, AI phải chặn ngay
    {
        "name": "S4 - Phải chặn",
        "desc": "HUMAN có 3 quân liên tiếp mở, nếu AI không chặn sẽ thua",
        "rows": [
            ".........",
            ".........",
            "....O....",
            ".....O...",
            "..XXX....",
            ".........",
            ".........",
            ".........",
            ".........",
        ],
    },
    # (5) Cả hai bên đều có cơ hội tấn công
    {
        "name": "S5 - Hai bên đều mạnh",
        "desc": "AI có 2-mở, HUMAN cũng có 2-mở; AI phải chọn ưu tiên",
        "rows": [
            ".........",
            ".........",
            "..OO.....",
            "...XX....",
            "....XX...",
            ".....OO..",
            ".........",
            ".........",
            ".........",
        ],
    },
    # (6) Trạng thái rộng: nhiều quân rải rác, nhiều nhánh cần xét
    {
        "name": "S6 - Nhiều nước hợp lệ",
        "desc": "Quân rải đều khắp bàn cờ, branching factor lớn",
        "rows": [
            "....X....",
            ".O.......",
            "...O.....",
            "....X....",
            ".....O...",
            "...X.....",
            "......O..",
            ".X.......",
            ".........",
        ],
    },
]


# ---------------------------------------------------------------------
# 2. HÀM HỖ TRỢ IN
# ---------------------------------------------------------------------
def print_state(state):
    print(f"\n--- {state['name']} ---")
    print(state["desc"])
    for row in state["rows"]:
        print("  " + " ".join(row))


def run_one_case(state, depth):
    """Chạy Minimax và Alpha-Beta trên một trạng thái với 1 độ sâu."""
    board, size = board_from_strings(state["rows"])

    # Tạo 2 bản sao bàn cờ để 2 thuật toán hoạt động độc lập
    g1 = CaroGame(size=size, board=board)
    g2 = CaroGame(size=size, board=board)

    mm = find_move_minimax(g1, depth)
    ab = find_move_alphabeta(g2, depth)

    return mm, ab


# ---------------------------------------------------------------------
# 3. CHẠY TOÀN BỘ THỰC NGHIỆM
# ---------------------------------------------------------------------
def main():
    DEPTHS = [1, 2, 3]
    all_results = []

    for state in TEST_STATES:
        print_state(state)
        for d in DEPTHS:
            mm, ab = run_one_case(state, d)
            same_move = (mm.best_move == ab.best_move)
            reduction = (1 - ab.states / mm.states) * 100 if mm.states else 0
            speedup = mm.elapsed / ab.elapsed if ab.elapsed > 0 else float('inf')

            print(f"\n  Độ sâu {d}:")
            print(f"    Minimax    : move={mm.best_move}  value={mm.best_value:>7}  "
                  f"states={mm.states:>6}  time={mm.elapsed*1000:>8.2f} ms")
            print(f"    Alpha-Beta : move={ab.best_move}  value={ab.best_value:>7}  "
                  f"states={ab.states:>6}  time={ab.elapsed*1000:>8.2f} ms")
            print(f"    -> cùng nước đi: {same_move}, giảm trạng thái: {reduction:.1f}%, "
                  f"tăng tốc: {speedup:.2f}x")

            all_results.append({
                "state": state["name"],
                "depth": d,
                "minimax": {
                    "move": mm.best_move, "value": mm.best_value,
                    "states": mm.states, "time_ms": mm.elapsed * 1000,
                },
                "alphabeta": {
                    "move": ab.best_move, "value": ab.best_value,
                    "states": ab.states, "time_ms": ab.elapsed * 1000,
                },
                "same_move": same_move,
                "states_reduction_pct": reduction,
                "speedup": speedup,
            })

    # ----- Bảng tổng hợp -----
    print("\n" + "=" * 110)
    print("BẢNG TỔNG HỢP (tất cả trạng thái, tất cả độ sâu)")
    print("=" * 110)
    header = (f"{'Trạng thái':<22} {'D':>2} | "
              f"{'MM move':>8} {'MM val':>8} {'MM #st':>8} {'MM ms':>9} | "
              f"{'AB move':>8} {'AB val':>8} {'AB #st':>8} {'AB ms':>9} | "
              f"{'same':>5} {'cut%':>6} {'speed':>6}")
    print(header)
    print("-" * 110)
    for r in all_results:
        mm = r["minimax"]; ab = r["alphabeta"]
        print(f"{r['state']:<22} {r['depth']:>2} | "
              f"{str(mm['move']):>8} {mm['value']:>8} {mm['states']:>8} {mm['time_ms']:>9.2f} | "
              f"{str(ab['move']):>8} {ab['value']:>8} {ab['states']:>8} {ab['time_ms']:>9.2f} | "
              f"{str(r['same_move']):>5} {r['states_reduction_pct']:>6.1f} {r['speedup']:>6.2f}")

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print("\nĐã lưu kết quả chi tiết vào results.json")


if __name__ == "__main__":
    main()
