import pygame

from spaceshooter.app import App
from spaceshooter.scenes import Scene, SceneManager


class Recorder(Scene):
    def __init__(self, manager, name, overlay=False):
        super().__init__(manager)
        self.name = name
        self.is_overlay = overlay
        self.log: list[str] = []
        self.updates = 0

    def on_enter(self):
        self.log.append("enter")

    def on_exit(self):
        self.log.append("exit")

    def update(self, dt):
        self.updates += 1


def test_only_top_scene_updates():
    manager = SceneManager()
    bottom, top = Recorder(manager, "bottom"), Recorder(manager, "top")
    manager.push(bottom)
    manager.push(top)
    manager.update(0.016)
    assert (bottom.updates, top.updates) == (0, 1)


def test_pop_resumes_previous_scene_and_empty_stack_stops():
    manager = SceneManager()
    bottom, top = Recorder(manager, "bottom"), Recorder(manager, "top")
    manager.push(bottom)
    manager.push(top)
    manager.pop()
    assert bottom.log == ["enter", "exit", "enter"]
    assert manager.running
    manager.pop()
    assert not manager.running


def test_overlay_draws_over_the_scene_below():
    manager = SceneManager()
    under, game, pause = (
        Recorder(manager, "under"),
        Recorder(manager, "game"),
        Recorder(manager, "pause", overlay=True),
    )
    for scene in (under, game, pause):
        manager.push(scene)
    assert [s.name for s in manager.visible_scenes()] == ["game", "pause"]


def test_app_runs_frames_headless_and_quits():
    app = App()
    for _ in range(5):
        app.frame(1 / 60)
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    app.frame(1 / 60)
    assert not app.scenes.running
    pygame.quit()
