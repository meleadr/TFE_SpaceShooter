"""Small UI helpers: centered text, dimming overlay and menus."""

from collections.abc import Callable

import pygame

from spaceshooter import assets
from spaceshooter.audio import audio
from spaceshooter.controls import Command, command
from spaceshooter.settings import HEIGHT, WIDTH

WHITE = (255, 255, 255)
GREY = (170, 170, 200)
GOLD = (255, 210, 90)


def draw_text(
    surface: pygame.Surface,
    text: str,
    size: int,
    center: tuple[float, float],
    color: tuple[int, int, int] = WHITE,
) -> pygame.Rect:
    label = assets.font(size).render(text, True, color)
    return surface.blit(label, label.get_rect(center=center))


def dim(surface: pygame.Surface, alpha: int = 160) -> None:
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((10, 5, 25, alpha))
    surface.blit(veil, (0, 0))


class Menu:
    """Vertical list of options driven by the keyboard or a gamepad."""

    def __init__(
        self,
        items: list[tuple[str, Callable[[], None]]],
        top: float,
        spacing: float = 56,
        size: int = 26,
    ) -> None:
        self.items = items
        self.top = top
        self.spacing = spacing
        self.size = size
        self.selected = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        match command(event):
            case Command.UP:
                self.selected = (self.selected - 1) % len(self.items)
                audio.play("menu_move")
            case Command.DOWN:
                self.selected = (self.selected + 1) % len(self.items)
                audio.play("menu_move")
            case Command.CONFIRM:
                audio.play("menu_confirm")
                self.items[self.selected][1]()

    def draw(self, surface: pygame.Surface) -> None:
        for index, (label, _) in enumerate(self.items):
            y = self.top + index * self.spacing
            if index == self.selected:
                draw_text(surface, f">  {label}  <", self.size + 4, (WIDTH / 2, y), GOLD)
            else:
                draw_text(surface, label, self.size, (WIDTH / 2, y), GREY)
