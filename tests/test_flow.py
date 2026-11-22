"""Navigation between title, game, pause and game over screens."""

import pygame
import pytest

from spaceshooter.effects import Particles, Starfield
from spaceshooter.save import SaveData
from spaceshooter.scenes import SceneManager
from spaceshooter.scenes.game import GameScene
from spaceshooter.scenes.gameover import GameOverScene
from spaceshooter.scenes.pause import PauseScene
from spaceshooter.scenes.title import TitleScene
from spaceshooter.settings import HEIGHT, WIDTH


def press(scene, key):
    scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))


@pytest.fixture
def manager():
    return SceneManager()


@pytest.fixture
def save(tmp_path):
    return SaveData(tmp_path / "save.json")


def test_title_play_starts_a_game(display, manager, save):
    manager.push(TitleScene(manager, save))
    press(manager.top, pygame.K_RETURN)
    assert [type(s) for s in manager.stack] == [GameScene]


def test_title_quit_option(display, manager, save):
    manager.push(TitleScene(manager, save))
    press(manager.top, pygame.K_UP)  # wraps around to the last option
    press(manager.top, pygame.K_RETURN)
    assert not manager.running


def test_pause_resume_and_back_to_title(display, manager, save):
    manager.push(GameScene(manager, save))
    press(manager.top, pygame.K_p)
    press(manager.top, pygame.K_p)
    assert [type(s) for s in manager.stack] == [GameScene]

    press(manager.top, pygame.K_ESCAPE)
    press(manager.top, pygame.K_DOWN)
    press(manager.top, pygame.K_RETURN)
    assert [type(s) for s in manager.stack] == [TitleScene]


def test_paused_game_does_not_advance(display, manager, save):
    game = GameScene(manager, save)
    manager.push(game)
    press(game, pygame.K_p)
    before = game.starfield.offset
    manager.update(1.0)
    assert game.starfield.offset == before


@pytest.mark.parametrize(("moves", "expected"), [(0, GameScene), (1, TitleScene)])
def test_game_over_menu(display, manager, save, moves, expected):
    manager.push(GameScene(manager, save))
    over = GameOverScene(manager, save, score=5, new_record=False)
    manager.push(over)
    press(over, pygame.K_RETURN)  # ignored: too early, could be a held fire key
    assert manager.top is over

    manager.update(GameOverScene.INPUT_DELAY)
    for _ in range(moves):
        press(over, pygame.K_DOWN)
    press(over, pygame.K_RETURN)
    assert [type(s) for s in manager.stack] == [expected]


def test_every_scene_draws(display, manager, save):
    screen = pygame.display.get_surface()
    game = GameScene(manager, save)
    for scene in (
        TitleScene(manager, save),
        game,
        PauseScene(manager, save),
        GameOverScene(manager, save, 3, True),
    ):
        scene.update(0.1)
        scene.draw(screen)


def test_particles_fade_out():
    particles = Particles()
    particles.burst((100, 100), 20, [(255, 0, 0)], life=(0.2, 0.5))
    assert len(particles) == 20
    for _ in range(40):
        particles.update(1 / 60)
    assert len(particles) == 0


def test_starfield_stars_stay_on_screen(display):
    starfield = Starfield()
    for _ in range(600):
        starfield.update(1 / 60)
    for layer in starfield.stars:
        for star in layer:
            assert 0 <= star.x <= WIDTH and 0 <= star.y <= HEIGHT
