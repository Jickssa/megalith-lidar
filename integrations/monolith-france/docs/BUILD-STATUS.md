# État de validation — Monolith France

## État GitHub

- Branche de travail : `feature/monolith-france-1.1.0`.
- PR #1 : ouverte, en brouillon, non fusionnée ; cible `main`.
- Aucune modification n'a été poussée sur `main`.
- Commit applicatif testé : `9049f8142e27a7d3699dfcdad36fac2e41c5355a`.
- Le code fonctionnel courant contient la validation des observations GeoJSON et les limites de stockage cumulées.

## Dernier APK téléchargé et inspecté directement

- Workflow pull request #81 : succès intégral, deux jobs verts.
- Run : https://github.com/Jickssa/megalith-lidar/actions/runs/45094996607
- Commit testé : `9049f8142e27a7d3699dfcdad36fac2e41c5355a`.
- Environnement : Temurin JDK 17, Android Platform 35, Build Tools 35.0.0.
- Commande : `./android/gradlew -p android assembleDebug --no-daemon --stacktrace --warning-mode all`.
- Installateur exécuté sur le véritable checkout Android avant Gradle.
- APK Debug : `megalith-lidar-france-debug.apk`.
- Taille : 19 008 767 octets.
- SHA-256 : `9f49ee1bb86c40ff125cf61cf9fac6064d736c16591f75749aceeba1137e7197`.
- CRC ZIP : valide pour l'archive d'artefact et l'APK.
- APK : 94 entrées, toutes les ressources UK / France / Leaflet attendues présentes.
- Sélecteur embarqué : géocodage IGN et recherche OSM uniquement ; POI IGN « mégalithe » absent.
- Le JavaScript embarqué contient les gardes de validation et de stockage GeoJSON.
- Les cinq images Leaflet embarquées sont décodables, visibles (canal alpha non vide) et à leurs dimensions attendues.
- `zipalign -c -v 4` : succès.
- `apksigner verify --verbose` : succès, signature APK v2 valide.
- Artefact GitHub Actions ID : `14782609107`.
- URL : https://github.com/Jickssa/megalith-lidar/actions/runs/45094996607/artifacts/14782609107
- Expiration annoncée : 7 décembre 2026.

## CI du commit applicatif

- Run push #80 : succès intégral.
- Run pull request #81 : succès intégral.
- Job statique :
  - validateur de paquet ;
  - syntaxe JavaScript ;
  - tests unitaires Node sur le traitement GeoJSON ;
  - syntaxe Python ;
  - fixture de régression de l'installateur.
- Job Android :
  - installation du module dans le projet Android ;
  - compilation Gradle Debug ;
  - vérification des ressources et de l'intégrité ZIP ;
  - vérifications `zipalign` et `apksigner` ;
  - dépôt APK + checksum.

## Correctifs fonctionnels apportés

- Le sélecteur ne propose pas le POI IGN « mégalithe » tant que son schéma de recherche n'est pas validé.
- Le géocodage IGN est le mode par défaut ; la recherche OSM se fait sur l'emprise cartographique.
- Le gestionnaire de recherche refuse explicitement les modes inconnus.
- Les ressources Leaflet transparentes ont été remplacées par les PNG officiels Leaflet 1.9.4 ; dimensions et alpha sont contrôlés.
- Le plafond `maxFeatures = 5000` est désormais appliqué au total local, et non uniquement à chaque fichier importé.
- Les importations GeoJSON doivent être des FeatureCollections constituées de points WGS84 valides ; longitude et latitude sont bornées.
- Les limites configurées sont utilisées pour la taille de fichier et le nombre cumulé d'observations.
- Les écritures locales sont traitées de façon transactionnelle : l'état mémoire n'est mis à jour qu'après réussite de l'écriture.
- Des tests Node couvrent les coordonnées, géométries, propriétés, tailles et limites cumulées.

## Sources Géoplateforme

- L'API de géocodage direct documentée par l'IGN est `https://data.geopf.fr/geocodage/search`.
- Le service WMTS documente GetCapabilities et GetTile, avec LAYER, STYLE, FORMAT, TILEMATRIXSET, TILEMATRIX, TILEROW et TILECOL.
- La disponibilité des flux LiDAR HD reste progressive et doit être contrôlée pour chaque emprise.

## Recette non effectuée sur appareil

La compilation et les contrôles d'archive ne remplacent pas un test fonctionnel sur téléphone ou émulateur. Restent à vérifier :
- installation, démarrage et navigation vers l'atlas britannique ;
- affichage effectif des tuiles IGN WMTS et comportement sur les emprises non couvertes ;
- géocodage IGN et requêtes Overpass depuis la WebView réelle ;
- refus / octroi des permissions et géolocalisation ;
- ajout, suppression et persistance des observations après redémarrage ;
- import GeoJSON par le sélecteur Android et export via le pont natif ;
- gestion des indisponibilités réseau, erreurs HTTP et éventuelles restrictions CORS ;
- ergonomie et performances sur un téléphone physique.

## Limites connues

- La recherche POI IGN dédiée au sous-type mégalithe reste désactivée.
- La détection IA française reste désactivée ; aucun modèle britannique n'est réutilisé comme détecteur français.
- La couverture LiDAR HD est progressive et n'est pas un inventaire archéologique.
- OSM et les catalogues patrimoniaux ne sont pas exhaustifs.
- Les services distants nécessitent une connexion ; le mode hors ligne n'est pas garanti.

## Prochaine étape

Effectuer et consigner la recette sur appareil Android, corriger les anomalies réelles et compléter la validation réseau avant de sortir la PR du brouillon. Ne pas fusionner avant cette validation.
