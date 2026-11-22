"""Keyboard mapping: arrows, plus WASD (QWERTY) and ZQSD (AZERTY)."""

from collections.abc import Sequence
from dataclasses import dataclass

import pygame

LEFT_KEYS = (pygame.K_LEFT, pygame.K_a, pygame.K_q)
RIGHT_KEYS = (pygame.K_RIGHT, pygame.K_d)
FIRE_KEYS = (pygame.K_SPACE, pygame.K_UP, pygame.K_w, pygame.K_z)


@dataclass(frozen=True)
class PlayerInput:
    direction: int  # -1 left, 0 none, +1 right
    fire: bool


def read_input(pressed: Sequence[bool]) -> PlayerInput:
    """Translate the state from pygame.key.get_pressed() into player intent."""
    left = any(pressed[key] for key in LEFT_KEYS)
    right = any(pressed[key] for key in RIGHT_KEYS)
    return PlayerInput(direction=int(right) - int(left), fire=any(pressed[k] for k in FIRE_KEYS))
