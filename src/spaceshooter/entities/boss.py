"""The boss: a big ship that cycles through bullet patterns until destroyed."""

import math
import random

import pygame

from spaceshooter.audio import audio
from spaceshooter.entities.enemy import Enemy, EnemyBullet
from spaceshooter.settings import WIDTH

ORB = {"image": "Lasers/laserRed10.png", "scale": 0.55, "radius": 8}


def boss_hp(number: int) -> int:
    """Health of the n-th boss met in a game (1-based)."""
    return 50 + 25 * (number - 1)


class Boss(Enemy):
    IMAGE = "Enemies/enemyBlack5.png"
    SCALE = 2.0
    SCORE = 100  # multiplied by the boss number
    HOLD_Y = 170.0
    ENTRY_SPEED = 90.0
    SWAY = 170.0  # horizontal amplitude in px
    ENRAGE_RATIO = 0.5  # below this share of health, attacks speed up
    PAUSE = 1.2  # seconds of calm between two patterns

    def __init__(
        self,
        position: tuple[float, float],
        bullets: pygame.sprite.Group,
        rng: random.Random,
        fire_rate: float = 1.0,
        *groups: pygame.sprite.Group,
        number: int = 1,
    ) -> None:
        super().__init__(position, bullets, rng, fire_rate, *groups)
        self.number = number
        self.max_hp = self.hp = boss_hp(number)
        self.points = self.SCORE * number
        self.radius = min(self.image.get_size()) * 0.4
        self.entered = False
        self.sway_time = 0.0
        self.patterns = (self.burst, self.aimed, self.spiral)
        self.pattern = 0
        self.pattern_time = -self.PAUSE  # negative: pausing before the pattern starts
        self.shots = 0  # shots fired in the current pattern
        self.spin = 0.0  # current spiral angle

    @property
    def enraged(self) -> bool:
        return self.hp <= self.max_hp * self.ENRAGE_RATIO

    @property
    def tempo(self) -> float:
        """Multiplier on delays between shots: smaller is faster."""
        return 0.7 if self.enraged else 1.0

    def update(self, dt: float, target: tuple[float, float]) -> None:
        self.age += dt
        self.move(dt)
        self.rect = self.image.get_frect(center=self.position)
        self.flash = max(self.flash - dt, 0.0)
        self.image = self.flash_image if self.flash > 0 else self.base_image
        if self.entered:
            self.attack(dt, pygame.Vector2(target))

    def move(self, dt: float) -> None:
        if not self.entered:
            self.position.y = min(self.position.y + self.ENTRY_SPEED * dt, self.HOLD_Y)
            self.entered = self.position.y >= self.HOLD_Y
            return
        self.sway_time += dt
        self.position.x = WIDTH / 2 + self.SWAY * math.sin(0.6 * self.sway_time)
        self.position.y = self.HOLD_Y + 20 * math.sin(1.3 * self.sway_time)

    # --- attacks -------------------------------------------------------------

    def attack(self, dt: float, target: pygame.Vector2) -> None:
        self.pattern_time += dt
        if self.pattern_time < 0:
            return
        finished = self.patterns[self.pattern](target)
        if finished:
            self.pattern = (self.pattern + 1) % len(self.patterns)
            self.pattern_time = -self.PAUSE * self.tempo
            self.shots = 0

    def due(self, interval: float) -> bool:
        """True when the next shot of a pattern firing every `interval` seconds is due."""
        if self.pattern_time >= self.shots * interval * self.tempo:
            self.shots += 1
            return True
        return False

    def shoot(self, velocity: pygame.Vector2) -> None:
        EnemyBullet(self.rect.center, velocity, self.bullets, **ORB)

    def burst(self, target: pygame.Vector2) -> bool:
        """Three rings of orbs, each one slightly turned."""
        if self.due(0.9):
            count = 20 if self.enraged else 14
            offset = self.shots * 360 / count / 2
            for i in range(count):
                self.shoot(pygame.Vector2(0, 170).rotate(offset + i * 360 / count))
            audio.play("enemy_shoot")
        return self.shots >= 3

    def aimed(self, target: pygame.Vector2) -> bool:
        """Volleys of three orbs at the player."""
        if self.due(0.35):
            aim = target - pygame.Vector2(self.rect.center)
            if aim.length_squared():
                aim.scale_to_length(260)
                for spread in (-12, 0, 12):
                    self.shoot(aim.rotate(spread))
            audio.play("enemy_shoot")
        return self.shots >= 6

    def spiral(self, target: pygame.Vector2) -> bool:
        """A rotating stream (two arms when enraged)."""
        if self.due(0.08):
            self.spin += 17
            arms = 2 if self.enraged else 1
            for arm in range(arms):
                self.shoot(pygame.Vector2(0, 200).rotate(self.spin + arm * 180))
            if self.shots % 4 == 0:
                audio.play("enemy_shoot")
        return self.shots >= 30

    def fire(self, target: pygame.Vector2) -> None:  # patterns replace the generic shot
        pass
