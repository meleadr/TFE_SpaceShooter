import random

import pygame
import pytest

from spaceshooter.entities import Bullet, Meteor, Player
from spaceshooter.entities.meteor import METEOR_IMAGES
from spaceshooter.scenes import SceneManager
from spaceshooter.scenes.game import GameScene
from spaceshooter.settings import HEIGHT, STEP, WIDTH


@pytest.fixture
def game(display):
    scene = GameScene(SceneManager(), rng=random.Random(42))
    scene.spawner.timer = float("inf")  # tests place meteors themselves
    return scene


def place_meteor(game: GameScene, center: tuple[float, float], speed: float = 0.0) -> Meteor:
    meteor = Meteor(center[0], speed, 0.0, METEOR_IMAGES[0], game.meteors)
    meteor.position.update(center)
    meteor.update(0.0)
    return meteor


def test_meteor_falls_and_is_removed_below_screen(game):
    meteor = place_meteor(game, (WIDTH / 2, 0), speed=300)
    game.step(1.0)
    assert meteor.position.y == pytest.approx(300)
    game.step(3.0)
    assert not meteor.alive()


def test_shooting_a_meteor_scores_and_removes_both(game):
    meteor = place_meteor(game, (300, 300))
    Bullet((300, 340), game.bullets)
    game.step(STEP)
    assert game.score == 1
    assert not meteor.alive()
    assert len(game.bullets) == 0


def test_meteor_hit_costs_a_life_then_grants_grace(game):
    first = place_meteor(game, game.player.rect.center)
    game.step(STEP)
    assert game.player.lives == Player.MAX_LIVES - 1
    assert not first.alive()

    place_meteor(game, game.player.rect.center)
    game.step(STEP)
    assert game.player.lives == Player.MAX_LIVES - 1  # still invulnerable


def test_invulnerability_wears_off(game):
    game.player.hit()
    for _ in range(round(Player.INVULNERABLE_TIME / STEP) + 1):
        game.step(STEP)
    assert game.player.hit()


def test_losing_all_lives_ends_the_game_and_freezes_it(game):
    game.player.lives = 1
    place_meteor(game, game.player.rect.center)
    game.step(STEP)
    assert game.game_over

    meteor = place_meteor(game, (100, 100), speed=300)
    game.update(1.0)
    assert meteor.position.y == pytest.approx(100)


def test_enter_restarts_after_game_over(game):
    game.manager.push(game)
    game.game_over = True
    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert game.manager.top is not game
    assert isinstance(game.manager.top, GameScene)


def test_spawner_respects_max_meteors(game):
    game.spawner.timer = 0.0
    for _ in range(round(10 / STEP)):
        game.spawner.update(STEP, score=0)
    assert len(game.meteors) == 3
    for meteor in game.meteors:
        assert meteor.rect.left >= 0 and meteor.rect.right <= WIDTH
        assert meteor.rect.bottom <= HEIGHT
