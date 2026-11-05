"""Restrained ASCII fire in emerald: heat-diffusion flames plus floating embers."""
import numpy as np

from core import config as cfg
from utils.color import FIRE_LUT

RAMP = np.array([ord(c) for c in " .:^*x#%@"], dtype=np.int32)
STEP = 1 / 11.0       # flame simulation rate; frames are interpolated between steps


class AsciiFire:
    def __init__(self, w, fire_h, rng):
        self.w, self.h = w, max(3, fire_h)
        self.rng = rng
        self.nrng = np.random.default_rng(rng.randrange(1 << 30))
        self.heat = np.zeros((self.h, w))
        self.prev = self.heat.copy()
        self.acc = 0.0
        self.intensity = 0.0
        self.embers = []
        x = (np.arange(w) + 0.5) / w
        self.profile = np.sin(np.pi * x) ** 0.6

    def _step(self):
        below = self.heat[1:]
        # stochastic lateral advection gives flickering tongues; a little blur keeps it soft
        shift = self.nrng.integers(-1, 2, size=below.shape)
        cols = (np.arange(self.w)[None, :] + shift) % self.w
        adv = np.take_along_axis(below, cols, axis=1)
        soft = (np.roll(below, 1, 1) + 2 * below + np.roll(below, -1, 1)) * 0.25
        new = 0.55 * adv + 0.45 * soft
        cool = (0.95 / self.h) * (0.1 + 1.8 * self.nrng.random(new.shape))
        new = np.clip(new - cool, 0, 1)
        self.prev = self.heat
        self.heat = np.zeros_like(self.heat)
        self.heat[:-1] = new
        flicker = 0.7 + 0.3 * self.nrng.random(self.w)
        self.heat[-1] = np.clip(self.intensity * self.profile * flicker * 1.15, 0, 1)

    def update(self, dt, intensity):
        self.intensity = min(1.0, intensity * (0.8 if cfg.REDUCED_MOTION else 1.0))
        self.acc += dt
        while self.acc >= STEP:
            self.acc -= STEP
            self._step()
        r = self.rng
        if r.random() < dt * 5.0 * self.intensity:
            self.embers.append([r.uniform(self.w * 0.1, self.w * 0.9), 0.0, r.uniform(-1.2, 1.2),
                                -r.uniform(2.0, 5.0), r.uniform(2.0, 4.2), 0.0, r.random() * 6])
        m = cfg.motion()
        for e in self.embers:
            e[5] += dt
            e[0] += (e[2] + 0.8 * np.sin(e[5] * 2.2 + e[6])) * dt * m
            e[1] += e[3] * dt * m
        self.embers = [e for e in self.embers if e[5] < e[4]]

    def draw(self, canvas, exclude=None):
        a = self.acc / STEP
        hv = self.prev * (1 - a) + self.heat * a
        oy = canvas.h - self.h
        idx = np.minimum((hv * 8.99).astype(int), 8)
        col = FIRE_LUT[np.minimum((hv * 11.99).astype(int), 11)]
        m = hv > 0.07
        x1 = min(canvas.w, self.w)
        canvas.ch[oy:, :x1][m[:, :x1]] = RAMP[idx][:, :x1][m[:, :x1]]
        canvas.fg[oy:, :x1][m[:, :x1]] = col[:, :x1][m[:, :x1]]
        for ex, ey, vx, vy, life, age, ph in self.embers:
            x, y = int(ex), int(oy + self.h * 0.55 + ey)
            if exclude and any(x0 <= x < x1_ and y0 <= y < y1 for x0, y0, x1_, y1 in exclude):
                continue
            k = age / life
            canvas.put(x, y, "*" if k < 0.3 else ("'" if k < 0.65 else "."),
                       int(FIRE_LUT[max(0, int((1 - k) * 8))]))
