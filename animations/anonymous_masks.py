"""The two theatrical masks: separated from the supplied image and animated.

Each mask becomes its own sprite. Motion is built by warping the real image data:
drift, tiny rotation, eye squash/stretch (and blinks), mouth open/close and widen.
A noise dissolve provides the "emerge from darkness" reveal.
"""
import math

import numpy as np

from utils.image_to_ascii import (block_mean, dilate, label_components, load_gray,
                                  sample_bilinear, sample_grid)

RAMP = np.array([ord(c) for c in " .:-=+*#%@"], dtype=np.int32)

# Feature positions in the supplied 526x473 image: (cx, cy, rx, ry) in pixels.
FEATURES = {
    "sad":   dict(eyes=[(110, 262, 24, 14), (193, 222, 24, 14)], mouth=(200, 340, 42, 30)),
    "happy": dict(eyes=[(315, 187, 24, 14), (395, 218, 24, 14)], mouth=(313, 290, 40, 30)),
}


class MaskState:
    __slots__ = ("dx", "dy", "rot", "mouth_y", "mouth_x", "eye_y")

    def __init__(self, dx=0.0, dy=0.0, rot=0.0, mouth_y=1.0, mouth_x=1.0, eye_y=(1.0, 1.0)):
        self.dx, self.dy, self.rot = dx, dy, rot
        self.mouth_y, self.mouth_x, self.eye_y = mouth_y, mouth_x, eye_y


def idle_state(t, phase, kind, motion=1.0):
    """Gentle, independent life for one mask at scene-time t."""
    m = motion
    sad = kind == "sad"
    blink_a = _blink(t + phase * 1.7, 5.3)
    blink_b = _blink(t + phase * 1.7 - 0.12, 5.3)
    mouth = 1.0 + m * ((0.34 if sad else 0.22) * math.sin(0.55 * t + phase))
    return MaskState(
        dx=m * 0.012 * math.sin(0.5 * t + phase),
        dy=m * 0.010 * math.sin(0.37 * t + 2 * phase),
        rot=m * 0.022 * math.sin(0.31 * t + phase),
        mouth_y=mouth,
        mouth_x=1.0 + m * 0.14 * math.sin(0.43 * t + phase * 1.3),
        eye_y=((1.0 + m * 0.16 * math.sin(0.8 * t + phase)) * (1 - 0.75 * blink_a),
               (1.0 + m * 0.16 * math.sin(0.7 * t + phase + 1)) * (1 - 0.75 * blink_b)),
    )


def _blink(t, period):
    x = (t % period)
    return max(0.0, 1.0 - abs(x - 0.2) / 0.16) if x < 0.4 else 0.0


class MaskSprite:
    def __init__(self, lum, bbox, features, noise_seed):
        self.lum = lum
        self.bbox = bbox              # (x0, y0, x1, y1) in source pixels
        H, W = lum.shape
        self.size_px = (W, H)
        x0, y0 = bbox[0], bbox[1]
        self.eyes = [((cx - x0) / W, (cy - y0) / H, rx / W, ry / H) for cx, cy, rx, ry in features["eyes"]]
        mx, my, rx, ry = features["mouth"]
        self.mouth = ((mx - x0) / W, (my - y0) / H, rx / W, ry / H)
        self._noise = {}
        self._seed = noise_seed

    def noise(self, rows, cols):
        key = (rows, cols)
        if key not in self._noise:
            self._noise[key] = np.random.default_rng(self._seed).random((rows, cols))
        return self._noise[key]

    def fit(self, max_cols, max_rows):
        W, H = self.size_px
        s = min(max_cols / W, max_rows * 2.0 / H)
        return max(1, int(W * s)), max(1, int(H * s / 2.0))

    def render(self, cols, rows, st=None, reveal=1.0):
        st = st or MaskState()
        SY, SX = 3, 2
        U, V = sample_grid(rows, cols, SY, SX)
        W, H = self.size_px
        x, y = (U - 0.5) * W, (V - 0.5) * H
        c, s = math.cos(st.rot), math.sin(st.rot)
        U1 = (c * x + s * y) / W + 0.5 - st.dx
        V1 = (-s * x + c * y) / H + 0.5 - st.dy
        for (fu, fv, ru, rv), ey in zip(self.eyes, st.eye_y):
            g = np.exp(-(((U1 - fu) / (ru * 1.6)) ** 2 + ((V1 - fv) / (rv * 1.6)) ** 2))
            V1 = fv + (V1 - fv) / (1 + g * (max(ey, 0.15) - 1))
        fu, fv, ru, rv = self.mouth
        g = np.exp(-(((U1 - fu) / (ru * 1.7)) ** 2 + ((V1 - fv) / (rv * 1.7)) ** 2))
        V1 = fv + (V1 - fv) / (1 + g * (max(st.mouth_y, 0.2) - 1))
        U1 = fu + (U1 - fu) / (1 + g * (st.mouth_x - 1))
        L = block_mean(sample_bilinear(self.lum, U1, V1), SY, SX)
        L = np.clip((L - 0.04) / 0.80, 0, 1) ** 1.45
        if reveal < 1.0:
            a = np.clip(reveal * 1.6 - self.noise(rows, cols) * 0.6, 0, 1)
            L = L * a
        ch = RAMP[np.minimum((L * 9.99).astype(int), 9)]
        fg = np.select([L < 0.15, L < 0.3, L < 0.5, L < 0.7, L < 0.85],
                       [22, 29, 36, 42, 250], 255).astype(np.uint8)
        ch = np.where(L < 0.05, 32, ch).astype(np.int32)
        return ch, fg


