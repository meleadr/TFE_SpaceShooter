import random

import pygame
import pytest

from spaceshooter.entities import Bullet, Gunship, Player, PowerUp, PowerUpKind
from spaceshooter.save import SaveData
from spaceshooter.scenes import SceneManager
from spaceshooter.scenes.game import MAXED_WEAPON_BONUS, GameScene
from spaceshooter.settings import STEP, WIDTH


@pytest.fixture
def game(display, tmp_path):
    scene = GameScene(SceneManager(), SaveData(tmp_path / "save.json"), rng=random.Random(5))
    scene.meteor_spawner.timer = float("inf")
    scene.powerup_spawner.timer = float("inf")
    scene.waves.timer = float("inf")
    return scene


def pick_up(game, kind):
    powerup = PowerUp(kind, game.player.rect.centerx, game.powerups)
    powerup.rect.center = game.player.rect.center
    game.step(STEP)


@pytest.mark.parametrize("level", sorted(Player.WEAPON_PATTERNS))
def test_each_weapon_level_fires_its_pattern(game, level):
    game.player.weapon = level
    game.player.fire()
    assert len(game.bullets) == len(Player.WEAPON_PATTERNS[level])


def test_spread_shots_fan_out_symmetrically(game):
    game.player.weapon = 3
    game.player.fire()
    xs = sorted(bullet.velocity.x for bullet in game.bullets)
    assert xs[0] < 0 and xs[1] == pytest.approx(0) and xs[2] == pytest.approx(-xs[0])
    assert all(bullet.velocity.y < 0 for bullet in game.bullets)
    assert all(bullet.velocity.length() == pytest.approx(Bullet.SPEED) for bullet in game.bullets)


def test_angled_bullet_leaves_through_the_side(game):
    bullet = Bullet((WIDTH - 5, 400), game.bullets, angle=60)
    for _ in range(30):
        game.bullets.update(STEP)
    assert not bullet.alive()


def test_weapon_pickup_upgrades_until_max_then_scores(game):
    for expected in range(2, Player.MAX_WEAPON + 1):
        pick_up(game, PowerUpKind.WEAPON)
        assert game.player.weapon == expected
    assert game.score == 0
    pick_up(game, PowerUpKind.WEAPON)
    assert game.player.weapon == Player.MAX_WEAPON
    assert game.score == MAXED_WEAPON_BONUS


def test_losing_a_life_costs_a_weapon_level(game):
    game.player.weapon = 3
    game.player.hit()
    assert game.player.weapon == 2
    game.player.weapon = 1
    game.player.invulnerable = 0
    game.player.hit()
    assert game.player.weapon == 1


def test_shield_hit_keeps_the_weapon(game):
    game.player.weapon = 3
    game.player.activate_shield()
    game.player.hit()
    assert game.player.weapon == 3


def test_destroyed_gunship_drops_a_weapon_upgrade(game):
    gunship = Gunship((300, 300), game.enemy_bullets, game.rng, 1.0, game.enemies)
    gunship.fire_timer = float("inf")
    gunship.hp = 1
    Bullet((300, 330), game.bullets)
    game.step(STEP)
    assert not gunship.alive()
    (drop,) = game.powerups
    assert drop.kind is PowerUpKind.WEAPON
    assert drop.rect.centery == pytest.approx(300, abs=5)


def test_hud_draws_every_weapon_level(game):
    surface = pygame.display.get_surface()
    for level in range(1, Player.MAX_WEAPON + 1):
        game.player.weapon = level
        game.draw(surface)
