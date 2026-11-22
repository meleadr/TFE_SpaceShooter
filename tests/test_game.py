import random

import pygame
import pytest

from spaceshooter import difficulty
from spaceshooter.controls import PlayerInput
from spaceshooter.entities import Bullet, HitResult, Meteor, Player, PowerUp, PowerUpKind
from spaceshooter.entities.meteor import METEOR_IMAGES
from spaceshooter.save import SaveData
from spaceshooter.scenes import SceneManager
from spaceshooter.scenes.game import GameScene
from spaceshooter.scenes.gameover import GameOverScene
from spaceshooter.scenes.pause import PauseScene
from spaceshooter.settings import HEIGHT, STEP, WIDTH


@pytest.fixture
def game(display, tmp_path):
    scene = GameScene(SceneManager(), SaveData(tmp_path / "save.json"), rng=random.Random(42))
    # Tests place meteors and power-ups themselves.
    scene.meteor_spawner.timer = float("inf")
    scene.powerup_spawner.timer = float("inf")
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
    assert game.player.hit() is HitResult.DAMAGED


def test_losing_all_lives_shows_game_over_after_a_delay(game):
    game.manager.push(game)
    game.player.lives = 1
    place_meteor(game, game.player.rect.center)
    game.step(STEP)
    assert game.game_over
    assert game.manager.top is game  # explosion plays first

    for _ in range(round(GameScene.GAME_OVER_DELAY / STEP) + 1):
        game.step(STEP)
    assert isinstance(game.manager.top, GameOverScene)


def test_player_is_frozen_once_dead(game):
    game.player.lives = 0
    game.step(STEP)
    x = game.player.rect.x
    game.player.input = PlayerInput(direction=1, fire=True)
    game.step(STEP)
    assert game.player.rect.x == x
    assert len(game.bullets) == 0


@pytest.mark.parametrize("key", [pygame.K_ESCAPE, pygame.K_p])
def test_pause_key_opens_pause_overlay(game, key):
    game.manager.push(game)
    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))
    assert isinstance(game.manager.top, PauseScene)
    assert [type(s) for s in game.manager.visible_scenes()] == [GameScene, PauseScene]


def test_losing_window_focus_pauses(game):
    game.manager.push(game)
    game.handle_event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
    assert isinstance(game.manager.top, PauseScene)


def test_spawner_respects_max_meteors(game):
    game.meteor_spawner.timer = 0.0
    for _ in range(round(10 / STEP)):
        game.meteor_spawner.update(STEP, score=0)
    assert len(game.meteors) == difficulty.max_meteors(0)
    for meteor in game.meteors:
        assert meteor.rect.left >= 0 and meteor.rect.right <= WIDTH
        assert meteor.rect.bottom <= HEIGHT


def test_shield_absorbs_meteors_without_losing_lives(game):
    game.player.activate_shield()
    meteor = place_meteor(game, game.player.rect.center)
    game.step(STEP)
    assert game.player.lives == Player.MAX_LIVES
    assert not meteor.alive()


def test_shield_wears_off(game):
    game.player.activate_shield()
    for _ in range(round(Player.SHIELD_TIME / STEP) + 1):
        game.step(STEP)
    assert game.player.shield == 0
    place_meteor(game, game.player.rect.center)
    game.step(STEP)
    assert game.player.lives == Player.MAX_LIVES - 1


@pytest.mark.parametrize(
    ("kind", "lives_before", "lives_after", "shielded"),
    [
        (PowerUpKind.SHIELD, 3, 3, True),
        (PowerUpKind.LIFE, 2, 3, False),
        (PowerUpKind.LIFE, 3, 3, False),  # capped at MAX_LIVES
    ],
)
def test_picking_up_powerups(game, kind, lives_before, lives_after, shielded):
    game.player.lives = lives_before
    powerup = PowerUp(kind, game.player.rect.centerx, game.powerups)
    powerup.rect.center = game.player.rect.center
    game.step(STEP)
    assert not powerup.alive()
    assert game.player.lives == lives_after
    assert (game.player.shield > 0) is shielded


def test_powerup_spawner_only_drops_lives_when_hurt(game):
    kinds = {game.powerup_spawner.spawn(player_hurt=False).kind for _ in range(50)}
    assert kinds == {PowerUpKind.SHIELD}
    kinds = {game.powerup_spawner.spawn(player_hurt=True).kind for _ in range(50)}
    assert kinds == {PowerUpKind.SHIELD, PowerUpKind.LIFE}


def test_game_over_records_best_score(game):
    game.score = 12
    game.player.lives = 0
    game.step(STEP)
    assert game.new_record
    assert SaveData(game.save.path).best_score == 12
