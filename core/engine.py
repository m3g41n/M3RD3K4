"""The frame loop: timeline, fades, scene changes, resize and key handling.

Timeline: each scene runs on `tau` ("timeline seconds"), advancing at
ANIMATION_SPEED / SCENE_DURATION_MULTIPLIER. Simulation steps (rain, fire) use
`dt * ANIMATION_SPEED` so a longer scene does not make the rain crawl.
"""
import time

from core import config as cfg
from core.renderer import Canvas, Renderer
from core.transitions import apply_fade
from utils.timing import FrameClock, smoothstep

SKIP_KEYS = {"space", "right", "enter"}
FADE_ON_SKIP = 0.9


class Quit(Exception):
    pass


class Engine:
    def __init__(self, terminal, scenes, ctx):
        self.term = terminal
        self.scenes = scenes
        self.ctx = ctx
        self.renderer = Renderer()
        self.clock = FrameClock()

    def run(self, start_index=0):
        self.term.start()
        try:
            prev = None
            for cls in self.scenes[start_index:]:
                scene = cls()
                seamless = prev is not None and prev.fade_out == 0 and scene.fade_in == 0
                if prev is not None and not seamless:
                    self._pause(cfg.SCENE_GAP_SECONDS)
                self._play(scene, keep_screen=seamless)
                prev = scene
        except (KeyboardInterrupt, Quit):
            pass
        finally:
            self.term.stop()

    # ------------------------------------------------------------------
    def _pause(self, seconds):
        end = time.perf_counter() + seconds
        while time.perf_counter() < end:
            self._check_quit()
            time.sleep(0.03)
        self.clock.reset()

    def _check_quit(self):
        if self.term.poll_key() in ("q", "esc"):
            raise Quit

    def _play(self, scene, keep_screen=False):
        size = self.term.size()
        canvas = Canvas(*size)
        scene.setup(*size, self.ctx)
        if not keep_screen:
            self.renderer.reset()
            self.term.write("\x1b[2J")
        mult = max(0.05, cfg.SCENE_DURATION_MULTIPLIER)
        tau, skip_at = 0.0, None
        self.clock.reset()
        while True:
            new_size = self.term.size()
            if new_size != size:
                size = new_size
                canvas = Canvas(*size)
                self.renderer.reset()
                self.term.write("\x1b[2J")
                if size[0] >= cfg.MIN_COLS and size[1] >= cfg.MIN_ROWS:
                    scene.setup(*size, self.ctx)

            key = self.term.poll_key()
            if key in ("q", "esc"):
                raise Quit
            if key is not None and skip_at is None:
                waiting_at_end = scene.hold_for_key and tau >= scene.duration
                if waiting_at_end or key in SKIP_KEYS:
                    skip_at = tau

            dt = self.clock.tick(cfg.effective_fps())
            if size[0] < cfg.MIN_COLS or size[1] < cfg.MIN_ROWS:
                self._too_small(canvas)
                continue
            tau += dt * cfg.ANIMATION_SPEED / mult
            dt_anim = dt * cfg.ANIMATION_SPEED

            canvas.clear()
            scene.draw(canvas, tau, dt_anim)
            self.ctx.glitch.step(dt_anim, ambient=scene.ambient_glitch and tau > 6)
            self.ctx.glitch.apply(canvas)

            f = smoothstep(0.0, scene.fade_in, tau) if scene.fade_in > 0 else 1.0
            if skip_at is not None:
                f = min(f, 1.0 - smoothstep(skip_at, skip_at + FADE_ON_SKIP, tau))
            elif scene.fade_out > 0 and not scene.hold_for_key:
                f = min(f, 1.0 - smoothstep(scene.duration - scene.fade_out, scene.duration, tau))
            apply_fade(canvas, f)
            self.term.write(self.renderer.render(canvas, cfg.ENABLE_COLOR))

            if skip_at is not None and tau >= skip_at + FADE_ON_SKIP:
                return
            if not scene.hold_for_key and skip_at is None and tau >= scene.duration:
                return

    def _too_small(self, canvas):
        canvas.clear()
        msg = "Please enlarge the terminal (%dx%d minimum)" % (cfg.MIN_COLS, cfg.MIN_ROWS)
        canvas.text(max(0, (canvas.w - len(msg)) // 2), canvas.h // 2, msg[:canvas.w], 244)
        self.term.write(self.renderer.render(canvas, cfg.ENABLE_COLOR))
