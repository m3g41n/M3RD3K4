"""SCENE 07 - THE DECLARATION: emerald fire frames the slogan without covering it."""
from animations.ascii_fire import AsciiFire
from scenes.base import Scene
from utils.color import EMERALD
from utils.text import best_big_px, draw_big, draw_message, draw_rule, spaced
from utils.color import gray
from utils.timing import bump, smoothstep

L1, L2 = "IF WE BURN,", "YOU BURN WITH US."
SUB = "SOLIDARITY AND SHARED CONSEQUENCES"


class Scene07(Scene):
    name = "The Declaration"
    duration = 23.0
    fade_in = 2.0
    fade_out = 2.0

    def setup(self, w, h, ctx):
        super().setup(w, h, ctx)
        self.fire_h = max(8, int(h * 0.36))
        self.fire = AsciiFire(w, self.fire_h, ctx.rng)
        self.px = best_big_px(L2, w - 6)
        self.block_h = 12 if self.px else 7
        self.top = max(1, (h - self.fire_h - self.block_h) // 2)

    def draw(self, canvas, t, dt):
        w = self.w
        inten = 0.15 + 0.62 * smoothstep(0.5, 5.0, t) + 0.16 * bump(t, 6.4, 1.2, 1.0, 2.5)
        self.fire.update(dt, inten)
        keep_clear = (3, self.top - 2, w - 3, self.top + self.block_h + 3)
        self.fire.draw(canvas, exclude=[keep_clear])
        p1, p2 = smoothstep(3.2, 6.0, t), smoothstep(6.4, 9.6, t)
        if self.px:
            draw_big(canvas, L1, self.top, p1, self.px)
            draw_big(canvas, L2, self.top + 6, p2, self.px)
            sub_y = self.top + 12
        else:
            for i, (txt, p) in enumerate(((L1, p1), (L2, p2))):
                if p > 0.02:
                    s = spaced(txt, 3) if len(spaced(txt, 3)) <= w - 4 else txt
                    canvas.text_center(self.top + 1 + i * 2, s, gray(p))
            draw_rule(canvas, self.top + 5, 24, p2)
            sub_y = self.top + 6
        a = smoothstep(11.0, 14.0, t)
        if a > 0.02:
            canvas.text_center(min(sub_y, self.h - 3), spaced(SUB, 2) if len(spaced(SUB, 2)) < w - 4 else SUB,
                               244 if a > 0.6 else 240)
