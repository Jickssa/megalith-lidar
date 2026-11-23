# État de validation — Monolith International

## 1.3.1 — précision du moteur de recherche

Branche : `feature/monolith-international-next`  
Dernier périmètre : moteur OSM guidé par taxonomie, recherche de sous-types et déduplication.

### Correctifs inclus

- Règles OSM par conjonction de tags, avec priorité aux combinaisons archéologiques spécifiques.
- Champs de recherche par catégorie : noms, références et sous-types comme `megalith_type` ou `fortification_type`.
- Regex utilisateur échappées avant l'échappement de la chaîne Overpass.
- Déduplication des entités reconnues par plusieurs champs.
- Exclusion des pistes génériques `highway=track` et du cairn générique `man_made=cairn` des familles archéologiques.
- Tests de non-régression et validateur enrichis.

### Portée qui reste non réalisée

- Sélecteur international pays/langue et profils pays.
- Espace communauté et modèle de contribution.
- Équivalence fonctionnelle de l'interface France avec STEP 1/2/3 britannique.
- Validation live GetCapabilities pour le POI IGN et tests réseau réels Overpass/IGN/WMTS.
- Recette physique Android et comparaison des certificats de signature.

### Validation

La CI 1.3.1 doit être exécutée sur le HEAD courant avant toute annonce de build. Aucun détecteur IA français n'est revendiqué.
