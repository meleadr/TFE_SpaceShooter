import pygame
import pytest

from spaceshooter.controls import PlayerInput, read_input
from spaceshooter.entities import Bullet, Player
from spaceshooter.entities.player import HUD_HEIGHT, PLAYFIELD
from spaceshooter.settings import HEIGHT, STEP, WIDTH


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
        ({}, PlayerInput()),
        ({pygame.K_LEFT: True}, PlayerInput(dx=-1)),
        ({pygame.K_q: True, pygame.K_SPACE: True}, PlayerInput(dx=-1, fire=True)),  # AZERTY
        ({pygame.K_a: True, pygame.K_w: True}, PlayerInput(dx=-1, dy=-1)),  # QWERTY
        ({pygame.K_d: True, pygame.K_z: True}, PlayerInput(dx=1, dy=-1)),
        ({pygame.K_DOWN: True, pygame.K_s: True}, PlayerInput(dy=1)),
        ({pygame.K_UP: True}, PlayerInput(dy=-1)),  # up moves, it no longer fires
        ({pygame.K_LEFT: True, pygame.K_RIGHT: True}, PlayerInput()),
    ],
)
def test_read_input(pressed, expected):
    assert read_input(Keys(pressed)) == expected


def test_player_starts_centered(player):
    assert player.rect.centerx == pytest.approx(WIDTH / 2)


def test_player_moves_at_constant_speed(player):
    start = player.rect.x
    simulate(player, 0.5, PlayerInput(dx=1))
    assert player.rect.x - start == pytest.approx(Player.SPEED * 0.5)


def test_diagonal_is_not_faster(player):
    start = pygame.Vector2(player.rect.center)
    simulate(player, 0.25, PlayerInput(dx=-1, dy=-1))
    assert start.distance_to(player.rect.center) == pytest.approx(
        Player.SPEED * 0.25, abs=0.01
    )  # FRect is float32


@pytest.mark.parametrize(("dx", "dy"), [(-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (-1, 1)])
def test_player_stays_in_playfield(player, dx, dy):
    simulate(player, 5.0, PlayerInput(dx=dx, dy=dy))
    assert PLAYFIELD.contains(player.rect)


def test_player_cannot_enter_the_hud_band(player):
    simulate(player, 5.0, PlayerInput(dy=-1))
    assert player.rect.top == pytest.approx(HUD_HEIGHT)
    assert player.rect.bottom <= HEIGHT


def test_holding_fire_respects_cooldown(player):
    simulate(player, 1.0, PlayerInput(fire=True))
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
