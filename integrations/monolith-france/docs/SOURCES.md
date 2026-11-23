# Sources de données et services

- Plan IGN v2 : Géoplateforme WMTS, attribution IGN.
- LiDAR HD : MNT, MNS et MNH ombrés via les capacités WMTS de la Géoplateforme ; disponibilité progressive, à vérifier par dalle.
- Géocodage / POI : service de géocodage Géoplateforme ; le sous-type « mégalithe » doit être résolu depuis la taxonomie du service et non posé arbitrairement comme catégorie racine.
- OpenStreetMap : requêtes Overpass en fonction de l'emprise courante, à partir du zoom 8 ; attribution © OpenStreetMap contributors.
- Mérimée : source documentaire complémentaire, non exhaustive.

Le module ne télécharge pas l'intégralité d'un inventaire national dans l'APK. Les requêtes sont effectuées à la demande et nécessitent une connexion.


## Vérification des identifiants WMTS — novembre 2026

Les noms techniques configurés sont confirmés par la documentation IGN pour les flux ombragés LiDAR HD : MNT `IGNF_LIDAR-HD_MNT_ELEVATION.ELEVATIONGRIDCOVERAGE.SHADOW`, MNS `IGNF_LIDAR-HD_MNS_ELEVATION.ELEVATIONGRIDCOVERAGE.SHADOW`, MNH `IGNF_LIDAR-HD_MNH_ELEVATION.ELEVATIONGRIDCOVERAGE.SHADOW`. Le fond `GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2` apparaît également dans les mises à jour des ressources WMTS. Cette vérification valide les identifiants, pas la disponibilité de chaque tuile à une coordonnée donnée.

Références :
- https://cartes.gouv.fr/aide/fr/partenaires/ign/generalites-ign/actualites/2025-03-lidarhd-et-produits-derives/
- https://cartes.gouv.fr/aide/fr/partenaires/ign/generalites-ign/actualites/2026-08-mises-a-jour/
