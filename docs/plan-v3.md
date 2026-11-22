# Plan de la v3

Décidé le 22/11/2026, après la sortie de la v2.0.0. Objectif : une version de finition et
jouable sur mobile, avant d'ajouter du contenu.

Une branche par fonctionnalité, dans cet ordre, puis tag `v3.0.0`.

## 1. Écran Options et musique

- 3 pistes chiptune en boucle (menu, jeu, boss), avec fondus enchaînés.
- Source : Juhani Junkala sur OpenGameArt, « 5 Chiptunes (Action) » pour le menu et le jeu,
  « Boss Fight » de « 4 Chiptunes (Adventure) » pour le boss. Licence CC0 à vérifier sur
  chaque page au téléchargement, sinon on prend d'autres pistes CC0.
- Écran **Options**, qui remplace « Commandes » dans le menu titre :
  - volume de la musique (0 à 10, 6 par défaut) et des effets (0 à 10, 8 par défaut) ;
  - plein écran (PC seulement) ;
  - tremblements d'écran activés ou non ;
  - accès à l'écran Commandes.
- Tout est sauvegardé. La touche M coupe toujours tous les sons d'un coup.

## 2. Ressenti

- Tremblements d'écran : vaisseau touché, mort du boss, et un peu sur les grosses météorites.
- Courts arrêts sur image (environ 50 ms) à la mort du boss et à la perte d'une vie.
- Points flottants (« +30 ») là où un ennemi est détruit.

## 3. Combo

- Chaque ennemi ou météorite détruit allonge la chaîne.
- Multiplicateur : ×2 à 10 destructions, ×3 à 25, ×4 à 50 (maximum).
- Retour à ×1 quand on perd une vie, pas quand le bouclier absorbe le coup.
- Il s'applique à tous les points et s'affiche dans le HUD.
- La difficulté se calcule sur les points **sans** multiplicateur : le combo récompense sans punir.

## 4. Boss variés

Trois boss qui tournent, chacun avec son sprite, sa couleur et une attaque signature :

1. le boss actuel (anneaux, salves visées, spirale) ;
2. des murs de tirs avec un trou à trouver ;
3. il lance des drones et des tirs à tête chercheuse lente.

Après le 3e, le cycle recommence, avec plus de vie et des tirs plus rapides.

## 5. Contrôles tactiles

- Glisser relatif : le doigt se pose n'importe où et le vaisseau suit son mouvement.
- Tir automatique tant que le doigt est posé.
- Menus touchables (et cliquables à la souris sur PC).
- Bouton pause en haut à droite, uniquement sur écran tactile.
- Saisie du nom avec des flèches touchables et un bouton OK.

## Plus tard

- Peut-être pour une v4 : nouveaux ennemis (kamikaze, mines), modes de difficulté.
- Écartés : classement en ligne (demande un serveur), coop locale à 2 joueurs.
