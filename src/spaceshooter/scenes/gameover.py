"""Game over overlay: final score, name entry for the top 10, and what to do next."""

import string

import pygame

from spaceshooter import assets
from spaceshooter.audio import audio
from spaceshooter.controls import Command, command
from spaceshooter.save import NAME_LENGTH, SaveData
from spaceshooter.scenes.base import Scene, SceneManager
from spaceshooter.settings import HEIGHT, WIDTH
from spaceshooter.ui import GOLD, GREY, WHITE, Menu, dim, draw_text

LETTERS = string.ascii_uppercase
LETTER_KEYS = {getattr(pygame, f"K_{c.lower()}"): c for c in LETTERS}


class NameEntry:
    """Arcade-style initials: up/down change a letter, left/right or confirm move on.

    Letters can also be typed straight from the keyboard.
    """

    SLOT = 54  # px between two letters

    def __init__(self, name: str) -> None:
        self.letters = list(name[:NAME_LENGTH].ljust(NAME_LENGTH, "A"))
        self.cursor = 0
        self.done = False

    @property
    def name(self) -> str:
        return "".join(self.letters)

    def cycle(self, step: int) -> None:
        index = LETTERS.index(self.letters[self.cursor])
        self.letters[self.cursor] = LETTERS[(index + step) % len(LETTERS)]
        audio.play("menu_move")

    def move(self, step: int) -> None:
        self.cursor = max(0, min(self.cursor + step, NAME_LENGTH - 1))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in LETTER_KEYS:
            # Typed letters win over their menu meaning (Z/W/S also mean up/down).
            self.letters[self.cursor] = LETTER_KEYS[event.key]
            self.move(1)
            audio.play("menu_move")
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
            self.move(-1)
            return
        match command(event):
            case Command.UP:
                self.cycle(1)
            case Command.DOWN:
                self.cycle(-1)
            case Command.LEFT:
                self.move(-1)
            case Command.RIGHT:
                self.move(1)
            case Command.CONFIRM if self.cursor < NAME_LENGTH - 1:
                self.move(1)
            case Command.CONFIRM | Command.BACK:  # last letter, or skip: keep the name as is
                self.done = True
                audio.play("menu_confirm")

    def draw(self, surface: pygame.Surface, center_y: float, blink: bool) -> None:
        font = assets.font(48)
        left = WIDTH / 2 - self.SLOT * (NAME_LENGTH - 1) / 2
        for i, letter in enumerate(self.letters):
            x = left + i * self.SLOT
            current = i == self.cursor
            label = font.render(letter, True, GOLD if current else WHITE)
            surface.blit(label, label.get_rect(center=(x, center_y)))
            if current:
                top, bottom = center_y - 38, center_y + 38
                pygame.draw.polygon(surface, GOLD, [(x - 9, top), (x + 9, top), (x, top - 10)])
                if blink:
                    pygame.draw.line(surface, GOLD, (x - 18, bottom - 6), (x + 18, bottom - 6), 3)
                pygame.draw.polygon(
                    surface, GOLD, [(x - 9, bottom), (x + 9, bottom), (x, bottom + 10)]
                )


class GameOverScene(Scene):
    is_overlay = True
    INPUT_DELAY = 0.6  # ignore keys briefly so a held fire key does not skip the screen

    def __init__(self, manager: SceneManager, save: SaveData, score: int, rank: int | None) -> None:
        super().__init__(manager)
        self.save = save
        self.score = score
        self.rank = rank  # place in the top 10 (already recorded), None if it did not make it
        self.time = 0.0
        self.entry = NameEntry(save.last_name) if rank else None
        self.menu = Menu(
            [
                ("Rejouer", self.restart),
                ("Meilleurs scores", self.show_scores),
                ("Menu principal", self.to_title),
            ],
            470,
        )

    @property
    def entering_name(self) -> bool:
        return self.entry is not None and not self.entry.done

    def restart(self) -> None:
        from spaceshooter.scenes.game import GameScene

        self.manager.reset(GameScene(self.manager, self.save))

    def show_scores(self) -> None:
        from spaceshooter.scenes.scores import ScoresScene

        self.manager.push(ScoresScene(self.manager, self.save, highlight=self.rank))

    def to_title(self) -> None:
        from spaceshooter.scenes.title import TitleScene

        self.manager.reset(TitleScene(self.manager, self.save))

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.time < self.INPUT_DELAY:
            return
        if self.entering_name:
            self.entry.handle_event(event)
            if self.entry.done:
                self.save.rename(self.rank, self.entry.name)
        else:
            self.menu.handle_event(event)

    def update(self, dt: float) -> None:
        self.time += dt

    def draw(self, surface: pygame.Surface) -> None:
        dim(surface)
        draw_text(surface, "GAME OVER", 56, (WIDTH / 2, HEIGHT / 2 - 180))
        draw_text(surface, f"Score : {self.score}", 30, (WIDTH / 2, HEIGHT / 2 - 100))
        if self.rank == 1:
            draw_text(surface, "Nouveau record !", 24, (WIDTH / 2, HEIGHT / 2 - 50), GOLD)
        elif self.rank:
            draw_text(
                surface, f"{self.rank}e au classement !", 24, (WIDTH / 2, HEIGHT / 2 - 50), GOLD
            )
        else:
            draw_text(
                surface, f"Record : {self.save.best_score}", 20, (WIDTH / 2, HEIGHT / 2 - 50), GREY
            )
        if self.entering_name:
            draw_text(surface, "Entre ton nom", 22, (WIDTH / 2, 440))
            self.entry.draw(surface, 530, blink=int(self.time * 3) % 2 == 0)
            draw_text(
                surface, "Lettres ou haut / bas, Entrée : valider", 14, (WIDTH / 2, 620), GREY
            )
        else:
            self.menu.draw(surface)
