import pygame
import pytest

from spaceshooter.controls import PlayerInput, read_input
from spaceshooter.entities import Bullet, Player
from spaceshooter.settings import STEP, WIDTH


class Keys(dict):
    """Stand-in for pygame.key.get_pressed(): unknown keys are not pressed."""

    def __missing__(self, key):
        return False


def simulate(player: Player, seconds: float, player_input: PlayerInput) -> None:
    player.input = player_input
    for _ in range(round(seconds / STEP)):
        player.update(STEP)
        player.bullets.update(STEP)


@pytest.fixture
def player(display):
    return Player(pygame.sprite.Group())


@pytest.mark.parametrize(
    ("pressed", "expected"),
    [
        ({}, PlayerInput(0, False)),
        ({pygame.K_LEFT: True}, PlayerInput(-1, False)),
        ({pygame.K_q: True, pygame.K_SPACE: True}, PlayerInput(-1, True)),
        ({pygame.K_d: True, pygame.K_UP: True}, PlayerInput(1, True)),
        ({pygame.K_LEFT: True, pygame.K_RIGHT: True}, PlayerInput(0, False)),
    ],
)
def test_read_input(pressed, expected):
    assert read_input(Keys(pressed)) == expected


def test_player_starts_centered(player):
    assert player.rect.centerx == pytest.approx(WIDTH / 2)


def test_player_moves_at_constant_speed(player):
    start = player.rect.x
    simulate(player, 0.5, PlayerInput(direction=1, fire=False))
    assert player.rect.x - start == pytest.approx(Player.SPEED * 0.5)


@pytest.mark.parametrize("direction", [-1, 1])
def test_player_stays_on_screen(player, direction):
    simulate(player, 5.0, PlayerInput(direction=direction, fire=False))
    assert player.rect.left >= 0
    assert player.rect.right <= WIDTH


def test_holding_fire_respects_cooldown(player):
    simulate(player, 1.0, PlayerInput(direction=0, fire=True))
    assert len(player.bullets) == 4  # t = 0, 0.3, 0.6, 0.9


def test_bullet_spawns_above_ship(player):
    player.fire()
    (bullet,) = player.bullets
    assert bullet.rect.bottom == pytest.approx(player.rect.top)
    assert bullet.rect.centerx == pytest.approx(player.rect.centerx)


def test_bullet_is_removed_off_screen(display):
    bullets = pygame.sprite.Group()
    Bullet((100, 50), bullets)
    for _ in range(60):
        bullets.update(STEP)
    assert len(bullets) == 0
