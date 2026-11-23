# Changelog

## 1.1.2 — 2026-11-23

- Validation des imports GeoJSON : FeatureCollection, géométries Point, coordonnées WGS84, taille de fichier et nombre cumulé d'observations.
- Écriture locale transactionnelle : l'état mémoire ne change qu'après une persistance réussie.
- Tests unitaires Node ajoutés au workflow CI pour les cas GeoJSON et les plafonds de stockage.
- Correctif Android : le callback WebView du sélecteur de fichiers reçoit explicitement `null` si Android ne peut pas ouvrir le sélecteur.
- Fixture installateur renforcée pour contrôler ce chemin d'annulation, la réinstallation et les sauvegardes.
- Le dossier de sauvegarde `.monolith-france-backups/` est ignoré par Git.
- Ressources PNG Leaflet 1.9.4 officielles intégrées et contrôlées (dimensions et canal alpha).

## 1.1.1 — 2026-11-22

- Correctifs des URLs appassets : chemins explicites pour les styles, scripts et configurations.
- Copie des PNG Leaflet à côté de la feuille de style partagée, sans modifier le CSS amont.
- Installateur spécialisé rendu tolérant aux variantes de mise en forme de `START_URL`.
- Tests de réinstallation forcée et d'idempotence.

## 1.1.0 — 2026-11-22

- Inspection de l'APK fourni : identité Android, permissions, WebView, pont natif et ressources.
- Adaptation spécifique au projet Android amont.
- Écran français configuré comme entrée principale, atlas britannique conservé comme accès secondaire.
- Exploration de la taxonomie POI IGN ; la recherche du sous-type « mégalithe » est désactivée tant que le schéma et le filtre ne sont pas confirmés.
- Aucune détection IA britannique présentée comme résultat français.

## 1.0.0 — 2026-11-22

- Première interface de prospection France métropolitaine.
- Cartographie IGN, couches LiDAR HD et OpenStreetMap.
- Recherche, carnet de terrain, import/export GeoJSON.
