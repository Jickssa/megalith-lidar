# État de validation — Monolith International

## Version 1.3.0 — tranche de recherche française

Branche dédiée : `feature/monolith-international-next`  
Branche de départ : `fa3d5d34cbfb1cb386bf261eaa40ab1cfa2e2729` (HEAD vérifié de la PR #1 au démarrage).

### Travail implémenté dans cette tranche

- Taxonomie française déclarative de six familles, reliée à la recherche OSM.
- Sélecteur de catégorie archéologique dans l'interface France.
- Générateur Overpass basé sur la catégorie, le texte de recherche et l'emprise actuelle.
- Prise en charge nodes, ways et relations ; normalisation des centres géométriques et liens OSM.
- Limitation de l'emprise, annulation des recherches antérieures, rejet des réponses périmées.
- Déclaration corrigée de l'autocomplétion POI IGN : `/geocodage/completion/`, type `poiType` attendu depuis GetCapabilities.
- Validateur et CI renforcés ; les chemins Android, le préparateur d'assets et l'index UK déclenchent désormais le workflow.
- Manifeste aligné sur la version 1.3.0.

### Travail restant

- Sélecteur international pays/langue indépendant et persistant.
- Profils territoriaux indépendants et schéma de contribution communautaire.
- Interface France reprenant réellement les fonctions STEP 1, STEP 2 et STEP 3 de l'original.
- Inspecteur de site, vues diagnostiques et carnet enrichi.
- Validation réelle de l'autocomplétion POI IGN et de la découverte des capacités.
- Tests d'intégration réseau et contrôle WMTS réel dans WebView.
- Recette physique Android.
- Contrôle de signature avec l'application installée.

### Validation

Aucune compilation 1.3.0 n'est déclarée réussie à ce stade. Les anciens artefacts 1.2.4 ne doivent pas être présentés comme construits depuis cette branche.
