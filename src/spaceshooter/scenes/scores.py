"""High scores screen: the local top 10."""

import pygame

from spaceshooter.controls import Command, command
from spaceshooter.effects import Starfield
from spaceshooter.save import TOP_SIZE, SaveData
from spaceshooter.scenes.base import Scene, SceneManager
from spaceshooter.settings import HEIGHT, WIDTH
from spaceshooter.ui import GOLD, GREY, WHITE, draw_text

ROW_HEIGHT = 44
FIRST_ROW = 200


class ScoresScene(Scene):
    def __init__(
        self,
        manager: SceneManager,
        save: SaveData,
        starfield: Starfield | None = None,
        highlight: int | None = None,
    ) -> None:
        super().__init__(manager)
        self.save = save
        self.starfield = starfield or Starfield()
        self.highlight = highlight  # rank to show in gold (the game just played)
        self.time = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if command(event) in (Command.BACK, Command.CONFIRM):
            self.manager.pop()

    def update(self, dt: float) -> None:
        self.time += dt
        self.starfield.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.starfield.draw(surface)
        draw_text(surface, "MEILLEURS SCORES", 40, (WIDTH / 2, 110))
        if not self.save.scores:
            draw_text(surface, "Aucun score pour l'instant", 22, (WIDTH / 2, HEIGHT / 2), GREY)
        for rank, entry in enumerate(self.save.scores[:TOP_SIZE], start=1):
            y = FIRST_ROW + (rank - 1) * ROW_HEIGHT
            color = WHITE
            if rank == self.highlight:
                if int(self.time * 3) % 2:  # the new entry blinks
                    continue
                color = GOLD
            elif rank > 3:
                color = GREY
            draw_text(surface, f"{rank}.", 24, (WIDTH / 2 - 150, y), color)
            draw_text(surface, entry.name, 24, (WIDTH / 2 - 40, y), color)
            draw_text(surface, str(entry.score), 24, (WIDTH / 2 + 120, y), color)
        draw_text(surface, "Entrée / Échap : retour", 14, (WIDTH / 2, HEIGHT - 40), GREY)
