"""Visual effects: particle explosions and the scrolling starfield."""

import random
from dataclasses import dataclass

import pygame

from spaceshooter import assets
from spaceshooter.settings import HEIGHT, WIDTH

ROCK_COLORS = [(150, 110, 80), (120, 120, 130), (255, 170, 60), (255, 230, 150)]
FIRE_COLORS = [(255, 90, 40), (255, 170, 60), (255, 240, 180), (90, 170, 255)]


@dataclass
class Particle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    life: float
    max_life: float
    color: tuple[int, int, int]
    size: float


class Particles:
    DRAG = 2.5  # velocity lost per second, as a fraction

    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.items: list[Particle] = []

    def __len__(self) -> int:
        return len(self.items)

    def burst(
        self,
        center: tuple[float, float],
        count: int,
        colors: list[tuple[int, int, int]],
        speed: tuple[float, float] = (60, 260),
        size: tuple[float, float] = (2, 5),
        life: tuple[float, float] = (0.4, 0.9),
    ) -> None:
        for _ in range(count):
            velocity = pygame.Vector2(self.rng.uniform(*speed), 0).rotate(self.rng.uniform(0, 360))
            duration = self.rng.uniform(*life)
            self.items.append(
                Particle(
                    pygame.Vector2(center),
                    velocity,
                    duration,
                    duration,
                    self.rng.choice(colors),
                    self.rng.uniform(*size),
                )
            )

    def update(self, dt: float) -> None:
        damping = max(1.0 - self.DRAG * dt, 0.0)
        for particle in self.items:
            particle.position += particle.velocity * dt
            particle.velocity *= damping
            particle.life -= dt
        self.items = [p for p in self.items if p.life > 0]

    def draw(self, surface: pygame.Surface) -> None:
        for p in self.items:
            radius = max(p.size * p.life / p.max_life, 1.0)
            pygame.draw.circle(surface, p.color, p.position, radius)


class Starfield:
    """Scrolling background tile plus three parallax layers of stars."""

    TILE_SPEED = 20.0
    LAYERS = (  # (count, speed px/s, radius, color)
        (45, 40.0, 1, (90, 90, 130)),
        (25, 80.0, 1, (160, 160, 200)),
        (12, 150.0, 2, (235, 235, 255)),
    )

    def __init__(self, rng: random.Random | None = None) -> None:
        rng = rng or random.Random()
        tile = assets.image("backgrounds/darkPurple.png")
        self.tile_height = tile.get_height()
        self.background = assets.tiled(
            "backgrounds/darkPurple.png", (WIDTH, HEIGHT + self.tile_height)
        )
        self.offset = 0.0
        self.stars = [
            [pygame.Vector2(rng.uniform(0, WIDTH), rng.uniform(0, HEIGHT)) for _ in range(count)]
            for count, *_ in self.LAYERS
        ]

    def update(self, dt: float) -> None:
        self.offset = (self.offset + self.TILE_SPEED * dt) % self.tile_height
        for layer, (_, speed, *_) in zip(self.stars, self.LAYERS, strict=True):
            for star in layer:
                star.y += speed * dt
                if star.y > HEIGHT:
                    star.y -= HEIGHT
                    star.x = (star.x * 7.31) % WIDTH  # cheap reshuffle, no RNG needed

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, self.offset - self.tile_height))
        for layer, (_, _, radius, color) in zip(self.stars, self.LAYERS, strict=True):
            for star in layer:
                pygame.draw.circle(surface, color, star, radius)
