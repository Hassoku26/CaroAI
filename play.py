"""
play.py
-------
Chơi tương tác giữa Người và Máy.
Người dùng có thể chọn:
  - Kích thước bàn cờ (mặc định 9x9, tối thiểu 9).
  - Thuật toán AI: Minimax hoặc Alpha-Beta.
  - Độ sâu tìm kiếm (mặc định 3).

Người chơi đi quân X (HUMAN, MIN). Máy đi quân O (AI, MAX).
Trò chơi kết thúc khi một bên có 4 quân liên tiếp hoặc bàn cờ đầy.
"""

from caro_game import (
    CaroGame, EMPTY, HUMAN, AI, DEFAULT_SIZE,
    find_move_minimax, find_move_alphabeta,
)


def read_int(prompt, default, min_val=None):
    raw = input(f"{prompt} (Enter để dùng {default}): ").strip()
    if raw == "":
        return default
    try:
        v = int(raw)
    except ValueError:
        print("  -> Giá trị không hợp lệ, dùng mặc định.")
        return default
    if min_val is not None and v < min_val:
        print(f"  -> Quá nhỏ, dùng {min_val}.")
        return min_val
    return v


def read_choice(prompt, options, default):
    raw = input(f"{prompt} {options} (Enter để dùng {default}): ").strip().lower()
    if raw == "":
        return default
    if raw in options:
        return raw
    print("  -> Lựa chọn không hợp lệ, dùng mặc định.")
    return default


def get_human_move(game):
    """Đọc nước đi của người chơi."""
    while True:
        try:
            raw = input("Nước đi của bạn (hàng cột, ví dụ '4 5'): ").strip()
            parts = raw.split()
            if len(parts) != 2:
                print("  -> Cần nhập 2 số.")
                continue
            r, c = int(parts[0]), int(parts[1])
        except ValueError:
            print("  -> Nhập số nguyên hợp lệ.")
            continue
        if not game.is_valid_move(r, c):
            print("  -> Nước đi không hợp lệ (ngoài bàn cờ hoặc ô đã có quân).")
            continue
        return r, c


def main():
    print("=" * 50)
    print("       CỜ CARO  -  Người vs Máy")
    print("  (Thắng khi có 4 quân liên tiếp)")
    print("=" * 50)

    size = read_int("Kích thước bàn cờ", DEFAULT_SIZE, min_val=9)
    algo = read_choice("Chọn thuật toán AI",
                       ["minimax", "alphabeta"], "alphabeta")
    depth = read_int("Độ sâu tìm kiếm của AI", 3, min_val=1)
    first = read_choice("Ai đi trước?", ["human", "ai"], "human")

    game = CaroGame(size=size)
    ai_func = find_move_minimax if algo == "minimax" else find_move_alphabeta

    turn = HUMAN if first == "human" else AI
    game.print_board()

    while True:
        terminal, _ = game.is_terminal()
        if terminal:
            break

        if turn == HUMAN:
            r, c = get_human_move(game)
            game.make_move(r, c, HUMAN)
        else:
            print(f"Máy đang suy nghĩ ({algo}, độ sâu {depth})...")
            stats = ai_func(game, depth)
            print(f"  Nước đi của máy: {stats.best_move}")
            print(f"  Giá trị đánh giá: {stats.best_value}")
            print(f"  Số trạng thái đã xét: {stats.states}")
            print(f"  Thời gian chạy: {stats.elapsed*1000:.1f} ms")
            r, c = stats.best_move
            game.make_move(r, c, AI)

        game.print_board()
        turn = AI if turn == HUMAN else HUMAN

    # ----- Hiển thị kết quả -----
    if game.check_win(AI):
        print(">>> Máy thắng!")
    elif game.check_win(HUMAN):
        print(">>> Bạn thắng!")
    else:
        print(">>> Hòa.")


if __name__ == "__main__":
    main()
