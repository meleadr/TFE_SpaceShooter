"""Heads-up display: score, best score, level, lives and shield gauge."""

import pygame

from spaceshooter import assets
from spaceshooter.entities import Player
from spaceshooter.settings import WIDTH

WHITE = (255, 255, 255)
GREY = (170, 170, 200)
GOLD = (255, 210, 90)
SHIELD_BLUE = (80, 170, 255)
MARGIN = 12


class Hud:
    def __init__(self) -> None:
        self.font = assets.font(24)
        self.small_font = assets.font(16)
        self.life_icon = assets.image("UI/playerLife1_blue.png")
        self.shield_icon = assets.image("Power-ups/powerupBlue_shield.png", 0.7)

    def draw(
        self, surface: pygame.Surface, score: int, best: int, level: int, player: Player
    ) -> None:
        surface.blit(self.font.render(f"Score {score}", True, WHITE), (MARGIN, MARGIN))
        surface.blit(
            self.small_font.render(f"Record {max(best, score)}  -  Niveau {level + 1}", True, GREY),
            (MARGIN, MARGIN + 32),
        )
        self.draw_weapon(surface, player.weapon)
        self.draw_lives(surface, player.lives)
        if player.shield > 0 and player.has_lives:
            self.draw_shield_gauge(surface, player.shield / Player.SHIELD_TIME)

    def draw_weapon(self, surface: pygame.Surface, level: int) -> None:
        label = self.small_font.render("Arme", True, GREY)
        surface.blit(label, (MARGIN, MARGIN + 54))
        for i in range(Player.MAX_WEAPON):
            pip = pygame.Rect(MARGIN + label.get_width() + 10 + i * 14, MARGIN + 58, 10, 10)
            if i < level:
                pygame.draw.rect(surface, GOLD, pip, border_radius=2)
            else:
                pygame.draw.rect(surface, GREY, pip, width=1, border_radius=2)

    def draw_lives(self, surface: pygame.Surface, lives: int) -> None:
        width = self.life_icon.get_width()
        for i in range(lives):
            x = WIDTH - MARGIN - (i + 1) * width - i * 6
            surface.blit(self.life_icon, (x, MARGIN + 4))

    def draw_shield_gauge(self, surface: pygame.Surface, ratio: float) -> None:
        icon_rect = self.shield_icon.get_rect(topright=(WIDTH - MARGIN - 110, MARGIN + 40))
        surface.blit(self.shield_icon, icon_rect)
        bar = pygame.Rect(0, 0, 100, 8)
        bar.midleft = (icon_rect.right + 8, icon_rect.centery)
        pygame.draw.rect(surface, GREY, bar, width=1, border_radius=4)
        fill = bar.inflate(-2, -2)
        fill.width = round(fill.width * max(min(ratio, 1.0), 0.0))
        if fill.width > 0:
            pygame.draw.rect(surface, SHIELD_BLUE, fill, border_radius=3)
