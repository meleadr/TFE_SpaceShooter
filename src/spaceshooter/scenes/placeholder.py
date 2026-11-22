"""Temporary start screen, replaced by the real title menu in M4."""

import pygame

from spaceshooter.scenes.base import Scene
from spaceshooter.settings import HEIGHT, TITLE, WIDTH


class PlaceholderScene(Scene):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.font = pygame.font.Font(None, 64)
        self.small_font = pygame.font.Font(None, 28)
        self.elapsed = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.quit()

    def update(self, dt: float) -> None:
        self.elapsed += dt

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((8, 8, 24))
        title = self.font.render(TITLE, True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        hint = self.small_font.render(
            f"M0 skeleton - {self.elapsed:5.1f}s - Esc to quit, F11 fullscreen",
            True,
            (150, 150, 180),
        )
        surface.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))
