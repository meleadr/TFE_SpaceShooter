# Space Shooter

Shoot'em up vertical en Python / [pygame-ce](https://pyga.me/).
Remaster 2026 de mon TFE de 2019 (la version d'origine est dans [`legacy/`](legacy/) et sous le tag `v2019`).

**Jouer dans le navigateur : https://meleadr.github.io/TFE_SpaceShooter/**

Détruis les météorites (les grosses se brisent en plus petites), repousse les vagues
d'ennemis (drones et canonnières qui te visent), attrape les bonus (🛡️ bouclier 4 s, ❤️ vie, ⚡ arme : tir double, triple puis en éventail)
et bats ton record. La difficulté augmente tous les 20 points.

## Lancer le jeu

Prérequis : [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run spaceshooter
```

| Touche | Action |
|---|---|
| Flèches / ZQSD / WASD | Se déplacer (8 directions) |
| Espace | Tirer (maintenir pour tir automatique) |
| ↑ ↓ + Entrée | Naviguer dans les menus |
| Échap / P | Pause |
| M | Couper / remettre le son |
| F11 | Plein écran |

Le record est sauvegardé dans `%APPDATA%\spaceshooter\save.json` (Windows).

## Développement

```sh
uv run ruff check        # lint
uv run ruff format       # formatage
uv run pytest            # tests (headless)
uv run python -m pygbag --template web/template.tmpl src   # version web sur http://localhost:8000
```

À chaque push sur `main`, la CI lance lint + tests, et la version web est publiée sur GitHub Pages.

## Feuille de route

- **M0** : outillage, boucle à pas fixe, pile de scènes ✅
- **M1** : vaisseau et tir ✅
- **M2** : météorites, collisions, score, difficulté ✅
- **M3** : bonus (bouclier, vie), HUD, meilleur score ✅
- **M4** : menu, pause, game over, sons, explosions, fond défilant, version web ✅ → **v1.0**
- **v2** : déplacement 8 directions et météorites qui se brisent ✅, ennemis et vagues ✅, armes ✅, boss, manette, top 10

## Crédits et licences

- Code : [MIT](LICENSE).
- Images et sons : [Space Shooter Redux](https://kenney.nl/assets/space-shooter-redux) et [Sci-fi Sounds](https://kenney.nl/assets/sci-fi-sounds) par Kenney (CC0, voir `src/spaceshooter/data/`).
- Police : [Orbitron](https://github.com/theleagueof/orbitron) (SIL OFL 1.1).
