import random
from enum import Enum

import pygame

from spaceshooter import assets
from spaceshooter.settings import HEIGHT, WIDTH


class PowerUpKind(Enum):
    SHIELD = "Power-ups/powerupBlue_shield.png"
    LIFE = "UI/playerLife1_blue.png"  # same icon as the lives in the HUD
    WEAPON = "Power-ups/bolt_gold.png"

    @property
    def image_name(self) -> str:
        return self.value


class PowerUp(pygame.sprite.Sprite):
    SPEED = 120.0  # px/s, slow enough to be caught on purpose

    def __init__(
        self, kind: PowerUpKind, x: float, *groups: pygame.sprite.Group, y: float = 0.0
    ) -> None:
        """Starts just above the screen unless `y` (its center) is given, e.g. for drops."""
        super().__init__(*groups)
        self.kind = kind
        self.image = assets.image(kind.image_name, 1.2 if kind is PowerUpKind.LIFE else 1.0)
        self.rect = self.image.get_frect(midbottom=(x, 0))
        if y:
            self.rect.center = (x, y)

    def update(self, dt: float) -> None:
        self.rect.y += self.SPEED * dt
        if self.rect.top > HEIGHT:
            self.kill()


class PowerUpSpawner:
    """Drops a power-up every MIN_DELAY..MAX_DELAY seconds."""

    MIN_DELAY = 10.0
    MAX_DELAY = 18.0
    MARGIN = 30

    def __init__(self, powerups: pygame.sprite.Group, rng: random.Random | None = None) -> None:
        self.powerups = powerups
        self.rng = rng or random.Random()
        self.timer = self.next_delay()

    def next_delay(self) -> float:
        return self.rng.uniform(self.MIN_DELAY, self.MAX_DELAY)

    def update(self, dt: float, player_hurt: bool) -> None:
        self.timer -= dt
        if self.timer <= 0:
            self.spawn(player_hurt)
            self.timer = self.next_delay()

    LIFE_CHANCE = 0.4  # only when the player has lost a life
    WEAPON_CHANCE = 0.4

    def spawn(self, player_hurt: bool) -> PowerUp:
        if player_hurt and self.rng.random() < self.LIFE_CHANCE:
            kind = PowerUpKind.LIFE
        elif self.rng.random() < self.WEAPON_CHANCE:
            kind = PowerUpKind.WEAPON
        else:
            kind = PowerUpKind.SHIELD
        x = self.rng.uniform(self.MARGIN, WIDTH - self.MARGIN)
        return PowerUp(kind, x, self.powerups)
