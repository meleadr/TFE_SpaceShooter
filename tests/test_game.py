import random

import pygame
import pytest

from spaceshooter import difficulty
from spaceshooter.controls import PlayerInput
from spaceshooter.entities import Bullet, HitResult, Meteor, Player, PowerUp, PowerUpKind
from spaceshooter.entities.meteor import MeteorSize, MeteorSpawner, on_screen_weight
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
    scene.waves.timer = float("inf")
    return scene


def place_meteor(
    game: GameScene,
    center: tuple[float, float],
    speed: float = 0.0,
    size: MeteorSize = MeteorSize.BIG,
) -> Meteor:
    image = size.image_names("Brown")[0]
    meteor = Meteor(size, "Brown", image, center, (0, speed), 0.0, game.meteors)
    meteor.update(0.0)
    return meteor


def test_meteor_falls_and_is_removed_below_screen(game):
    meteor = place_meteor(game, (WIDTH / 2, 0), speed=300)
    game.step(1.0)
    assert meteor.position.y == pytest.approx(300)
    game.step(3.0)
    assert not meteor.alive()


def test_shooting_a_meteor_scores_and_removes_both(game):
    meteor = place_meteor(game, (300, 300), size=MeteorSize.SMALL)
    Bullet((300, 330), game.bullets)
    game.step(STEP)
    assert game.score == 1
    assert not meteor.alive()
    assert len(game.bullets) == 0
    assert len(game.meteors) == 0  # the smallest size does not split


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
    game.player.input = PlayerInput(dx=1, fire=True)
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
    assert on_screen_weight(game.meteors) >= difficulty.max_meteors(0)
    assert on_screen_weight(game.meteors) < difficulty.max_meteors(0) + 1
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
    kinds = {game.powerup_spawner.spawn(player_hurt=False).kind for _ in range(80)}
    assert kinds == {PowerUpKind.SHIELD, PowerUpKind.WEAPON}
    kinds = {game.powerup_spawner.spawn(player_hurt=True).kind for _ in range(80)}
    assert kinds == {PowerUpKind.SHIELD, PowerUpKind.LIFE, PowerUpKind.WEAPON}


def test_game_over_records_best_score(game):
    game.score = 12
    game.player.lives = 0
    game.step(STEP)
    assert game.new_record
    assert SaveData(game.save.path).best_score == 12


@pytest.mark.parametrize(
    ("size", "child"), [(MeteorSize.BIG, MeteorSize.MEDIUM), (MeteorSize.MEDIUM, MeteorSize.SMALL)]
)
def test_shot_meteor_splits_into_two_smaller_ones_flying_apart(game, size, child):
    parent = place_meteor(game, (300, 300), speed=200, size=size)
    Bullet((300, 330), game.bullets)
    game.step(STEP)
    assert game.score == 1 and not parent.alive()
    fragments = list(game.meteors)
    assert [f.size for f in fragments] == [child, child]
    assert sorted(f.velocity.x > 0 for f in fragments) == [False, True]
    assert all(f.velocity.y > 0 for f in fragments)


def test_crashing_into_a_big_meteor_does_not_split_it(game):
    place_meteor(game, game.player.rect.center, size=MeteorSize.BIG)
    game.step(STEP)
    assert len(game.meteors) == 0


def test_big_meteor_takes_seven_shots_to_clear(game):
    place_meteor(game, (300, 300), size=MeteorSize.BIG)
    while game.meteors:
        target = next(iter(game.meteors))
        target.velocity.update(0, 0)
        Bullet((target.position.x, target.position.y + 10), game.bullets)
        game.step(STEP)
    assert game.score == 7


def test_fragments_leaving_the_side_are_removed(game):
    meteor = place_meteor(game, (5, 300), size=MeteorSize.SMALL)
    meteor.velocity.update(-300, 0)
    game.step(0.5)
    assert not meteor.alive()


def test_spawner_mixes_sizes(game):
    spawner = MeteorSpawner(pygame.sprite.Group(), random.Random(1))
    sizes = {spawner.spawn(0).size for _ in range(40)}
    assert sizes == {MeteorSize.BIG, MeteorSize.MEDIUM}
