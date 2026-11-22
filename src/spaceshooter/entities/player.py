import pygame

from spaceshooter import assets
from spaceshooter.controls import PlayerInput
from spaceshooter.entities.bullet import Bullet
from spaceshooter.settings import HEIGHT, WIDTH

PLAYFIELD = pygame.Rect(0, 0, WIDTH, HEIGHT)


class Player(pygame.sprite.Sprite):
    SPEED = 360.0  # px/s (the 2019 version moved 6 px per frame at 60 fps)
    FIRE_COOLDOWN = 0.3  # seconds between two shots
    BOTTOM_MARGIN = 30
    MAX_LIVES = 3
    INVULNERABLE_TIME = 1.5  # seconds of grace after being hit
    BLINK_RATE = 10  # visibility toggles per second while invulnerable
    HITBOX_RATIO = 0.4

    def __init__(self, bullets: pygame.sprite.Group, *groups: pygame.sprite.Group) -> None:
        super().__init__(*groups)
        self.visible_image = assets.image("playerShip1_blue.png", 0.8)
        self.hidden_image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.image = self.visible_image
        self.rect = self.image.get_frect(midbottom=(WIDTH / 2, HEIGHT - self.BOTTOM_MARGIN))
        self.radius = min(self.image.get_size()) * self.HITBOX_RATIO
        self.bullets = bullets
        self.input = PlayerInput(direction=0, fire=False)
        self.cooldown = 0.0
        self.lives = self.MAX_LIVES
        self.invulnerable = 0.0

    @property
    def has_lives(self) -> bool:
        return self.lives > 0

    def update(self, dt: float) -> None:
        self.rect.x += self.input.direction * self.SPEED * dt
        self.rect.clamp_ip(PLAYFIELD)

        self.cooldown = max(self.cooldown - dt, 0.0)
        if self.input.fire and self.cooldown == 0.0:
            self.fire()

        self.invulnerable = max(self.invulnerable - dt, 0.0)
        blink_off = int(self.invulnerable * self.BLINK_RATE) % 2 == 1
        self.image = self.hidden_image if blink_off else self.visible_image

    def fire(self) -> None:
        Bullet(self.rect.midtop, self.bullets)
        self.cooldown = self.FIRE_COOLDOWN

    def hit(self) -> bool:
        """Take one hit unless still invulnerable. Returns whether a life was lost."""
        if self.invulnerable > 0 or not self.has_lives:
            return False
        self.lives -= 1
        self.invulnerable = self.INVULNERABLE_TIME
        return True
