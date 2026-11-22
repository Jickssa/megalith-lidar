# Changelog

## 1.1.1 — 2026-11-22

- Correctifs des URLs appassets : chemins explicites pour les styles, scripts et configurations.
- Copie des PNG Leaflet manquants à côté de la feuille de style partagée, sans modifier le CSS amont.
- Installateur spécialisé rendu tolérant aux variantes de mise en forme de `START_URL`.
- Tests de réinstallation forcée et d'idempotence.

## 1.1.0 — 2026-11-22

- Inspection de l'APK fourni : identité Android, permissions, WebView, pont natif et ressources.
- Adaptation spécifique au projet Android amont.
- Écran français configuré comme entrée principale, atlas britannique conservé comme accès secondaire.
- Découverte dynamique du sous-type POI mégalithe dans les capacités IGN.
- Aucune détection IA britannique présentée comme résultat français.

## 1.0.0 — 2026-11-22

- Première interface de prospection France métropolitaine.
- Cartographie IGN, couches LiDAR HD et OpenStreetMap.
- Recherche, carnet de terrain, import/export GeoJSON.
