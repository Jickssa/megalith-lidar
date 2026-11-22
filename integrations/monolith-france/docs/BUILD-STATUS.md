# État de validation — Monolith France

## Références GitHub

- Branche : `feature/monolith-france-1.1.0`.
- PR #1 : brouillon, ouverte, non fusionnée.
- Branche `main` non modifiée.
- Build initial validé sur le commit `175bbc22bcf8cd8c093d28539c36ec209c9d1c35`.
- Workflow push #60 : succès.
- Workflow pull request #61 : succès.

## Build Android réellement effectué

- Environnement GitHub Actions : Temurin JDK 17.0.21, Android Platform 35 et Build Tools 35.0.0.
- Commande : `./gradlew assembleDebug --no-daemon --stacktrace`.
- Installateur exécuté sur le véritable checkout Android avant Gradle.
- APK Debug générée : `megalith-lidar-france-debug.apk`.
- Taille APK : 18 994 407 octets.
- SHA-256 : `fad8b092bd53cdb791ef036bb6f321adc48791e4115bc96bd48e637f0e292c78`.
- ZIP interne : test CRC valide.
- Ressources UK, France et Leaflet attendues présentes.
- `zipalign -c -v 4` : succès.
- `apksigner verify --verbose` : succès, signature APK v2 valide, un signataire.
- Artefact GitHub Actions ID : `14776914469`, rétention annoncée jusqu'au 6 décembre 2026.

## Validation CI

- Workflow #60 (push) : succès.
- Workflow #61 (pull request) : succès.
- Validateur paquet, JavaScript, Python et test de régression installateur : succès.
- Installateur exécuté sur le vrai projet Android : succès.
- Génération des assets après nettoyage : vérifiée par fixture.
- Réinstallation forcée et sauvegardes hors ressources Android : vérifiées.

## Défaut détecté après inspection APK

L'interface embarquée exposait encore l'option « Mégalithes IGN », alors que le gestionnaire JavaScript refusait déjà cette recherche faute de schéma API IGN validé. Cette incohérence a été corrigée sur la branche de travail après le build #60 :

- seuls les modes de géocodage IGN et de recherche OSM sont exposés ;
- le mode par défaut est le géocodage IGN ;
- le POI IGN « mégalithe » est présenté explicitement comme désactivé ;
- le gestionnaire de recherche rejette tout mode non pris en charge ;
- le validateur du paquet impose le mode par défaut `place` et l'absence de l'option POI non validée.

**Ces derniers changements nécessitent une nouvelle exécution CI et une nouvelle APK ; le SHA APK ci-dessus correspond à la version précédente, qui n'intègre pas cette dernière correction UI.**

## Fonctions non validées en conditions réelles

- Installation et lancement sur téléphone ou émulateur Android.
- Affichage réel des tuiles WMTS IGN et validation de la couverture pour une emprise donnée.
- Géocodage IGN et requêtes Overpass depuis la WebView en réseau réel.
- Permission et géolocalisation en fonctionnement.
- Import GeoJSON par sélecteur Android et export via le pont natif.
- Persistance des observations après arrêt/redémarrage.
- Performance et gestion des erreurs réseau sur appareil.

## Limites fonctionnelles connues

- La recherche POI IGN dédiée au sous-type mégalithe reste désactivée jusqu'à validation du schéma API.
- La détection IA française est désactivée ; aucun modèle britannique n'est réutilisé.
- La couverture LiDAR HD est progressive.
- Les icônes PNG Leaflet du paquet sont des images de repli, pas les icônes officielles finales.
- Les appels cartographiques et de recherche nécessitent une connexion réseau.

## Prochaine étape

Exécuter GitHub Actions sur la dernière tête de branche, regénérer l'APK après la correction UI, vérifier son SHA et ses signatures, puis procéder à la recette appareil avant de déclarer la PR prête.
