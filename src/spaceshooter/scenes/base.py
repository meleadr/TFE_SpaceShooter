"""Scene stack: menus, gameplay, pause and game over are all scenes."""

from __future__ import annotations

import pygame


class Scene:
    """Base class for a screen of the game.

    Only the top scene receives events and updates. An overlay scene (e.g. pause)
    is drawn on top of the scenes below it instead of replacing them.
    """

    is_overlay = False

    def __init__(self, manager: SceneManager) -> None:
        self.manager = manager

    def on_enter(self) -> None:
        """Called when the scene becomes the top of the stack."""

    def on_exit(self) -> None:
        """Called when the scene stops being the top of the stack."""

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass


class SceneManager:
    def __init__(self) -> None:
        self.stack: list[Scene] = []
        self.running = True

    @property
    def top(self) -> Scene | None:
        return self.stack[-1] if self.stack else None

    def push(self, scene: Scene) -> None:
        if self.top:
            self.top.on_exit()
        self.stack.append(scene)
        scene.on_enter()

    def pop(self) -> Scene:
        scene = self.stack.pop()
        scene.on_exit()
        if self.top:
            self.top.on_enter()
        else:
            self.running = False
        return scene

    def replace(self, scene: Scene) -> None:
        if self.stack:
            self.stack.pop().on_exit()
        self.stack.append(scene)
        scene.on_enter()

    def quit(self) -> None:
        self.running = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.top:
            self.top.handle_event(event)

    def update(self, dt: float) -> None:
        if self.top:
            self.top.update(dt)

    def visible_scenes(self) -> list[Scene]:
        """Scenes to draw, bottom to top: the topmost opaque scene and the overlays above it."""
        start = 0
        for index in range(len(self.stack) - 1, -1, -1):
            if not self.stack[index].is_overlay:
                start = index
                break
        return self.stack[start:]

    def draw(self, surface: pygame.Surface) -> None:
        for scene in self.visible_scenes():
            scene.draw(surface)
