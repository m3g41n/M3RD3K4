"""The three-finger symbol: converted from the supplied image and *animated*.

The source image has no motion, so poses are constructed procedurally by warping
the real image data:
  * each raised finger is shortened/lengthened independently (finger "bending"),
  * fingers sway about their common base,
  * the thumb region flexes,
  * the whole hand breathes (tiny scale pulse).
The warped ink + silhouette maps are re-sampled to ASCII every frame.
"""
import numpy as np

from utils.color import EMERALD_RAMP, ramp_pick
from utils.image_to_ascii import (block_mean, dilate, fit_cells, flood_from_border,
                                  load_gray, sample_bilinear, sample_grid)

# Measured on the supplied image (fractions of the ink bounding box).
FINGER_EDGES = (0.101, 0.329, 0.538, 0.741)   # x of outer-left / 2 dividers / outer-right
BASE_V = 0.48                                 # y where the fingers meet the palm
INK_CHARS = np.array([ord(c) for c in ".:-=+*#%@"], dtype=np.int32)


class Pose:
    __slots__ = ("s", "sw", "sway", "thumb")

    def __init__(self, s=(1.0, 1.0, 1.0), sw=(0.0, 0.0, 0.0), sway=0.0, thumb=(0.0, 0.0)):
        self.s, self.sw, self.sway, self.thumb = s, sw, sway, thumb


NEUTRAL = Pose()


