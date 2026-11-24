# État de validation — Monolith International 2.0

## Harmonisation initiale de l'Atlas France

Branche : `feature/monolith-international-next`  
HEAD validé : `a6b634fe760998a8dc9cf870a8dab10bb5650e60`  
PR : [#2](https://github.com/Jickssa/megalith-lidar/pull/2) — ouverte, brouillon, non fusionnée.

### Changements intégrés

- Interface France organisée en trois espaces : Carte & LiDAR, Liste des candidats, Détails du site.
- Sélection synchronisée entre résultats, marqueurs, tableau et inspecteur.
- Modèle de candidat normalisé avec source, catégorie, nature et état de vérification ; aucun score archéologique français n'est inventé.
- Carnet GeoJSON intégré à l'espace Détails du site.
- Design cartographique clair inspiré du langage visuel de l'Atlas britannique, avec thème sombre mémorisé et mise en page responsive.
- Script Codespaces : installation de `jsonschema` et exécution des tests JavaScript.
- README, changelog et manifeste alignés sur la version 2.0.0.

### Validation GitHub Actions — commit a6b634fe760998a8dc9cf870a8dab10bb5650e60

Les deux déclenchements sont terminés en succès :

| Événement | Run | Résultat |
|---|---:|---|
| Push | [45381106088](https://github.com/Jickssa/megalith-lidar/actions/runs/45381106088) | <span style="color:green">success</span> |
| Pull request #2 | [45381119538](https://github.com/Jickssa/megalith-lidar/actions/runs/45381119538) | <span style="color:green">success</span> |

Les deux exécutions ont validé :
- validation statique du paquet ;
- syntaxe JavaScript ;
- tests de logique Web ;
- compilation syntaxique Python ;
- fixture de régression de l'installateur ;
- compilation Android Debug ;
- présence des routes et ressources Web dans l'APK ;
- intégrité CRC de l'archive APK ;
- contrôle `zipalign` ;
- vérification `apksigner`.

### APK Debug et artefacts

L'APK construite par les deux événements possède le même SHA-256 binaire :

`09303ed07eb77cdcea2576facf983734045f10c1913f7df0c984726c8eaaf972`

Artefact du run Push :
- ID : `14912074868`
- [Télécharger l'artefact](https://github.com/Jickssa/megalith-lidar/actions/runs/45381106088/artifacts/14912074868)
- Taille de l'archive artefact : 19 001 420 octets.
- SHA-256 de l'archive artefact : `bc21fa3d5db769bf0db12f9e3c9201d358c7e810ee27393feb4079f5f2d6f161`.

Artefact du run PR :
- ID : `14914890180`
- [Télécharger l'artefact](https://github.com/Jickssa/megalith-lidar/actions/runs/45381119538/artifacts/14914890180)
- Taille de l'archive artefact : 19 001 422 octets.
- SHA-256 de l'archive artefact : `5748dcc62235572cd82e02248698299798d232d522479965e2eb0df644fc61bc`.

Les SHA-256 des archives artefacts sont différents car les ZIP d'artefacts sont produits par deux exécutions distinctes ; ils ne doivent pas être confondus avec le SHA-256 du fichier APK, identique pour les deux runs.

### Limites non couvertes

- La source et le moteur UK restent inchangés ; les trois sections historiques sont préservées, mais pas encore refactorisées dans un shell JavaScript partagé avec France.
- Le regroupement des marqueurs UK et l'audit du pourcentage de couverture supérieur à 100 % restent à réaliser.
- La zone sombre de la carte France nécessite un diagnostic réel des tuiles et du rendu.
- POI IGN non validé et détection IA France désactivée.
- Tests réseau et emprises de référence LiDAR restent à réaliser.
- Aucun test d'installation/mise à jour sur appareil Android physique, aucune vérification de compatibilité du certificat de signature avec une installation existante ne sont revendiqués.
