# Validation 1.3.1 — recherche française, sources et CI

## Recherche OSM implémentée

- Six familles taxonomiques, chacune avec règles tag et champs de texte configurés.
- Règles composées multi-tags afin d'éviter qu'un tag générique renvoie tous les sites archéologiques.
- Requêtes par emprise actuelle, déclinées pour nodes, ways et relations.
- Texte appliqué aux noms, noms français, références et sous-types par catégorie.
- Regex utilisateur échappées avant encodage de la chaîne Overpass.
- Résultats normalisés avec coordonnées, type/ID OSM et URL source.
- Déduplication par identifiant stable.
- Emprise excessive refusée, requêtes antérieures annulées et réponses périmées ignorées.

## Sources OSM vérifiées

- `archaeological_site=megalith` requiert `historic=archaeological_site` ; combinaisons utiles : `name=*`, `megalith_type=*`.
- `archaeological_site=roman_villa` et `archaeological_site=fortification` sont également documentés comme sous-types de `historic=archaeological_site`.
- `man_made=cairn` peut identifier des cairns de repérage, pas nécessairement des structures archéologiques ; ce tag est donc exclu des familles automatiques.
- Les résultats OSM restent des données contributives, à recouper avec les sources patrimoniales et les données de terrain.

Sources :
- https://wiki.openstreetmap.org/wiki/Tag:archaeological_site%3Dmegalith
- https://wiki.openstreetmap.org/wiki/Tag:archaeological_site%3Droman_villa
- https://wiki.openstreetmap.org/wiki/Tag:archaeological_site%3Dfortification
- https://wiki.openstreetmap.org/wiki/Tag:historic%3Darchaeological_site
- https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dcairn

## IGN

- Géocodage direct et POI autocomplete restent séparés.
- L'autocomplétion POI utilise `/geocodage/completion/`; le `poiType` doit provenir de GetCapabilities.
- L'activation live du POI mégalithe n'est pas déclarée tant que le schéma n'est pas interrogé et testé réellement.
- Une recherche géocodage ou POI ne constitue pas un inventaire archéologique exhaustif.

## CI / APK

- Push workflow #? ID `45180531041` : succès.
- PR workflow #? ID `45180547052` : succès à confirmer au besoin, même commit.
- Gradle, vérifications ZIP, alignement et signature : succès.
- APK 1.3.1 : 19 027 801 octets, 97 entrées, CRC valide.
- SHA-256 : `1ff35b618e67a5afc559106daccd5c5d01bb6a26f066df0834aab29ea7b6ce92`.

## Recette restante

Tests réseau réels des services externes et recette sur téléphone Android non réalisés dans cet environnement. Aucune installation par-dessus l'application existante n'est recommandée avant sauvegarde et vérification de signature.
