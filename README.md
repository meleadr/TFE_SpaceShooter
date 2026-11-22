# Space Shooter

Shoot'em up vertical en Python / [pygame-ce](https://pyga.me/).
Remaster 2026 de mon TFE de 2019 (la version d'origine est dans [`legacy/`](legacy/) et sous le tag `v2019`).

**Jouer dans le navigateur : https://meleadr.github.io/TFE_SpaceShooter/**

Détruis les météorites (les grosses se brisent en plus petites), repousse les vagues
d'ennemis (drones et canonnières qui te visent), attrape les bonus (🛡️ bouclier 4 s, ❤️ vie, ⚡ arme : tir double, triple puis en éventail)
et entre dans le top 10 (nom en 3 lettres, façon borne d'arcade). La difficulté augmente tous les 20 points.

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

Les touches (hors flèches et Espace, toujours actives) se changent dans **Commandes**
depuis l'écran titre.

**Manette** (Xbox, PlayStation, Switch Pro… branchée à chaud) : stick gauche ou croix pour
bouger, A / X / RB / RT pour tirer, Start pour la pause, A / B pour valider / revenir.

Le top 10 et les touches sont sauvegardés dans `%APPDATA%\spaceshooter\save.json` (Windows), et dans le `localStorage` du navigateur pour la version web.

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
- **v2** : déplacement 8 directions et météorites qui se brisent ✅, ennemis et vagues ✅, armes ✅, boss toutes les 4 vagues ✅, manette et touches personnalisables ✅, top 10 local ✅ → **v2.0**
- **v3** : musique, contrôles tactiles pour le mobile… (à définir)

## Crédits et licences

- Code : [MIT](LICENSE).
- Images et sons : [Space Shooter Redux](https://kenney.nl/assets/space-shooter-redux) et [Sci-fi Sounds](https://kenney.nl/assets/sci-fi-sounds) par Kenney (CC0, voir `src/spaceshooter/data/`).
- Police : [Orbitron](https://github.com/theleagueof/orbitron) (SIL OFL 1.1).
