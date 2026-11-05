"""Canvas (a grid of characters + colours) and the ANSI frame renderer."""
import numpy as np


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.ch = np.full((h, w), 32, dtype=np.int32)
        self.fg = np.zeros((h, w), dtype=np.uint8)
        self._noise = None

    @property
    def noise(self):
        if self._noise is None:
            self._noise = np.random.default_rng(1234).random((self.h, self.w))
        return self._noise

    def clear(self):
        self.ch.fill(32)
        self.fg.fill(0)

    def put(self, x, y, c, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.ch[y, x] = ord(c) if isinstance(c, str) else c
            self.fg[y, x] = col

    def text(self, x, y, s, col, skip_space=True):
        if not 0 <= y < self.h:
            return
        for i, c in enumerate(s):
            if skip_space and c == " ":
                continue
            xx = x + i
            if 0 <= xx < self.w:
                self.ch[y, xx] = ord(c)
                self.fg[y, xx] = col

    def text_center(self, y, s, col):
        self.text((self.w - len(s)) // 2, y, s, col)

    def blit(self, ch, fg, x, y):
        """Copy non-space cells of (ch, fg) onto the canvas at (x, y), clipped."""
        hh, ww = ch.shape
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + ww), min(self.h, y + hh)
        if x0 >= x1 or y0 >= y1:
            return
        sc = ch[y0 - y:y1 - y, x0 - x:x1 - x]
        sf = fg[y0 - y:y1 - y, x0 - x:x1 - x]
        m = sc != 32
        self.ch[y0:y1, x0:x1][m] = sc[m]
        self.fg[y0:y1, x0:x1][m] = sf[m]

    def clear_rect(self, x0, y0, x1, y1):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w, x1), min(self.h, y1)
        if x0 < x1 and y0 < y1:
            self.ch[y0:y1, x0:x1] = 32
            self.fg[y0:y1, x0:x1] = 0


ENTER_SEQ = "\x1b[?1049h\x1b[?25l\x1b[?7l\x1b[48;5;16m\x1b[2J"
LEAVE_SEQ = "\x1b[0m\x1b[?7h\x1b[?25h\x1b[?1049l"


class Renderer:
    """Turns a Canvas into one ANSI string. Only changed rows are re-sent."""

    def __init__(self):
        self.prev = None
        self.size = None

    def reset(self):
        self.prev = None

    def render(self, canvas, color=True):
        h, w = canvas.h, canvas.w
        if self.prev is None or self.size != (w, h):
            self.prev = [None] * h
            self.size = (w, h)
        xs = np.arange(w)
        out = []
        for y in range(h):
            ch = canvas.ch[y]
            fg = canvas.fg[y]
            if color:
                idx = np.where(ch != 32, xs, 0)
                np.maximum.accumulate(idx, out=idx)
                f = fg[idx]
                key = (ch.tobytes(), f.tobytes())
            else:
                f = None
                key = ch.tobytes()
            if self.prev[y] == key:
                continue
            self.prev[y] = key
            text = ch.astype("<u4").tobytes().decode("utf-32-le")
            if color:
                cuts = np.flatnonzero(f[1:] != f[:-1]) + 1
                bounds = [0, *cuts.tolist(), w]
                segs = []
                for a, b in zip(bounds[:-1], bounds[1:]):
                    c = int(f[a])
                    segs.append(("\x1b[38;5;%dm" % c if c else "\x1b[39m") + text[a:b])
                out.append("\x1b[%d;1H%s" % (y + 1, "".join(segs)))
            else:
                out.append("\x1b[%d;1H%s" % (y + 1, text))
        return "".join(out)
