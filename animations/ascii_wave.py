"""ASCII waves: layered sine ribbons drawn with slope-aware characters."""
import math

import numpy as np

from core import config as cfg
from utils.color import EMERALD_RAMP, ramp_pick


class AsciiWave:
    CURVES = 9

    def __init__(self, w, h, rng):
        self.w, self.h = w, h
        # One shared wave shape; each ribbon is a phase-shifted copy, so the layers flow
        # together like a single sheet instead of tangling.
        base = (rng.uniform(0.052, 0.064), rng.uniform(0.55, 0.7), rng.uniform(0, 6.28),
                rng.uniform(0.115, 0.14), rng.uniform(0.4, 0.55), rng.uniform(0, 6.28))
        self.p = [(base[0], base[1], base[2] + i * 0.30, base[3], base[4], base[5] + i * 0.55)
                  for i in range(self.CURVES)]
        x = np.arange(w)
        self.env = 0.4 + 0.6 * np.sin(np.pi * (x + 0.5) / w)     # tapers toward the edges

    def curve(self, i, t, amp, collapse, yc):
        k1, w1, p1, k2, w2, p2 = self.p[i]
        x = np.arange(self.w)
        spread = (i - (self.CURVES - 1) / 2) * self.h * 0.042 * (1 - collapse)
        a = self.h * 0.105 * amp * (0.8 + 0.2 * math.sin(0.23 * t + i * 0.3)) * self.env
        m = cfg.motion()
        return yc + spread + a * np.sin(k1 * x + w1 * t * m + p1) + 0.28 * a * np.sin(k2 * x - w2 * t * m + p2)

    def draw(self, canvas, t, amp=1.0, alpha=1.0, collapse=0.0, yc=None):
        yc = self.h * 0.5 if yc is None else yc
        n = self.CURVES
        order = sorted(range(n), key=lambda i: -abs(i - (n - 1) / 2))   # centre curve drawn last
        for i in order:
            y = self.curve(i, t, amp, collapse, yc)
            slope = np.gradient(y)
            d = abs(i - (n - 1) / 2) / ((n - 1) / 2)
            bright = (1 - 0.72 * d) * alpha
            col = 255 if (d < 0.2 and bright > 0.8) else ramp_pick(EMERALD_RAMP, bright)
            for x in range(self.w):
                yy = y[x]
                ry = int(math.floor(yy + 0.5))
                fr = yy - ry
                s = slope[x]
                if abs(s) < 0.28:
                    c = "`" if fr < -0.17 else ("_" if fr > 0.17 else "-")
                elif abs(s) > 1.3:
                    c = "|"
                else:
                    c = "\\" if s > 0 else "/"
                canvas.put(x, ry, c, col)
                if d > 0.5 and x % 3 == 0:          # faint dotted echo under outer ribbons
                    canvas.put(x, ry + 2, ".", ramp_pick(EMERALD_RAMP, bright * 0.4))