class MaskPair:
    def __init__(self, path):
        self.error = None
        lum = None
        if path:
            try:
                lum = load_gray(path)
            except Exception as e:
                self.error = str(e)
        else:
            self.error = "no image found in assets/anonymous_masks/"
        if lum is None:
            lum = self._placeholder()
        self.sprites = self._split(lum)      # [left (sad), right (happy)]

    @staticmethod
    def _placeholder():
        from PIL import Image, ImageDraw
        im = Image.new("L", (526, 473), 0)
        d = ImageDraw.Draw(im)
        d.ellipse((50, 130, 240, 400), fill=210)
        d.ellipse((270, 80, 470, 350), fill=225)
        for box in ((90, 250, 130, 275), (175, 210, 215, 235), (295, 175, 335, 200),
                    (375, 205, 415, 230), (165, 315, 235, 365), (280, 265, 345, 320)):
            d.ellipse(box, fill=0)
        return np.asarray(im, dtype=float) / 255.0

    @staticmethod
    def _enhance(crop):
        """Local-contrast boost so facial relief survives the jump to ~10 ASCII levels."""
        from PIL import Image, ImageFilter
        im = Image.fromarray((np.clip(crop, 0, 1) * 255).astype("uint8"))
        blur = np.asarray(im.filter(ImageFilter.GaussianBlur(7)), dtype=float) / 255.0
        out = crop + 1.6 * (crop - blur) * (crop > 0.02)
        return np.clip(out, 0, 1)

    def _split(self, lum):
        H, W = lum.shape
        small = lum[::2, ::2] > 0.10
        labels, n = label_components(small)
        masks = []
        if n >= 2:
            sizes = [(int((labels == i).sum()), i) for i in range(1, n + 1)]
            sizes.sort(reverse=True)
            ids = [sizes[0][1], sizes[1][1]]
            full = [np.kron(labels == i, np.ones((2, 2), bool))[:H, :W] for i in ids]
            full = [np.pad(m, ((0, H - m.shape[0]), (0, W - m.shape[1]))) for m in full]
            cx = [np.nonzero(m)[1].mean() for m in full]
            if cx[0] > cx[1]:
                full.reverse()
            masks = [dilate(full[0], 2) & ~full[1], dilate(full[1], 2) & ~full[0]]
        else:   # masks touch: split down the middle
            xs = np.arange(W)[None, :].repeat(H, 0)
            bright = lum > 0.05
            masks = [bright & (xs < W * 0.49), bright & (xs >= W * 0.49)]
        sprites = []
        for kind, m, seed in zip(("sad", "happy"), masks, (11, 23)):
            ys, xs = np.nonzero(m)
            pad = 16
            x0, x1 = max(0, xs.min() - pad), min(W, xs.max() + pad + 1)
            y0, y1 = max(0, ys.min() - pad), min(H, ys.max() + pad + 1)
            crop = self._enhance((lum * m)[y0:y1, x0:x1])
            sprites.append(MaskSprite(crop, (x0, y0, x1, y1), FEATURES[kind], seed))
        return sprites

    def layout(self, max_cols, max_rows):
        """Place both masks as they sit in the source image, scaled to fit."""
        bx = [s.bbox for s in self.sprites]
        X0, Y0 = min(b[0] for b in bx), min(b[1] for b in bx)
        X1, Y1 = max(b[2] for b in bx), max(b[3] for b in bx)
        s = min(max_cols / (X1 - X0), max_rows * 2.0 / (Y1 - Y0))
        out = []
        for b in bx:
            out.append((int((b[0] - X0) * s), int((b[1] - Y0) * s / 2),
                        max(1, int((b[2] - b[0]) * s)), max(1, int((b[3] - b[1]) * s / 2))))
        total = (max(o[0] + o[2] for o in out), max(o[1] + o[3] for o in out))
        return total, out
