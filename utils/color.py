"""Palette: deep black, emerald, white, muted gray (xterm-256 codes)."""
import numpy as np

_BASE16 = [(0, 0, 0), (205, 0, 0), (0, 205, 0), (205, 205, 0), (0, 0, 238), (205, 0, 205),
           (0, 205, 205), (229, 229, 229), (127, 127, 127), (255, 0, 0), (0, 255, 0),
           (255, 255, 0), (92, 92, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255)]

BLACK = 16
WHITE = 255
EMERALD = 42
EMERALD_DIM = 29
EMERALD_DEEP = 22
GRAY = 244
GRAY_DARK = 240

EMERALD_RAMP = (22, 29, 35, 36, 42, 48, 84, 121)          # dim -> bright
GRAY_RAMP = (233, 235, 238, 241, 244, 247, 250, 253, 255)  # near-black -> white
FIRE_RAMP = (22, 28, 29, 35, 36, 42, 48, 84, 121, 157, 194, 231)


def xterm_rgb(c):
    if c < 16:
        return _BASE16[c]
    if c < 232:
        c -= 16
        lv = (0, 95, 135, 175, 215, 255)
        return (lv[c // 36], lv[(c // 6) % 6], lv[c % 6])
    v = 8 + 10 * (c - 232)
    return (v, v, v)


PALETTE = np.array([xterm_rgb(i) for i in range(256)], dtype=float)
LUMA = PALETTE @ np.array([0.299, 0.587, 0.114])
GRAY_LUT = np.array(GRAY_RAMP, dtype=np.uint8)
EMERALD_LUT = np.array(EMERALD_RAMP, dtype=np.uint8)
FIRE_LUT = np.array(FIRE_RAMP, dtype=np.uint8)


def ramp_pick(ramp, a):
    a = 0.0 if a < 0 else 1.0 if a > 1 else a
    return ramp[int(round(a * (len(ramp) - 1)))]


def gray(a):
    return ramp_pick(GRAY_RAMP, a)


def emerald(a):
    return ramp_pick(EMERALD_RAMP, a)


def _nearest(rgb):
    d = ((rgb[:, None, :] - PALETTE[None, 16:, :]) ** 2).sum(-1)
    return d.argmin(1) + 16


def fade_table(levels):
    """tbl[k][code] = code darkened to k/levels brightness (nearest xterm colour)."""
    tbl = np.zeros((levels + 1, 256), dtype=np.uint8)
    for k in range(levels + 1):
        tbl[k] = _nearest(PALETTE * (k / levels))
        tbl[k, 0] = 0
    return tbl
