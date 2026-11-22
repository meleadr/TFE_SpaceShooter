import random

import pygame
import pytest

from spaceshooter import waves
from spaceshooter.entities import Boss, Bullet, Player
from spaceshooter.entities.boss import boss_hp
from spaceshooter.save import SaveData
from spaceshooter.scenes import SceneManager
from spaceshooter.scenes.game import GameScene
from spaceshooter.settings import STEP


@pytest.fixture
def game(display, tmp_path):
    scene = GameScene(SceneManager(), SaveData(tmp_path / "save.json"), rng=random.Random(9))
    scene.meteor_spawner.timer = float("inf")
    scene.powerup_spawner.timer = float("inf")
    scene.waves.timer = float("inf")
    return scene


def spawn_boss(game, number=1, entered=True) -> Boss:
    boss = Boss((300, Boss.HOLD_Y), game.enemy_bullets, game.rng, 1.0, game.enemies, number=number)
    boss.entered = entered
    return boss


def run_boss(boss, seconds, target=(300, 700)):
    for _ in range(round(seconds / STEP)):
        boss.update(STEP, target)


def test_every_fourth_wave_is_a_boss(game):
    for number in range(1, 9):
        wave = game.waves.build(number)
        assert wave.boss == (number % waves.BOSS_EVERY == 0)
    boss_wave = game.waves.build(8)
    (spawn,) = boss_wave.schedule
    assert spawn.make().number == 2


def test_boss_banner(game):
    game.waves.number = waves.BOSS_EVERY - 1
    game.waves.start_wave()
    assert game.waves.banner == "ALERTE : BOSS"


def test_boss_health_and_reward_grow():
    assert [boss_hp(n) for n in (1, 2, 3)] == [50, 75, 100]


def test_boss_enters_then_sways(game):
    boss = spawn_boss(game, entered=False)
    boss.position.y = -90
    run_boss(boss, 4)
    assert boss.entered
    xs = []
    for _ in range(round(6 / STEP)):
        boss.update(STEP, (300, 700))
        xs.append(boss.position.x)
    assert max(xs) - min(xs) > 200


def test_boss_does_not_shoot_before_it_has_entered(game):
    boss = spawn_boss(game, entered=False)
    boss.position.y = -90
    run_boss(boss, 1)
    assert len(game.enemy_bullets) == 0


def test_boss_cycles_through_its_three_patterns(game):
    boss = spawn_boss(game)
    seen = set()
    for _ in range(round(20 / STEP)):
        boss.update(STEP, (300, 700))
        seen.add(boss.pattern)
    assert seen == {0, 1, 2}
    assert len(game.enemy_bullets) > 50


def test_burst_is_a_full_ring(game):
    boss = spawn_boss(game)
    boss.pattern_time = 0.0
    boss.burst(pygame.Vector2(300, 700))
    assert len(game.enemy_bullets) == 14
    angles = sorted(round(b.velocity.as_polar()[1]) % 360 for b in game.enemy_bullets)
    assert angles[-1] - angles[0] > 300


def test_enraged_boss_fires_bigger_rings_faster(game):
    boss = spawn_boss(game)
    boss.hp = boss.max_hp // 2
    assert boss.enraged and boss.tempo < 1
    boss.pattern_time = 0.0
    boss.burst(pygame.Vector2(300, 700))
    assert len(game.enemy_bullets) == 20


def test_ramming_the_boss_hurts_only_the_player(game):
    boss = spawn_boss(game)
    boss.patterns = (lambda target: False,)  # no shots in this test
    game.player.rect.center = boss.rect.center
    game.step(STEP)
    assert boss.alive() and boss.hp == boss.max_hp
    assert game.player.lives == Player.MAX_LIVES - 1


def test_killing_the_boss_scores_and_drops_rewards(game):
    boss = spawn_boss(game, number=2)
    boss.patterns = (lambda target: False,)
    boss.hp = 1
    Bullet(boss.rect.midbottom, game.bullets)
    game.step(STEP)
    assert not boss.alive()
    assert game.score == Boss.SCORE * 2
    assert sorted(p.kind.name for p in game.powerups) == ["LIFE", "WEAPON"]


def test_boss_wave_ends_when_boss_dies(game):
    game.player.shield = 1e9
    game.waves.number = waves.BOSS_EVERY - 1
    game.waves.start_wave()
    for _ in range(round((waves.BANNER_TIME + 0.1) / STEP)):
        game.step(STEP)
    (boss,) = game.enemies
    boss.kill()
    game.step(STEP)
    assert not game.waves.active


def test_boss_bar_draws(game):
    boss = spawn_boss(game)
    boss.hp = boss.max_hp // 3
    surface = pygame.display.get_surface()
    game.draw(surface)
    assert surface.get_at((300, 100))[:3] != (0, 0, 0)  # the bar is drawn below the HUD
