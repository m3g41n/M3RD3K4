"""Central configuration for M3RD3K4.

Edit the values here, or override them from the command line
(see ``python main.py --help``). Animation files never hard-code speed,
frame rate or intensity; they read from this module.
"""

FPS = 18                         # target frames per second (15-20 recommended)
ANIMATION_SPEED = 1.0            # 1.0 = normal, 0.5 = half speed, 2.0 = double
REDUCED_MOTION = False           # calmer: lower fps, slower, no glitch, softer fire
ENABLE_COLOR = True              # False = monochrome output
ENABLE_GLITCH = True             # occasional, short glitch transitions
SCENE_DURATION_MULTIPLIER = 1.0  # 1.5 = every scene lasts 50% longer

MIN_COLS = 60                    # smallest supported terminal
MIN_ROWS = 20
FADE_LEVELS = 14                 # brightness steps used by fades
SCENE_GAP_SECONDS = 0.35         # black pause between scenes
BIG_FONT_FILL = "#"              # character used to build large title letters
CONSTITUTION_LABEL = "PEMBUKAAN UUD 1945"   # small caption on scene 08 ("" to hide)


def motion():
    """Global motion intensity: 1.0 normally, lower when REDUCED_MOTION."""
    return 0.45 if REDUCED_MOTION else 1.0


def effective_fps():
    return min(FPS, 10) if REDUCED_MOTION else FPS


def glitch_enabled():
    return ENABLE_GLITCH and not REDUCED_MOTION
