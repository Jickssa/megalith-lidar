# Audit de recette et validation — Monolith France 1.2.1

## Environnement de test

- APK originale et APK Debug 1.2.0 disponibles et inspectées directement.
- Aucun appareil Android ni émulateur exposé dans l'environnement : `adb` absent et aucun device accessible. Aucune recette tactile n'est revendiquée.
- SHA-256 APK originale : `cf6362d6c5513c08740f2b0f58ac3178f29b11f0584117a2b3bd2911d6bdd3dd`.
- SHA-256 APK Debug 1.2.0 : `5e7b1cc3c6b2361e883c41408d59c6b7fd8e4030af4e3ce4a090d84095071022`.

## Constats reproductibles sur APK 1.2.0

- Les deux APK ont le même applicationId : `uk.megalith.lidar`.
- APK originale : 41 entrées, 18 assets Web, une seule page HTML `assets/web/index.html`, démarrage DEX sur cette page.
- APK finale 1.2.0 : 97 entrées, 46 assets Web, cinq pages attendues, démarrage DEX sur `assets/web/atlas-home.html`.
- Le hash de l'index britannique source est différent parce que la copie APK reçoit exactement un lien « Choose atlas ». Après retrait de cette insertion, son HTML est identique à l'original.
- Les références locales des cinq pages se résolvent dans le paquet.
- Les identifiants WMTS IGN pour MNT, MNS, MNH et Plan IGN v2 correspondent aux catalogues/documentations IGN consultés.
- Les fichiers de données britanniques ne sont pas tous byte-identiques entre les deux APK : le préparateur actuel compact/déduplique les GeoJSON et régénère des exports OsmAnd/GPX. Les effectifs du survey_summary diffèrent aussi (ancienne version : 28 379 carrés terminés / 113 500 km² ; version embarquée : 35 036 / 140 128 km²). Ce changement correspond à une version de données plus récente et au mécanisme de compactage ; la recette fonctionnelle des tableaux et filtres reste nécessaire.

## Correctifs 1.2.1

- Pont d'export natif : limite 25 Mio, MIME restreints, écriture asynchrone, noms de fichiers temporaires uniques.
- File chooser : normalisation des acceptTypes Android.
- WebView : restriction des routes appassets et blocage des schémas non pris en charge.
- Import GeoJSON : validation extension/MIME avant lecture.
- Cibles tactiles et CSS paysage.

## CI et compilation

Les résultats de CI 1.2.1 seront ajoutés après le commit. Les contrôles 1.2.0 précédents étaient verts sur push #120 et PR #121.

## Recette physique à faire

La procédure ADB et la liste des scénarios sont fournies dans le rapport de cette reprise. L'installation par-dessus l'application 3.2.0 doit d'abord vérifier la signature. Ne pas désinstaller l'application en production sans sauvegarde des données locales.

## Limites résiduelles

- Tests en direct des couches WMTS, géocodeur IGN et Overpass non exécutés depuis Android.
- Pas de test de géolocalisation/permis, de partage via FileProvider ni de stockage WebView sur appareil.
- Nettoyage et plafond de taille de cache des PNG de diagnostic à prévoir.
- Gestion Android predictive back à tester.
- Compatibilité de signature entre l'APK originale et la Debug non établie par cette analyse.

