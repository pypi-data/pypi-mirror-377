# ui.py
# واجهة رسومية باستخدام pygame (بدون صور/أصوات)
import pygame
import sys
import colorsys
from settings import *
from game import TicTacToe
from datetime import datetime

import arabic_reshaper
from bidi.algorithm import get_display


def render_arabic(text, font, color):
    """
    يُعيد تشكيل النص العربي واتجاهه ليُعرض بشكل صحيح في pygame.
    """
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    return font.render(bidi_text, True, color)


class Button:
    def __init__(self, rect, text, callback, font, bg=PRIMARY, fg=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.bg = bg
        self.fg = fg

    def draw(self, surf):
        pygame.draw.rect(surf, self.bg, self.rect, border_radius=8)
        text_s = render_arabic(self.text, self.font, self.fg)
        txt_rect = text_s.get_rect(center=self.rect.center)
        surf.blit(text_s, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()


class GameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("لعبة XO")
        self.clock = pygame.time.Clock()

        # خطوط النص
        self.font = pygame.font.Font(FONT_NAME, 22)
        self.bigfont = pygame.font.Font(FONT_NAME, 32)

        # AI والإحصائيات
        self.game = TicTacToe()
        self.vs_ai = True
        self.ai_difficulty = "hard"
        self.round_start = datetime.now()

        # hue لفلترة الألوان الفسفورية
        self.hue = 0

        # أزرار الواجهة
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        pad, btn_w = 12, 140
        x, y = WIDTH - btn_w - pad, WIDTH + 10
        self.buttons.append(Button((x, y, btn_w, 40), "إعادة تشغيل", self.reset_game, self.font))
        y += 50
        self.buttons.append(Button((x, y, btn_w, 40), "تغيير الوضع", self.toggle_mode, self.font, bg=(180,100,160)))
        y += 50
        self.buttons.append(Button((x, y, btn_w, 40), "مستوى AI", self.cycle_ai, self.font, bg=(200,140,60)))

    def cycle_ai(self):
        order = ["easy", "medium", "hard"]
        idx = order.index(self.ai_difficulty)
        self.ai_difficulty = order[(idx + 1) % len(order)]

    def toggle_mode(self):
        self.vs_ai = not self.vs_ai

    def reset_game(self):
        self.game.reset()
        self.round_start = datetime.now()

    def draw_grid(self):
        for i in range(1, GRID_SIZE):
            pygame.draw.line(self.screen, BLACK, (i*CELL_SIZE, 0), (i*CELL_SIZE, WIDTH), 3)
            pygame.draw.line(self.screen, BLACK, (0, i*CELL_SIZE), (WIDTH, i*CELL_SIZE), 3)

    def draw_cells(self):
        for r in range(3):
            for c in range(3):
                val = self.game.board[r][c]
                if val:
                    center = (c*CELL_SIZE + CELL_SIZE//2, r*CELL_SIZE + CELL_SIZE//2)
                    color = ACCENT if val == "X" else PRIMARY
                    txt = self.bigfont.render(val, True, color)
                    rect = txt.get_rect(center=center)
                    self.screen.blit(txt, rect)

    def draw_ui_panel(self):
        panel_rect = pygame.Rect(0, WIDTH, WIDTH, HEIGHT - WIDTH)
        pygame.draw.rect(self.screen, (250, 250, 250), panel_rect)

        status = f"الدور: {self.game.current_player} | الوضع: {'كمبيوتر' if self.vs_ai else 'لاعبين'} | AI: {self.ai_difficulty}"
        status_surf = render_arabic(status, self.font, BLACK)
        self.screen.blit(status_surf, (14, WIDTH + 8))

        stats_txt = f"X: {self.game.stats['X']} | O: {self.game.stats['O']} | تعادلات: {self.game.stats['Draws']}"
        stats_surf = render_arabic(stats_txt, self.font, (80, 80, 80))
        self.screen.blit(stats_surf, (14, WIDTH + 40))

        elapsed = datetime.now() - self.round_start
        mm, ss = divmod(int(elapsed.total_seconds()), 60)
        time_txt = f"الوقت: {mm:02d}:{ss:02d}"
        time_surf = render_arabic(time_txt, self.font, (100, 100, 100))
        self.screen.blit(time_surf, (14, WIDTH + 70))

        if self.game.winner:
            msg = "تعادل!" if self.game.winner == "Draw" else f"الفائز: {self.game.winner}"
            big_surf = render_arabic(msg, pygame.font.Font(FONT_NAME, 36), ACCENT)
            rect = big_surf.get_rect(center=(WIDTH // 2, WIDTH + 100))
            self.screen.blit(big_surf, rect)

    def draw_flashing_name(self):
        # زيادة hue وتدوير بين 0-360
        self.hue = (self.hue + 1) % 360
        # تحويل HSV إلى RGB
        r, g, b = colorsys.hsv_to_rgb(self.hue / 360.0, 1.0, 1.0)
        color = (int(r*255), int(g*255), int(b*255))
        # عرض الاسم مع اللون المتغير
        surf = render_arabic("اعدد الطالب: ايمن المهدي", self.font, color)
        rect = surf.get_rect(midtop=(WIDTH // 4.5, 640))
        self.screen.blit(surf, rect)

    def handle_click_on_board(self, pos):
        x, y = pos
        if y >= WIDTH or self.game.winner:
            return
        row, col = y // CELL_SIZE, x // CELL_SIZE
        moved = self.game.make_move(row, col)
        if moved and self.vs_ai and not self.game.winner and self.game.current_player == "O":
            move = self.game.best_move(self.ai_difficulty)
            if move:
                self.game.make_move(*move)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for b in self.buttons:
                        b.handle_event(event)
                    self.handle_click_on_board(event.pos)

            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_cells()
            self.draw_ui_panel()
            for b in self.buttons:
                b.draw(self.screen)

            # النص الثابت الملون الفسفوري
            self.draw_flashing_name()

            pygame.display.flip()
            self.clock.tick(FPS)
