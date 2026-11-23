# Validation et recette — Monolith France

## CI automatisée vérifiée — commit `fd1d68e`

Runs vérifiés sur la tête de branche :
- Push #88 : deux jobs réussis.
- Pull request #89 : deux jobs réussis.
- Validation spécifique du paquet : réussie.
- Syntaxe JavaScript : réussie.
- Tests unitaires Node : réussis.
- Syntaxe Python / compilation des scripts : réussies.
- Test de régression de l'installateur Android : réussi, y compris le chemin de callback du sélecteur de fichiers.
- Compilation Gradle `assembleDebug` : réussie.
- Contrôle CRC de l'APK : réussi.
- `zipalign -c -v 4` : réussi.
- `apksigner verify --verbose` : réussi, signature APK v2 valide.

Run PR : https://github.com/Jickssa/megalith-lidar/actions/runs/45095513607

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

## Régression installateur Android

La fixture reproduit l'hôte Android et valide :
- l'absence de régression sur le démarrage France et l'atlas britannique ;
- l'injection après régénération des assets ;
- la sauvegarde des sources modifiées et la réinstallation forcée ;
- l'idempotence du hook ;
- le callback WebView explicitement libéré (`onReceiveValue(null)`) quand Android ne peut pas démarrer le sélecteur ;
- l'exclusion Git du dossier de sauvegarde `.monolith-france-backups/`.

Les runs #84–#87 ont révélé deux défauts dans le fixture (nom de méthode et échappement de chaîne). Les tests ont été corrigés ; runs #88 et #89 verts. Ces quatre échecs intermédiaires n'ont pas été des échecs de compilation Android.

## Contrôle direct de l'APK run #89

Artefact téléchargé depuis GitHub Actions et inspecté directement :
- ZIP de l'artefact valide ;
- CRC interne de l'APK valide ;
- 94 entrées APK ;
- assets UK et France attendus présents ;
- sélecteur de recherche sans option POI IGN « mégalithe » ;
- fonctions de validation GeoJSON et limites de stockage présentes dans le JavaScript embarqué ;
- PNG Leaflet décodables, visibles et aux dimensions attendues.

APK Debug :
- Taille : 19 010 059 octets.
- SHA-256 : `8c6de9c70e0a6c5da85f7c1818c98ddffa2ddf70320c04550529b540b478bcb1`.
- Checksum de l'artefact : correspondance exacte.
- Artefact GitHub ID : `14783575119`.
- URL : https://github.com/Jickssa/megalith-lidar/actions/runs/45095513607/artifacts/14783575119

## Tests non exécutés

Aucun essai sur téléphone physique ou émulateur n'est revendiqué. La compilation et les tests unitaires ne prouvent pas le comportement WebView en réseau réel. Restent à effectuer :
- installation et lancement sur appareil ;
- affichage réel des tuiles WMTS ;
- requêtes IGN / Overpass à travers WebView ;
- permission et géolocalisation ;
- annulation réelle du sélecteur Android et sélection d'un GeoJSON ;
- export natif et ouverture du partage ;
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
9. Ouvrir le sélecteur Android, l'annuler, puis refaire l'opération et sélectionner un GeoJSON.
10. Exporter les observations, ouvrir le partage Android et vérifier la réimportation du fichier exporté.
11. Tester une panne réseau, une latence, une erreur HTTP et le retour à la carte après échec.
12. Vérifier l'absence de régression de l'atlas britannique.

## Limites scientifiques et de couverture

- La recherche POI IGN « mégalithe » reste désactivée tant que le schéma API n'est pas validé.
- La détection IA France reste désactivée ; aucun modèle britannique n'est réutilisé.
- La couverture LiDAR HD est progressive.
- Les données IGN, OSM et les catalogues patrimoniaux ne sont pas un inventaire archéologique exhaustif.
- Aucun score de détection ou de performance archéologique française n'est revendiqué.
