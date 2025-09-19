# settings.py
# إعدادات عامة للعبة (ألوان، أحجام، خطوط)

# ألوان
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (200, 200, 200)
PRIMARY = [30, 144, 255]
ACCENT = (255, 99, 71)

WIDTH, HEIGHT = 520, 700   # مساحة اللعب + واجهة تحتها
GRID_SIZE = 3
CELL_SIZE = WIDTH // GRID_SIZE

FONT_NAME = "خط مزخرف1.ttf"  # None => الخط الافتراضي من pygame
FPS = 60