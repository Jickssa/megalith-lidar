# Contribuer à un nouveau pays — Monolith International

## État actuel

Les seuls profils opérationnels fournis sont la France métropolitaine et le Royaume-Uni. Les autres territoires ne sont pas déclarés fonctionnels.

## Contenu requis

1. Profil pays JSON conforme à `country-profile.schema.json`.
2. Code ISO, CRS et emprise géographique documentés.
3. Centre et niveaux de zoom.
4. Langues réellement traduites.
5. Sources cartographiques, altimétriques et patrimoniales avec couverture, attribution et licence.
6. Taxonomie locale et références vérifiables.
7. Exemples de données non sensibles et tests reproductibles.

## Règles

- Ne pas transposer les modèles ou métriques d'un autre pays.
- Ne pas annoncer une couche LiDAR sans vérifier ses capacités, sa disponibilité et sa licence.
- Ne pas assimiler une présence OSM à une validation archéologique.
- Ne pas inclure de données sans droit de réutilisation.
- Ne pas publier de coordonnées précises de sites sensibles.
- Ne pas déclarer un profil actif avant validation de ses sources, de ses tests et de son interface.

## Structure proposée

```
config/countries/XX/profile.json
config/languages/xx-XX.json
config/taxonomies/XX.json
community/data/XX/
community/tests/XX/
```

## Processus GitHub

1. Fork du dépôt.
2. Branche dédiée.
3. Profil, traduction, taxonomie, sources, licences et tests.
4. Exécution du validateur.
5. Pull Request en brouillon avec un rapport de couverture.
6. Corrections des tests et commentaires avant activation.

## Import

L'installation de paquets ZIP territoriaux dans l'application n'est pas encore activée. Les contributions sont actuellement proposées par pull request ; n'importe quel ZIP ne doit pas être installé dans l'APK.
