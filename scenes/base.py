"""Scene interface. All timing is in 'timeline seconds' (see core/engine.py)."""


class Scene:
    name = ""
    duration = 10.0       # timeline seconds
    fade_in = 1.0
    fade_out = 1.0
    hold_for_key = False  # final scene waits for a key press
    ambient_glitch = False

    def setup(self, w, h, ctx):
        """Called at scene start and again whenever the terminal is resized."""
        self.w, self.h, self.ctx = w, h, ctx

    def draw(self, canvas, t, dt):
        """t = timeline seconds since scene start, dt = animation-time step."""
        raise NotImplementedError
