"""The gameplay scene."""

import random

import pygame

from spaceshooter import assets, difficulty
from spaceshooter.controls import read_input
from spaceshooter.entities import (
    HitResult,
    MeteorSpawner,
    Player,
    PowerUpKind,
    PowerUpSpawner,
)
from spaceshooter.hud import WHITE, Hud
from spaceshooter.save import SaveData
from spaceshooter.scenes.base import Scene, SceneManager
from spaceshooter.settings import HEIGHT, WIDTH

GOLD = (255, 210, 90)


class GameScene(Scene):
    def __init__(
        self,
        manager: SceneManager,
        save: SaveData,
        rng: random.Random | None = None,
    ) -> None:
        super().__init__(manager)
        self.save = save
        self.rng = rng or random.Random()
        self.background = assets.tiled("backgrounds/darkPurple.png", (WIDTH, HEIGHT))
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
        self.hud = Hud()
        # Temporary game over overlay; becomes its own scene in M4.
        self.font = assets.font(24)
        self.big_font = assets.font(48)

    @property
    def level(self) -> int:
        return difficulty.level(self.score)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        # Escape quits for now; it opens the pause menu from M4 on.
        if event.key == pygame.K_ESCAPE:
            self.manager.quit()
        elif self.game_over and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.manager.replace(GameScene(self.manager, self.save))

    def update(self, dt: float) -> None:
        if self.game_over:
            return
        self.player.input = read_input(pygame.key.get_pressed())
        self.step(dt)

    def step(self, dt: float) -> None:
        """Advance the world by one fixed step (input already applied)."""
        self.players.update(dt)
        self.bullets.update(dt)
        self.meteor_spawner.update(dt, self.score)
        self.powerup_spawner.update(dt, self.player.is_hurt)
        self.meteors.update(dt)
        self.powerups.update(dt)
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
            if self.player.hit() is not HitResult.IGNORED:
                meteor.kill()

        for powerup in pygame.sprite.spritecollide(self.player, self.powerups, True):
            if powerup.kind is PowerUpKind.SHIELD:
                self.player.activate_shield()
            else:
                self.player.gain_life()

        if not self.player.has_lives:
            self.end_game()

    def end_game(self) -> None:
        self.game_over = True
        self.new_record = self.save.submit_score(self.score)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, 0))
        self.powerups.draw(surface)
        self.meteors.draw(surface)
        self.bullets.draw(surface)
        if self.player.has_lives:
            self.players.draw(surface)
            self.player.draw_shield(surface)
        self.hud.draw(surface, self.score, self.best_before, self.level, self.player)
        if self.game_over:
            self.draw_game_over(surface)

    def draw_game_over(self, surface: pygame.Surface) -> None:
        lines = [("GAME OVER", self.big_font, WHITE)]
        if self.new_record:
            lines.append(("Nouveau record !", self.font, GOLD))
        lines.append(("Entrée pour rejouer", self.font, WHITE))
        y = HEIGHT / 2 - 40
        for text, font, color in lines:
            label = font.render(text, True, color)
            surface.blit(label, label.get_rect(center=(WIDTH / 2, y)))
            y += 60
