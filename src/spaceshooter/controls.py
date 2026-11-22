"""Keyboard mapping: arrows, plus WASD (QWERTY) and ZQSD (AZERTY)."""

from collections.abc import Sequence
from dataclasses import dataclass

import pygame

LEFT_KEYS = (pygame.K_LEFT, pygame.K_a, pygame.K_q)
RIGHT_KEYS = (pygame.K_RIGHT, pygame.K_d)
UP_KEYS = (pygame.K_UP, pygame.K_w, pygame.K_z)
DOWN_KEYS = (pygame.K_DOWN, pygame.K_s)
FIRE_KEYS = (pygame.K_SPACE,)


@dataclass(frozen=True)
class PlayerInput:
    dx: int = 0  # -1 left, 0 none, +1 right
    dy: int = 0  # -1 up, 0 none, +1 down
    fire: bool = False


def _held(pressed: Sequence[bool], keys: tuple[int, ...]) -> bool:
    return any(pressed[key] for key in keys)


def read_input(pressed: Sequence[bool]) -> PlayerInput:
    """Translate the state from pygame.key.get_pressed() into player intent."""
    return PlayerInput(
        dx=int(_held(pressed, RIGHT_KEYS)) - int(_held(pressed, LEFT_KEYS)),
        dy=int(_held(pressed, DOWN_KEYS)) - int(_held(pressed, UP_KEYS)),
        fire=_held(pressed, FIRE_KEYS),
    )
