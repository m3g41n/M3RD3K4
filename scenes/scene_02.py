"""SCENE 02 - THE FLOW OF THOUGHT: an ASCII wave that condenses into the hand symbol."""
import numpy as np

from animations.ascii_wave import AsciiWave
from animations.three_fingers import NEUTRAL, hand_layout, pulse_at
from core.renderer import Canvas
from scenes.base import Scene
from utils.text import draw_caption
from utils.timing import smoothstep

MORPH_START, MORPH_END = 10.0, 16.0


class Scene02(Scene):
    name = "The Flow of Thought"
    duration = 17.0
    fade_in = 2.0
    fade_out = 0.0          # seamless hand-over into scene 03

    def setup(self, w, h, ctx):
        super().setup(w, h, ctx)
        self.wave = AsciiWave(w, h, ctx.rng)
        cols, rows, x, y = hand_layout(ctx.hand, w, h)
        lay = Canvas(w, h)
        ch, fg = ctx.hand.render(cols, rows, NEUTRAL, pulse_at(0))
        lay.blit(ch, fg, x, y)
        self.hand_ch, self.hand_fg = lay.ch, lay.fg
        g = np.random.default_rng(7)
        nz, self.nz2 = g.random((h, w)), g.random((h, w))
        yy, xx = np.mgrid[0:h, 0:w]
        dist = np.hypot((xx - (x + cols / 2)) / (cols / 2 + 1), (yy - (y + rows / 2)) / (rows / 2 + 1))
        self.key = 0.65 * np.clip(dist / 1.6, 0, 1) + 0.35 * nz     # hand grows outward from its core
        self.layer = Canvas(w, h)

    def draw(self, canvas, t, dt):
        p = smoothstep(MORPH_START, MORPH_END, t)
        self.layer.clear()
        self.wave.draw(self.layer, t, amp=1 - 0.35 * p, alpha=1 - 0.5 * p, collapse=0.6 * p)
        if p <= 0:
            canvas.ch[:] = self.layer.ch
            canvas.fg[:] = self.layer.fg
        else:
            hand = self.hand_ch != 32
            lead = p * 1.3 - self.key
            shown = hand & (lead > 0)
            spark = shown & (lead < 0.12) & (p < 1)
            keep = (self.layer.ch != 32) & ~shown & (self.nz2 > p * 1.15)
            canvas.ch[:] = np.where(shown, self.hand_ch, np.where(keep, self.layer.ch, 32))
            canvas.fg[:] = np.where(shown, self.hand_fg, np.where(keep, self.layer.fg, 0))
            canvas.ch[spark] = ord("*")
            canvas.fg[spark] = 255
        draw_caption(canvas, "THE FLOW OF THOUGHT", smoothstep(1.5, 3.0, t) * (1 - smoothstep(11.0, 12.5, t)))
