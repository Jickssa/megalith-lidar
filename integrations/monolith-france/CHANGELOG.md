# Changelog

## 1.1.4 — 2026-11-23

- Correction de l'insertion du hook Android après contrôle sur le véritable préparateur `prepare_android_assets.py`.
- Test de régression étendu : exécution synthétique des assets et validation syntaxique de l'injection dans le préparateur amont réel.
- Écran commun des atlas compilé et contrôlé directement dans l'APK Debug du run PR #111.


## 1.1.3 — 2026-11-23

- Ajout d'un écran d'accueil commun présentant deux destinations : Atlas France et Atlas britannique.
- L'écran commun est généré après la reconstruction des assets sous `/assets/web/atlas-home.html`.
- Le fichier historique `/assets/web/index.html` de l'Atlas britannique est conservé à son emplacement et n'est jamais écrasé.
- L'Atlas France permet de revenir au choix des atlas et de passer directement au Royaume-Uni.
- Le validateur et la fixture contrôlent les routes communes, le maintien de l'index UK et les chemins internes.
- La déclaration Android `START_URL` est migrée depuis l'ancienne URL UK ou l'ancienne URL France vers l'écran de choix commun.

## 1.1.2 — 2026-11-23

- Validation des imports GeoJSON, coordonnées WGS84 et limites cumulées de stockage.
- Écriture locale transactionnelle et tests Node des limites de stockage.
- Callback WebView d'import libéré explicitement si le sélecteur Android ne peut pas s'ouvrir.
- Images Leaflet 1.9.4 officielles vérifiées (dimensions et canal alpha).

## 1.1.1 — 2026-11-22

- Correctifs des URLs appassets et des ressources Leaflet.
- Installateur tolérant aux variations de déclaration START_URL.
- Tests de réinstallation forcée et d'idempotence.

## 1.1.0 — 2026-11-22

- Intégration du module France sans supprimer l'atlas britannique.
- POI IGN « mégalithe » désactivé tant que son schéma n'est pas validé.
- Aucune détection IA britannique transposée à la France.

## 1.0.0 — 2026-11-22

- Première interface France : cartographie IGN, LiDAR HD, OSM et carnet de terrain.