class HandSprite:
    def __init__(self, path):
        self.error = None
        g = None
        if path:
            try:
                g = load_gray(path)
            except Exception as e:          # missing / corrupt file
                self.error = str(e)
        else:
            self.error = "no image found in assets/three_fingers/"
        if g is None:
            g = self._placeholder()
        self._prepare(g)

    # -- preparation -------------------------------------------------------
    @staticmethod
    def _placeholder():
        from PIL import Image, ImageDraw
        im = Image.new("L", (100, 200), 225)
        d = ImageDraw.Draw(im)
        for x, top in ((20, 14), (40, 8), (60, 18)):
            d.rounded_rectangle((x, top, x + 18, 120), 8, outline=20, width=2)
        d.rounded_rectangle((14, 100, 84, 170), 14, outline=20, width=2)
        d.rectangle((30, 168, 68, 199), outline=20, width=2)
        return np.asarray(im, dtype=float) / 255.0

    def _prepare(self, g):
        bg = float(np.median(g))
        ink = np.clip((bg - 0.2 - g) / 0.4, 0, 1)          # dark line work -> 1
        ys, xs = np.nonzero(ink > 0.3)
        if len(ys) == 0:
            ink[:] = 0
            ink[g.shape[0] // 4: 3 * g.shape[0] // 4, g.shape[1] // 3: 2 * g.shape[1] // 3] = 1
            ys, xs = np.nonzero(ink > 0.3)
        bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
        bw, bh = bx1 - bx0 + 1, by1 - by0 + 1
        pad = int(max(bw, bh) * 0.06)
        x0, x1 = max(0, bx0 - pad), min(g.shape[1], bx1 + pad + 1)
        y0, y1 = max(0, by0 - pad), min(g.shape[0], by1 + pad + 1)
        ink = ink[y0:y1, x0:x1]
        ink = np.maximum(ink, 0.8 * dilate(ink > 0.45, 1))  # thicken hairlines a touch
        self.ink = ink
        self.fill = self._silhouette(ink)
        H, W = ink.shape
        self.size_px = (W, H)
        self.edges = [((bx0 - x0) + e * bw) / W for e in FINGER_EDGES]
        self.base_v = ((by0 - y0) + BASE_V * bh) / H
        self.thumb_c = (((bx0 - x0) + 0.50 * bw) / W, ((by0 - y0) + 0.60 * bh) / H)

    @staticmethod
    def _silhouette(ink):
        closed = dilate(ink > 0.3, 2)
        closed[-1, :] = True                      # seal the open wrist
        outside = flood_from_border(~closed)
        fill = ~dilate(outside, 1)
        frac = fill.mean()
        return fill.astype(float) if 0.05 < frac < 0.95 else np.zeros_like(ink)

    # -- geometry ----------------------------------------------------------
    def fit(self, max_cols, max_rows):
        return fit_cells(self.size_px[0], self.size_px[1], max_cols, max_rows)

    def _warp(self, U, V, pose, pulse):
        e = self.edges
        w = 0.025
        sig = lambda x: 1.0 / (1.0 + np.exp(-x))
        g = [sig((U - e[i]) / w) - sig((U - e[i + 1]) / w) for i in range(3)]
        s = 1.0 + sum(g[i] * (pose.s[i] - 1.0) for i in range(3))
        sw = pose.sway + sum(g[i] * pose.sw[i] for i in range(3))
        vb = self.base_v
        above = V < vb
        Vp = np.where(above, vb + (V - vb) / np.maximum(s, 0.25), V)   # finger length
        lift = np.clip((vb - V) / vb, 0, 1)
        Up = U - sw * lift ** 1.4                                        # sway about the base
        k = 1.0 + 0.012 * pulse                                          # breathing
        Up = 0.5 + (Up - 0.5) / k
        Vp = 0.5 + (Vp - 0.5) / k
        if pose.thumb[0] or pose.thumb[1]:                               # thumb flex
            tu, tv = self.thumb_c
            gt = np.exp(-(((U - tu) / 0.17) ** 2 + ((V - tv) / 0.11) ** 2))
            Up = Up - gt * pose.thumb[0]
            Vp = Vp - gt * pose.thumb[1]
        return Up, Vp

    # -- rendering ---------------------------------------------------------
    def render(self, cols, rows, pose=None, pulse=0.0):
        """Return (ch, fg) int32/uint8 arrays of shape (rows, cols)."""
        SY, SX = 4, 2
        U, V = sample_grid(rows, cols, SY, SX)
        Up, Vp = self._warp(U, V, pose or NEUTRAL, pulse)
        d = block_mean(sample_bilinear(self.ink, Up, Vp), SY, SX)
        f = block_mean(sample_bilinear(self.fill, Up, Vp), SY, SX)
        dn = np.clip(d * 2.6, 0, 1)
        ch = np.full(d.shape, 32, dtype=np.int32)
        fg = np.zeros(d.shape, dtype=np.uint8)
        body = f > 0.45
        ch[body] = ord(".")
        fg[body] = ramp_pick(EMERALD_RAMP, 0.08 + 0.22 * pulse)
        line = dn > 0.14
        ch[line] = INK_CHARS[np.minimum((dn[line] * 9).astype(int), 8)]
        fg[line] = np.select([dn[line] > 0.7, dn[line] > 0.4], [255, 252], 42)
        return ch, fg


def hand_layout(hand, w, h, top=2, reserve_bottom=4, max_rows=40):
    """Shared placement so scene 02's morph lands exactly where scene 03 draws it."""
    avail = max(6, h - top - reserve_bottom)
    cols, rows = hand.fit(w - 4, min(max_rows, avail))
    return cols, rows, (w - cols) // 2, top + (avail - rows) // 2


def gesture_pose(t, motion=1.0):
    """Scene 03 choreography: three single-finger gestures, then a rippling wave."""
    import math
    from utils.timing import bump, smoothstep
    s = [1.0, 1.0, 1.0]
    sw = [0.0, 0.0, 0.0]
    for i, t0 in enumerate((2.0, 6.6, 11.2)):
        s[i] -= 0.42 * motion * bump(t, t0, 1.7, 0.5, 1.7)
    r = smoothstep(15.5, 17.5, t) * (1 - smoothstep(21.5, 23.5, t)) * motion
    for i in range(3):
        s[i] -= r * 0.30 * (0.5 + 0.5 * math.sin(1.8 * t - i * 0.9))
        sw[i] += r * 0.03 * math.sin(1.4 * t - i * 0.7)
    env = smoothstep(0.0, 3.0, t)
    for i in range(3):
        s[i] *= 1 + 0.012 * env * math.sin(1.3 * t + i * 0.8)
    sway = r * 0.07 * math.sin(0.9 * t)
    thumb = (r * 0.02 * math.sin(1.4 * t), r * 0.03 * math.sin(1.1 * t))
    return Pose(tuple(s), tuple(sw), sway, thumb)


def calm_pose(t, motion=1.0):
    """Subtle ongoing life for the final composition."""
    import math
    m = motion
    return Pose(tuple(1 - 0.07 * m * (0.5 + 0.5 * math.sin(0.8 * t - i * 0.9)) for i in range(3)),
                (0, 0, 0), 0.015 * m * math.sin(0.5 * t), (0.006 * m * math.sin(0.7 * t), 0.008 * m * math.sin(0.9 * t)))


def pulse_at(t):
    import math
    return 0.5 - 0.5 * math.cos(2 * math.pi * t / 5.0)    # 0 at t=0, gentle 5 s cycle
