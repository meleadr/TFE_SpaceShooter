import pygame

from spaceshooter import assets


class Bullet(pygame.sprite.Sprite):
    SPEED = 600.0  # px/s (the 2019 version moved 10 px per frame at 60 fps)

    def __init__(self, midbottom: tuple[float, float], *groups: pygame.sprite.Group) -> None:
        super().__init__(*groups)
        self.image = assets.image("Lasers/laserBlue01.png")
        self.rect = self.image.get_frect(midbottom=midbottom)

    def update(self, dt: float) -> None:
        self.rect.y -= self.SPEED * dt
        if self.rect.bottom < 0:
            self.kill()
