"""Window, main loop and global keys."""

import asyncio

import pygame

from spaceshooter.audio import audio
from spaceshooter.save import SaveData
from spaceshooter.scenes import SceneManager
from spaceshooter.scenes.title import TitleScene
from spaceshooter.settings import FPS, HEIGHT, STEP, TITLE, WIDTH
from spaceshooter.timing import FixedStep


class App:
    def __init__(self, save: SaveData | None = None) -> None:
        pygame.mixer.pre_init(44100, -16, 2, 512)  # small buffer: low latency for sound effects
        pygame.init()
        audio.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.stepper = FixedStep()
        self.scenes = SceneManager()
        self.save = save or SaveData()
        self.scenes.push(TitleScene(self.scenes, self.save))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.scenes.quit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            audio.toggle_mute()
        else:
            self.scenes.handle_event(event)

    def frame(self, frame_time: float) -> None:
        """Process one rendered frame: events, fixed updates, drawing."""
        for event in pygame.event.get():
            self.handle_event(event)
        for _ in range(self.stepper.advance(frame_time)):
            self.scenes.update(STEP)
        self.scenes.draw(self.screen)
        pygame.display.flip()

    async def run(self) -> None:
        # Async so the same loop runs in the browser through pygbag.
        while self.scenes.running:
            self.frame(self.clock.tick(FPS) / 1000)
            await asyncio.sleep(0)
        pygame.quit()
