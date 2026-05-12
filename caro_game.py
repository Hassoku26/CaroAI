"""
caro_game.py
-------------
Module lõi cho bài tập Cờ Caro.

Cài đặt:
  - Biểu diễn bàn cờ (mặc định 9x9).
  - Luật chơi: đánh luân phiên, không đánh vào ô đã có quân.
  - Điều kiện thắng: 4 quân liên tiếp theo hàng/cột/đường chéo.
  - Hàm sinh nước đi hợp lệ (chỉ xét các ô trống cạnh quân đã có để tăng tốc).
  - Hàm đánh giá trạng thái (heuristic phân biệt chuỗi mở/nửa-mở/bị-chặn).
  - Thuật toán Minimax có giới hạn độ sâu (Level 1).
  - Thuật toán Alpha-Beta Pruning với sắp xếp nước đi (Level 2).

Quy ước:
  EMPTY = 0  -> ô trống, ký hiệu '.'
  HUMAN = 1  -> người chơi (MIN), ký hiệu 'X'
  AI    = 2  -> máy      (MAX), ký hiệu 'O'
"""

import time

# ----- Hằng số -----
EMPTY = 0
HUMAN = 1   # MIN
AI = 2      # MAX

DEFAULT_SIZE = 9
WIN_LENGTH = 4         # số quân liên tiếp để thắng
NEIGHBOR_RADIUS = 1    # bán kính sinh nước đi quanh các quân đã đặt

SYMBOLS = {EMPTY: '.', HUMAN: 'X', AI: 'O'}

WIN_SCORE = 100_000


# =====================================================================
# 1. LỚP BÀN CỜ
# =====================================================================
class CaroGame:
    """Biểu diễn trạng thái bàn cờ và các thao tác cơ bản."""

    def __init__(self, size=DEFAULT_SIZE, board=None):
        self.size = size
        if board is not None:
            self.board = [row[:] for row in board]
        else:
            self.board = [[EMPTY] * size for _ in range(size)]

    # ---------- thao tác cơ bản ----------
    def copy(self):
        return CaroGame(self.size, self.board)

    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def is_valid_move(self, r, c):
        return self.in_bounds(r, c) and self.board[r][c] == EMPTY

    def make_move(self, r, c, player):
        self.board[r][c] = player

    def undo_move(self, r, c):
        self.board[r][c] = EMPTY

    def is_empty(self):
        return all(self.board[r][c] == EMPTY
                   for r in range(self.size) for c in range(self.size))

    def is_full(self):
        return all(self.board[r][c] != EMPTY
                   for r in range(self.size) for c in range(self.size))

    # ---------- sinh nước đi hợp lệ ----------
    def get_valid_moves(self):
        """Chỉ sinh các ô trống nằm cạnh ít nhất một quân đã đặt."""
        if self.is_empty():
            return [(self.size // 2, self.size // 2)]

        moves = set()
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == EMPTY:
                    continue
                for dr in range(-NEIGHBOR_RADIUS, NEIGHBOR_RADIUS + 1):
                    for dc in range(-NEIGHBOR_RADIUS, NEIGHBOR_RADIUS + 1):
                        nr, nc = r + dr, c + dc
                        if self.in_bounds(nr, nc) and self.board[nr][nc] == EMPTY:
                            moves.add((nr, nc))
        return sorted(moves)

    # ---------- kiểm tra thắng ----------
    def check_win(self, player):
        """Trả về True nếu `player` có đủ WIN_LENGTH quân liên tiếp."""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] != player:
                    continue
                for dr, dc in directions:
                    count = 1
                    nr, nc = r + dr, c + dc
                    while self.in_bounds(nr, nc) and self.board[nr][nc] == player:
                        count += 1
                        if count >= WIN_LENGTH:
                            return True
                        nr += dr
                        nc += dc
        return False

    def is_terminal(self):
        """Trả về (đã_kết_thúc, giá_trị_kết_thúc).

        AI thắng -> +WIN_SCORE ; HUMAN thắng -> -WIN_SCORE ; hòa -> 0
        """
        if self.check_win(AI):
            return True, WIN_SCORE
        if self.check_win(HUMAN):
            return True, -WIN_SCORE
        if self.is_full():
            return True, 0
        return False, 0

    def get_winning_cells(self, player):
        """Trả về danh sách WIN_LENGTH ô tạo thành chuỗi thắng, hoặc []."""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] != player:
                    continue
                for dr, dc in directions:
                    cells = [(r, c)]
                    for _ in range(WIN_LENGTH - 1):
                        nr = cells[-1][0] + dr
                        nc = cells[-1][1] + dc
                        if self.in_bounds(nr, nc) and self.board[nr][nc] == player:
                            cells.append((nr, nc))
                        else:
                            break
                    if len(cells) >= WIN_LENGTH:
                        return cells
        return []

    # ---------- in bàn cờ ----------
    def print_board(self):
        header = "    " + " ".join(f"{c}" for c in range(self.size))
        print(header)
        print("   " + "--" * self.size)
        for r in range(self.size):
            row = " ".join(SYMBOLS[self.board[r][c]] for c in range(self.size))
            print(f"{r:2d}| {row}")
        print()


