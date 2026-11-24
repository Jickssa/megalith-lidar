# Validation et recette — Monolith International 2.0

## Périmètre France

L'Atlas France comprend trois espaces fonctionnels : Carte & LiDAR, Liste des candidats, Détails du site et carnet de terrain. Les résultats IGN/OSM et les observations locales alimentent un modèle d'affichage commun, avec source, catégorie, nature et état de vérification. La sélection relie la liste, la carte et l'inspecteur. Aucun score ou verdict archéologique n'est fabriqué.

## Validation automatisée

Exécuter sur le HEAD final :

- `node --check integrations/monolith-france/web/app.js`
- `node integrations/monolith-france/scripts/test_web_logic.js`
- `python integrations/monolith-france/scripts/validate_package.py`
- `python -m py_compile integrations/monolith-france/scripts/*.py`
- `python integrations/monolith-france/scripts/test_android_installer.py`
- CI Android Debug, inventaire des assets, CRC ZIP, zipalign et apksigner.

## Recette fonctionnelle restante

- Parcours des trois onglets sur appareil Android, retour liste ↔ carte ↔ inspecteur.
- Import/export GeoJSON, création d'observations et rattachement à un candidat.
- Écrans 360–430 px en portrait et paysage.
- Chargement WMTS IGN et comportement hors ligne.
- Vérification du rendu Leaflet après affichage de l'onglet Carte.

## Limites

- L'interface source UK n'est pas refactorisée en composants JavaScript communs.
- La source UK n'est pas modifiée.
- Le regroupement des marqueurs UK et le calcul de couverture de la campagne restent à auditer.
- La cause du rectangle sombre de la carte France n'est pas établie.
- POI IGN et IA France restent désactivés.
- Aucun test physique Android, réseau réel, ni test de mise à jour signée n'est revendiqué.
