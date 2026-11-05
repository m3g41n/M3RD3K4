"""Slow geometric/fractal backgrounds: a log-polar tunnel and a Mandelbrot zoom."""
import math

import numpy as np

from core import config as cfg

TUNNEL_CHARS = np.array([32, ord("."), ord(":"), ord("+"), ord("*")], dtype=np.int32)
BAND_CHARS = np.array([32, ord("."), 32, ord(":"), 32, ord(".")], dtype=np.int32)   # sparse on purpose


class TunnelZoom:
    """Nested rounded squares receding to the centre; very slow rotation."""

    def draw(self, canvas, t, colors=(0, 234, 236, 238, 240)):
        t *= cfg.motion()
        h, w = canvas.h, canvas.w
        yy, xx = np.mgrid[0:h, 0:w]
        px, py = (xx + 0.5 - w / 2) / 2.0, (yy + 0.5 - h / 2)
        a = 0.12 * math.sin(0.08 * t)
        c, s = math.cos(a), math.sin(a)
        xr, yr = px * c - py * s, px * s + py * c
        r = np.maximum((np.abs(xr) ** 4 + np.abs(yr) ** 4) ** 0.25, 0.5)
        f = (np.log(r) * 3.2 - t * 0.2) % 1.0
        line = np.exp(-((f - 0.5) / 0.09) ** 2) * np.clip((r - 2.0) / 6.0, 0, 1)
        lvl = np.clip((line * 4.99).astype(int), 0, 4)
        m = lvl > 0
        canvas.ch[m] = TUNNEL_CHARS[lvl[m]]
        canvas.fg[m] = np.array(colors, dtype=np.uint8)[lvl[m]]


class MandelbrotZoom:
    """Continuous zoom into the seahorse valley, drawn as drifting character bands."""
    CENTER = (-0.7436438870371587, 0.13182590420531198)

    def draw(self, canvas, t, colors=(0, 22, 0, 22, 0, 236)):
        t *= cfg.motion()
        h, w = canvas.h, canvas.w
        scale = 2.8 * math.exp(-0.13 * t)
        unit = scale / (h / 2.0)
        yy, xx = np.mgrid[0:h, 0:w]
        c = (self.CENTER[0] + (xx - w / 2 + 0.5) * unit * 0.5) + 1j * (self.CENTER[1] + (yy - h / 2 + 0.5) * unit)
        z = np.zeros_like(c)
        n = np.zeros(c.shape, dtype=np.int32)
        alive = np.ones(c.shape, dtype=bool)
        maxit = int(min(120, 40 + 14 * math.log(2.8 / scale + 1)))
        for i in range(maxit):
            z[alive] = z[alive] ** 2 + c[alive]
            esc = alive & (z.real ** 2 + z.imag ** 2 > 4.0)
            n[esc] = i
            alive &= ~esc
        band = (((n + t * 2.0) % 12) / 12.0 * 5.99).astype(int)
        m = ~alive & (n >= 3)
        canvas.ch[m] = BAND_CHARS[band[m]]
        canvas.fg[m] = np.array(colors, dtype=np.uint8)[band[m]]
