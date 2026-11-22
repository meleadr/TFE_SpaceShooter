import os

# Run pygame headless in tests and CI.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from spaceshooter import assets
from spaceshooter.settings import HEIGHT, WIDTH


@pytest.fixture
def display():
    """An initialised headless display, needed to load and convert images."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    yield screen
    assets.image.cache_clear()
    assets.font.cache_clear()
    pygame.quit()
