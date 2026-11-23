# Validation 1.3.0 — recherche française et CI

## Implémentation présente

- La taxonomie décrit six familles OSM et leurs règles de recherche.
- La catégorie sélectionnée commande les clauses Overpass.
- Le texte saisi est ajouté comme filtre sur les noms.
- Les requêtes incluent nodes, ways et relations.
- Les résultats sont normalisés avec type, identifiant OSM, coordonnées et lien vers la source.
- Les emprises trop importantes sont refusées.
- Les recherches antérieures sont annulées ; les réponses asynchrones périmées ne remplacent pas les résultats courants.
- La recherche de lieux IGN reste séparée de la recherche OSM.
- Le service d'autocomplétion POI est déclaré sur son endpoint dédié ; le type POI doit être découvert, non inventé.

## Tests déterministes ajoutés

- taxonomie et unicité des identifiants ;
- construction de l'emprise ;
- requêtes Overpass par catégorie ;
- échappement des valeurs ;
- filtre textuel ;
- nodes/ways/relations ;
- rejet d'emprise excessive ;
- conversion d'objet OSM et liens sources ;
- URL d'autocomplétion POI IGN.

## Vérifications encore nécessaires

- Exécuter la suite Node et le validateur sur le commit complet.
- Vérifier par tests réseau les réponses réelles d'Overpass et de l'IGN.
- Interroger GetCapabilities POI et contrôler le type correspondant aux mégalithes avant d'activer cette recherche.
- Interroger les capacités WMTS et valider les couches en emprises connues.
- Vérifier l'interface sur Android.
- Vérifier les fonctions originales UK après compilation.

Aucun résultat réseau ni test physique n'est déclaré réussi sans exécution réelle.
