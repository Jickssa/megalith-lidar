# Validation 1.2.3 — navigation et cache diagnostic

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


## Contrôles ajoutés en 1.2.3

- Sélecteur principal : la destination UK est explicitement libellée « Atlas UK » et conserve la cible réelle `/assets/web/index.html`.
- Atlas UK : le lien « Choose atlas » revient au sélecteur ; le lien ajouté ouvre réellement l’Atlas France. Aucun lien « UK Atlas » ne recharge la page courante.
- La page d’introduction UK est en français (`lang="fr"`). L’interface cartographique UK historique reste en anglais : elle n’a pas été traduite dans ce lot.
- Téléchargement de diagnostics : réponse limitée à 8 Mio, MIME `image/png`, signature PNG contrôlée, redirections désactivées.
- Cache diagnostics : plafond de 64 Mio et 24 PNG, expiration après 30 jours, suppression des fichiers temporaires orphelins.
- Les contrats sont contrôlés par le validateur et la fixture d’installation ; la compilation Gradle CI contrôle la syntaxe Kotlin.

La recette physique sur appareil Android et la comparaison de certificat entre APK de production et APK Debug restent à effectuer.
