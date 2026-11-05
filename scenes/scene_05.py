"""SCENE 05 - THE QUESTION: five statements over a barely-moving geometric tunnel."""
from animations.fractal import TunnelZoom
from scenes.base import Scene
from utils.text import draw_message, message_alpha

MESSAGES = [
    "A SOCIETY THAT STOPS THINKING STOPS MOVING FORWARD.",
    "QUESTION EVERYTHING.",
    "CHALLENGE ASSUMPTIONS.",
    "SEEK THE TRUTH.",
    "UNDERSTANDING IS THE BEGINNING OF CHANGE.",
]
START, SLOT = 1.5, 4.9


class Scene05(Scene):
    name = "The Question"
    duration = START + SLOT * len(MESSAGES) + 0.6
    fade_in = 1.5
    fade_out = 1.5

    def setup(self, w, h, ctx):
        super().setup(w, h, ctx)
        self.bg = TunnelZoom()

    def draw(self, canvas, t, dt):
        self.bg.draw(canvas, t)
        for i, text in enumerate(MESSAGES):
            t0 = START + i * SLOT
            a = message_alpha(t, t0, t0 + SLOT, fade=1.0)
            if a > 0.02:
                draw_message(canvas, text, self.h // 2, a, clear_pad=(4, 1), rules=True)
