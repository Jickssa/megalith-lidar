# État de validation — Monolith France

## État GitHub

- Branche de travail : `feature/monolith-france-1.1.0`.
- PR #1 : ouverte, en brouillon, non fusionnée ; cible `main`.
- Aucune modification n'a été poussée sur `main`.
- Tête applicative et installateur testée : `fd1d68e2e49c04f771db813d61db9cde489231f1`.
- Le commit documentaire suivant, s'il existe, ne doit pas être confondu avec le commit du code embarqué dans l'APK.

## Dernier APK téléchargé et inspecté directement

- Workflow pull request #89 : succès intégral, deux jobs verts.
- Run : https://github.com/Jickssa/megalith-lidar/actions/runs/45095513607
- Commit testé : `fd1d68e2e49c04f771db813d61db9cde489231f1`.
- Environnement : Temurin JDK 17, Android Platform 35, Build Tools 35.0.0.
- Commande : `./android/gradlew -p android assembleDebug --no-daemon --stacktrace --warning-mode all`.
- L'installateur mis à jour a été exécuté sur le véritable checkout Android avant Gradle.
- APK Debug : `megalith-lidar-france-debug.apk`.
- Taille : 19 010 059 octets.
- SHA-256 : `8c6de9c70e0a6c5da85f7c1818c98ddffa2ddf70320c04550529b540b478bcb1`.
- Le checksum contenu dans l'artefact GitHub correspond au SHA-256 recalculé après téléchargement.
- Archive d'artefact et ZIP interne de l'APK : CRC valides.
- APK : 94 entrées ; assets UK, France, Leaflet et les cinq images Leaflet attendues présents.
- Sélecteur embarqué : géocodage IGN et recherche OSM uniquement ; POI IGN « mégalithe » absent.
- Le JavaScript embarqué contient les validations GeoJSON, les plafonds de stockage et les gardes cumulés.
- Les cinq images Leaflet sont décodables, visibles (canal alpha non vide) et aux dimensions attendues.
- `zipalign -c -v 4` : succès.
- `apksigner verify --verbose` : succès, signature APK v2 valide.
- Artefact GitHub Actions ID : `14783575119`.
- URL : https://github.com/Jickssa/megalith-lidar/actions/runs/45095513607/artifacts/14783575119
- Expiration annoncée : 7 décembre 2026.

## CI du commit `fd1d68e`

- Run push #88 : jobs statique et Android réussis.
- Run pull request #89 : succès intégral.
- Job statique :
  - validation du paquet ;
  - syntaxe JavaScript ;
  - tests unitaires Node sur les observations GeoJSON ;
  - syntaxe Python ;
  - fixture de régression installateur, incluant le callback du sélecteur Android.
- Job Android :
  - installation du module dans le projet Android ;
  - compilation Gradle Debug ;
  - vérification des ressources et de l'intégrité ZIP ;
  - contrôles `zipalign` et `apksigner` ;
  - dépôt de l'APK et du checksum.

### Historique transparent des échecs intermédiaires

Les runs #84 à #87 ont échoué dans le test de régression de l'installateur, pas dans Gradle : le faux Activity du fixture ne reproduisait pas le nom exact de la méthode Android, puis l'assertion du retour à la ligne comportait un échappement incorrect. Ces deux défauts du test ont été corrigés. Les runs #88 et #89 ont ensuite passé le test statique complet et la compilation Android.

## Correctifs applicatifs et Android apportés

- Le sélecteur ne propose pas le POI IGN « mégalithe » tant que son schéma de recherche n'est pas validé.
- Le géocodage IGN est le mode par défaut ; la recherche OSM se fait sur l'emprise cartographique.
- Le gestionnaire de recherche refuse explicitement les modes inconnus.
- Les ressources PNG Leaflet transparentes ont été remplacées par les PNG officiels Leaflet 1.9.4 ; dimensions et canal alpha sont contrôlés.
- Le plafond `maxFeatures = 5000` est appliqué au total local, y compris après imports successifs.
- Les imports doivent être des FeatureCollections contenant des points GeoJSON valides ; les coordonnées WGS84 sont bornées.
- La taille maximale d'import et le nombre maximal de relevés sont lus depuis la configuration.
- L'état mémoire n'est modifié qu'après une écriture `localStorage` réussie.
- Tests Node ajoutés pour les coordonnées, géométries, propriétés, tailles et limites cumulées.
- Si Android ne peut pas démarrer le sélecteur de fichier, le callback WebView reçoit `null` avant d'être libéré.
- Le dossier `.monolith-france-backups/` est exclu par le `.gitignore` racine.

## Sources Géoplateforme

- L'API de géocodage direct documentée par l'IGN est `https://data.geopf.fr/geocodage/search`.
- Le service WMTS documente GetCapabilities et GetTile avec les paramètres LAYER, STYLE, FORMAT, TILEMATRIXSET, TILEMATRIX, TILEROW et TILECOL.
- La disponibilité des flux LiDAR HD reste progressive et doit être contrôlée pour chaque emprise.

## Recette non effectuée sur appareil

La compilation et les contrôles d'archive ne remplacent pas un test fonctionnel sur téléphone ou émulateur. Restent à vérifier :
- installation, démarrage et navigation vers l'atlas britannique ;
- affichage effectif des tuiles IGN WMTS et comportement sur les emprises non couvertes ;
- géocodage IGN et requêtes Overpass depuis la WebView réelle ;
- refus / octroi des permissions et géolocalisation ;
- ajout, suppression et persistance des observations après redémarrage ;
- import GeoJSON par le sélecteur Android, annulation du sélecteur et export via le pont natif ;
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
