"""Pause overlay, drawn over the frozen game."""

import pygame

from spaceshooter.save import SaveData
from spaceshooter.scenes.base import Scene, SceneManager
from spaceshooter.settings import HEIGHT, WIDTH
from spaceshooter.ui import Menu, dim, draw_text

RESUME_KEYS = (pygame.K_ESCAPE, pygame.K_p)


class PauseScene(Scene):
    is_overlay = True

    def __init__(self, manager: SceneManager, save: SaveData) -> None:
        super().__init__(manager)
        self.save = save
        self.menu = Menu(
            [("Reprendre", self.resume), ("Menu principal", self.to_title)], HEIGHT / 2
        )

    def resume(self) -> None:
        self.manager.pop()

    def to_title(self) -> None:
        from spaceshooter.scenes.title import TitleScene

        self.manager.reset(TitleScene(self.manager, self.save))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in RESUME_KEYS:
            self.resume()
        else:
            self.menu.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        dim(surface)
        draw_text(surface, "PAUSE", 56, (WIDTH / 2, HEIGHT / 2 - 100))
        self.menu.draw(surface)
