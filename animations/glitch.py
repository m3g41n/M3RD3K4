"""Short, controlled glitch bursts: row displacement, ghosting, symbol swaps."""
import numpy as np

from core import config as cfg

SYMBOLS = np.array([ord(c) for c in "#@$%&*+=<>/\\|01:;"], dtype=np.int32)


class Glitch:
    def __init__(self, rng):
        self.rng = rng
        self.nprng = np.random.default_rng(rng.randrange(1 << 30))
        self.remaining = 0.0
        self.intensity = 0.0
        self.clock = 0.0
        self.next_ambient = rng.uniform(9, 14)

    def trigger(self, duration=0.25, intensity=0.8):
        if not cfg.glitch_enabled():
            return
        self.remaining = max(self.remaining, duration)
        self.intensity = max(self.intensity, intensity)

    def step(self, dt, ambient=False):
        self.clock += dt
        if self.remaining > 0:
            self.remaining -= dt
            if self.remaining <= 0:
                self.intensity = 0.0
        elif ambient and cfg.glitch_enabled() and self.clock >= self.next_ambient:
            self.trigger(0.14, 0.35)
            self.clock = 0.0
            self.next_ambient = self.rng.uniform(9, 16)

    def apply(self, canvas):
        if self.remaining <= 0 or not cfg.glitch_enabled():
            return
        r, I = self.rng, self.intensity
        h, w = canvas.h, canvas.w
        for _ in range(1 + int(3 * I)):
            y0 = r.randrange(h)
            band = slice(y0, min(h, y0 + r.randint(1, 3)))
            dx = r.choice((-1, 1)) * r.randint(2, 7)
            ghost_ch = np.roll(canvas.ch[band], dx, axis=1)
            ghost_fg = np.roll(canvas.fg[band], dx, axis=1)
            empty = canvas.ch[band] == 32
            # displaced band + a dim emerald ghost where the original was empty
            canvas.ch[band] = np.where(ghost_ch != 32, ghost_ch, canvas.ch[band])
            canvas.fg[band] = np.where(ghost_ch != 32, ghost_fg, canvas.fg[band])
            m = empty & (ghost_ch != 32)
            canvas.fg[band][m] = 29
        ys, xs = np.nonzero(canvas.ch != 32)
        if len(ys):
            n = int(len(ys) * 0.025 * I)
            if n:
                pick = self.nprng.integers(0, len(ys), n)
                canvas.ch[ys[pick], xs[pick]] = self.nprng.choice(SYMBOLS, n)
