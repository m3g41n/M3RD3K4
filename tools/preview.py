"""Developer tool: render a scene at a given time to a PNG (no terminal needed).

    python tools/preview.py <scene 1-9> <seconds> [cols rows] [out.png]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from core.renderer import Canvas
from utils.color import PALETTE

FONT_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "C:/Windows/Fonts/consola.ttf", "/System/Library/Fonts/Menlo.ttc"]


def canvas_to_image(canvas, cw=9, ch=18, size=15):
    font = None
    for p in FONT_PATHS:
        if os.path.exists(p):
            font = ImageFont.truetype(p, size)
            break
    img = Image.new("RGB", (canvas.w * cw, canvas.h * ch), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(canvas.h):
        for x in range(canvas.w):
            c = int(canvas.ch[y, x])
            if c != 32:
                col = tuple(int(v) for v in PALETTE[canvas.fg[y, x]]) if canvas.fg[y, x] else (200, 200, 200)
                d.text((x * cw, y * ch), chr(c), fill=col, font=font)
    return img


def run(scene_no, t_target, w=110, h=36, step=1 / 18):
    from core.context import Context
    from scenes import SCENES
    ctx = Context(seed=5)
    scene = SCENES[scene_no - 1]()
    scene.setup(w, h, ctx)
    canvas = Canvas(w, h)
    t = 0.0
    while True:                      # simulate real frames so stateful effects evolve
        canvas.clear()
        scene.draw(canvas, t, step)
        if t >= t_target:
            return canvas
        t += step


if __name__ == "__main__":
    a = sys.argv[1:]
    n, t = int(a[0]), float(a[1])
    w, h = (int(a[2]), int(a[3])) if len(a) >= 4 else (110, 36)
    out = a[4] if len(a) >= 5 else "/tmp/preview_%d_%s.png" % (n, a[1])
    canvas_to_image(run(n, t, w, h)).save(out)
    print(out)
