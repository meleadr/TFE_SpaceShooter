"""Controls screen: shows the gamepad layout and lets the player rebind keys."""

import pygame

from spaceshooter.audio import audio
from spaceshooter.controls import ACTION_LABELS, RESERVED_KEYS, Action, Command, command
from spaceshooter.effects import Starfield
from spaceshooter.save import SaveData
from spaceshooter.scenes.base import Scene, SceneManager
from spaceshooter.settings import WIDTH
from spaceshooter.ui import GOLD, GREY, Menu, draw_text

MESSAGE_TIME = 1.5


class ControlsScene(Scene):
    def __init__(self, manager: SceneManager, save: SaveData, starfield: Starfield) -> None:
        super().__init__(manager)
        self.save = save
        self.starfield = starfield  # shared with the title screen so the stars keep flowing
        self.waiting: Action | None = None  # action waiting for its new key
        self.message = ""
        self.message_time = 0.0
        self.menu = Menu([], top=190, spacing=48, size=22)
        self.refresh()

    def refresh(self) -> None:
        bindings = self.save.bindings
        items = [
            (f"{ACTION_LABELS[action]} : {bindings.label(action)}", self.rebinder(action))
            for action in Action
        ]
        items += [("Réinitialiser", self.reset), ("Retour", self.close)]
        self.menu.items = items

    def rebinder(self, action: Action):
        def start() -> None:
            self.waiting = action

        return start

    def reset(self) -> None:
        self.save.bindings.reset()
        self.save.save()
        self.refresh()
        self.say("Touches par défaut rétablies")

    def close(self) -> None:
        self.manager.pop()

    def say(self, message: str) -> None:
        self.message = message
        self.message_time = MESSAGE_TIME

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.waiting is not None:
            self.capture(event)
        elif command(event) is Command.BACK:
            self.close()
        else:
            self.menu.handle_event(event)

    def capture(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.waiting = None  # cancelled
        elif event.type == pygame.KEYDOWN:
            if self.save.bindings.bind(self.waiting, event.key):
                self.save.save()
                self.refresh()
                self.waiting = None
                audio.play("menu_confirm")
            elif event.key in RESERVED_KEYS:
                self.say("Touche réservée")
        elif command(event) is Command.BACK:  # B on a gamepad also cancels
            self.waiting = None

    def update(self, dt: float) -> None:
        self.starfield.update(dt)
        self.message_time = max(self.message_time - dt, 0.0)

    def draw(self, surface: pygame.Surface) -> None:
        self.starfield.draw(surface)
        draw_text(surface, "COMMANDES", 44, (WIDTH / 2, 90))
        draw_text(surface, "Flèches et Espace marchent toujours", 14, (WIDTH / 2, 140), GREY)
        self.menu.draw(surface)
        if self.waiting is not None:
            label = ACTION_LABELS[self.waiting]
            draw_text(surface, f"Appuie sur une touche : {label}", 20, (WIDTH / 2, 560), GOLD)
            draw_text(surface, "Échap : annuler", 14, (WIDTH / 2, 590), GREY)
        elif self.message_time > 0:
            draw_text(surface, self.message, 18, (WIDTH / 2, 575), GOLD)
        lines = (
            "Manette",
            "Stick gauche ou croix : bouger",
            "A / X / RB / RT : tirer   Start : pause",
            "A : valider   B : retour",
        )
        for i, line in enumerate(lines):
            draw_text(surface, line, 18 if i == 0 else 14, (WIDTH / 2, 650 + i * 26), GREY)
