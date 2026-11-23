# Validation et recette — Monolith France

## CI automatisée vérifiée

Runs PR et push sur le commit applicatif `9049f8142e27a7d3699dfcdad36fac2e41c5355a` :

- Push #80 : succès intégral.
- Pull request #81 : succès intégral.
- Validation spécifique du paquet : réussie.
- Syntaxe JavaScript : réussie.
- Tests unitaires Node : réussis.
- Syntaxe Python / compilation des scripts : réussies.
- Test de régression de l'installateur Android : réussi.
- Compilation Gradle `assembleDebug` : réussie.
- Contrôle CRC de l'APK : réussi.
- `zipalign -c -v 4` : réussi.
- `apksigner verify --verbose` : réussi, signature APK v2 valide.

## Tests unitaires JavaScript — observations GeoJSON

Script CI : `scripts/test_web_logic.js`.

Cas couverts :
- Feature Point WGS84 valide acceptée ;
- longitude hors [-180, 180] et latitude hors [-90, 90] refusées ;
- coordonnées non numériques refusées ;
- géométrie autre que Point refusée ;
- propriétés non conformes refusées, `properties: null` admis ;
- taille de fichier au-delà de la limite refusée ;
- FeatureCollection invalide refusée ;
- taille d'une collection au-delà du plafond par fichier refusée ;
- plafond cumulé de 5 000 observations respecté entre observations existantes et import ;
- comptage séparé des entités invalides et des entités valides écartées par le plafond ;
- valeurs par défaut rétablies si la configuration de stockage est invalide.

## Contrôle direct de l'APK run #81

Artefact téléchargé depuis GitHub Actions et inspecté directement :
- CRC ZIP valide pour l'archive et l'APK ;
- 94 entrées APK ;
- assets UK et France attendus présents ;
- sélecteur de recherche sans option POI IGN « mégalithe » ;
- nouvelles fonctions de contrôle GeoJSON et de stockage présentes dans le JavaScript embarqué ;
- PNG Leaflet décodables, visibles et à leurs dimensions attendues.

APK Debug :
- SHA-256 : `9f49ee1bb86c40ff125cf61cf9fac6064d736c16591f75749aceeba1137e7197`.
- Artefact : https://github.com/Jickssa/megalith-lidar/actions/runs/45094996607/artifacts/14782609107

## Tests non exécutés

Aucun essai sur téléphone physique ou émulateur n'est revendiqué. La compilation et les tests unitaires ne prouvent pas le comportement WebView en réseau réel. Restent à effectuer :
- installation et lancement sur appareil ;
- affichage réel des tuiles WMTS ;
- requêtes IGN / Overpass à travers WebView ;
- permission et géolocalisation ;
- choix d'un GeoJSON via le sélecteur Android et export par le pont natif ;
- persistance après fermeture forcée et redémarrage ;
- comportement en réseau lent, absent, HTTP 429/5xx ou CORS refusé ;
- retour vers l'atlas britannique.

## Recette manuelle sur téléphone

1. Installer l'APK Debug sur l'appareil de test.
2. Vérifier l'écran France, la carte et le lien vers l'atlas britannique.
3. Activer séparément MNT, MNS et MNH sur plusieurs niveaux de zoom et emprises.
4. Tester le géocodage IGN d'une adresse et d'un toponyme.
5. Zoomer au moins au niveau minimal requis puis lancer la recherche OSM.
6. Tester refus puis autorisation de géolocalisation.
7. Ajouter des observations, supprimer un relevé, fermer complètement l'application puis la relancer et vérifier la persistance.
8. Importer un petit GeoJSON valide, un fichier contenant des points invalides et un fichier trop volumineux ; vérifier les messages et les compteurs.
9. Exporter les observations, ouvrir le partage Android et vérifier la réimportation du fichier exporté.
10. Tester une panne réseau, une latence, une erreur HTTP et le retour à la carte après échec.
11. Vérifier l'absence de régression de l'atlas britannique.

## Limites scientifiques et de couverture

- La recherche POI IGN « mégalithe » reste désactivée tant que le schéma API n'est pas validé.
- La détection IA France reste désactivée ; aucun modèle britannique n'est réutilisé.
- La couverture LiDAR HD est progressive.
- Les données IGN, OSM et les catalogues patrimoniaux ne sont pas un inventaire archéologique exhaustif.
- Aucun score de détection ou de performance archéologique française n'est revendiqué.
