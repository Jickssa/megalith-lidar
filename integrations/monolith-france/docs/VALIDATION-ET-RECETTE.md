# Navigation 1.2.2 — clarification après retour utilisateur

## Architecture rectifiée

- Le sélecteur commun expose des accès directs aux deux véritables cartes : `/assets/web/france/web/index.html` (Atlas France) et `/assets/web/index.html` (Atlas britannique).
- `france-home.html` et `uk-home.html` sont explicitement des pages de présentation, pas les Atlas cartographiques.
- L'Atlas UK conserve le lien retour au sélecteur et expose aussi un accès « UK Atlas ».
- L'Atlas France renvoie directement à l'Atlas britannique via sa barre d'en-tête.

## Constat de rétro-ingénierie

Le dépôt amont contient un seul document HTML racine, `index.html`, qui est l'interface cartographique UK complète. La navigation précédente envoyait le sélecteur vers `uk-home.html`, puis présentait ce dernier comme l'Atlas. La correction 1.2.2 rétablit le lien principal direct vers la carte UK. Le module français `france/web/index.html` est lui aussi accessible directement depuis le sélecteur.

## Tests CI

- Sélecteur → Atlas France.
- Sélecteur → Atlas britannique.
- Introduction France → Atlas France.
- Introduction UK → Atlas UK.
- Atlas UK → sélecteur.
- Atlas France → Atlas UK.

Tests physiques : non exécutés faute d'appareil.

---

