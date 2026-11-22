# État de validation — Monolith France

## État GitHub

- Branche de travail : `feature/monolith-france-1.1.0`.
- PR #1 : ouverte, en brouillon, non fusionnée ; cible `main`.
- Aucune modification n'a été poussée sur `main`.
- Commit source testé par le dernier build : `946d3125d88fb671b192a7b77a17bdf26ffa1f0b`.

## Dernier build Android validé

- Workflow GitHub Actions : run PR #75 — succès intégral.
- Run : https://github.com/Jickssa/megalith-lidar/actions/runs/45083702285
- Environnement : Temurin JDK 17, Android Platform 35, Build Tools 35.0.0.
- Commande : `./android/gradlew -p android assembleDebug --no-daemon --stacktrace --warning-mode all`.
- L'installateur a été exécuté sur le véritable checkout Android avant Gradle.
- APK Debug : `megalith-lidar-france-debug.apk`.
- Taille : 19 007 219 octets.
- SHA-256 : `fc8562ecf9b34cdfeed67cc31cb933cd870f70f6ddf55d556c1d2b1c4e0b48a9`.
- ZIP interne : CRC valide, 94 entrées.
- Ressources UK, France, JavaScript/CSS Leaflet et configuration France présentes.
- L'APK embarque uniquement les modes UI IGN « Lieu / adresse » et OSM « Archéologie » ; l'option POI IGN « mégalithe » non validée est absente.
- Les cinq images Leaflet intégrées sont décodables, non transparentes et à leurs dimensions attendues.
- `zipalign -c -v 4` : succès.
- `apksigner verify --verbose` : succès, signature APK v2 valide.
- Artefact GitHub Actions ID : `14778635318`.
- URL de l'artefact : https://github.com/Jickssa/megalith-lidar/actions/runs/45083702285/artifacts/14778635318
- Expiration annoncée : 6 décembre 2026.

## Contrôles automatisés du run #75

Les deux jobs sont terminés avec succès :

1. **Static validation and installer regression**
   - validateur du paquet ;
   - syntaxe JavaScript ;
   - syntaxe Python ;
   - fixture de régression de l'installateur ;
   - contrôle des dimensions et du canal alpha des images Leaflet après copie dans les assets Android.

2. **Android Debug APK build**
   - installation du module France ;
   - compilation Gradle ;
   - contrôle des ressources APK et du CRC ;
   - vérification d'alignement et de signature ;
   - dépôt de l'APK et de son fichier SHA-256.

## Corrections incluses dans le build #75

- Le sélecteur ne propose plus le POI IGN « mégalithe » tant que son schéma de recherche n'est pas validé.
- Le géocodage IGN est le mode de recherche par défaut ; la recherche OSM se fait sur l'emprise cartographique.
- Le gestionnaire refuse explicitement les modes inconnus.
- Les cinq PNG Leaflet de substitution 1×1 ont été remplacés par les ressources de distribution officielle Leaflet 1.9.4.
- Le validateur vérifie les dimensions attendues et refuse les images entièrement transparentes.
- Le test de régression vérifie les images après génération effective des assets Android.
- Le fichier de licence BSD 2-Clause Leaflet reste inclus dans le module.

## Sources IGN

Les identifiants WMTS MNT, MNS et MNH sont documentés par l'IGN. Leur disponibilité réelle reste dépendante de la couverture publiée pour chaque emprise :
- https://cartes.gouv.fr/aide/fr/partenaires/ign/generalites-ign/actualites/2025-03-lidarhd-et-produits-derives/
- https://cartes.gouv.fr/aide/fr/partenaires/ign/generalites-ign/actualites/2025-10-mises-a-jour/

## Recette non effectuée sur appareil

La compilation et les contrôles d'archive ne remplacent pas un test fonctionnel sur téléphone ou émulateur. Restent à vérifier :
- installation, démarrage et navigation vers l'atlas britannique ;
- rendu effectif des tuiles IGN WMTS et comportement sur les zones non couvertes ;
- géocodage IGN et requêtes Overpass depuis la WebView ;
- autorisation et géolocalisation ;
- ajout, suppression et persistance des observations ;
- import GeoJSON depuis le sélecteur Android et export par le pont natif ;
- fonctionnement réseau, erreurs et performances sur appareil réel.

## Limites connues

- La recherche POI IGN dédiée au sous-type mégalithe reste désactivée.
- La détection IA française reste désactivée : aucun modèle britannique n'est réutilisé comme détecteur français.
- La couverture LiDAR HD est progressive et ne forme pas un inventaire archéologique.
- OSM et les catalogues patrimoniaux ne sont pas exhaustifs.
- Les services distants nécessitent une connexion ; le mode hors ligne n'est pas garanti.

## Prochaine étape

Effectuer la recette fonctionnelle sur un appareil Android, consigner les résultats et corriger les éventuels défauts constatés avant de sortir la PR du brouillon. Ne pas fusionner sans cette validation.
