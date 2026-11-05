"""Timing helpers and easing functions."""
import math
import time


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(a, b, x):
    if b == a:
        return 1.0 if x >= b else 0.0
    t = clamp((x - a) / (b - a))
    return t * t * (3 - 2 * t)


def ease_in_out(t):
    return smoothstep(0.0, 1.0, t)


def bump(t, t0, rise, hold, fall):
    """0 -> 1 over `rise`, hold, 1 -> 0 over `fall`, starting at t0."""
    if t < t0:
        return 0.0
    if t < t0 + rise:
        return smoothstep(0, 1, (t - t0) / rise)
    if t < t0 + rise + hold:
        return 1.0
    return 1.0 - smoothstep(0, 1, (t - t0 - rise - hold) / fall)


def pulse(t, period=4.0, phase=0.0):
    return 0.5 + 0.5 * math.sin(2 * math.pi * t / period + phase)


class FrameClock:
    """Sleeps just enough to hold a target FPS; returns the real frame dt."""

    def __init__(self):
        self.last = time.perf_counter()

    def tick(self, fps):
        target = 1.0 / max(1, fps)
        now = time.perf_counter()
        spare = target - (now - self.last)
        if spare > 0:
            time.sleep(spare)
            now = time.perf_counter()
        dt = now - self.last
        self.last = now
        return min(dt, 0.1)   # never let a stall teleport the animation

    def reset(self):
        self.last = time.perf_counter()
