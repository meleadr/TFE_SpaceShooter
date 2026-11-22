import pytest

from spaceshooter.timing import FixedStep


def test_no_step_before_a_full_step_elapsed():
    stepper = FixedStep(step=0.1)
    assert stepper.advance(0.05) == 0
    assert stepper.alpha == pytest.approx(0.5)


def test_leftover_time_carries_over():
    # Binary-exact values so float rounding does not blur the boundary.
    stepper = FixedStep(step=0.25, max_frame_time=1.0)
    assert stepper.advance(0.625) == 2
    assert stepper.advance(0.125) == 1


def test_long_frame_is_clamped():
    stepper = FixedStep(step=0.1, max_frame_time=0.25)
    assert stepper.advance(10.0) == 2


def test_negative_frame_time_is_ignored():
    stepper = FixedStep(step=0.1)
    assert stepper.advance(-1.0) == 0
