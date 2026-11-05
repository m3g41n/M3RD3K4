"""SCENE 09 - FINAL REVELATION: hand and masks together, then the identity."""
from animations.anonymous_masks import idle_state
from animations.three_fingers import calm_pose, pulse_at
from core.renderer import Canvas
from core.transitions import dissolve_layer
from scenes.base import Scene
from utils.color import EMERALD
from utils.text import best_big_px, draw_big, draw_rule, spaced
from utils.color import gray
from utils.timing import smoothstep

TITLE, SUB = "M3RD3K4", "THE AWAKENING OF MINDS"
GLITCHES = [(2.4, 0.2, 0.6), (3.8, 0.2, 0.7), (8.0, 0.18, 0.5)]


class Scene09(Scene):
    name = "Final Revelation"
    duration = 22.0
    fade_in = 2.0
    fade_out = 1.6
    hold_for_key = True
    ambient_glitch = True

    def setup(self, w, h, ctx):
        super().setup(w, h, ctx)
        self.px = best_big_px(TITLE, w - 6)
        title_h = 5 if self.px else 1
        self.ty = h - (title_h + 2) - 2
        vis_rows = max(6, self.ty - 3)
        self.hcols, self.hrows = ctx.hand.fit(w // 3, min(vis_rows, 36))
        self.hx, self.hy = (w - self.hcols) // 2, 1 + (vis_rows - self.hrows) // 2
        side = (w - self.hcols) // 2 - 3
        self.mask_boxes = []
        for i, sp in enumerate(ctx.masks.sprites):
            cols, rows = sp.fit(max(8, side), vis_rows)
            x = (w // 2 - self.hcols // 2 - 2 - cols) if i == 0 else (w // 2 + self.hcols // 2 + 2)
            self.mask_boxes.append((x, 1 + (vis_rows - rows) // 2, cols, rows))
        self.layer = Canvas(w, h)
        self.fired = set()

    def draw(self, canvas, t, dt):
        for i, (gt, dur, amt) in enumerate(GLITCHES):
            if t >= gt and i not in self.fired:
                self.fired.add(i)
                self.ctx.glitch.trigger(dur, amt)
        m = self.ctx.motion
        # hand (dissolves in via its own layer)
        self.layer.clear()
        ch, fg = self.ctx.hand.render(self.hcols, self.hrows, calm_pose(t, m), pulse_at(t))
        self.layer.blit(ch, fg, self.hx, self.hy)
        dissolve_layer(self.layer, smoothstep(0.8, 4.0, t))
        canvas.blit(self.layer.ch, self.layer.fg, 0, 0)
        # masks
        for sp, (x, y, cols, rows), kind, ph, rv in zip(
                self.ctx.masks.sprites, self.mask_boxes, ("sad", "happy"), (0.0, 2.1),
                (smoothstep(2.0, 7.0, t), smoothstep(3.0, 8.0, t))):
            if rv > 0:
                ch, fg = sp.render(cols, rows, idle_state(t, ph, kind, 0.8 * m), rv)
                canvas.blit(ch, fg, x, y)
        # identity
        pt = smoothstep(7.5, 11.5, t)
        if self.px:
            draw_big(canvas, TITLE, self.ty, pt, self.px)
            sub_y = self.ty + 6
        else:
            s = spaced(TITLE, 2)
            canvas.text_center(self.ty, s, gray(pt))
            sub_y = self.ty + 2
        a = smoothstep(10.5, 13.5, t)
        s = spaced(SUB, 3) if len(spaced(SUB, 3)) <= self.w - 4 else SUB
        canvas.text_center(sub_y, s, gray(a))
        # exit hint
        h = smoothstep(self.duration, self.duration + 2.5, t)
        if h > 0.02:
            canvas.text_center(self.h - 1, "PRESS ANY KEY TO EXIT", 240 if h < 0.7 else 244)
