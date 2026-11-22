"""Enemy waves: the game alternates meteor phases and scripted enemy waves.

Timeline: meteors fall for a while, then a wave is announced, its ships arrive on a
schedule, and once every ship is gone (destroyed or off screen) the meteors resume.
"""

import random
from collections.abc import Callable
from dataclasses import dataclass, field

import pygame

from spaceshooter.entities.enemy import Drone, Enemy, Gunship
from spaceshooter.settings import WIDTH

FIRST_WAVE_DELAY = 20.0  # seconds of meteors before the first wave
WAVE_INTERVAL = 30.0  # seconds of meteors between two waves
BANNER_TIME = 2.0  # the "VAGUE n" banner shows before the ships arrive
DRONE_SPACING = 0.45  # seconds between two drones of the same column


@dataclass
class Spawn:
    delay: float  # seconds after the wave starts
    make: Callable[[], Enemy]


@dataclass
class Wave:
    number: int
    schedule: list[Spawn] = field(default_factory=list)


def drone_count(number: int) -> int:
    return min(3 + number, 10)


def gunship_count(number: int) -> int:
    return 0 if number < 2 else min(1 + (number - 2) // 2, 3)


def fire_rate(number: int) -> float:
    """Enemies shoot a little more often with every wave."""
    return min(1.0 + 0.08 * (number - 1), 1.8)


class WaveDirector:
    def __init__(
        self,
        enemies: pygame.sprite.Group,
        enemy_bullets: pygame.sprite.Group,
        rng: random.Random | None = None,
    ) -> None:
        self.enemies = enemies
        self.enemy_bullets = enemy_bullets
        self.rng = rng or random.Random()
        self.number = 0
        self.timer = FIRST_WAVE_DELAY  # counts down to the next wave while idle
        self.wave: Wave | None = None
        self.elapsed = 0.0  # time since the current wave started
        self.pending: list[Spawn] = []

    @property
    def active(self) -> bool:
        """True from the banner until the last ship of the wave is gone."""
        return self.wave is not None

    @property
    def banner(self) -> str | None:
        if self.wave is not None and self.elapsed < BANNER_TIME:
            return f"VAGUE {self.wave.number}"
        return None

    def update(self, dt: float) -> None:
        if self.wave is None:
            self.timer -= dt
            if self.timer <= 0:
                self.start_wave()
            return

        self.elapsed += dt
        while self.pending and self.pending[0].delay <= self.elapsed:
            self.pending.pop(0).make()
        if not self.pending and not self.enemies:
            self.wave = None
            self.timer = WAVE_INTERVAL

    def start_wave(self) -> None:
        self.number += 1
        self.wave = self.build(self.number)
        self.pending = sorted(self.wave.schedule, key=lambda spawn: spawn.delay)
        self.elapsed = 0.0

    def build(self, number: int) -> Wave:
        wave = Wave(number)
        rate = fire_rate(number)
        drones = drone_count(number)
        # Odd waves: one weaving column; even waves: two mirrored columns.
        columns = [WIDTH / 2] if number % 2 else [WIDTH * 0.28, WIDTH * 0.72]
        for i in range(drones):
            x = columns[i % len(columns)]
            row = i // len(columns)
            phase = 0.0 if len(columns) == 1 or i % 2 == 0 else 3.14159
            wave.schedule.append(
                Spawn(BANNER_TIME + row * DRONE_SPACING, self.drone_factory(x, phase, rate))
            )
        last_drone = BANNER_TIME + (drones // len(columns)) * DRONE_SPACING
        for j in range(gunship_count(number)):
            x = self.rng.uniform(80, WIDTH - 80)
            hold_y = 130 + 70 * (j % 3)
            wave.schedule.append(
                Spawn(last_drone + 1.0 + 1.5 * j, self.gunship_factory(x, hold_y, rate))
            )
        return wave

    def drone_factory(self, x: float, phase: float, rate: float) -> Callable[[], Enemy]:
        def make() -> Enemy:
            return Drone((x, -40), self.enemy_bullets, self.rng, rate, self.enemies, phase=phase)

        return make

    def gunship_factory(self, x: float, hold_y: float, rate: float) -> Callable[[], Enemy]:
        def make() -> Enemy:
            return Gunship(
                (x, -50), self.enemy_bullets, self.rng, rate, self.enemies, hold_y=hold_y
            )

        return make
