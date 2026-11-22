"""Title screen: the first thing shown, and where 'Menu principal' leads back to."""

import math
import sys

import pygame

from spaceshooter.controls import Action, Command, command
from spaceshooter.effects import Starfield
from spaceshooter.gamepad import gamepads
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
        items = [
            ("Jouer", self.start_game),
            ("Meilleurs scores", self.open_scores),
            ("Commandes", self.open_controls),
        ]
        if not IS_WEB:  # a browser tab cannot be closed from the game
            items.append(("Quitter", manager.quit))
        self.menu = Menu(items, top=HEIGHT / 2 + 40)

    def start_game(self) -> None:
        from spaceshooter.scenes.game import GameScene  # local import: scenes refer to each other

        self.manager.reset(GameScene(self.manager, self.save))

    def open_scores(self) -> None:
        from spaceshooter.scenes.scores import ScoresScene

        self.manager.push(ScoresScene(self.manager, self.save, self.starfield))

    def open_controls(self) -> None:
        from spaceshooter.scenes.controls import ControlsScene

        self.manager.push(ControlsScene(self.manager, self.save, self.starfield))

    def handle_event(self, event: pygame.event.Event) -> None:
        if command(event) is Command.BACK and not IS_WEB:
            self.manager.quit()
        else:
            self.menu.handle_event(event)

    def keys_hint(self) -> str:
        bindings = self.save.bindings
        if bindings.is_default:
            return "Flèches / ZQSD / WASD : bouger   Espace : tirer"
        move = " ".join(
            bindings.label(a) for a in (Action.UP, Action.LEFT, Action.DOWN, Action.RIGHT)
        )
        fire = "Espace" + (
            f" / {bindings.label(Action.FIRE)}" if bindings.custom[Action.FIRE] else ""
        )
        return f"Flèches / {move} : bouger   {fire} : tirer"

    def update(self, dt: float) -> None:
        self.time += dt
        self.starfield.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.starfield.draw(surface)
        bob = 6 * math.sin(self.time * 1.5)
        draw_text(surface, "SPACE", 72, (WIDTH / 2, 180 + bob))
        draw_text(surface, "SHOOTER", 72, (WIDTH / 2, 255 + bob))
        draw_text(surface, "Remaster 2026 du TFE 2019", 16, (WIDTH / 2, 320), GREY)
        if self.save.scores:
            best = self.save.scores[0]
            draw_text(surface, f"Record : {best.score} ({best.name})", 22, (WIDTH / 2, 370), GOLD)
        self.menu.draw(surface)
        if gamepads.count:
            draw_text(
                surface,
                "Manette : stick / croix, A : tirer, Start : pause",
                14,
                (WIDTH / 2, HEIGHT - 85),
                GOLD,
            )
        draw_text(surface, self.keys_hint(), 14, (WIDTH / 2, HEIGHT - 60), GREY)
        draw_text(
            surface,
            "Échap / P : pause   M : son   F11 : plein écran",
            14,
            (WIDTH / 2, HEIGHT - 35),
            GREY,
        )
