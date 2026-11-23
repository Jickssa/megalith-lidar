# Changelog

## 1.2.3 — navigation réciproque et cache diagnostic borné

- Remplacement du lien UK qui rechargeait la carte courante par un accès direct à l’Atlas France.
- Libellé du sélecteur harmonisé sur « Atlas UK » ; la page d’introduction UK est maintenant rédigée en français.
- Conservation explicite de la distinction : l’interface cartographique britannique historique reste celle du dépôt amont et demeure en anglais.
- Téléchargement des PNG de diagnostic limité à 8 Mio par fichier, avec contrôle du type MIME et de la signature PNG.
- Redirections HTTP désactivées pour cette source fixe ; cache limité à 64 Mio, 24 fichiers et 30 jours, avec éviction des plus anciens.
- Tests de navigation, de contrat natif et de limites du cache renforcés.

## 1.2.2 — navigation rectifiée après recette utilisateur

- Restauration des accès directs depuis le sélecteur commun vers les deux véritables interfaces cartographiques : Atlas France et Atlas britannique.
- Les pages france-home.html et uk-home.html restent des introductions territoriales et ne sont plus présentées comme les Atlas eux-mêmes.
- Dans l'en-tête UK embarqué, conservation du retour vers le sélecteur et ajout d'un lien direct explicite « UK Atlas ».
- Dans l'interface cartographique française, le lien Royaume-Uni ouvre directement la carte UK, pas sa page d'introduction.
- Tests de navigation mis à jour pour distinguer les pages d'accueil et les Atlas.


## 1.2.1 — 2026-11-23

- Pont d'export Android borné à 25 Mio, écrit hors du thread UI et stocké sous nom temporaire unique.
- MIME d'export limités à une liste connue.
- Filtre Android de sélection de fichiers basé sur les types acceptés par le champ Web.
- Schémas URI internes strictement limités à HTTPS/appassets ; les schémas non pris en charge sont bloqués.
- Import France : contrôle du type JSON/GeoJSON par extension ou MIME avant lecture.
- Tests Node, fixture installateur et validation statique étendus.
- CSS : cibles tactiles et disposition paysage mobile améliorées.


## 1.2.0 — 2026-11-23

- Ajout de deux pages d'accueil territoriales distinctes entre le sélecteur commun et les Atlas France / Royaume-Uni.
- Le sélecteur commun ouvre désormais les accueils France et Royaume-Uni ; chaque accueil propose un accès explicite à l'Atlas complet correspondant.
- Navigation de retour vers le sélecteur et de bascule entre territoires ; le module France expose également son accueil territorial.
- Ajout dans la copie Android de l'Atlas britannique d'un lien « Choose atlas », sans modifier le fichier source britannique.
- Mise à niveau idempotente du hook de génération : un hook 1.1.x existant est remplacé proprement au lieu de rester obsolète.
- Correction de l'ordre de sauvegarde du préparateur Android : la copie de sauvegarde est créée avant modification.
- Tests étendus pour contrôler les routes, les pages cibles, les appels vers les véritables atlas et l'immuabilité de la source britannique.


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
