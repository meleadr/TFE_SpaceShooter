"""Sound effects. Silently does nothing when no audio device is available."""

import logging
import random

import pygame

from spaceshooter.assets import ASSETS_DIR

log = logging.getLogger(__name__)

# Event name -> (candidate files, volume). A random candidate is played each time.
SOUNDS: dict[str, tuple[tuple[str, ...], float]] = {
    "shoot": (("sfx_laser1.ogg",), 0.25),
    "enemy_shoot": (("laserSmall_000.ogg",), 0.2),
    "explosion": (tuple(f"explosionCrunch_00{i}.ogg" for i in range(4)), 0.45),
    "player_hit": (("lowFrequency_explosion_000.ogg",), 0.8),
    "shield_up": (("sfx_shieldUp.ogg",), 0.6),
    "shield_down": (("sfx_shieldDown.ogg",), 0.6),
    "life_up": (("sfx_twoTone.ogg",), 0.6),
    "weapon_up": (("forceField_000.ogg",), 0.6),
    "game_over": (("sfx_lose.ogg",), 0.7),
    "menu_move": (("sfx_laser2.ogg",), 0.2),
    "menu_confirm": (("sfx_zap.ogg",), 0.5),
}


class Audio:
    def __init__(self) -> None:
        self.enabled = False
        self.muted = False
        self.cache: dict[str, pygame.mixer.Sound] = {}

    def init(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.enabled = True
        except pygame.error as error:
            log.warning("Audio disabled: %s", error)

    def load(self, filename: str) -> pygame.mixer.Sound:
        if filename not in self.cache:
            self.cache[filename] = pygame.mixer.Sound(ASSETS_DIR / "sounds" / filename)
        return self.cache[filename]

    def play(self, name: str) -> None:
        if not self.enabled or self.muted:
            return
        files, volume = SOUNDS[name]
        try:
            sound = self.load(random.choice(files))
        except (pygame.error, FileNotFoundError) as error:
            log.warning("Cannot play %s: %s", name, error)
            return
        sound.set_volume(volume)
        sound.play()

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        if self.muted and self.enabled:
            pygame.mixer.stop()


audio = Audio()
