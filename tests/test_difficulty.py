import pytest

from spaceshooter import difficulty


@pytest.mark.parametrize(("score", "lvl"), [(0, 0), (7, 0), (8, 1), (9, 1), (17, 2), (80, 10)])
def test_level_rises_every_8_points_even_when_skipping_the_exact_value(score, lvl):
    assert difficulty.level(score) == lvl


def test_difficulty_grows_then_caps():
    levels = range(0, 100)
    mins = [difficulty.meteor_speed_range(lvl)[0] for lvl in levels]
    counts = [difficulty.max_meteors(lvl) for lvl in levels]
    intervals = [difficulty.spawn_interval(lvl) for lvl in levels]
    assert mins == sorted(mins) and mins[-1] == 500
    assert counts == sorted(counts) and counts[0] == 4 and counts[-1] == 10
    assert intervals == sorted(intervals, reverse=True) and intervals[-1] == 0.25


def test_speed_range_is_never_inverted():
    for lvl in range(100):
        low, high = difficulty.meteor_speed_range(lvl)
        assert low < high
