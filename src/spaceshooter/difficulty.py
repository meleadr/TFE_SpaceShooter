"""Difficulty curve: everything scales with the level, which rises every few points.

Pure functions so the balance can be tested and tuned without running the game.
"""

POINTS_PER_LEVEL = 8  # same pace as the 2019 version


def level(score: int) -> int:
    # Integer division instead of the 2019 `score == buff + 8` check, which could skip a tier.
    return score // POINTS_PER_LEVEL


def meteor_speed_range(lvl: int) -> tuple[float, float]:
    """Min and max falling speed in px/s."""
    return min(120.0 + 20.0 * lvl, 450.0), min(220.0 + 30.0 * lvl, 650.0)


def max_meteors(lvl: int) -> int:
    """How many meteors may be on screen at once."""
    return min(3 + lvl // 2, 10)


def spawn_interval(lvl: int) -> float:
    """Minimum delay in seconds between two meteor spawns."""
    return max(0.8 - 0.05 * lvl, 0.25)
