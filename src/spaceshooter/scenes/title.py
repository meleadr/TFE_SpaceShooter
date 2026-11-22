"""Title screen: the first thing shown, and where 'Menu principal' leads back to."""

import math
import sys

import pygame

from spaceshooter.effects import Starfield
from spaceshooter.save import SaveData
from spaceshooter.scenes.base import Scene, SceneManager
from spaceshooter.settings import HEIGHT, WIDTH
from spaceshooter.ui import GOLD, GREY, Menu, draw_text

IS_WEB = sys.platform == "emscripten"


class TitleScene(Scene):
    def __init__(self, manager: SceneManager, save: SaveData) -> None:
        super().__init__(manager)
        self.save = save
        self.starfield = Starfield()
        self.time = 0.0
        items = [("Jouer", self.start_game)]
        if not IS_WEB:  # a browser tab cannot be closed from the game
            items.append(("Quitter", manager.quit))
        self.menu = Menu(items, top=HEIGHT / 2 + 40)

    def start_game(self) -> None:
        from spaceshooter.scenes.game import GameScene  # local import: scenes refer to each other

        self.manager.reset(GameScene(self.manager, self.save))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not IS_WEB:
            self.manager.quit()
        else:
            self.menu.handle_event(event)

    def update(self, dt: float) -> None:
        self.time += dt
        self.starfield.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.starfield.draw(surface)
        bob = 6 * math.sin(self.time * 1.5)
        draw_text(surface, "SPACE", 72, (WIDTH / 2, 180 + bob))
        draw_text(surface, "SHOOTER", 72, (WIDTH / 2, 255 + bob))
        draw_text(surface, "Remaster 2026 du TFE 2019", 16, (WIDTH / 2, 320), GREY)
        if self.save.best_score:
            draw_text(surface, f"Record : {self.save.best_score}", 22, (WIDTH / 2, 370), GOLD)
        self.menu.draw(surface)
        draw_text(
            surface,
            "Flèches / ZQSD / WASD : bouger   Espace : tirer",
            14,
            (WIDTH / 2, HEIGHT - 60),
            GREY,
        )
        draw_text(
            surface,
            "Échap / P : pause   M : son   F11 : plein écran",
            14,
            (WIDTH / 2, HEIGHT - 35),
            GREY,
        )
