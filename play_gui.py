"""
play_gui.py
-----------
Giao diện đồ họa cho trò chơi Cờ Caro (Gomoku) sử dụng tkinter.
Người chơi là X (HUMAN), máy là O (AI).
"""

import tkinter as tk
from tkinter import messagebox
import threading

from caro_game import (
    CaroGame, EMPTY, HUMAN, AI,
    find_move_minimax, find_move_alphabeta,
)

# ── Hằng số giao diện ──────────────────────────────────────────────────
CELL = 48
PADDING = 30
PIECE_R = 17
LINE_COLOR = "#8B7355"
BOARD_BG = "#DEB887"
X_COLOR = "#1a1aff"
O_COLOR = "#cc0000"
X_SHADOW = "#0000aa"
O_SHADOW = "#880000"
HOVER_COLOR = "#90EE90"
WIN_RING_COLOR = "#FFD700"
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_STATUS = ("Segoe UI", 11)
FONT_LABEL = ("Segoe UI", 10)
FONT_BTN = ("Segoe UI", 10, "bold")

BOARD_SIZES = [9, 11, 13, 15]


class CaroGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cờ Caro – Minimax / Alpha-Beta")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c2c2c")

        self._build_side_panel()
        self._build_canvas()
        self._new_game()

    # ── Xây dựng UI ───────────────────────────────────────────────────

    def _build_side_panel(self):
        side = tk.Frame(self.root, bg="#2c2c2c", padx=14, pady=14)
        side.grid(row=0, column=1, sticky="ns")

        tk.Label(side, text="Cờ Caro", font=FONT_TITLE,
                 bg="#2c2c2c", fg="white").pack(pady=(0, 14))

        # ── kích thước bàn cờ ──
        tk.Label(side, text="Kích thước bàn cờ:", font=FONT_LABEL,
                 bg="#2c2c2c", fg="#dddddd").pack(anchor="w")
        self.size_var = tk.IntVar(value=9)
        size_frame = tk.Frame(side, bg="#2c2c2c")
        size_frame.pack(anchor="w", pady=(2, 10))
        for s in BOARD_SIZES:
            tk.Radiobutton(size_frame, text=f"{s}×{s}",
                           variable=self.size_var, value=s,
                           font=FONT_LABEL,
                           bg="#2c2c2c", fg="white",
                           selectcolor="#444444",
                           activebackground="#2c2c2c",
                           activeforeground="white").pack(anchor="w")

        # ── thuật toán ──
        tk.Label(side, text="Thuật toán AI:", font=FONT_LABEL,
                 bg="#2c2c2c", fg="#dddddd").pack(anchor="w")
        self.algo_var = tk.StringVar(value="Alpha-Beta")
        for algo in ("Minimax", "Alpha-Beta"):
            tk.Radiobutton(side, text=algo, variable=self.algo_var,
                           value=algo, font=FONT_LABEL,
                           bg="#2c2c2c", fg="white",
                           selectcolor="#444444",
                           activebackground="#2c2c2c",
                           activeforeground="white").pack(anchor="w")

        # ── độ sâu ──
        tk.Label(side, text="Độ sâu:", font=FONT_LABEL,
                 bg="#2c2c2c", fg="#dddddd").pack(anchor="w", pady=(10, 0))
        self.depth_var = tk.IntVar(value=3)
        tk.Spinbox(side, from_=1, to=6, width=5,
                   textvariable=self.depth_var,
                   font=FONT_LABEL).pack(anchor="w", pady=(2, 0))

        # ── ai đi trước ──
        self.ai_first_var = tk.BooleanVar(value=False)
        tk.Checkbutton(side, text="AI đi trước",
                       variable=self.ai_first_var,
                       font=FONT_LABEL, bg="#2c2c2c", fg="white",
                       selectcolor="#444444",
                       activebackground="#2c2c2c",
                       activeforeground="white").pack(anchor="w", pady=(10, 0))

        # ── nút ──
        tk.Button(side, text="Ván mới", font=FONT_BTN,
                  command=self._new_game,
                  bg="#27ae60", fg="white", relief="flat",
                  padx=10, pady=6, cursor="hand2").pack(fill="x", pady=(16, 6))

        tk.Button(side, text="Gợi ý nước đi", font=FONT_BTN,
                  command=self._hint,
                  bg="#2980b9", fg="white", relief="flat",
                  padx=10, pady=6, cursor="hand2").pack(fill="x", pady=3)

        tk.Button(side, text="Thoát", font=FONT_BTN,
                  command=self.root.quit,
                  bg="#c0392b", fg="white", relief="flat",
                  padx=10, pady=6, cursor="hand2").pack(fill="x", pady=3)

        # ── trạng thái ──
        self.status_var = tk.StringVar()
        tk.Label(side, textvariable=self.status_var,
                 font=FONT_STATUS, bg="#2c2c2c", fg="#f0c040",
                 wraplength=160, justify="center").pack(pady=(16, 0))

    def _build_canvas(self):
        self._canvas_size = self._calc_canvas_size(self.size_var.get())
        self.canvas = tk.Canvas(self.root,
                                width=self._canvas_size,
                                height=self._canvas_size,
                                bg=BOARD_BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>", self._on_hover)
        self.canvas.bind("<Leave>", self._on_leave)
        self._hover_cell = None

    def _calc_canvas_size(self, n):
        return PADDING * 2 + CELL * n

    def _resize_canvas(self, n):
        new_size = self._calc_canvas_size(n)
        self.canvas.configure(width=new_size, height=new_size)
        self._canvas_size = new_size

    # ── Vẽ bàn cờ ─────────────────────────────────────────────────────

    def _draw_board(self):
        self.canvas.delete("all")
        n = self.game.size
        for i in range(n + 1):
            x = PADDING + i * CELL
            y = PADDING + i * CELL
            self.canvas.create_line(PADDING, y, PADDING + n * CELL, y,
                                    fill=LINE_COLOR, width=1)
            self.canvas.create_line(x, PADDING, x, PADDING + n * CELL,
                                    fill=LINE_COLOR, width=1)
        for i in range(n):
            cx = PADDING + i * CELL + CELL // 2
            cy = PADDING + i * CELL + CELL // 2
            self.canvas.create_text(cx, PADDING // 2,
                                    text=str(i), fill="#555544",
                                    font=("Consolas", 8))
            self.canvas.create_text(PADDING // 2, cy,
                                    text=str(i), fill="#555544",
                                    font=("Consolas", 8))
        for r in range(n):
            for c in range(n):
                v = self.game.board[r][c]
                if v != EMPTY:
                    self._draw_piece(r, c, v)
        if self._hover_cell and not self._game_over:
            hr, hc = self._hover_cell
            if self.game.is_valid_move(hr, hc) and self._human_turn:
                cx = PADDING + hc * CELL + CELL // 2
                cy = PADDING + hr * CELL + CELL // 2
                self.canvas.create_oval(
                    cx - PIECE_R, cy - PIECE_R,
                    cx + PIECE_R, cy + PIECE_R,
                    fill=HOVER_COLOR, outline="", stipple="gray50")

    def _draw_piece(self, r, c, player):
        cx = PADDING + c * CELL + CELL // 2
        cy = PADDING + r * CELL + CELL // 2
        color  = X_COLOR  if player == HUMAN else O_COLOR
        shadow = X_SHADOW if player == HUMAN else O_SHADOW
        self.canvas.create_oval(cx - PIECE_R + 2, cy - PIECE_R + 2,
                                cx + PIECE_R + 2, cy + PIECE_R + 2,
                                fill=shadow, outline="")
        self.canvas.create_oval(cx - PIECE_R, cy - PIECE_R,
                                cx + PIECE_R, cy + PIECE_R,
                                fill=color, outline="white", width=1.5)
        sym = "X" if player == HUMAN else "O"
        self.canvas.create_text(cx, cy, text=sym,
                                fill="white", font=("Segoe UI", 12, "bold"))

    def _highlight_win(self, winning_cells):
        for r, c in winning_cells:
            cx = PADDING + c * CELL + CELL // 2
            cy = PADDING + r * CELL + CELL // 2
            self.canvas.create_oval(cx - PIECE_R - 3, cy - PIECE_R - 3,
                                    cx + PIECE_R + 3, cy + PIECE_R + 3,
                                    outline=WIN_RING_COLOR, width=3)

    # ── Logic trò chơi ─────────────────────────────────────────────────

    def _new_game(self):
        n = self.size_var.get()
        self._resize_canvas(n)
        self.game = CaroGame(size=n)
        self._game_over = False
        self._human_turn = not self.ai_first_var.get()
        self._hover_cell = None
        self._draw_board()
        if self._human_turn:
            self.status_var.set("Lượt của bạn  (X)")
        else:
            self.status_var.set("AI đang suy nghĩ…")
            self.root.after(200, self._ai_move_thread)

    def _cell_from_xy(self, x, y):
        c = (x - PADDING) // CELL
        r = (y - PADDING) // CELL
        n = self.game.size
        if 0 <= r < n and 0 <= c < n:
            return r, c
        return None, None

    def _on_hover(self, event):
        r, c = self._cell_from_xy(event.x, event.y)
        cell = (r, c) if r is not None else None
        if cell != self._hover_cell:
            self._hover_cell = cell
            self._draw_board()

    def _on_leave(self, _):
        self._hover_cell = None
        self._draw_board()

    def _on_click(self, event):
        if self._game_over or not self._human_turn:
            return
        r, c = self._cell_from_xy(event.x, event.y)
        if r is None or not self.game.is_valid_move(r, c):
            return
        self.game.make_move(r, c, HUMAN)
        self._draw_board()
        if self._check_end():
            return
        self._human_turn = False
        self.status_var.set("AI đang suy nghĩ…")
        self.root.after(80, self._ai_move_thread)

    def _ai_move_thread(self):
        threading.Thread(target=self._ai_move, daemon=True).start()

    def _ai_move(self):
        algo = self.algo_var.get()
        depth = self.depth_var.get()
        snapshot = self.game.copy()  # tránh race condition với main thread
        if algo == "Minimax":
            stats = find_move_minimax(snapshot, depth)
        else:
            stats = find_move_alphabeta(snapshot, depth)
        move = stats.best_move
        self.root.after(0, lambda: self._apply_ai_move(move))

    def _apply_ai_move(self, move):
        if move is None or self._game_over:
            return
        self.game.make_move(move[0], move[1], AI)
        self._draw_board()
        if self._check_end():
            return
        self._human_turn = True
        self.status_var.set("Lượt của bạn  (X)")

    def _check_end(self):
        terminal, _ = self.game.is_terminal()
        if not terminal:
            return False
        self._game_over = True
        self._draw_board()
        if self.game.check_win(HUMAN):
            self._highlight_win(self.game.get_winning_cells(HUMAN))
            self.status_var.set("Bạn thắng!")
            self.root.after(400, lambda: messagebox.showinfo(
                "Kết thúc", "Chúc mừng! Bạn đã thắng!"))
        elif self.game.check_win(AI):
            self._highlight_win(self.game.get_winning_cells(AI))
            self.status_var.set("AI thắng!")
            self.root.after(400, lambda: messagebox.showinfo(
                "Kết thúc", "AI thắng rồi. Cố lên nhé!"))
        else:
            self.status_var.set("Hòa cờ!")
            self.root.after(400, lambda: messagebox.showinfo(
                "Kết thúc", "Hòa cờ! Ván hay đấy."))
        return True

    def _hint(self):
        if self._game_over or not self._human_turn:
            return
        self.status_var.set("Đang tính gợi ý…")

        def compute():
            algo = self.algo_var.get()
            depth = self.depth_var.get()
            snapshot = self.game.copy()
            if algo == "Minimax":
                s = find_move_minimax(snapshot, depth)
            else:
                s = find_move_alphabeta(snapshot, depth)
            self.root.after(0, lambda: self._show_hint(s.best_move))

        threading.Thread(target=compute, daemon=True).start()

    def _show_hint(self, move):
        if move is None:
            return
        r, c = move
        self.status_var.set(f"Gợi ý: hàng {r}, cột {c}")
        self._draw_board()
        cx = PADDING + c * CELL + CELL // 2
        cy = PADDING + r * CELL + CELL // 2
        self.canvas.create_oval(cx - PIECE_R - 4, cy - PIECE_R - 4,
                                cx + PIECE_R + 4, cy + PIECE_R + 4,
                                outline="#00cc66", width=3, dash=(6, 3))
        self.root.after(2000, self._draw_board)


# ── Chạy ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = CaroGUI(root)
    root.mainloop()
