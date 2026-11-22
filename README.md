# Space Shooter

Shoot'em up vertical en Python / [pygame-ce](https://pyga.me/).
Remaster 2026 de mon TFE de 2019 (la version d'origine est dans [`legacy/`](legacy/) et sous le tag `v2019`).

## Lancer le jeu

Prérequis : [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run spaceshooter
```

| Touche | Action |
|---|---|
| ← → / Q D / A D | Se déplacer |
| Espace / ↑ | Tirer |
| Échap | Pause / quitter |
| F11 | Plein écran |

## Développement

```sh
uv run ruff check        # lint
uv run ruff format       # formatage
uv run pytest            # tests (headless)
```

## Feuille de route

- **M0** : outillage, boucle à pas fixe, pile de scènes ✅
- **M1** : vaisseau et tir ✅
- **M2** : météorites, collisions, score, difficulté ✅
- **M3** : bonus (bouclier, vie), HUD, meilleur score ✅
- **M4** : menu, pause, game over, sons, fond défilant → **v1.0** (+ version web via pygbag)
- **v2** : déplacement 8 directions, ennemis, armes, boss, manette, top 10

## Licence

Code sous licence [MIT](LICENSE). La police est [Orbitron](https://github.com/theleagueof/orbitron) (SIL OFL 1.1). Les images et sons proviennent du pack [Space Shooter Redux de Kenney](https://kenney.nl/assets/space-shooter-redux) (CC0, voir `src/spaceshooter/data/LICENSE-kenney.txt`).
