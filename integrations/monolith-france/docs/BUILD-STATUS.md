# État de validation — Monolith International

## Correctif du sélecteur international — 2026-11-24

Branche : `feature/monolith-international-next`  
Commit CI : `db2a542a683f11fc15bb47f294726ed8ac63fff6`  
Commit de correction de la validation du schéma : `f01dd16ee6b0f267e304af4c6766d5374d09a21e`  
Dernier commit de la fixture : `db2a542a683f11fc15bb47f294726ed8ac63fff6`  
PR : [#2](https://github.com/Jickssa/megalith-lidar/pull/2) — ouverte, brouillon, non fusionnée.

### Exécution CI

Run : [45316298442](https://github.com/Jickssa/megalith-lidar/actions/runs/45316298442)  
SHA testé : `db2a542a683f11fc15bb47f294726ed8ac63fff6`.

- Static validation and installer regression : succès.
- `validate_package.py` : succès, avec contrôle du schéma JSON des profils FR/GB, des catalogues de langues et des routes d’Atlas autorisées.
- `node --check integrations/monolith-france/web/app.js` : succès.
- `node integrations/monolith-france/scripts/test_web_logic.js` : succès.
- `python -m py_compile integrations/monolith-france/scripts/*.py` : succès.
- `python integrations/monolith-france/scripts/test_android_installer.py` : succès.
- Android Debug APK build : succès avec JDK 17 et Android SDK 35.
- Installation du module dans le projet Android de CI : succès.
- `assembleDebug` : succès.
- Vérification du contenu APK et des CRC ZIP : succès.
- Vérification `zipalign -c -v 4` : succès.
- Vérification `apksigner verify --verbose` : succès.
- Upload APK et checksum : succès.

Artefact : [megalith-lidar-france-debug — ID 14884244756](https://github.com/Jickssa/megalith-lidar/actions/runs/45316298442/artifacts/14884244756)  
Taille de l’archive d’artefact : 18 997 547 octets.  
Digest SHA-256 déclaré par GitHub pour l’archive : `5715b76917673844cd76e2346089625e11a6c7bc3c9012af4e884c00ff5f3fa3`.

Le digest ci-dessus concerne l’archive d’artefact GitHub, pas directement le fichier APK. Le fichier APK n’a pas été extrait ni recalculé indépendamment dans l’environnement de travail de cette session.

### Correctifs apportés

- Le générateur du sélecteur commun affiche désormais « Choisir un atlas » en français dans son état initial ; la navigation vers l’interface reste bilingue via les catalogues existants.
- Les routes sont limitées aux destinations déclarées et exactes : FR vers `/assets/web/france/web/index.html`, GB vers `/assets/web/index.html`.
- Les profils actifs sont validés contre `country-profile.schema.json`. Seules les combinaisons FR/fr-FR et GB/en-GB sont actives et acceptées.
- La fixture vérifie les rôles distincts du sélecteur commun, des deux pages territoriales et des deux véritables atlas.
- Le hook d’intégration reste unique et le test de l’installateur contrôle la réinstallation ainsi que l’absence de modification du `index.html` source britannique.

### Limites de validation

- Les tests réseau physiques des services IGN/Overpass et les essais WMTS sur emprises de référence ne sont pas exécutés par ce run.
- Aucun test manuel sur téléphone Android, GPS réel ou installation par-dessus une APK existante n’a été réalisé.
- La signature prouvée ici est celle de l’APK Debug produite par la CI ; la compatibilité de signature avec une application déjà installée n’est pas vérifiée.
- Les résultats OSM sont des données contributives à recouper, pas des découvertes archéologiques certaines.
- Aucun modèle IA français n’est activé ni revendiqué. Les modèles et métriques britanniques ne sont pas transposés à la France.
- La contribution communautaire reste indicative ; aucun mécanisme sécurisé d’installation de paquet territorial arbitraire n’est déclaré opérationnel.

## État fonctionnel restant

- Équivalence complète de l’interface France avec les workflows STEP 1–3 britanniques.
- Inspecteur français, diagnostics LiDAR et carnet enrichi.
- Validation live GetCapabilities et test réel du type POI IGN avant toute activation.
- Recette externe des services, appareil Android physique et contrôle d’installation/mise à jour.
