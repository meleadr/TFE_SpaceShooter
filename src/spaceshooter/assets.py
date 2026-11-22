"""Loading of bundled assets (Kenney Space Shooter Redux, CC0)."""

from functools import cache
from pathlib import Path

import pygame

ASSETS_DIR = Path(__file__).parent / "data"


@cache
def image(name: str, scale: float = 1.0) -> pygame.Surface:
    """Load an image from data/images once, optionally scaled. Needs an open display."""
    surface = pygame.image.load(ASSETS_DIR / "images" / name).convert_alpha()
    if scale != 1.0:
        surface = pygame.transform.smoothscale_by(surface, scale)
    return surface


def tiled(name: str, size: tuple[int, int]) -> pygame.Surface:
    """Build a surface of the given size by repeating a tile image."""
    tile = image(name)
    surface = pygame.Surface(size).convert()
    for x in range(0, size[0], tile.get_width()):
        for y in range(0, size[1], tile.get_height()):
            surface.blit(tile, (x, y))
    return surface