# =====================================================================
# 2. HÀM ĐÁNH GIÁ TRẠNG THÁI (HEURISTIC)
# =====================================================================
def evaluate(game):
    """Đánh giá trạng thái không kết thúc. Điểm = AI - HUMAN."""
    return _score_for(game, AI) - _score_for(game, HUMAN)


def _score_for(game, player):
    """Tính điểm heuristic cho một bên.

    Quét mọi cửa sổ WIN_LENGTH ô theo 4 hướng. Với mỗi cửa sổ không
    có quân đối thủ, tính điểm dựa trên số quân và số đầu mở:

      chuỗi 3 mở 2 đầu  ->  5 000  (gần như thắng chắc)
      chuỗi 3 mở 1 đầu  ->    500
      chuỗi 2 mở 2 đầu  ->    200
      chuỗi 2 mở 1 đầu  ->     50
      chuỗi 1            ->     10
      bị chặn cả 2 đầu  ->      0  (chuỗi không có tiềm năng)
    """
    opponent = HUMAN if player == AI else AI
    score = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    W = WIN_LENGTH

    for r in range(game.size):
        for c in range(game.size):
            for dr, dc in directions:
                # Xây cửa sổ W ô
                core = []
                valid = True
                for i in range(W):
                    nr, nc = r + dr * i, c + dc * i
                    if not game.in_bounds(nr, nc):
                        valid = False
                        break
                    core.append(game.board[nr][nc])
                if not valid or opponent in core:
                    continue

                count = core.count(player)
                if count == 0:
                    continue

                # Kiểm tra đầu mở (ô ngay ngoài cửa sổ)
                lr, lc = r - dr, c - dc
                rr, rc = r + dr * W, c + dc * W
                left_open  = game.in_bounds(lr, lc) and game.board[lr][lc] == EMPTY
                right_open = game.in_bounds(rr, rc) and game.board[rr][rc] == EMPTY
                ends = left_open + right_open

                if ends == 0:
                    continue  # bị chặn hoàn toàn, không có tiềm năng

                if count == W:
                    score += WIN_SCORE
                elif count == W - 1:
                    score += 5_000 if ends == 2 else 500
                elif count == W - 2:
                    score += 200 if ends == 2 else 50
                else:
                    score += 10

    return score


# =====================================================================
# 3. SẮP XẾP NƯỚC ĐI (dùng cho Alpha-Beta)
# =====================================================================
def _order_moves(game, moves):
    """Sắp xếp nước đi: mật độ quân xung quanh cao hơn lên trước,
    ưu tiên gần trung tâm bàn cờ. Giúp Alpha-Beta cắt nhánh hiệu quả hơn.
    """
    center = game.size // 2

    def key(m):
        r, c = m
        density = sum(
            1 for dr in range(-2, 3) for dc in range(-2, 3)
            if (dr, dc) != (0, 0)
            and game.in_bounds(r + dr, c + dc)
            and game.board[r + dr][c + dc] != EMPTY
        )
        dist = abs(r - center) + abs(c - center)
        return (-density, dist)  # density cao trước, gần trung tâm trước

    return sorted(moves, key=key)


# =====================================================================
# 4. THỐNG KÊ TÌM KIẾM
# =====================================================================
class Stats:
    """Lưu thông tin một lần tìm nước đi."""
    def __init__(self, algo_name="", depth=0):
        self.algo = algo_name
        self.depth = depth
        self.states = 0
        self.elapsed = 0.0
        self.best_move = None
        self.best_value = 0

    def __str__(self):
        return (f"[{self.algo:9s} d={self.depth}] "
                f"move={self.best_move}, value={self.best_value}, "
                f"states={self.states}, time={self.elapsed*1000:.1f} ms")


