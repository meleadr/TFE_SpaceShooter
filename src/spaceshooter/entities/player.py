from enum import Enum, auto

import pygame

from spaceshooter import assets
from spaceshooter.controls import PlayerInput
from spaceshooter.entities.bullet import Bullet
from spaceshooter.settings import HEIGHT, WIDTH

PLAYFIELD = pygame.Rect(0, 0, WIDTH, HEIGHT)


class HitResult(Enum):
    IGNORED = auto()  # still blinking from a previous hit: the meteor passes through
    ABSORBED = auto()  # the shield took it
    DAMAGED = auto()  # a life was lost


class Player(pygame.sprite.Sprite):
    SPEED = 360.0  # px/s (the 2019 version moved 6 px per frame at 60 fps)
    FIRE_COOLDOWN = 0.3  # seconds between two shots
    BOTTOM_MARGIN = 30
    MAX_LIVES = 3
    INVULNERABLE_TIME = 1.5  # seconds of grace after being hit
    BLINK_RATE = 10  # visibility toggles per second while invulnerable
    HITBOX_RATIO = 0.4
    SHIELD_TIME = 4.0

    def __init__(self, bullets: pygame.sprite.Group, *groups: pygame.sprite.Group) -> None:
        super().__init__(*groups)
        self.visible_image = assets.image("playerShip1_blue.png", 0.8)
        self.hidden_image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.shield_image = assets.image("Effects/shield3.png", 0.8)
        self.image = self.visible_image
        self.rect = self.image.get_frect(midbottom=(WIDTH / 2, HEIGHT - self.BOTTOM_MARGIN))
        self.radius = min(self.image.get_size()) * self.HITBOX_RATIO
        self.bullets = bullets
        self.input = PlayerInput(direction=0, fire=False)
        self.cooldown = 0.0
        self.lives = self.MAX_LIVES
        self.invulnerable = 0.0
        self.shield = 0.0  # seconds of shield left

    @property
    def has_lives(self) -> bool:
        return self.lives > 0

    @property
    def is_hurt(self) -> bool:
        return self.lives < self.MAX_LIVES

    def update(self, dt: float) -> None:
        self.rect.x += self.input.direction * self.SPEED * dt
        self.rect.clamp_ip(PLAYFIELD)

        self.cooldown = max(self.cooldown - dt, 0.0)
        if self.input.fire and self.cooldown == 0.0:
            self.fire()

        self.shield = max(self.shield - dt, 0.0)
        self.invulnerable = max(self.invulnerable - dt, 0.0)
        blink_off = int(self.invulnerable * self.BLINK_RATE) % 2 == 1
        self.image = self.hidden_image if blink_off else self.visible_image

    def fire(self) -> None:
        Bullet(self.rect.midtop, self.bullets)
        self.cooldown = self.FIRE_COOLDOWN

    def hit(self) -> HitResult:
        if self.shield > 0:
            return HitResult.ABSORBED
        if self.invulnerable > 0 or not self.has_lives:
            return HitResult.IGNORED
        self.lives -= 1
        self.invulnerable = self.INVULNERABLE_TIME
        return HitResult.DAMAGED

    def activate_shield(self) -> None:
        self.shield = self.SHIELD_TIME

    def gain_life(self) -> None:
        self.lives = min(self.lives + 1, self.MAX_LIVES)

    def draw_shield(self, surface: pygame.Surface) -> None:
        # Flicker during the last second so the player sees it running out.
        if self.shield > 1.0 or (self.shield > 0 and int(self.shield * 8) % 2 == 0):
            surface.blit(self.shield_image, self.shield_image.get_rect(center=self.rect.center))
