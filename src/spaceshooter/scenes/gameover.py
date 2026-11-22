"""Game over overlay with the final score and what to do next."""

import pygame

from spaceshooter.save import SaveData
from spaceshooter.scenes.base import Scene, SceneManager
from spaceshooter.settings import HEIGHT, WIDTH
from spaceshooter.ui import GOLD, GREY, Menu, dim, draw_text


class GameOverScene(Scene):
    is_overlay = True
    INPUT_DELAY = 0.6  # ignore keys briefly so a held fire key does not skip the screen

    def __init__(self, manager: SceneManager, save: SaveData, score: int, new_record: bool) -> None:
        super().__init__(manager)
        self.save = save
        self.score = score
        self.new_record = new_record
        self.time = 0.0
        self.menu = Menu([("Rejouer", self.restart), ("Menu principal", self.to_title)], 470)

    def restart(self) -> None:
        from spaceshooter.scenes.game import GameScene

        self.manager.reset(GameScene(self.manager, self.save))

    def to_title(self) -> None:
        from spaceshooter.scenes.title import TitleScene

        self.manager.reset(TitleScene(self.manager, self.save))

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.time >= self.INPUT_DELAY:
            self.menu.handle_event(event)

    def update(self, dt: float) -> None:
        self.time += dt

    def draw(self, surface: pygame.Surface) -> None:
        dim(surface)
        draw_text(surface, "GAME OVER", 56, (WIDTH / 2, HEIGHT / 2 - 180))
        draw_text(surface, f"Score : {self.score}", 30, (WIDTH / 2, HEIGHT / 2 - 100))
        if self.new_record:
            draw_text(surface, "Nouveau record !", 24, (WIDTH / 2, HEIGHT / 2 - 50), GOLD)
        else:
            draw_text(
                surface, f"Record : {self.save.best_score}", 20, (WIDTH / 2, HEIGHT / 2 - 50), GREY
            )
        self.menu.draw(surface)
