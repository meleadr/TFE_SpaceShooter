"""Fixed-timestep accumulator, kept free of pygame so it is trivially testable."""

from spaceshooter.settings import MAX_FRAME_TIME, STEP


class FixedStep:
    """Turns variable frame durations into a whole number of fixed simulation steps."""

    def __init__(self, step: float = STEP, max_frame_time: float = MAX_FRAME_TIME) -> None:
        self.step = step
        self.max_frame_time = max_frame_time
        self.accumulator = 0.0

    def advance(self, frame_time: float) -> int:
        """Add the elapsed real time and return how many steps to simulate now."""
        self.accumulator += min(max(frame_time, 0.0), self.max_frame_time)
        steps = 0
        while self.accumulator >= self.step:
            self.accumulator -= self.step
            steps += 1
        return steps

    @property
    def alpha(self) -> float:
        """Fraction of a step left over, usable to interpolate rendering."""
        return self.accumulator / self.step
