"""Headless checks: every scene runs at several sizes, and visibly MOVES.

    python tests/smoke_test.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from core.context import Context
from core.renderer import Canvas, Renderer
from scenes import SCENES

SIZES = [(80, 24), (110, 36), (160, 48)]
STEP = 1 / 12


def frame(scene, canvas, t):
    canvas.clear()
    scene.draw(canvas, t, STEP)
    return canvas.ch.copy(), canvas.fg.copy()


def main():
    ctx = Context(seed=3)
    bad = 0
    for w, h in SIZES:
        print("== %dx%d" % (w, h))
        for cls in SCENES:
            sc = cls()
            sc.setup(w, h, ctx)
            cv, rd = Canvas(w, h), Renderer()
            t, prev, changes, n = 0.0, None, [], 0
            checkpoints = {}
            while t < sc.duration:
                ch, fg = frame(sc, cv, t)
                rd.render(cv)                       # exercise the ANSI renderer too
                n += 1
                if abs(t % 1.0) < STEP / 2 and t > 1:
                    key = int(round(t))
                    if prev is not None:
                        changes.append(float((ch != prev).mean()))
                    prev = ch
                t += STEP
            moving = np.mean([c > 0.002 for c in changes]) if changes else 0
            ok = moving > 0.6
            bad += not ok
            print("  %-30s frames=%4d  moving-seconds=%3.0f%%  %s" % (cls.name if hasattr(cls, 'name') else cls.__name__,
                                                                      n, moving * 100, "OK" if ok else "STATIC?"))
    # hand poses must differ; masks must differ
    hs, ms = ctx.hand, ctx.masks
    from animations.three_fingers import gesture_pose
    a = hs.render(28, 30, gesture_pose(0.0))[0]
    b = hs.render(28, 30, gesture_pose(3.5))[0]
    d = float((a != b).mean())
    print("hand pose difference neutral vs index-lowered: %.1f%% of cells" % (d * 100))
    bad += d < 0.01
    from animations.anonymous_masks import idle_state
    for i, (sp, k) in enumerate(zip(ms.sprites, ("sad", "happy"))):
        x = sp.render(40, 26, idle_state(0.0, 0, k))[0]
        y = sp.render(40, 26, idle_state(1.6, 0, k))[0]
        d = float((x != y).mean())
        print("mask %d (%s) animation difference: %.1f%% of cells" % (i, k, d * 100))
        bad += d < 0.005
    print("RESULT:", "ALL PASS" if not bad else "%d PROBLEM(S)" % bad)
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
