"""The gameplay scene."""

import pygame

from spaceshooter import assets
from spaceshooter.controls import read_input
from spaceshooter.entities import Player
from spaceshooter.scenes.base import Scene, SceneManager
from spaceshooter.settings import HEIGHT, WIDTH


class GameScene(Scene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.background = assets.tiled("backgrounds/darkPurple.png", (WIDTH, HEIGHT))
        self.bullets = pygame.sprite.Group()
        self.player = Player(self.bullets)
        self.players = pygame.sprite.GroupSingle(self.player)

    def handle_event(self, event: pygame.event.Event) -> None:
        # Escape quits for now; it opens the pause menu from M4 on.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.quit()

    def update(self, dt: float) -> None:
        self.player.input = read_input(pygame.key.get_pressed())
        self.players.update(dt)
        self.bullets.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, 0))
        self.bullets.draw(surface)
        self.players.draw(surface)
