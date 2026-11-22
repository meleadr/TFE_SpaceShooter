"""Global constants shared by the whole game."""

TITLE = "Space Shooter"

# Logical resolution: everything is laid out in these coordinates and
# pygame.SCALED stretches it to the actual window size.
WIDTH = 600
HEIGHT = 800

# Simulation runs at a fixed rate, rendering is capped at the same rate.
UPDATE_HZ = 60
STEP = 1.0 / UPDATE_HZ
FPS = 60

# Longest frame we try to catch up on (avoids the "spiral of death" after a stall).
MAX_FRAME_TIME = 0.25
