"""SCENE 04 - THE MASKS: two masks emerge from darkness and come alive, independently."""
from animations.anonymous_masks import idle_state
from scenes.base import Scene
from utils.text import draw_caption
from utils.timing import smoothstep

GLITCHES = [(2.0, 0.22, 0.7), (3.6, 0.20, 0.8), (5.2, 0.25, 0.8), (6.9, 0.20, 0.6),
            (14.0, 0.18, 0.5), (19.0, 0.18, 0.5)]


class Scene04(Scene):
    name = "The Masks"
    duration = 22.0
    fade_in = 1.5
    fade_out = 1.8

    def setup(self, w, h, ctx):
        super().setup(w, h, ctx)
        (tw, th), self.lay = ctx.masks.layout(w - 6, h - 5)
        self.ox, self.oy = (w - tw) // 2, max(1, (h - th) // 2 - 1)
        self.fired = set()

    def draw(self, canvas, t, dt):
        for i, (gt, dur, amt) in enumerate(GLITCHES):
            if t >= gt and i not in self.fired:
                self.fired.add(i)
                self.ctx.glitch.trigger(dur, amt)
        reveals = (smoothstep(1.0, 6.5, t), smoothstep(3.0, 8.5, t))
        phases = (0.0, 2.1)
        for sprite, (x, y, cols, rows), kind, ph, rv in zip(self.ctx.masks.sprites, self.lay,
                                                           ("sad", "happy"), phases, reveals):
            if rv <= 0:
                continue
            ch, fg = sprite.render(cols, rows, idle_state(t, ph, kind, self.ctx.motion), rv)
            canvas.blit(ch, fg, self.ox + x, self.oy + y)
        draw_caption(canvas, "THE MASKS", smoothstep(8.0, 9.5, t) * (1 - smoothstep(19.0, 21.0, t)))
