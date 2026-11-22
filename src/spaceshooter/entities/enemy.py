"""Enemy ships and their shots."""

import math
import random

import pygame

from spaceshooter import assets
from spaceshooter.audio import audio
from spaceshooter.settings import HEIGHT, WIDTH

SCREEN = pygame.Rect(0, 0, WIDTH, HEIGHT)


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(
        self,
        center: tuple[float, float],
        velocity: pygame.Vector2,
        *groups: pygame.sprite.Group,
    ) -> None:
        super().__init__(*groups)
        self.velocity = pygame.Vector2(velocity)
        # The laser sprite points up; turn it to face where it is going.
        angle = self.velocity.angle_to(pygame.Vector2(0, -1))
        self.image = pygame.transform.rotate(assets.image("Lasers/laserRed01.png", 0.8), angle)
        self.rect = self.image.get_frect(center=center)
        self.radius = 5

    def update(self, dt: float) -> None:
        self.rect.center += self.velocity * dt
        if not self.rect.colliderect(SCREEN):
            self.kill()


class Enemy(pygame.sprite.Sprite):
    IMAGE = ""
    SCALE = 1.0
    HP = 1
    SCORE = 1
    FIRE_DELAY = (1.0, 2.0)  # seconds between shots, picked at random in this range
    BULLET_SPEED = 280.0
    HIT_FLASH = 0.08  # seconds the ship flashes white when hit

    def __init__(
        self,
        position: tuple[float, float],
        bullets: pygame.sprite.Group,
        rng: random.Random,
        fire_rate: float = 1.0,
        *groups: pygame.sprite.Group,
    ) -> None:
        super().__init__(*groups)
        self.base_image = assets.image(self.IMAGE, self.SCALE)
        self.flash_image = self.base_image.copy()
        self.flash_image.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
        self.image = self.base_image
        self.position = pygame.Vector2(position)
        self.rect = self.image.get_frect(center=self.position)
        self.radius = min(self.image.get_size()) * 0.42
        self.bullets = bullets
        self.rng = rng
        self.fire_rate = fire_rate  # >1 shoots more often
        self.hp = self.HP
        self.age = 0.0
        self.flash = 0.0
        self.fire_timer = self.next_fire_delay()

    def next_fire_delay(self) -> float:
        return self.rng.uniform(*self.FIRE_DELAY) / self.fire_rate

    @property
    def can_fire(self) -> bool:
        # Only shoot while fully visible and above the lower part of the screen.
        return self.rect.top > 0 and self.rect.bottom < HEIGHT * 0.75

    def update(self, dt: float, target: tuple[float, float]) -> None:
        self.age += dt
        self.move(dt)
        self.rect = self.image.get_frect(center=self.position)
        self.flash = max(self.flash - dt, 0.0)
        self.image = self.flash_image if self.flash > 0 else self.base_image

        self.fire_timer -= dt
        if self.fire_timer <= 0:
            self.fire_timer = self.next_fire_delay()
            if self.can_fire:
                self.fire(pygame.Vector2(target))

        if self.rect.top > HEIGHT or self.rect.bottom < -200:
            self.kill()

    def move(self, dt: float) -> None:
        raise NotImplementedError

    def fire(self, target: pygame.Vector2) -> None:
        raise NotImplementedError

    def damage(self) -> bool:
        """Take one hit. Returns whether the enemy is destroyed."""
        self.hp -= 1
        self.flash = self.HIT_FLASH
        if self.hp <= 0:
            self.kill()
            return True
        return False


class Drone(Enemy):
    """Light fighter: weaves down the screen and fires straight ahead."""

    IMAGE = "Enemies/enemyGreen1.png"
    SCALE = 0.6
    HP = 1
    SCORE = 3
    FIRE_DELAY = (1.4, 2.6)
    SPEED = 110.0
    AMPLITUDE = 70.0
    FREQUENCY = 1.6  # radians per second

    def __init__(self, *args, phase: float = 0.0, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.origin_x = self.position.x
        self.phase = phase

    def move(self, dt: float) -> None:
        self.position.y += self.SPEED * dt
        self.position.x = self.origin_x + self.AMPLITUDE * math.sin(
            self.FREQUENCY * self.age + self.phase
        )

    def fire(self, target: pygame.Vector2) -> None:
        EnemyBullet(self.rect.midbottom, pygame.Vector2(0, self.BULLET_SPEED), self.bullets)
        audio.play("enemy_shoot")


class Gunship(Enemy):
    """Heavy ship: drops in, strafes sideways, aims at the player, then leaves."""

    IMAGE = "Enemies/enemyRed2.png"
    SCALE = 0.75
    HP = 4
    SCORE = 10
    FIRE_DELAY = (1.1, 1.7)
    BULLET_SPEED = 240.0
    ENTRY_SPEED = 140.0
    STRAFE_SPEED = 90.0
    STAY_TIME = 12.0  # then it dives away so the screen does not get clogged
    EXIT_SPEED = 160.0
    MARGIN = 50

    def __init__(self, *args, hold_y: float = 160.0, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.hold_y = hold_y
        self.direction = self.rng.choice((-1, 1))

    def move(self, dt: float) -> None:
        if self.age > self.STAY_TIME:
            self.position.y += self.EXIT_SPEED * dt
        elif self.position.y < self.hold_y:
            self.position.y = min(self.position.y + self.ENTRY_SPEED * dt, self.hold_y)
        else:
            self.position.x += self.direction * self.STRAFE_SPEED * dt
            if not self.MARGIN <= self.position.x <= WIDTH - self.MARGIN:
                self.direction *= -1
                self.position.x = max(self.MARGIN, min(self.position.x, WIDTH - self.MARGIN))

    def fire(self, target: pygame.Vector2) -> None:
        aim = target - pygame.Vector2(self.rect.midbottom)
        if aim.length_squared() == 0:
            return
        aim.scale_to_length(self.BULLET_SPEED)
        EnemyBullet(self.rect.midbottom, aim, self.bullets)
        audio.play("enemy_shoot")
