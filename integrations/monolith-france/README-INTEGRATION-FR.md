# Monolith France — module cartographique LiDAR & archéologie

**Version du paquet :** 1.1.1  
**Langue / territoire initial :** français / France métropolitaine  
**Cible :** intégration dans une APK Android hôte nommée « Monolith » via `WebViewAssetLoader`.

Ce module fournit une interface cartographique mobile, des couches IGN LiDAR HD, la recherche de sites documentés dans les POI de la Géoplateforme et OpenStreetMap, ainsi qu'un carnet de prospection local exportable en GeoJSON.

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

Le script vérifie d'abord les points d'insertion, sauvegarde les fichiers modifiés, ajoute le module sous `integrations/monolith-france/`, ajoute le hook de préparation des assets et le déclare comme entrée de la tâche Gradle. Il fait démarrer `MainActivity` sur `/assets/web/france/web/index.html`; l'atlas anglais reste disponible à `/assets/web/index.html`.

L'intégration réutilise les permissions, le pont natif et le sélecteur de fichiers de l'application amont. Elle ne modifie ni `applicationId`, ni `namespace`, ni la signature, ni les niveaux SDK.

## Compilation Debug

Le guide `docs/CODESPACES-ET-BUILD.md` documente les prérequis et l'exécution. La commande automatisée est :

```bash
bash integrations/monolith-france/scripts/integrate_and_build_codespace.sh "$PWD"
```

Elle prépare les ressources, exécute les contrôles, lance `assembleDebug`, puis vérifie l'alignement et la signature de debug. Elle ne publie pas de Release et ne pousse aucun commit.

## Fonctions
1. France métropolitaine, locale `fr-FR`, coordonnées WGS84.
2. Fonds Plan IGN v2 et OpenStreetMap.
3. Couches IGN LiDAR HD MNT, MNS et MNH via WMTS.
4. Recherche des POI mégalithiques via découverte du sous-type dans les capacités de l'API IGN.
5. Recherche d'adresses et de lieux via le géocodeur de la Géoplateforme.
6. Recherche OSM de sites archéologiques dans l'emprise cartographique.
7. Géolocalisation à la demande ; relevés sauvegardés localement ; import/export GeoJSON.

## Limites scientifiques
**Aucune détection IA française n'est activée.** Le dépôt amont ne fournit pas de poids de modèles prêts à l'emploi et les modèles / résultats britanniques ne sont pas transposables à la France. Les anomalies visibles sur une couche LiDAR ne sont pas classées comme découvertes. La couverture IGN LiDAR HD est progressive et les bases IGN/OSM ne forment pas un inventaire archéologique exhaustif.

## Sources et licences
IGN / Géoplateforme, OpenStreetMap (ODbL) et Leaflet (BSD-2-Clause) sont référencés. Les attributions et conditions sont décrites dans `docs/LICENCES-ET-ATTRIBUTIONS.md`. Le logiciel amont est sous AGPL-3.0-or-later : les conditions de redistribution et la fourniture du code source correspondant doivent être respectées.
