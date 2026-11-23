# État de validation — Monolith International

## 1.3.1 — recherche archéologique française affinée

Branche : `feature/monolith-international-next`  
Commit validé : `de755ee8e2286ba742b0715e523ee3df99790432`  
Branche de départ : `fa3d5d34cbfb1cb386bf261eaa40ab1cfa2e2729`.

### CI et APK

- Workflow push : succès — https://github.com/Jickssa/megalith-lidar/actions/runs/45180531041
- Workflow PR : succès attendu pour le même SHA — https://github.com/Jickssa/megalith-lidar/actions/runs/45180547052
- Validation statique, tests Node/Python et fixture installateur : succès.
- Gradle `assembleDebug` : succès.
- Contrôle ZIP/CRC, `zipalign` et `apksigner verify` : succès en CI.
- APK extraite et inspectée localement : 19 027 801 octets, 97 entrées, aucun défaut CRC.
- SHA-256 APK : `1ff35b618e67a5afc559106daccd5c5d01bb6a26f066df0834aab29ea7b6ce92`.
- Artefact CI ID `14821396027`, archive 18 987 711 octets, digest SHA-256 `506ad72afb52472c5f7b22dde1e279fdcaac6a7d5529f4b4f1cb8d6311e8b62d`.
- Artefact : https://github.com/Jickssa/megalith-lidar/actions/runs/45180531041/artifacts/14821396027

### Recherche France 1.3.1

- Taxonomie française de six familles.
- Règles OSM déclaratives par conjonction de tags.
- Recherche textuelle pilotée par catégorie : nom, nom français, référence et sous-types configurés.
- Echappement de la regex utilisateur puis de la chaîne Overpass.
- Recherche nodes/ways/relations, normalisation des centres et identifiants, déduplication.
- Rejet des emprises excessives, annulation et protection contre les réponses périmées.
- Les règles mégalithiques emploient `historic=archaeological_site` + `archaeological_site=megalith`; les sous-types tels que `megalith_type=dolmen` sont recherchés par champ.
- Les tags génériques `highway=track` et `man_made=cairn` ne sont plus utilisés comme raccourcis archéologiques.

### Reste à faire

- Sélecteur international indépendant pays/langue et mémorisation.
- Profils pays versionnés et validés par schéma.
- Espace communautaire et paquet de contribution sécurisé.
- Équivalence complète de l'interface France avec STEP 1, STEP 2 et STEP 3 britanniques.
- Inspecteur français, diagnostics LiDAR et carnet enrichi.
- Validation live GetCapabilities pour le POI IGN et activation contrôlée du type approprié.
- Tests réseau réels pour les services externes, tests WMTS sur emprises de référence.
- Recette physique Android, GPS, import/export et comparaison du certificat avec l'application installée.

Aucun détecteur IA français n'est revendiqué. La recherche OSM retrouve les objets déjà cartographiés et ne découvre pas de structures non documentées.
