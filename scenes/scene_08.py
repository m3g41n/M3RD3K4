"""SCENE 08 - THE CONSTITUTIONAL FOUNDATION: three quiet statements over a slow fractal."""
from animations.fractal import MandelbrotZoom
from core import config as cfg
from scenes.base import Scene
from utils.text import draw_message, message_alpha, spaced

LINES = [
    "Bahwa sesungguhnya kemerdekaan itu ialah hak segala bangsa.",
    "Oleh sebab itu, penjajahan di atas dunia harus dihapuskan.",
    "Karena tidak sesuai dengan perikemanusiaan dan perikeadilan.",
]
START, SLOT = 1.5, 6.9


class Scene08(Scene):
    name = "The Constitutional Foundation"
    duration = START + SLOT * len(LINES) + 1.0
    fade_in = 1.8
    fade_out = 2.0

    def setup(self, w, h, ctx):
        super().setup(w, h, ctx)
        self.bg = MandelbrotZoom()

    def draw(self, canvas, t, dt):
        self.bg.draw(canvas, t)
        for i, text in enumerate(LINES):
            t0 = START + i * SLOT
            a = message_alpha(t, t0, t0 + SLOT, fade=1.3)
            if a > 0.02:
                draw_message(canvas, text, self.h // 2, a, spaced_ok=False, clear_pad=(4, 2), rules=True)
                label = cfg.CONSTITUTION_LABEL
                if label:
                    s = spaced(label, 2) if len(spaced(label, 2)) < self.w - 6 else label
                    canvas.clear_rect((self.w - len(s)) // 2 - 3, 2, (self.w + len(s)) // 2 + 3, 5)
                    canvas.text_center(3, s, 240 if a < 0.6 else 244)
