# État de validation — Monolith France

## État GitHub

- Dépôt : `Jickssa/megalith-lidar`.
- Branche : `feature/monolith-france-1.1.0`.
- PR #1 : ouverte, en brouillon, non fusionnée ; cible `main`.
- Aucun changement poussé sur `main`.
- Commit fonctionnel testé : `7a1cdd3776a4d1f4494f7c70520227b2388ab50e`.
- Les modifications documentaires postérieures doivent être distinguées du code déjà compilé dans l'APK.

## Navigation commune des atlas — paquet 1.1.3

- Démarrage Android : `/assets/web/atlas-home.html`.
- Atlas France : `/assets/web/france/web/index.html`.
- Atlas britannique : `/assets/web/index.html`, chemin historique conservé.
- L'écran d'accueil présente deux cartes d'accès internes, France et Royaume-Uni.
- L'index britannique n'est ni déplacé ni écrasé, préservant ses chemins relatifs et références aux jeux de données.
- L'en-tête France propose « Choisir un atlas » et le lien direct vers le Royaume-Uni.
- L'installateur reconnaît les anciennes URL de démarrage UK et France et migre vers l'écran commun.

## Dernier build Android téléchargé et inspecté

- Run push #110 : succès complet.
- Run PR #111 : succès complet.
- Run push : https://github.com/Jickssa/megalith-lidar/actions/runs/45097292720
- Run PR : https://github.com/Jickssa/megalith-lidar/actions/runs/45097297817
- Commit testé : `7a1cdd3776a4d1f4494f7c70520227b2388ab50e`.
- Environnement : JDK 17, Android Platform 35, Build Tools 35.0.0.
- Installateur exécuté sur le véritable checkout Android : succès.
- Gradle `assembleDebug` : succès.
- APK Debug : `megalith-lidar-france-debug.apk`.
- Taille : 19 010 091 octets.
- SHA-256 : `4ef84499c4e3a5d26515d5bc991cb3fd7f5c1695232a67539de03af92517956c`.
- ZIP de l'artefact : CRC valide.
- ZIP de l'APK : CRC valide, 95 entrées.
- Les trois pages attendues sont présentes :
  - `assets/web/atlas-home.html`
  - `assets/web/index.html` (Atlas britannique)
  - `assets/web/france/web/index.html` (Atlas France)
- L'accueil contient les deux destinations ; l'Atlas France contient les liens « Choisir un atlas » et « Atlas britannique ».
- Le fichier britannique reste à son emplacement historique.
- CI : vérifications ZIP, `zipalign` et `apksigner verify` réussies ; signature APK v2.
- Artefact GitHub Actions ID : `14783892920`.
- URL : https://github.com/Jickssa/megalith-lidar/actions/runs/45097292720/artifacts/14783892920
- Empreinte de l'archive artefact : `e4de90349637f078773c96114e3e8682bd5a4426c04b6ab7073c3a187555fd57`.

## CI et corrections de l'installateur

Les deux workflows du commit fonctionnel sont verts :

1. Run push #110 : succès.
2. Run pull_request #111 : succès.

Le job statique couvre :
- validation du paquet ;
- syntaxe JavaScript ;
- tests Node GeoJSON ;
- syntaxe Python ;
- fixture installateur (préparateur synthétique et insertion syntaxique du hook dans le préparateur amont réel).

Le job Android couvre :
- installateur sur le vrai checkout Android ;
- compilation Gradle ;
- vérification des ressources APK et CRC ;
- `zipalign` ;
- `apksigner verify` ;
- dépôt de l'APK et du checksum.

### Historique des échecs intermédiaires

- #92/#93 : assertion HTML incorrecte dans le fixture initial.
- #94/#95 : le validateur ne connaissait pas la route commune `atlas-home.html`.
- #96/#97 : l'installateur recherchait une fin de ligne incorrectement échappée.
- #98/#99 : même défaut de hook au stade de la migration documentaire.
- #100/#101 : double échappement dans le garde-fou de fin de ligne.
- #102/#103 : scénario de fixture exécutant le préparateur complet sans ses données et dépendance OsmAnd.
- #104/#105 : chemin d'installateur mal référencé après copie de l'arborescence runtime.
- #106/#107 : signature de fonction annotée non reconnue.
- #108/#109 : test de fixture utilisant une mauvaise référence de script source.
- #110/#111 : succès complet après correction des points ci-dessus.

Aucun de ces échecs intermédiaires n'a été présenté comme build APK réussi.

## Correctifs antérieurs conservés

- Import GeoJSON limité à 20 Mio ; FeatureCollection, points WGS84 et propriétés validés.
- Plafond local cumulé de 5 000 observations.
- État mémoire conservé si la persistance échoue.
- Tests Node pour les règles GeoJSON et stockage.
- PNG Leaflet 1.9.4 officiels, dimensions et alpha vérifiés.
- Callback WebView annulé proprement si le sélecteur Android ne peut pas s'ouvrir.
- Sauvegardes de l'installateur exclues de Git.
- POI IGN « mégalithe » désactivé tant que le schéma n'est pas validé.
- Détection IA française désactivée ; aucun modèle britannique n'est réutilisé.

## Recette physique non réalisée

L'utilisateur a testé une APK antérieure et a confirmé la qualité du rendu. La nouvelle navigation 1.1.3 n'a pas encore été retestée sur son téléphone ; aucun essai physique de cette version n'est revendiqué.

À contrôler :
- installation et démarrage sur l'écran commun ;
- parcours accueil → France, accueil → UK, France → accueil et France → UK ;
- chargement des datasets et fonctions existantes de l'Atlas britannique ;
- affichage réel MNT/MNS/MNH, géocodage IGN, Overpass et permissions ;
- stockage après redémarrage, import/export et annulation du sélecteur ;
- comportement réseau et retour arrière Android.

## Limites fonctionnelles

- Les couches LiDAR dépendent de la couverture publiée et des services distants.
- La recherche POI IGN dédiée aux mégalithes reste désactivée.
- La détection IA France reste absente.
- OSM et les catalogues patrimoniaux ne constituent pas un inventaire archéologique exhaustif.
- Les fonctions qui ne sont pas encore implémentées ne sont pas présentées comme disponibles.

## Prochaine étape

Installer cette APK sur le téléphone de test et valider le nouveau sélecteur et les quatre parcours. Corriger les anomalies observées. Garder la PR en brouillon jusqu'à cette recette.
