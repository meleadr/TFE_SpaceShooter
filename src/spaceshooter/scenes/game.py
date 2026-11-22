"""The gameplay scene."""

import random

import pygame

from spaceshooter import difficulty
from spaceshooter.audio import audio
from spaceshooter.controls import PlayerInput, read_input
from spaceshooter.effects import FIRE_COLORS, ROCK_COLORS, Particles, Starfield
from spaceshooter.entities import (
    Boss,
    Gunship,
    HitResult,
    MeteorSpawner,
    Player,
    PowerUp,
    PowerUpKind,
    PowerUpSpawner,
)
from spaceshooter.hud import Hud
from spaceshooter.save import SaveData
from spaceshooter.scenes.base import Scene, SceneManager
from spaceshooter.scenes.gameover import GameOverScene
from spaceshooter.scenes.pause import PauseScene
from spaceshooter.settings import HEIGHT, WIDTH
from spaceshooter.ui import GOLD, draw_text
from spaceshooter.waves import WaveDirector

PAUSE_KEYS = (pygame.K_ESCAPE, pygame.K_p)
MAXED_WEAPON_BONUS = 5  # points for a weapon pickup when already at max
ENEMY_COLORS = [(255, 90, 60), (255, 170, 60), (255, 240, 180), (140, 220, 120)]


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
        self.enemies = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.player = Player(self.bullets)
        self.players = pygame.sprite.GroupSingle(self.player)
        self.meteor_spawner = MeteorSpawner(self.meteors, self.rng)
        self.powerup_spawner = PowerUpSpawner(self.powerups, self.rng)
        self.waves = WaveDirector(self.enemies, self.enemy_bullets, self.rng)
        self.score = 0
        self.best_before = save.best_score
        self.game_over = False
        self.new_record = False
        self.game_over_timer = 0.0
        self.time = 0.0
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
            self.player.input = PlayerInput()
        else:
            self.player.input = read_input(pygame.key.get_pressed())
        self.step(dt)

    def step(self, dt: float) -> None:
        """Advance the world by one fixed step (input already applied)."""
        self.time += dt
        self.starfield.update(dt)
        self.particles.update(dt)
        if not self.game_over:
            self.players.update(dt)
            self.waves.update(dt)
            if not self.waves.active:  # meteors pause while an enemy wave is on
                self.meteor_spawner.update(dt, self.score)
            self.powerup_spawner.update(dt, self.player.is_hurt)
        self.bullets.update(dt)
        self.meteors.update(dt)
        self.powerups.update(dt)
        self.enemies.update(dt, self.player.rect.center)
        self.enemy_bullets.update(dt)
        if self.game_over:
            self.game_over_timer += dt
            if self.game_over_timer >= self.GAME_OVER_DELAY and self.manager.top is self:
                self.manager.push(
                    GameOverScene(self.manager, self.save, self.score, self.new_record)
                )
        else:
            self.resolve_collisions()

    def resolve_collisions(self) -> None:
        self.shoot_meteors()
        self.shoot_enemies()
        for group, colors in (
            (self.meteors, ROCK_COLORS),
            (self.enemies, ENEMY_COLORS),
            (self.enemy_bullets, FIRE_COLORS),
        ):
            for sprite in pygame.sprite.spritecollide(
                self.player, group, False, pygame.sprite.collide_circle
            ):
                self.crash(sprite, colors)
        self.collect_powerups()
        if not self.player.has_lives:
            self.end_game()

    def shoot_meteors(self) -> None:
        shot = pygame.sprite.groupcollide(
            self.meteors, self.bullets, True, True, pygame.sprite.collide_circle
        )
        for meteor in shot:
            meteor.split(self.rng, self.meteors)
            self.particles.burst(meteor.rect.center, meteor.size.particles, ROCK_COLORS)
            audio.play("explosion")
        self.score += len(shot)

    def shoot_enemies(self) -> None:
        hits = pygame.sprite.groupcollide(
            self.enemies, self.bullets, False, True, pygame.sprite.collide_circle
        )
        for enemy, bullets in hits.items():
            for _ in bullets:
                if not enemy.alive():
                    break
                if enemy.damage():
                    self.destroyed(enemy)
                else:
                    self.particles.burst(enemy.rect.center, 6, FIRE_COLORS, speed=(40, 120))

    def destroyed(self, enemy: pygame.sprite.Sprite) -> None:
        self.score += enemy.points
        x, y = enemy.rect.center
        if isinstance(enemy, Boss):
            # Big finale and a reward: a life and a weapon upgrade.
            for _ in range(4):
                center = (x + self.rng.uniform(-60, 60), y + self.rng.uniform(-50, 50))
                self.particles.burst(center, 50, ENEMY_COLORS, speed=(80, 360), size=(3, 9))
            PowerUp(PowerUpKind.LIFE, x - 40, self.powerups, y=y)
            PowerUp(PowerUpKind.WEAPON, x + 40, self.powerups, y=y)
            audio.play("player_hit")
        else:
            if isinstance(enemy, Gunship):  # gunships always drop a weapon upgrade
                PowerUp(PowerUpKind.WEAPON, x, self.powerups, y=y)
            self.particles.burst(enemy.rect.center, 36, ENEMY_COLORS, size=(3, 7))
        audio.play("explosion")

    def crash(self, sprite: pygame.sprite.Sprite, colors: list[tuple[int, int, int]]) -> None:
        """Something hit the player ship: meteor, enemy ship or enemy shot."""
        result = self.player.hit()
        if result is HitResult.IGNORED:
            return
        if not isinstance(sprite, Boss):  # the boss shrugs off a ram
            sprite.kill()  # destroyed outright: no fragments, no score
        self.particles.burst(sprite.rect.center, 16, colors)
        if result is HitResult.DAMAGED:
            self.particles.burst(self.player.rect.center, 30, FIRE_COLORS, size=(3, 6))
            audio.play("player_hit")
        else:
            audio.play("explosion")

    def collect_powerups(self) -> None:
        for powerup in pygame.sprite.spritecollide(self.player, self.powerups, True):
            if powerup.kind is PowerUpKind.SHIELD:
                self.player.activate_shield()
                audio.play("shield_up")
            elif powerup.kind is PowerUpKind.WEAPON:
                if not self.player.upgrade_weapon():
                    self.score += MAXED_WEAPON_BONUS
                audio.play("weapon_up")
            else:
                self.player.gain_life()
                audio.play("life_up")

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
        self.enemies.draw(surface)
        self.bullets.draw(surface)
        self.enemy_bullets.draw(surface)
        if not self.game_over:
            self.players.draw(surface)
            self.player.draw_shield(surface)
        self.particles.draw(surface)
        self.hud.draw(surface, self.score, self.best_before, self.level, self.player)
        for enemy in self.enemies:
            if isinstance(enemy, Boss):
                self.hud.draw_boss_bar(surface, enemy.hp / enemy.max_hp)
        banner = self.waves.banner
        if banner and int(self.time * 4) % 2 == 0:  # blinks twice a second
            draw_text(surface, banner, 48, (WIDTH / 2, HEIGHT * 0.4), GOLD)
