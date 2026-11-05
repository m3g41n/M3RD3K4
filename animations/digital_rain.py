"""Digital rain: calm vertical streams in emerald/gray, some spelling real words."""
import numpy as np

from core import config as cfg
from utils.color import EMERALD_RAMP, GRAY_RAMP, ramp_pick

CHARSET = "0123456789abcdefghijklmnopqrstuvwxyz<>[]{}=+*/\\|:;"
WORDS = ["KNOWLEDGE", "FREEDOM", "JUSTICE", "TRUTH", "EDUCATION", "THINK", "QUESTION"]


class DigitalRain:
    def __init__(self, w, h, rng, density=0.2, word_chance=0.14):
        self.w, self.h, self.rng = w, h, rng
        self.density = density          # 0..1 fraction of "full" stream count
        self.word_chance = word_chance
        self.streams = []

    def _spawn(self):
        r = self.rng
        occupied = {s["x"] for s in self.streams}
        x = r.randrange(self.w)
        for _ in range(6):
            if x not in occupied:
                break
            x = r.randrange(self.w)
        if r.random() < self.word_chance:
            word = r.choice(WORDS)
            chars = list(word)[::-1]            # reads top-to-bottom as it falls
            kind = "word"
        else:
            n = r.randint(6, max(7, min(22, self.h - 2)))
            chars = [r.choice(CHARSET) for _ in range(n)]
            kind = "gray" if r.random() < 0.3 else "green"
        self.streams.append(dict(x=x, y=-float(r.randint(0, 6)), speed=r.uniform(4.5, 13.0),
                                 chars=chars, kind=kind, bright=r.random() < 0.3))

    def update(self, dt):
        m = cfg.motion()
        r = self.rng
        for s in self.streams:
            s["y"] += s["speed"] * dt * m
            if s["kind"] != "word" and r.random() < 0.25:
                s["chars"][r.randrange(len(s["chars"]))] = r.choice(CHARSET)
        self.streams = [s for s in self.streams if s["y"] - len(s["chars"]) < self.h]
        target = int(self.density * self.w * 0.5 * (0.6 + 0.4 * m))
        if len(self.streams) < target and r.random() < 0.4:
            self._spawn()

    def draw(self, canvas, alpha=1.0, exclude=None):
        h = canvas.h
        for s in self.streams:
            L = len(s["chars"])
            head = int(s["y"])
            for i in range(L):
                yy = head - i
                if yy < 0 or yy >= h:
                    continue
                if exclude and any(x0 <= s["x"] < x1 and y0 <= yy < y1 for x0, y0, x1, y1 in exclude):
                    continue
                f = (1 - i / L) * alpha
                if i == 0:
                    col = 255 if (s["bright"] or s["kind"] == "word") else ramp_pick(EMERALD_RAMP, 0.9 * alpha + 0.1)
                elif s["kind"] == "gray":
                    col = ramp_pick(GRAY_RAMP, f * 0.7)
                elif s["kind"] == "word":
                    col = ramp_pick(EMERALD_RAMP, 0.35 + 0.65 * f)
                else:
                    col = ramp_pick(EMERALD_RAMP, f * 0.85)
                canvas.put(s["x"], yy, s["chars"][i], col)
