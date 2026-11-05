"""SCENE 03 - THE SYMBOL: the three-finger hand moves through poses."""
from animations.three_fingers import gesture_pose, hand_layout, pulse_at
from scenes.base import Scene
from utils.text import draw_caption
from utils.timing import smoothstep


class Scene03(Scene):
    name = "The Symbol"
    duration = 24.0
    fade_in = 0.0           # continues straight from scene 02
    fade_out = 1.6

    def setup(self, w, h, ctx):
        super().setup(w, h, ctx)
        self.cols, self.rows, self.x, self.y = hand_layout(ctx.hand, w, h)

    def draw(self, canvas, t, dt):
        ch, fg = self.ctx.hand.render(self.cols, self.rows, gesture_pose(t, self.ctx.motion), pulse_at(t))
        canvas.blit(ch, fg, self.x, self.y)
        draw_caption(canvas, "THE SYMBOL", smoothstep(1.0, 2.5, t) * (1 - smoothstep(20.0, 22.0, t)))
