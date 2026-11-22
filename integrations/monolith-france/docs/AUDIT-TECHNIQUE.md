# Audit technique — adaptation France du dépôt megalith-lidar

## Dépôt et périmètre

Dépôt amont étudié : `GlassOnTin/megalith-lidar`, branche `main`. Fork vérifié : `Jickssa/megalith-lidar`. Au moment de la comparaison, le fork était identique à l'amont, commit `ba08b3346895472dd68c27ab5435d614cec64356`.

L'arbre de l'amont contenait 85 fichiers suivis, dont environ 98,5 Mio sous `docs/`. Les principaux composants étaient `megalith_lidar/terrain_features.py`, `dataset.py`, `model.py`, `scanner.py`, `catalog.py`, `lidar_wcs.py`, `osm_context.py`, `arch_context.py`, les scripts nationaux, `index.html` et le projet Android Gradle.

## Architecture amont

- Six canaux de terrain multi-échelle calculés sur des MNT/MNS ; U-Net avec encodeur ResNet-34 et sorties spécialisées préhistorique, enclos et romain.
- Entraînement PyTorch, masques issus du registre NHLE, séparation spatiale par blocs BNG de 20 km, calibrage Platt et évaluation sur jeux tests anglais.
- Recoupements avec Historic England, OpenStreetMap, Megalithic Portal et cartes historiques Ordnance Survey.
- Interface Leaflet, inspecteur et exports GPX / OsmAnd.
- Application Android WebView avec permissions de localisation et sélecteur GeoJSON.

## Non-transposabilité France

Les modèles et jeux de données amont sont liés à l'Angleterre : British National Grid EPSG:27700, Environment Agency LiDAR, NHLE, OS historique et données OSM/Megalithic Portal. Les scores publiés dans le README ne sont pas des mesures de performances en France. Aucun poids de modèle prêt à l'inférence n'a été identifié dans l'arbre suivi. Les résultats anglais ne sont donc pas chargés ni réinterprétés comme des données françaises.

## Choix de l'adaptation

1. Utiliser WGS84/EPSG:4326 comme CRS d'échange.
2. Centrer la carte sur la France métropolitaine.
3. Utiliser Plan IGN v2 et les couches LiDAR HD MNT, MNS, MNH via WMTS Géoplateforme.
4. Résoudre le filtre POI « mégalithe » par découverte dynamique de sa catégorie parente dans les capacités de l'API ; ne pas traiter « mégalithe » comme catégorie racine sans résolution.
5. Utiliser le géocodeur IGN pour les lieux/adresses, Overpass pour les éléments OSM et les données ouvertes du ministère de la Culture uniquement comme recoupement.
6. Sauvegarder les observations dans le WebView et permettre l'import/export GeoJSON.
7. Garder la détection IA désactivée jusqu'à constitution et validation d'un jeu français.

## Limites

- La couverture LiDAR HD est progressive et doit être contrôlée pour chaque emprise.
- Les POI IGN, OSM et les immeubles protégés ne sont pas exhaustifs de l'archéologie.
- Les services cartographiques et les recherches nécessitent une connexion. Le cache hors ligne n'est pas garanti.
- La compilation Android et le test sur appareil ne sont pas réputés effectués par cet audit.
