"""The gameplay scene."""

import random

import pygame

from spaceshooter import difficulty
from spaceshooter.audio import audio
from spaceshooter.controls import PlayerInput, read_input
from spaceshooter.effects import FIRE_COLORS, ROCK_COLORS, Particles, Starfield
from spaceshooter.entities import (
    HitResult,
    MeteorSpawner,
    Player,
    PowerUpKind,
    PowerUpSpawner,
)
from spaceshooter.hud import Hud
from spaceshooter.save import SaveData
from spaceshooter.scenes.base import Scene, SceneManager
from spaceshooter.scenes.gameover import GameOverScene
from spaceshooter.scenes.pause import PauseScene

PAUSE_KEYS = (pygame.K_ESCAPE, pygame.K_p)


class GameScene(Scene):
    GAME_OVER_DELAY = 1.2  # seconds to watch the ship explode before the game over screen

    def __init__(
        self,
        manager: SceneManager,
        save: SaveData,
        rng: random.Random | None = None,
    ) -> None:
        super().__init__(manager)
        self.save = save
        self.rng = rng or random.Random()
        self.starfield = Starfield(self.rng)
        self.particles = Particles(self.rng)
        self.bullets = pygame.sprite.Group()
        self.meteors = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player(self.bullets)
        self.players = pygame.sprite.GroupSingle(self.player)
        self.meteor_spawner = MeteorSpawner(self.meteors, self.rng)
        self.powerup_spawner = PowerUpSpawner(self.powerups, self.rng)
        self.score = 0
        self.best_before = save.best_score
        self.game_over = False
        self.new_record = False
        self.game_over_timer = 0.0
        self.hud = Hud()

    @property
    def level(self) -> int:
        return difficulty.level(self.score)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.game_over:
            return
        pause = event.type == pygame.KEYDOWN and event.key in PAUSE_KEYS
        if pause or event.type == pygame.WINDOWFOCUSLOST:
            self.manager.push(PauseScene(self.manager, self.save))

    def update(self, dt: float) -> None:
        if self.game_over:
            self.player.input = PlayerInput(direction=0, fire=False)
        else:
            self.player.input = read_input(pygame.key.get_pressed())
        self.step(dt)

    def step(self, dt: float) -> None:
        """Advance the world by one fixed step (input already applied)."""
        self.starfield.update(dt)
        self.particles.update(dt)
        if not self.game_over:
            self.players.update(dt)
            self.meteor_spawner.update(dt, self.score)
            self.powerup_spawner.update(dt, self.player.is_hurt)
        self.bullets.update(dt)
        self.meteors.update(dt)
        self.powerups.update(dt)
        if self.game_over:
            self.game_over_timer += dt
            if self.game_over_timer >= self.GAME_OVER_DELAY and self.manager.top is self:
                self.manager.push(
                    GameOverScene(self.manager, self.save, self.score, self.new_record)
                )
        else:
            self.resolve_collisions()

    def resolve_collisions(self) -> None:
        shot = pygame.sprite.groupcollide(
            self.meteors, self.bullets, True, True, pygame.sprite.collide_circle
        )
        for meteor in shot:
            self.particles.burst(meteor.rect.center, 24, ROCK_COLORS)
            audio.play("explosion")
        self.score += len(shot)

        crashed = pygame.sprite.spritecollide(
            self.player, self.meteors, False, pygame.sprite.collide_circle
        )
        for meteor in crashed:
            result = self.player.hit()
            if result is HitResult.IGNORED:
                continue
            meteor.kill()
            self.particles.burst(meteor.rect.center, 24, ROCK_COLORS)
            if result is HitResult.DAMAGED:
                self.particles.burst(self.player.rect.center, 30, FIRE_COLORS, size=(3, 6))
                audio.play("player_hit")
            else:
                audio.play("explosion")

        for powerup in pygame.sprite.spritecollide(self.player, self.powerups, True):
            if powerup.kind is PowerUpKind.SHIELD:
                self.player.activate_shield()
                audio.play("shield_up")
            else:
                self.player.gain_life()
                audio.play("life_up")

        if not self.player.has_lives:
            self.end_game()

    def end_game(self) -> None:
        self.game_over = True
        self.new_record = self.save.submit_score(self.score)
        self.particles.burst(
            self.player.rect.center, 90, FIRE_COLORS, speed=(80, 380), size=(3, 8), life=(0.6, 1.4)
        )
        audio.play("game_over")

    def draw(self, surface: pygame.Surface) -> None:
        self.starfield.draw(surface)
        self.powerups.draw(surface)
        self.meteors.draw(surface)
        self.bullets.draw(surface)
        if not self.game_over:
            self.players.draw(surface)
            self.player.draw_shield(surface)
        self.particles.draw(surface)
        self.hud.draw(surface, self.score, self.best_before, self.level, self.player)
