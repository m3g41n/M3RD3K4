"""Typography: big block letters, letter-spaced captions, wrapped messages, fades."""
import textwrap

import numpy as np

from core import config as cfg
from utils.color import EMERALD, EMERALD_DIM, GRAY_LUT, GRAY_DARK, gray
from utils.timing import smoothstep

_G = {
    "I": ["#####", "..#..", "..#..", "..#..", "#####"],
    "F": ["#####", "#....", "####.", "#....", "#...."],
    "W": ["#...#", "#...#", "#.#.#", "##.##", "#...#"],
    "E": ["#####", "#....", "####.", "#....", "#####"],
    "B": ["####.", "#...#", "####.", "#...#", "####."],
    "U": ["#...#", "#...#", "#...#", "#...#", ".###."],
    "R": ["####.", "#...#", "####.", "#..#.", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#"],
    "Y": ["#...#", ".#.#.", "..#..", "..#..", "..#.."],
    "O": [".###.", "#...#", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#####", "#...#", "#...#"],
    "T": ["#####", "..#..", "..#..", "..#..", "..#.."],
    "S": [".####", "#....", ".###.", "....#", "####."],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#"],
    "D": ["####.", "#...#", "#...#", "#...#", "####."],
    "K": ["#...#", "#..#.", "###..", "#..#.", "#...#"],
    "A": [".###.", "#...#", "#####", "#...#", "#...#"],
    "G": [".####", "#....", "#..##", "#...#", ".###."],
    "3": ["####.", "....#", ".###.", "....#", "####."],
    "4": ["#..#.", "#..#.", "#####", "...#.", "...#."],
    ",": ["..", "..", "..", ".#", "#."],
    ".": ["..", "..", "..", "##", "##"],
    " ": ["...", "...", "...", "...", "..."],
}


def can_big(text):
    return all(c in _G for c in text)


def big_width(text, px=1):
    return sum(len(_G[c][0]) * px for c in text) + px * (len(text) - 1)


def big_array(text, px=1):
    """5-row array of char codes (space / fill) for `text`."""
    fill = ord(cfg.BIG_FONT_FILL)
    rows = [[] for _ in range(5)]
    for i, c in enumerate(text):
        g = _G[c]
        for r in range(5):
            rows[r].extend([fill if p == "#" else 32 for p in g[r] for _ in range(px)])
            if i < len(text) - 1:
                rows[r].extend([32] * px)
    return np.array(rows, dtype=np.int32)


def best_big_px(text, max_width):
    """Pick pixel width 2 (square-ish letters), then 1; None if neither fits."""
    if not can_big(text):
        return None
    for px in (2, 1):
        if big_width(text, px) <= max_width:
            return px
    return None


def spaced(text, gap=3):
    return (" " * gap).join(" ".join(word) for word in text.split(" "))


def message_alpha(t, t0, t1, fade=0.9):
    return smoothstep(t0, t0 + fade, t) * (1.0 - smoothstep(t1 - fade, t1, t))


def draw_message(canvas, text, cy, alpha, max_w=None, spaced_ok=True, color=None,
                 clear_pad=None, rules=False):
    """Centered message, wrapped to fit. Returns its bounding rect (x0, y0, x1, y1).

    clear_pad=(cols, rows) blanks the area behind the text so backgrounds never hurt
    readability; rules=True frames the text with thin emerald rules."""
    if alpha <= 0.02:
        return None
    maxw = max_w or min(canvas.w - 8, 76)
    if spaced_ok and len(text) <= 26 and len(spaced(text, 3)) <= maxw:
        lines = [spaced(text, 3)]
    else:
        lines = textwrap.wrap(text, maxw) or [text]
    col = color if color is not None else gray(alpha)
    wmax = max(len(l) for l in lines)
    y0 = cy - len(lines) // 2
    x0 = (canvas.w - wmax) // 2
    extra = 2 if rules else 0
    if clear_pad:
        canvas.clear_rect(x0 - clear_pad[0], y0 - clear_pad[1] - extra,
                          x0 + wmax + clear_pad[0], y0 + len(lines) + clear_pad[1] + extra)
    for i, line in enumerate(lines):
        canvas.text((canvas.w - len(line)) // 2, y0 + i, line, col)
    if rules:
        rw = min(wmax, 36)
        draw_rule(canvas, y0 - 2, rw, alpha)
        draw_rule(canvas, y0 + len(lines) + 1, rw, alpha)
    return (x0, y0, x0 + wmax, y0 + len(lines))


def draw_rule(canvas, y, width, alpha, col=None):
    if alpha <= 0.02:
        return
    c = col if col is not None else (EMERALD if alpha > 0.7 else EMERALD_DIM)
    canvas.text((canvas.w - width) // 2, y, "-" * width, c)


def draw_caption(canvas, text, alpha):
    """Small muted caption on the bottom row."""
    if alpha <= 0.02 or canvas.h < 8:
        return
    s = spaced(text, 3) if len(spaced(text, 3)) < canvas.w - 6 else text
    canvas.text_center(canvas.h - 2, s, GRAY_DARK if alpha < 0.6 else 244)


def draw_big(canvas, text, y, progress, px=1, mode="center"):
    """Large block letters revealed with a wipe (progress 0..1). Returns rect."""
    arr = big_array(text, px)
    h, w = arr.shape
    x0 = (canvas.w - w) // 2
    cols = np.arange(w)
    key = np.abs(cols - (w - 1) / 2) / max(1.0, w / 2) if mode == "center" else cols / max(1, w - 1)
    a = np.clip(progress * 1.7 - key * 0.7, 0, 1)
    codes = GRAY_LUT[np.round(a * (len(GRAY_LUT) - 1)).astype(int)]
    fg = np.broadcast_to(codes, (h, w)).copy()
    ch = np.where((arr != 32) & (a[None, :] > 0.04), arr, 32).astype(np.int32)
    canvas.blit(ch, fg, x0, y)
    return (x0, y, x0 + w, y + h)
