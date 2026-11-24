# État de validation — Monolith International 2.0

## Harmonisation initiale de l'Atlas France

Branche : `feature/monolith-international-next`  
HEAD initial de la tranche : `55cf67b1b8f7031a523e143b2944a12d8ed75227`  
PR : [#2](https://github.com/Jickssa/megalith-lidar/pull/2) — ouverte, brouillon, non fusionnée.

### Changements intégrés

- Interface France réorganisée en trois espaces : Carte & LiDAR, Liste des candidats, Détails du site.
- Sélection synchronisée entre résultats, marqueurs, tableau et inspecteur.
- Modèle de candidat normalisé avec source, catégorie, nature et état de vérification ; aucun score de confiance français inventé.
- Carnet de terrain GeoJSON intégré à l'espace Détails du site.
- Design system France rapproché du thème cartographique clair de l'Atlas britannique, avec thème sombre et disposition mobile.
- Script Codespaces : ajout de jsonschema et exécution des tests JavaScript.
- README, changelog et manifeste alignés sur la version 2.0.0.

### Validation

- Tests JavaScript, Python, validation paquet, fixture Android et build Android : en attente d'exécution sur le HEAD final.
- Aucun test physique Android, réseau en direct, ni comparaison de certificat d'installation n'est revendiqué.

### Limites non couvertes

- La source et le moteur UK restent inchangés ; les trois sections historiques sont préservées, mais pas encore refactorisées dans le même shell JavaScript.
- Le clustering des marqueurs UK et l'audit du pourcentage de couverture supérieur à 100 % restent à réaliser.
- La zone sombre de la carte France nécessite un test réel des tuiles et du rendu.
- POI IGN non validé et détection IA France désactivée.
- Les tests réseau, les emprises de référence LiDAR, la recette mobile réelle et la compatibilité de signature restent à effectuer.
