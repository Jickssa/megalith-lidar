# Validation et recette — Monolith France 1.1.3

## Routes et invariants

- Point de démarrage Android : `/assets/web/atlas-home.html`.
- Destination France : `/assets/web/france/web/index.html`.
- Destination Royaume-Uni : `/assets/web/index.html`.
- Le fichier britannique historique doit rester strictement inchangé lors de la génération des assets.
- L'Atlas France doit proposer un retour vers `/assets/web/atlas-home.html`.

## CI

- Runs #92/#93 : échec du fixture sur l'assertion de l'accueil ; Gradle a été ignoré.
- Runs #94/#95 : échec du validateur, qui bloquait l'URL commune.
- Run push #96 : validation statique, syntaxe JS, tests Node et fixture installateur réussis.
- Compilation Android du run #96 : en attente au dernier point de contrôle ; à vérifier à nouveau.
- Le résultat PR et le build Android de la tête finale doivent être vérifiés avant livraison.

## Tests du fixture

La fixture contrôle :
- remplacement START_URL depuis l'ancienne route UK ou France ;
- génération de `atlas-home.html` après le nettoyage des assets ;
- absence d'écrasement de l'index britannique ;
- présence des deux routes dans l'accueil ;
- retour vers l'accueil et accès UK depuis l'Atlas France ;
- réinstallation et génération répétée des assets.

## APK de référence précédente

Run PR #89, commit antérieur sans accueil commun :
- taille : 19 010 059 octets ;
- SHA-256 : `8c6de9c70e0a6c5da85f7c1818c98ddffa2ddf70320c04550529b540b478bcb1`;
- artefact ID : `14783575119`.
Ne pas utiliser cette APK pour valider la navigation 1.1.3.

## Recette manuelle sur téléphone

1. Démarrer : l'écran « Choisir un atlas » apparaît.
2. Ouvrir Atlas France : la carte France apparaît.
3. Revenir par « Choisir un atlas » : l'écran commun réapparaît.
4. Ouvrir l'Atlas britannique : son index et ses données doivent charger.
5. Depuis France, utiliser le lien direct vers le Royaume-Uni.
6. Utiliser le retour arrière Android et vérifier l'absence de boucle ou écran blanc.
7. Vérifier les fonctions cartographiques des deux atlas.
8. Tester séparément WMTS LiDAR, IGN géocodage, Overpass, géolocalisation, observations, persistance, import/export et annulation du sélecteur.
