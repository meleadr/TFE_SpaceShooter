import pygame

from spaceshooter import assets
from spaceshooter.settings import HEIGHT, WIDTH

SCREEN = pygame.Rect(0, 0, WIDTH, HEIGHT)


class Bullet(pygame.sprite.Sprite):
    SPEED = 600.0  # px/s (the 2019 version moved 10 px per frame at 60 fps)

    def __init__(
        self,
        midbottom: tuple[float, float],
        *groups: pygame.sprite.Group,
        angle: float = 0.0,
    ) -> None:
        """`angle` in degrees from straight up, positive towards the right."""
        super().__init__(*groups)
        self.velocity = pygame.Vector2(0, -self.SPEED).rotate(angle)
        image = assets.image("Lasers/laserBlue01.png")
        self.image = pygame.transform.rotate(image, -angle) if angle else image
        self.rect = self.image.get_frect(midbottom=midbottom)

    def update(self, dt: float) -> None:
        self.rect.center += self.velocity * dt
        if not self.rect.colliderect(SCREEN):
            self.kill()
