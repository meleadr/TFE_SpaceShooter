import random
from enum import Enum

import pygame

from spaceshooter import assets, difficulty
from spaceshooter.settings import HEIGHT, WIDTH

COLORS = ("Brown", "Grey")


class MeteorSize(Enum):
    # value: (weight against the on-screen cap, particles when destroyed)
    BIG = (1.0, 24)
    MEDIUM = (0.5, 16)
    SMALL = (0.25, 10)

    @property
    def weight(self) -> float:
        return self.value[0]

    @property
    def particles(self) -> int:
        return self.value[1]

    @property
    def child(self) -> "MeteorSize | None":
        """What a shot meteor breaks into, if anything."""
        return {MeteorSize.BIG: MeteorSize.MEDIUM, MeteorSize.MEDIUM: MeteorSize.SMALL}.get(self)

    def image_names(self, color: str) -> list[str]:
        suffixes = {
            MeteorSize.BIG: ("big1", "big2", "big3", "big4"),
            # Kenney numbers the medium meteors differently per color.
            MeteorSize.MEDIUM: ("med1", "med3") if color == "Brown" else ("med1", "med2"),
            MeteorSize.SMALL: ("small1", "small2"),
        }[self]
        return [f"Meteors/meteor{color}_{suffix}.png" for suffix in suffixes]


class Meteor(pygame.sprite.Sprite):
    HITBOX_RATIO = 0.42  # circle radius as a fraction of the sprite size, a bit forgiving
    FRAGMENT_SIDE_SPEED = (40.0, 90.0)  # px/s, fragments drift apart sideways
    FRAGMENT_FALL_RATIO = (0.75, 0.9)  # fragments fall a bit slower than their parent

    def __init__(
        self,
        size: MeteorSize,
        color: str,
        image_name: str,
        position: tuple[float, float],
        velocity: tuple[float, float],
        spin: float,
        *groups: pygame.sprite.Group,
    ) -> None:
        super().__init__(*groups)
        self.size = size
        self.color = color
        self.original = assets.image(image_name)
        self.image = self.original
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.spin = spin  # degrees per second
        self.angle = 0.0
        self.rect = self.image.get_frect(center=self.position)
        self.radius = min(self.original.get_size()) * self.HITBOX_RATIO

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.angle = (self.angle + self.spin * dt) % 360
        self.image = pygame.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_frect(center=self.position)
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

    def split(self, rng: random.Random, *groups: pygame.sprite.Group) -> list["Meteor"]:
        """Break into two smaller meteors flying apart (nothing for the smallest size).

        Groups are passed explicitly: a shot meteor has usually been removed from its own
        group by the collision check already.
        """
        child = self.size.child
        if child is None:
            return []
        return [
            Meteor(
                child,
                self.color,
                rng.choice(child.image_names(self.color)),
                self.position,
                (
                    side * rng.uniform(*self.FRAGMENT_SIDE_SPEED),
                    self.velocity.y * rng.uniform(*self.FRAGMENT_FALL_RATIO),
                ),
                self.spin * 1.5 * side,
                *groups,
            )
            for side in (-1, 1)
        ]


def on_screen_weight(meteors: pygame.sprite.Group) -> float:
    return sum(meteor.size.weight for meteor in meteors)


class MeteorSpawner:
    """Keeps the sky populated according to the current difficulty level."""

    MEDIUM_CHANCE = 0.3  # some meteors arrive already medium-sized, for variety

    def __init__(self, meteors: pygame.sprite.Group, rng: random.Random | None = None) -> None:
        self.meteors = meteors
        self.rng = rng or random.Random()
        self.timer = 0.5  # short breather before the first meteor

    def update(self, dt: float, score: int) -> None:
        lvl = difficulty.level(score)
        self.timer -= dt
        # Fragments count less than whole meteors, so splitting does not freeze spawning.
        if self.timer <= 0 and on_screen_weight(self.meteors) < difficulty.max_meteors(lvl):
            self.spawn(lvl)
            self.timer = difficulty.spawn_interval(lvl)

    def spawn(self, lvl: int) -> Meteor:
        size = MeteorSize.MEDIUM if self.rng.random() < self.MEDIUM_CHANCE else MeteorSize.BIG
        color = self.rng.choice(COLORS)
        image_name = self.rng.choice(size.image_names(color))
        image = assets.image(image_name)
        half_width = image.get_width() / 2
        return Meteor(
            size,
            color,
            image_name,
            (self.rng.uniform(half_width, WIDTH - half_width), -image.get_height() / 2),
            (0.0, self.rng.uniform(*difficulty.meteor_speed_range(lvl))),
            self.rng.uniform(-90, 90),
            self.meteors,
        )
