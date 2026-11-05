#!/usr/bin/env python3
"""M3RD3K4 - THE AWAKENING OF MINDS.  Run:  python main.py"""
import argparse
import sys
import time


def parse_args():
    p = argparse.ArgumentParser(description="M3RD3K4 - cinematic ASCII terminal experience")
    p.add_argument("--fps", type=int, help="target frame rate (default from core/config.py)")
    p.add_argument("--speed", type=float, help="animation speed multiplier (1.0 = normal)")
    p.add_argument("--duration-scale", type=float, help="scene duration multiplier (1.5 = 50%% longer)")
    p.add_argument("--reduced-motion", action="store_true", help="calmer, slower, no glitch")
    p.add_argument("--no-color", action="store_true", help="monochrome output")
    p.add_argument("--no-glitch", action="store_true", help="disable glitch effects")
    p.add_argument("--scene", type=int, default=1, metavar="N", help="start at scene N (1-9)")
    p.add_argument("--seed", type=int, help="random seed (reproducible runs)")
    return p.parse_args()


def main():
    args = parse_args()
    try:
        import numpy  # noqa: F401
        import PIL    # noqa: F401
    except ImportError as e:
        sys.exit("Missing dependency (%s).\nInstall with:  pip install -r requirements.txt" % e.name)

    from core import config as cfg
    if args.fps:
        cfg.FPS = max(5, min(60, args.fps))
    if args.speed:
        cfg.ANIMATION_SPEED = max(0.1, args.speed)
    if args.duration_scale:
        cfg.SCENE_DURATION_MULTIPLIER = args.duration_scale
    if args.reduced_motion:
        cfg.REDUCED_MOTION = True
    if args.no_color:
        cfg.ENABLE_COLOR = False
    if args.no_glitch:
        cfg.ENABLE_GLITCH = False

    from core.context import Context
    from core.engine import Engine
    from core.terminal import Terminal
    from scenes import SCENES

    ctx = Context(seed=args.seed)
    for w in ctx.warnings:
        print("warning:", w, file=sys.stderr)
    if ctx.warnings:
        time.sleep(1.5)
    start = max(1, min(len(SCENES), args.scene)) - 1
    Engine(Terminal(), SCENES, ctx).run(start)


if __name__ == "__main__":
    main()
