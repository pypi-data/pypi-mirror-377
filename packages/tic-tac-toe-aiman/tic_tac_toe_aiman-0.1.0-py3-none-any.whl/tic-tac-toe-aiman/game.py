# src/game.py
import random

class TicTacToe:
    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.winner = None
        self.stats = {"X": 0, "O": 0, "Draws": 0}

    def reset(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.winner = None

    def make_move(self, row, col):
        if self.board[row][col] == "" and not self.winner:
            self.board[row][col] = self.current_player
            self.check_winner()
            self.current_player = "O" if self.current_player == "X" else "X"
            return True
        return False

    def check_winner(self):
        lines = []

        # صفوف، أعمدة، قطرين
        lines.extend(self.board)
        lines.extend([[self.board[r][c] for r in range(3)] for c in range(3)])
        lines.append([self.board[i][i] for i in range(3)])
        lines.append([self.board[i][2 - i] for i in range(3)])

        for line in lines:
            if line == ["X"] * 3:
                self.winner = "X"
                self.stats["X"] += 1
                return
            if line == ["O"] * 3:
                self.winner = "O"
                self.stats["O"] += 1
                return

        # إذا امتلأ وبدون فائز → تعادل
        if all(self.board[r][c] for r in range(3) for c in range(3)):
            self.winner = "Draw"
            self.stats["Draws"] += 1

    def best_move(self, difficulty):
        # بالوضع hard نستخدم Minimax
        if difficulty == "hard":
            return self._minimax_move()
        # إعدادات بسيطة للبقية
        empties = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if difficulty == "medium" and random.random() < 0.6:
            return random.choice(empties)
        if difficulty == "easy":
            return random.choice(empties)
        return random.choice(empties)

    def _minimax_move(self):
        best_score = -float("inf")
        best_move = None

        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "":
                    # جرّب خطوة O
                    self.board[r][c] = "O"
                    score = self._minimax(False)
                    self.board[r][c] = ""
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)

        return best_move

    def _minimax(self, is_maximizing):
        # احكم على الحالة الحالية
        if self.winner or self._full_board():
            result = self._score()
            return result

        if is_maximizing:
            best = -float("inf")
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == "":
                        self.board[r][c] = "O"
                        self._update_winner_temp()
                        val = self._minimax(False)
                        self.board[r][c] = ""
                        self._clear_winner_temp()
                        best = max(best, val)
            return best
        else:
            worst = float("inf")
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == "":
                        self.board[r][c] = "X"
                        self._update_winner_temp()
                        val = self._minimax(True)
                        self.board[r][c] = ""
                        self._clear_winner_temp()
                        worst = min(worst, val)
            return worst

    def _score(self):
        if self.winner == "O":
            return 1
        if self.winner == "X":
            return -1
        return 0  # تعادل

    def _full_board(self):
        return all(self.board[r][c] for r in range(3) for c in range(3))

    def _update_winner_temp(self):
        # تقيّم من دون تغيير الإحصائيات الحقيقية
        prev = self.winner
        self.winner = None
        lines = []
        lines.extend(self.board)
        lines.extend([[self.board[r][c] for r in range(3)] for c in range(3)])
        lines.append([self.board[i][i] for i in range(3)])
        lines.append([self.board[i][2 - i] for i in range(3)])
        for line in lines:
            if line == ["X"] * 3:
                self.winner = "X"
                break
            if line == ["O"] * 3:
                self.winner = "O"
                break
        # لا نعالج التعادل هنا لأنه لا يؤثر على Minimax مباشرة
        if prev is not None and self.winner is None:
            self.winner = None

    def _clear_winner_temp(self):
        self.winner = None
