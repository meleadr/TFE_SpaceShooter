import random

import pygame
import pytest

from spaceshooter import waves
from spaceshooter.entities import Bullet, Drone, EnemyBullet, Gunship, Player
from spaceshooter.save import SaveData
from spaceshooter.scenes import SceneManager
from spaceshooter.scenes.game import GameScene
from spaceshooter.settings import HEIGHT, STEP, WIDTH


@pytest.fixture
def game(display, tmp_path):
    scene = GameScene(SceneManager(), SaveData(tmp_path / "save.json"), rng=random.Random(3))
    scene.meteor_spawner.timer = float("inf")
    scene.powerup_spawner.timer = float("inf")
    scene.waves.timer = float("inf")
    return scene


def make(game, cls, position, **kwargs):
    enemy = cls(position, game.enemy_bullets, game.rng, 1.0, game.enemies, **kwargs)
    enemy.fire_timer = float("inf")  # tests trigger shots explicitly
    return enemy


def run(game, seconds):
    for _ in range(round(seconds / STEP)):
        game.step(STEP)


# --- enemies -----------------------------------------------------------------


def test_drone_weaves_downwards(game):
    drone = make(game, Drone, (300, 100))
    xs = []
    for _ in range(240):  # 4 s: a full weave at 1.6 rad/s
        drone.update(STEP, (0, 0))
        xs.append(drone.position.x)
    assert drone.position.y == pytest.approx(100 + Drone.SPEED * 4, abs=1)
    assert min(xs) < 300 - 30 and max(xs) > 300 + 30


def test_drone_fires_straight_down(game):
    drone = make(game, Drone, (300, 200))
    drone.fire(pygame.Vector2(0, 0))
    (bullet,) = game.enemy_bullets
    assert bullet.velocity.x == 0 and bullet.velocity.y > 0


def test_gunship_aims_at_the_player(game):
    gunship = make(game, Gunship, (300, 150))
    target = pygame.Vector2(100, 700)
    gunship.fire(target)
    (bullet,) = game.enemy_bullets
    to_target = target - pygame.Vector2(gunship.rect.midbottom)
    assert bullet.velocity.angle_to(to_target) == pytest.approx(0, abs=0.5)
    assert bullet.velocity.length() == pytest.approx(Gunship.BULLET_SPEED)


def test_gunship_holds_position_strafes_then_leaves(game):
    gunship = make(game, Gunship, (300, -50), hold_y=160)
    for _ in range(round(3 / STEP)):
        gunship.update(STEP, (0, 0))
    assert gunship.position.y == pytest.approx(160)
    for _ in range(round(8 / STEP)):
        gunship.update(STEP, (0, 0))
        assert Gunship.MARGIN <= gunship.position.x <= WIDTH - Gunship.MARGIN
    for _ in range(round(10 / STEP)):
        gunship.update(STEP, (0, 0))
    assert not gunship.alive()


def test_enemies_only_fire_when_on_screen(game):
    drone = make(game, Drone, (300, -100))
    drone.fire_timer = 0.0
    drone.update(STEP, (0, 0))
    assert len(game.enemy_bullets) == 0


def test_enemy_bullet_leaves_the_screen(game):
    bullet = EnemyBullet((300, HEIGHT - 5), pygame.Vector2(0, 400), game.enemy_bullets)
    game.enemy_bullets.update(0.1)
    assert not bullet.alive()


# --- combat ------------------------------------------------------------------


def test_gunship_needs_several_hits_and_scores(game):
    gunship = make(game, Gunship, (300, 300))
    for hit in range(Gunship.HP):
        Bullet((300, 330), game.bullets)
        game.step(STEP)
        gunship.position.update(300, 300)
        assert gunship.alive() == (hit < Gunship.HP - 1)
    assert game.score == Gunship.SCORE


def test_drone_dies_in_one_hit(game):
    drone = make(game, Drone, (300, 300))
    drone.AMPLITUDE = 0
    Bullet((300, 320), game.bullets)
    game.step(STEP)
    assert not drone.alive()
    assert game.score == Drone.SCORE


def test_enemy_shot_hurts_the_player(game):
    EnemyBullet(game.player.rect.center, pygame.Vector2(0, 0), game.enemy_bullets)
    game.step(STEP)
    assert game.player.lives == Player.MAX_LIVES - 1
    assert len(game.enemy_bullets) == 0


def test_shield_blocks_enemy_shots(game):
    game.player.activate_shield()
    EnemyBullet(game.player.rect.center, pygame.Vector2(0, 0), game.enemy_bullets)
    game.step(STEP)
    assert game.player.lives == Player.MAX_LIVES


def test_ramming_an_enemy_destroys_it_without_score(game):
    drone = make(game, Drone, game.player.rect.center)
    drone.SPEED = 0
    drone.AMPLITUDE = 0
    game.step(STEP)
    assert not drone.alive()
    assert game.player.lives == Player.MAX_LIVES - 1
    assert game.score == 0


# --- waves -------------------------------------------------------------------


def test_wave_composition_grows():
    assert [waves.drone_count(n) for n in (1, 2, 7, 20)] == [4, 5, 10, 10]
    assert [waves.gunship_count(n) for n in (1, 2, 3, 4, 10)] == [0, 1, 1, 2, 3]
    assert waves.fire_rate(1) == 1.0 and waves.fire_rate(50) == 1.8


def test_first_wave_arrives_after_the_delay_with_a_banner(game):
    game.waves.timer = waves.FIRST_WAVE_DELAY
    run(game, waves.FIRST_WAVE_DELAY - 1)
    assert not game.waves.active
    run(game, 1.1)
    assert game.waves.active and game.waves.banner == "VAGUE 1"
    assert len(game.enemies) == 0  # ships come after the banner
    run(game, waves.BANNER_TIME + 2)
    assert game.waves.banner is None
    assert len(game.enemies) == waves.drone_count(1)


def test_meteors_pause_during_a_wave_and_resume_after(game):
    game.player.shield = 1e9  # keep the player alive whatever happens
    game.meteor_spawner.timer = 0.0
    game.waves.start_wave()
    run(game, 3)
    assert len(game.meteors) == 0
    for enemy in game.enemies:
        enemy.kill()
    game.waves.pending.clear()
    run(game, 0.1)
    assert not game.waves.active
    assert game.waves.timer == pytest.approx(waves.WAVE_INTERVAL - 0.1, abs=STEP * 2)
    run(game, 1)
    assert len(game.meteors) > 0


def test_wave_ends_once_ships_have_left_the_screen(game):
    game.player.shield = 1e9
    game.waves.start_wave()
    run(game, 15)  # drones fly through the whole screen in about 9 s
    assert not game.waves.active
    assert game.waves.number == 1


def test_even_waves_use_two_columns(game):
    xs = set()
    wave = game.waves.build(2)
    for spawn in wave.schedule:
        enemy = spawn.make()
        if isinstance(enemy, Drone):
            xs.add(round(enemy.origin_x))
    assert len(xs) == 2
