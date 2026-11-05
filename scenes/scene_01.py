"""SCENE 01 - INITIALIZATION: near-empty black, a restrained digital rain, slow title."""
from animations.digital_rain import DigitalRain
from scenes.base import Scene
from utils.color import EMERALD, EMERALD_DIM, GRAY, gray
from utils.text import draw_rule, spaced
from utils.timing import clamp, smoothstep

MSG = "M3RD3K4 SYSTEM INITIALIZING..."


class Scene01(Scene):
    name = "Initialization"
    duration = 17.0
    fade_in = 2.5
    fade_out = 1.8
    ambient_glitch = False

    def setup(self, w, h, ctx):
        super().setup(w, h, ctx)
        self.rain = DigitalRain(w, h, ctx.rng)

    def draw(self, canvas, t, dt):
        w, h = self.w, self.h
        cy = h // 2 - 2
        title = "THE AWAKENING OF MINDS"
        title = spaced(title, 3) if len(spaced(title, 3)) <= w - 8 else title
        bw = max(len(MSG), len(title)) + 8
        x0 = (w - bw) // 2
        self.rain.density = 0.05 + 0.17 * smoothstep(1.0, 9.0, t)
        self.rain.update(dt)
        self.rain.draw(canvas, alpha=0.75, exclude=[(x0, cy - 2, x0 + bw, cy + 9)])

        # typed init line + one slow cursor
        n = int(clamp((t - 1.8) / 3.0) * len(MSG))
        fade = 1 - 0.65 * smoothstep(12.5, 15.0, t)
        if n > 0:
            canvas.text((w - len(MSG)) // 2, cy, MSG[:n], gray(fade))
            if n < len(MSG) or (t < 9 and int(t * 1.4) % 2 == 0):
                canvas.put((w - len(MSG)) // 2 + n, cy, "_", EMERALD)
        # progress bar
        if t > 4.5:
            p = smoothstep(4.5, 9.0, t)
            k = int(p * 24)
            bar = "[" + "#" * k + "-" * (24 - k) + "] %3d%%" % int(p * 100)
            canvas.text((w - len(bar)) // 2, cy + 2, bar, EMERALD_DIM if p < 1 else EMERALD)
        # title
        a = smoothstep(9.5, 12.5, t)
        draw_rule(canvas, cy + 5, min(len(title), 40), a)
        canvas.text((w - len(title)) // 2, cy + 6, title, gray(a))
