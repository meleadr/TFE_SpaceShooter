"""The gameplay scene."""

import random

import pygame

from spaceshooter import assets
from spaceshooter.controls import read_input
from spaceshooter.entities import MeteorSpawner, Player
from spaceshooter.scenes.base import Scene, SceneManager
from spaceshooter.settings import HEIGHT, WIDTH

WHITE = (255, 255, 255)


class GameScene(Scene):
    def __init__(self, manager: SceneManager, rng: random.Random | None = None) -> None:
        super().__init__(manager)
        self.background = assets.tiled("backgrounds/darkPurple.png", (WIDTH, HEIGHT))
        self.bullets = pygame.sprite.Group()
        self.meteors = pygame.sprite.Group()
        self.player = Player(self.bullets)
        self.players = pygame.sprite.GroupSingle(self.player)
        self.spawner = MeteorSpawner(self.meteors, rng)
        self.score = 0
        self.game_over = False
        # Basic HUD; the real one (icons, best score) comes in M3.
        self.font = assets.font(24)
        self.big_font = assets.font(48)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        # Escape quits for now; it opens the pause menu from M4 on.
        if event.key == pygame.K_ESCAPE:
            self.manager.quit()
        elif self.game_over and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.manager.replace(GameScene(self.manager))

    def update(self, dt: float) -> None:
        if self.game_over:
            return
        self.player.input = read_input(pygame.key.get_pressed())
        self.step(dt)

    def step(self, dt: float) -> None:
        """Advance the world by one fixed step (input already applied)."""
        self.players.update(dt)
        self.bullets.update(dt)
        self.spawner.update(dt, self.score)
        self.meteors.update(dt)
        self.resolve_collisions()

    def resolve_collisions(self) -> None:
        shot = pygame.sprite.groupcollide(
            self.meteors, self.bullets, True, True, pygame.sprite.collide_circle
        )
        self.score += len(shot)

        crashed = pygame.sprite.spritecollide(
            self.player, self.meteors, False, pygame.sprite.collide_circle
        )
        for meteor in crashed:
            if self.player.hit():
                meteor.kill()
        if not self.player.has_lives:
            self.game_over = True

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, 0))
        self.meteors.draw(surface)
        self.bullets.draw(surface)
        if self.player.has_lives:
            self.players.draw(surface)
        self.draw_hud(surface)

    def draw_hud(self, surface: pygame.Surface) -> None:
        score = self.font.render(f"Score {self.score}", True, WHITE)
        surface.blit(score, (12, 12))
        lives = self.font.render(f"Vies {self.player.lives}", True, WHITE)
        surface.blit(lives, lives.get_rect(topright=(WIDTH - 12, 12)))
        if self.game_over:
            for text, font, y in (
                ("GAME OVER", self.big_font, HEIGHT / 2 - 30),
                ("Entree pour rejouer", self.font, HEIGHT / 2 + 30),
            ):
                label = font.render(text, True, WHITE)
                surface.blit(label, label.get_rect(center=(WIDTH / 2, y)))
