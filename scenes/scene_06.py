"""SCENE 06 - THE AWAKENING: particles collide and converge into a rising-sun formation."""
from animations.particles import ParticleConvergence
from scenes.base import Scene
from utils.text import draw_message, message_alpha
from utils.timing import clamp, smoothstep

A = "THE FOUNDATION OF CHANGE IS AN EDUCATED SOCIETY."
B1 = "EDUCATION IS NOT MERELY THE ABILITY TO READ."
B2 = "IT IS THE ABILITY TO THINK, TO QUESTION, AND TO UNDERSTAND."


class Scene06(Scene):
    name = "The Awakening"
    duration = 31.0
    fade_in = 1.5
    fade_out = 2.0

    def setup(self, w, h, ctx):
        super().setup(w, h, ctx)
        n = int(clamp(w * h / 18, 240, 320))
        self.parts = ParticleConvergence(w, h, ctx.rng, n)

    def draw(self, canvas, t, dt):
        p = smoothstep(2.0, 11.5, t)
        self.parts.draw(canvas, t, p)
        ty = int(self.h * 0.80)
        draw_message(canvas, A, ty, message_alpha(t, 11.0, 18.0), spaced_ok=False)
        draw_message(canvas, B1, ty - 1, message_alpha(t, 18.5, 31.0, fade=1.2), spaced_ok=False)
        draw_message(canvas, B2, ty + 1, message_alpha(t, 21.5, 31.0, fade=1.2), spaced_ok=False)
