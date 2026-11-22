"""Small UI helpers: centered text, dimming overlay and keyboard menus."""

from collections.abc import Callable

import pygame

from spaceshooter import assets
from spaceshooter.audio import audio
from spaceshooter.settings import HEIGHT, WIDTH

WHITE = (255, 255, 255)
GREY = (170, 170, 200)
GOLD = (255, 210, 90)

UP_KEYS = (pygame.K_UP, pygame.K_w, pygame.K_z)
DOWN_KEYS = (pygame.K_DOWN, pygame.K_s)
CONFIRM_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)


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
    """Vertical list of options driven by the keyboard."""

    SPACING = 56

    def __init__(self, items: list[tuple[str, Callable[[], None]]], top: float) -> None:
        self.items = items
        self.top = top
        self.selected = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in UP_KEYS:
            self.selected = (self.selected - 1) % len(self.items)
            audio.play("menu_move")
        elif event.key in DOWN_KEYS:
            self.selected = (self.selected + 1) % len(self.items)
            audio.play("menu_move")
        elif event.key in CONFIRM_KEYS:
            audio.play("menu_confirm")
            self.items[self.selected][1]()

    def draw(self, surface: pygame.Surface) -> None:
        for index, (label, _) in enumerate(self.items):
            y = self.top + index * self.SPACING
            if index == self.selected:
                draw_text(surface, f">  {label}  <", 30, (WIDTH / 2, y), GOLD)
            else:
                draw_text(surface, label, 26, (WIDTH / 2, y), GREY)
