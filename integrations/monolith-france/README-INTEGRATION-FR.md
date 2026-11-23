# Monolith France — module cartographique LiDAR & archéologie

**Version du paquet :** 1.2.0  
**Langue / territoire initial :** français / France métropolitaine  
**Cible :** intégration dans une APK Android hôte nommée « Monolith » via `WebViewAssetLoader`.

Ce module fournit une interface cartographique mobile, des couches IGN LiDAR HD, le géocodage de lieux/adresses par la Géoplateforme, la recherche OSM à l'échelle de l'emprise courante et un carnet de prospection local importable/exportable en GeoJSON. La recherche dédiée au sous-type POI « mégalithe » de l'IGN est actuellement désactivée : son schéma de catégorie et de filtrage n'est pas encore validé.

## Contenu
- `web/` : interface, carte Leaflet, recherche IGN / OSM et carnet de terrain.
- `config/` : territoire par défaut, sources cartographiques et typologie archéologique.
- `android/` : fragments Kotlin/XML à fusionner dans l'Activity hôte, sans créer une seconde Activity.
- `scripts/` : installateurs Android, validation du paquet et procédure de build Codespaces.
- `docs/` : audit, inspection de l'APK fourni, licences, compilation et recette.

## Installation dans le projet Android source amont

L'APK transmis correspond à l'application `uk.megalith.lidar` 3.2.0. Le projet amont possède déjà une WebView, la géolocalisation, un sélecteur GeoJSON, un pont de partage et Leaflet 1.9.4 dans `assets/web/leaflet/`.

Depuis un clone du dépôt `Jickssa/megalith-lidar` :

```bash
python3 integrations/monolith-france/scripts/install_into_megalith_lidar_android.py "$PWD" --dry-run
python3 integrations/monolith-france/scripts/install_into_megalith_lidar_android.py "$PWD"
```

Le script vérifie d'abord les points d'insertion, sauvegarde les fichiers modifiés, ajoute le module sous `integrations/monolith-france/`, ajoute le hook de préparation des assets et le déclare comme entrée de la tâche Gradle. Il fait démarrer `MainActivity` sur l'écran commun `/assets/web/atlas-home.html`, qui présente les deux destinations. Le fichier `/assets/web/index.html` de l'atlas britannique reste strictement à son emplacement historique pour préserver ses ressources relatives ; l'Atlas France reste sous `/assets/web/france/web/index.html`.

L'intégration réutilise les permissions, le pont natif et le sélecteur de fichiers de l'application amont. Si Android ne peut pas ouvrir le sélecteur, le callback WebView reçoit explicitement `null` afin de libérer le contrôle HTML. Les sauvegardes source sont placées dans `.monolith-france-backups/`, exclu par le `.gitignore` racine. L'installateur reste limité à ces points d'insertion et ne modifie ni `applicationId`, ni `namespace`, ni la signature, ni les niveaux SDK.

## Compilation Debug

Le guide `docs/CODESPACES-ET-BUILD.md` documente les prérequis et l'exécution. La commande automatisée est :

```bash
bash integrations/monolith-france/scripts/integrate_and_build_codespace.sh "$PWD"
```

Elle prépare les ressources, exécute les contrôles, lance `assembleDebug`, puis vérifie l'alignement et la signature de debug. Elle ne publie pas de Release et ne pousse aucun commit.

## Navigation entre atlas — architecture à trois niveaux

Le démarrage Android ouvre le sélecteur commun `/assets/web/atlas-home.html`. Celui-ci conduit aux deux pages territoriales intermédiaires : `/assets/web/france-home.html` et `/assets/web/uk-home.html`. Chaque page dispose d'un bouton d'action supérieur qui ouvre l'Atlas correspondant : France (`/assets/web/france/web/index.html`) ou Royaume-Uni (`/assets/web/index.html`). Les pages territoriales permettent de revenir au sélecteur et de basculer vers l'autre territoire. L'Atlas France propose également les liens « Accueil France » et « Choisir un atlas ». Dans l'Atlas britannique, le préparateur ajoute un seul lien « Choose atlas » à l'en-tête de la copie embarquée ; le fichier source racine `index.html` reste inchangé. Les deux pages territoriales sont générées par l'installateur après la reconstruction des assets : elles ne sont pas des copies des interfaces cartographiques.

## Fonctions
1. France métropolitaine, locale `fr-FR`, coordonnées WGS84.
2. Fonds Plan IGN v2 et OpenStreetMap.
3. Couches IGN LiDAR HD MNT, MNS et MNH via WMTS.
4. Recherche dédiée des POI mégalithiques IGN : désactivée dans cette version tant que le paramètre de catégorie et le schéma API ne sont pas vérifiés.
5. Recherche d'adresses et de lieux via le géocodeur de la Géoplateforme (à tester en ligne dans la WebView Android).
6. Recherche OSM de sites archéologiques dans l'emprise cartographique (données contributives non exhaustives, résultats à recouper).
7. Géolocalisation à la demande ; relevés sauvegardés localement ; import/export GeoJSON.
8. Validation des GeoJSON importés (points WGS84, taille et nombre cumulé) avec plafond local de 5 000 observations.

## Limites scientifiques
**Aucune détection IA française n'est activée.** Le dépôt amont ne fournit pas de poids de modèles prêts à l'emploi et les modèles / résultats britanniques ne sont pas transposables à la France. Les anomalies visibles sur une couche LiDAR ne sont pas classées comme découvertes. La couverture IGN LiDAR HD est progressive et les bases IGN/OSM ne forment pas un inventaire archéologique exhaustif.

## Sources et licences
IGN / Géoplateforme, OpenStreetMap (ODbL) et Leaflet (BSD-2-Clause) sont référencés. Les attributions et conditions sont décrites dans `docs/LICENCES-ET-ATTRIBUTIONS.md`. Le logiciel amont est sous AGPL-3.0-or-later : les conditions de redistribution et la fourniture du code source correspondant doivent être respectées.