# =====================================================================
# 5. MINIMAX (Level 1)
# =====================================================================
def minimax(game, depth, is_max_turn, stats):
    """Minimax có giới hạn độ sâu.

    Trả về: (giá_trị, nước_đi_tốt_nhất).
    """
    stats.states += 1

    terminal, value = game.is_terminal()
    if terminal:
        return value, None
    if depth == 0:
        return evaluate(game), None

    moves = game.get_valid_moves()
    if not moves:
        return evaluate(game), None

    best_move = moves[0]

    if is_max_turn:
        best_val = float('-inf')
        for r, c in moves:
            game.make_move(r, c, AI)
            val, _ = minimax(game, depth - 1, False, stats)
            game.undo_move(r, c)
            if val > best_val:
                best_val = val
                best_move = (r, c)
        return best_val, best_move
    else:
        best_val = float('inf')
        for r, c in moves:
            game.make_move(r, c, HUMAN)
            val, _ = minimax(game, depth - 1, True, stats)
            game.undo_move(r, c)
            if val < best_val:
                best_val = val
                best_move = (r, c)
        return best_val, best_move


# =====================================================================
# 6. ALPHA-BETA PRUNING (Level 2)
# =====================================================================
def alphabeta(game, depth, alpha, beta, is_max_turn, stats):
    """Alpha-Beta Pruning với sắp xếp nước đi.

    - alpha: giá trị tốt nhất hiện tại của MAX (AI).
    - beta : giá trị tốt nhất hiện tại của MIN (HUMAN).
    - Nước đi được sắp xếp trước để tăng tỷ lệ cắt nhánh.
    """
    stats.states += 1

    terminal, value = game.is_terminal()
    if terminal:
        return value, None
    if depth == 0:
        return evaluate(game), None

    moves = _order_moves(game, game.get_valid_moves())
    if not moves:
        return evaluate(game), None

    best_move = moves[0]

    if is_max_turn:
        best_val = float('-inf')
        for r, c in moves:
            game.make_move(r, c, AI)
            val, _ = alphabeta(game, depth - 1, alpha, beta, False, stats)
            game.undo_move(r, c)
            if val > best_val:
                best_val = val
                best_move = (r, c)
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break  # Beta cut-off
        return best_val, best_move
    else:
        best_val = float('inf')
        for r, c in moves:
            game.make_move(r, c, HUMAN)
            val, _ = alphabeta(game, depth - 1, alpha, beta, True, stats)
            game.undo_move(r, c)
            if val < best_val:
                best_val = val
                best_move = (r, c)
            beta = min(beta, best_val)
            if beta <= alpha:
                break  # Alpha cut-off
        return best_val, best_move


# =====================================================================
# 7. HÀM TIỆN ÍCH GỌI TÌM KIẾM
# =====================================================================
def find_move_minimax(game, depth):
    """Tìm nước đi tốt nhất bằng Minimax. Trả về đối tượng Stats."""
    stats = Stats("Minimax", depth)
    t0 = time.perf_counter()
    val, move = minimax(game, depth, True, stats)
    stats.elapsed = time.perf_counter() - t0
    stats.best_value = val
    stats.best_move = move
    return stats


def find_move_alphabeta(game, depth):
    """Tìm nước đi tốt nhất bằng Alpha-Beta. Trả về đối tượng Stats."""
    stats = Stats("Alpha-Beta", depth)
    t0 = time.perf_counter()
    val, move = alphabeta(game, depth, float('-inf'), float('inf'),
                          True, stats)
    stats.elapsed = time.perf_counter() - t0
    stats.best_value = val
    stats.best_move = move
    return stats


# =====================================================================
# 8. KIỂM TRA NHANH KHI CHẠY TRỰC TIẾP
# =====================================================================
if __name__ == "__main__":
    g = CaroGame()
    g.make_move(4, 4, AI)
    g.make_move(4, 5, HUMAN)
    g.print_board()
    print("Đánh giá:", evaluate(g))
    print(find_move_minimax(g, 2))
    print(find_move_alphabeta(g, 2))
