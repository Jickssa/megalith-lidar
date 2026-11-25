# État de validation — Monolith International 2.0

## Harmonisation initiale de l'Atlas France

Branche : `feature/monolith-international-next`  
Dernier HEAD de code validé : `96e0587490d1674075f62fb6a12caf725dd4bb11`  
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

- Les modèles, données d'entraînement et moteurs de détection UK restent inchangés ; le rendu cartographique et la présentation de la progression ont évolué. Le shell JavaScript UK/FR n'est pas encore partagé.
- L'agrégation visuelle des marqueurs UK et la suppression du ratio national codé en dur sont livrées. L'origine mathématique complète de l'ancien dépassement de 100 % reste à établir par audit des surfaces et éventuels recouvrements de carrés.
- La zone sombre de la carte France nécessite un diagnostic réel des tuiles et du rendu.
- POI IGN non validé et détection IA France désactivée.
- Tests réseau et emprises de référence LiDAR restent à réaliser.
- Aucun test d'installation/mise à jour sur appareil Android physique, aucune vérification de compatibilité du certificat de signature avec une installation existante ne sont revendiqués.
- `MainActivity.onDestroy()` libère désormais les callbacks de permission et de sélecteur, neutralise le passage de relais des exports asynchrones après destruction, arrête et détruit le WebView. La validation de cette modification repose sur les contrats statiques et le build Android ; aucun test d'appareil physique n'est revendiqué.


## Tranche suivante — agrégation UK et diagnostic des tuiles France

- Le moteur UK conserve ses données, filtres, tables, sélection et inspecteur. Sous le zoom 11, les candidats sont regroupés visuellement par cellule écran ; cliquer un groupe augmente le zoom, puis les marqueurs détaillés historiques réapparaissent au zoom 11. Les groupes sont recalculés après chaque déplacement et changement de zoom. Les objets GeoJSON ne sont ni supprimés ni fusionnés.
- La progression UK présente les carrés terminés et la surface calculée par le producteur (`total_scanned_area_km2`), sans ratio national codé en dur.
- Le profil GB précise que le territoire déclaré est le Royaume-Uni, tandis que la campagne actuellement publiée couvre l'Angleterre.
- Le module France affiche les chargements, tuiles reçues et erreurs des fonds et couches LiDAR. Une réponse HTTP réussie ne prouve pas à elle seule que la tuile contient une donnée LiDAR utile.
- Validation GitHub Actions de cette tranche : en attente.


## Installateur — remplacement transactionnel des assets

- Les arbres runtime `web`, `config` et `docs` sont copiés vers un répertoire de staging situé sur le même système de fichiers que le dépôt hôte.
- Leur remplacement s'effectue par `os.replace()` ; en cas d'exception capturée au cours des échanges, les arbres déjà remplacés sont supprimés et les sauvegardes restaurées.
- Une régression simule l'échec du deuxième renommage et vérifie le rétablissement du contenu antérieur des trois répertoires.


## Validation finale de la tranche — HEAD 1ce620e

Branche : `feature/monolith-international-next`  
PR #2 : ouverte, brouillon, non fusionnée.  
HEAD : `1ce620e14d9a2c9e50c820b12a9e2a8e7475b61d`.

Les workflows push et Pull Request ont réussi sur ce HEAD :

