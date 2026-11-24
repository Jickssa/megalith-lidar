# Validation et recette — Monolith International 2.0

## Périmètre livré dans cette tranche

L'Atlas France comprend trois espaces fonctionnels : Carte & LiDAR, Liste des candidats, Détails du site et carnet de terrain. Les résultats IGN/OSM et les observations locales alimentent un modèle d'affichage commun, avec source, catégorie, nature et état de vérification. La sélection relie la liste, la carte et l'inspecteur. Aucun score ou verdict archéologique n'est fabriqué.

## Validation automatisée — HEAD a6b634fe760998a8dc9cf870a8dab10bb5650e60

Deux workflows GitHub Actions ont réussi sur le même HEAD :
- Push : [45381106088](https://github.com/Jickssa/megalith-lidar/actions/runs/45381106088).
- Pull request #2 : [45381119538](https://github.com/Jickssa/megalith-lidar/actions/runs/45381119538).

Les étapes suivantes ont réussi dans les deux runs :
- `python integrations/monolith-france/scripts/validate_package.py`
- `node --check integrations/monolith-france/web/app.js`
- `node integrations/monolith-france/scripts/test_web_logic.js`
- `python -m py_compile integrations/monolith-france/scripts/*.py`
- `python integrations/monolith-france/scripts/test_android_installer.py`
- Build Gradle `assembleDebug`
- Vérification des assets internationaux et France dans l'APK.
- CRC ZIP, `zipalign` et `apksigner`.

SHA-256 de l'APK Debug, identique pour les deux workflows :

`09303ed07eb77cdcea2576facf983734045f10c1913f7df0c984726c8eaaf972`

Artefacts :
- Push : [14912074868](https://github.com/Jickssa/megalith-lidar/actions/runs/45381106088/artifacts/14912074868).
- PR : [14914890180](https://github.com/Jickssa/megalith-lidar/actions/runs/45381119538/artifacts/14914890180).

## Recette fonctionnelle restante

- Parcours des trois onglets sur appareil Android physique, y compris retour liste ↔ carte ↔ inspecteur.
- Import/export GeoJSON, création d'observations et vérification du rattachement à un candidat.
- Écrans 360–430 px en portrait et paysage sur appareil réel.
- Chargement WMTS IGN et comportement hors ligne.
- Diagnostic réel du rectangle sombre observé dans la capture précédente.
- Vérification du fonctionnement des couches LiDAR sur des emprises de référence.
- Validation en direct des services externes et du comportement réseau.

## Limites architecturales et scientifiques

- L'interface source UK n'est pas refactorisée en composants JavaScript communs ; elle reste préservée.
- La présente livraison établit la structure STEP 1–3 côté France et le modèle de sélection associé ; elle ne constitue pas encore un shell de composants partagé au niveau du code UK/FR.
- Le regroupement des marqueurs UK et le calcul de couverture de la campagne restent à auditer.
- La cause du rectangle sombre de la carte France n'est pas établie par capture seule.
- POI IGN et IA France restent désactivés.
- Aucun test physique Android ni test de mise à jour d'une application déjà installée avec vérification de certificat n'est revendiqué.
