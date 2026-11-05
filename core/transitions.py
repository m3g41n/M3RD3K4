"""Fades and dissolves applied to whole canvases or layers."""
import numpy as np

from core import config as cfg
from utils.color import fade_table

_TABLE = None


def _lut():
    global _TABLE
    if _TABLE is None or _TABLE.shape[0] != cfg.FADE_LEVELS + 1:
        _TABLE = fade_table(cfg.FADE_LEVELS)
    return _TABLE


def apply_fade(canvas, f):
    """Darken the whole canvas toward black. f=1 untouched, f=0 empty."""
    if f >= 0.999:
        return
    if f <= 0.001:
        canvas.ch.fill(32)
        return
    if cfg.ENABLE_COLOR:
        level = int(round(f * cfg.FADE_LEVELS))
        canvas.fg = _lut()[level][canvas.fg]
    else:   # monochrome: dissolve instead of dim
        canvas.ch[canvas.noise > f] = 32


def dissolve_layer(layer, alpha):
    """Fade a layer canvas in/out by alpha (0..1) with a noise dissolve + dimming."""
    if alpha >= 0.999:
        return
    if alpha <= 0.001:
        layer.ch.fill(32)
        return
    layer.ch[layer.noise > min(1.0, alpha * 1.25)] = 32
    if cfg.ENABLE_COLOR:
        layer.fg = _lut()[int(round(alpha * cfg.FADE_LEVELS))][layer.fg]