| Événement | Run | Résultat |
|---|---:|---|
| Push | [45535520209](https://github.com/Jickssa/megalith-lidar/actions/runs/45535520209) | success |
| PR #2 | [45535526503](https://github.com/Jickssa/megalith-lidar/actions/runs/45535526503) | success |

Les deux exécutions ont validé le paquet, la syntaxe JavaScript, les tests Web, le test international (groupement UK, emprise GB, script inline UK), la syntaxe Python, le test de rollback de l'installateur, le build Android Debug, les assets APK, l'intégrité ZIP, `zipalign` et `apksigner` (signature v2 vérifiée).

### APK de ce HEAD

Les deux fichiers APK proviennent de builds distincts ; leurs empreintes binaires sont donc rapportées séparément.

| Événement | Artefact | SHA-256 APK | Taille ZIP artefact | Expiration |
|---|---:|---|---:|---|
| Push | [14986982721](https://github.com/Jickssa/megalith-lidar/actions/runs/45535520209/artifacts/14986982721) | `08c8fe178efc371b311653d6f3053220e0d4150c44df05bb1360a1942edae965` | 19 006 598 octets | 2026-12-09 02:49 UTC |
| PR | [14986891901](https://github.com/Jickssa/megalith-lidar/actions/runs/45535526503/artifacts/14986891901) | `18701045a512668f3198ca67cbe2c88b69a0c6c183299b349e9e14831d5d4413` | 19 006 598 octets | 2026-12-09 02:49 UTC |

SHA-256 des archives ZIP d'artefact :
- Push : `cf7a3ecffebeb0bc11bc84925c8db162d64fd764536832730fbcc91b0af6e7e6`.
- PR : `66abb07dbaaca9b00c650772be40abd14230c4d6b5a43ee8bb9cd74dc78bf7a0`.

Les archives et APK sont des builds distincts ; ne pas substituer l'empreinte de l'archive à celle de l'APK.


## Validation finale de la couche Android et du rendu cartographique — HEAD 3248ec2

La tranche inclut aussi le nettoyage du cycle de vie Android et le recalcul des groupes UK après déplacement de la carte.

| Événement | Workflow | Résultat |
|---|---|---|
| Push | [45536266046](https://github.com/Jickssa/megalith-lidar/actions/runs/45536266046) | success |
| PR #2 | [45536272196](https://github.com/Jickssa/megalith-lidar/actions/runs/45536272196) | success |

Les deux workflows valident les tests statiques, les suites JavaScript Web et internationales, le contrat du cycle de vie Android, le test transactionnel de l'installateur, la compilation Kotlin/Gradle, la présence des assets, le contrôle d'intégrité ZIP, `zipalign` et `apksigner` (signature v2 vérifiée).

### Artefacts APK du HEAD 3248ec2

Les builds push et PR ont des empreintes distinctes :

| Événement | Artefact | SHA-256 APK | Taille ZIP artefact | Expiration |
|---|---:|---|---:|---|
| Push | [14986489107](https://github.com/Jickssa/megalith-lidar/actions/runs/45536266046/artifacts/14986489107) | `d196e2c0637e97916d72a481c4de7ffc6c8d51f19233f1484440724d9c18f6a2` | 19 009 377 octets | 2026-12-09 02:55 UTC |
| PR | [14987515465](https://github.com/Jickssa/megalith-lidar/actions/runs/45536272196/artifacts/14987515465) | `73f86fc443b7e5c55839ee627fd8de436cdfa19a448822cc54a4429d91810fbb` | 19 009 377 octets | 2026-12-09 02:55 UTC |

SHA-256 des ZIP d'artefacts :
- Push : `16bd1c23a7d83400dd7e0300844685bbcc8c16ca49b3b2cb947548884fbf6fe9`.
- PR : `eacc078abc4e9cbad7d90524a986b9ccd4487d84db65e5bcf012cd14d2583414`.

Ne pas assimiler les APK issues des deux builds distincts ni confondre l'empreinte du ZIP avec celle de l'APK.


## Contrats de profils territoriaux renforcés

Le schéma et le validateur contrôlent désormais la forme des bornes WGS84 `[ouest, sud, est, nord]`, l'inclusion du centre de carte, l'ordre `minZoom ≤ zoom ≤ maxZoom`, la cohérence de la langue par défaut entre catalogue et profil, les noms pour les langues déclarées et l'unicité des identifiants de sources. Les tests internationaux exercent ces invariants sur FR et GB.


## Validation finale des profils territoriaux — HEAD 96e0587

Les profils France et GB ont été contrôlés sur le nouveau schéma : bornes WGS84 en ordre `[ouest, sud, est, nord]`, centre contenu dans l'emprise, niveaux de zoom ordonnés, langue par défaut cohérente entre catalogue et profil, nom traduit pour chaque langue déclarée et identifiants de sources uniques.

Push : [45536902889](https://github.com/Jickssa/megalith-lidar/actions/runs/45536902889) — success.  
PR #2 : [45536912586](https://github.com/Jickssa/megalith-lidar/actions/runs/45536912586) — success.

Les deux workflows valident les tests internationaux, le paquet, le rollback installateur, la syntaxe JS/Python, la compilation Android, les assets APK, le CRC ZIP, `zipalign` et `apksigner` (signature v2).

| Événement | Artefact | SHA-256 APK | Taille ZIP artefact | Expiration |
|---|---:|---|---:|---|
| Push | [14987695617](https://github.com/Jickssa/megalith-lidar/actions/runs/45536902889/artifacts/14987695617) | `7efa312d329a65fbad5a318ebea0a474224188eadd7ce27e00fac6f809691db9` | 19 010 702 octets | 2026-12-09 03:01 UTC |
| PR | [14987163255](https://github.com/Jickssa/megalith-lidar/actions/runs/45536912586/artifacts/14987163255) | `806879d68e275e47f754a2f690a03fcb74f6ce00f7fdccf58853532f615b78a8` | 19 010 696 octets | 2026-12-09 03:01 UTC |

SHA-256 des ZIP d'artefacts :
- Push : `7f6e025e3b6ca6c5d5ab0e44b8eb8d6d925ad751b28058e1b861f4a2b926b505`.
- PR : `1ecbfd790547e78681c737fcda5228982eefd12e66ef88d8792c3cec85e2b3cf`.

Les APK push et PR sont issues de builds séparés ; leurs empreintes ne sont pas supposées identiques.
