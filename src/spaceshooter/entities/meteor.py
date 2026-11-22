import random

import pygame

from spaceshooter import assets, difficulty
from spaceshooter.settings import HEIGHT, WIDTH

METEOR_IMAGES = [
    f"Meteors/meteor{color}_big{n}.png" for color in ("Brown", "Grey") for n in range(1, 5)
]


class Meteor(pygame.sprite.Sprite):
    HITBOX_RATIO = 0.42  # circle radius as a fraction of the sprite size, a bit forgiving

    def __init__(
        self,
        x: float,
        speed: float,
        spin: float,
        image_name: str,
        *groups: pygame.sprite.Group,
    ) -> None:
        super().__init__(*groups)
        self.original = assets.image(image_name)
        self.image = self.original
        self.speed = speed
        self.spin = spin  # degrees per second
        self.angle = 0.0
        self.position = pygame.Vector2(x, -self.original.get_height() / 2)
        self.rect = self.image.get_frect(center=self.position)
        self.radius = min(self.original.get_size()) * self.HITBOX_RATIO

    def update(self, dt: float) -> None:
        self.position.y += self.speed * dt
        self.angle = (self.angle + self.spin * dt) % 360
        self.image = pygame.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_frect(center=self.position)
        if self.rect.top > HEIGHT:
            self.kill()


class MeteorSpawner:
    """Keeps the sky populated according to the current difficulty level."""

    def __init__(self, meteors: pygame.sprite.Group, rng: random.Random | None = None) -> None:
        self.meteors = meteors
        self.rng = rng or random.Random()
        self.timer = 0.5  # short breather before the first meteor

    def update(self, dt: float, score: int) -> None:
        lvl = difficulty.level(score)
        self.timer -= dt
        if self.timer <= 0 and len(self.meteors) < difficulty.max_meteors(lvl):
            self.spawn(lvl)
            self.timer = difficulty.spawn_interval(lvl)

    def spawn(self, lvl: int) -> Meteor:
        image_name = self.rng.choice(METEOR_IMAGES)
        half_width = assets.image(image_name).get_width() / 2
        return Meteor(
            self.rng.uniform(half_width, WIDTH - half_width),
            self.rng.uniform(*difficulty.meteor_speed_range(lvl)),
            self.rng.uniform(-90, 90),
            image_name,
            self.meteors,
        )
