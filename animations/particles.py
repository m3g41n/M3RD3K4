"""Particles that drift, collide at the centre, and settle into a rising-sun formation."""
import math

import numpy as np

from core import config as cfg
from utils.timing import smoothstep


class ParticleConvergence:
    def __init__(self, w, h, rng, count=250):
        self.w, self.h = w, h
        n = self.n = count
        g = np.random.default_rng(rng.randrange(1 << 30))
        self.cx, self.cy = w / 2.0, h * 0.38
        R = min(w * 0.20, h * 0.40)
        # --- formation (polar): outer ring, inner ring, 12 rays, core -------------
        r_list, th_list, kind = [], [], []
        for i in range(90):
            r_list.append(R); th_list.append(2 * math.pi * i / 90); kind.append(1)
        for i in range(56):
            r_list.append(R * 0.62); th_list.append(2 * math.pi * i / 56 + 0.05); kind.append(1)
        for ray in range(12):
            for j in range(6):
                r_list.append(R * (1.18 + 0.08 * j)); th_list.append(2 * math.pi * ray / 12); kind.append(0)
        for i in range(n - len(r_list)):
            r_list.append(R * 0.2 * g.random()); th_list.append(g.random() * 6.28); kind.append(2)
        self.r = np.array(r_list[:n]); self.th = np.array(th_list[:n]); self.kind = np.array(kind[:n])
        # --- paths -----------------------------------------------------------------
        self.sx = g.random(n) * w
        self.sy = g.random(n) * h * 0.85
        self.cpx = self.cx + g.normal(0, w * 0.035, n)       # control points cluster at the centre:
        self.cpy = self.cy + g.normal(0, h * 0.05, n)        # particles pass through each other
        self.delay = g.random(n) * 0.4
        self.ph = g.random(n) * 6.28
        self.white = (np.arange(n) % 9 == 0)

    def positions(self, t, p):
        q = np.clip((p - self.delay) / 0.6, 0, 1)
        q = q * q * (3 - 2 * q)
        spin = 0.12 * t * cfg.motion() * q
        breathe = 1 + 0.035 * math.sin(1.1 * t)
        tx = self.cx + self.r * breathe * np.cos(self.th + spin)
        ty = self.cy + 0.5 * self.r * breathe * np.sin(self.th + spin)
        drift = (1 - q)
        sx = self.sx + 2.0 * np.sin(0.5 * t + self.ph) * drift
        sy = self.sy + 1.0 * np.cos(0.4 * t + self.ph) * drift
        x = (1 - q) ** 2 * sx + 2 * (1 - q) * q * self.cpx + q * q * tx
        y = (1 - q) ** 2 * sy + 2 * (1 - q) * q * self.cpy + q * q * ty
        wob = q * (1 - q) * 3.0
        return x + wob * np.sin(2.5 * t + self.ph), y + 0.5 * wob * np.cos(2.1 * t + self.ph), q

    def draw(self, canvas, t, p, alpha=1.0):
        x, y, q = self.positions(t, p)
        tx, ty, _ = self.positions(t - 0.12, p)
        for i in range(self.n):
            moving = 0.02 < q[i] < 0.97
            if moving:
                canvas.put(int(round(tx[i])), int(round(ty[i])), ".", 29 if q[i] > 0.4 else 238)
            if q[i] < 0.35:
                c, col = ".", 244 if q[i] < 0.1 else 247
            elif q[i] < 0.9:
                c, col = "o", 36
            else:
                c = "@" if self.kind[i] == 2 else ("*" if self.kind[i] == 1 else ".")
                col = 42
            if self.white[i] and q[i] > 0.5:
                col = 255
            canvas.put(int(round(x[i])), int(round(y[i])), c, col)

    @property
    def bottom(self):
        return int(self.cy + 0.5 * self.r.max() * 1.1) + 1
