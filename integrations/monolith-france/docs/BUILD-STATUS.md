# État de validation — Monolith France

## État du dépôt

- Branche : `feature/monolith-france-1.1.0`.
- PR : #1, brouillon, non fusionnée.
- La branche `main` conserve le code amont ; cette PR ne la modifie pas.
- Le module France est une interface cartographique expérimentale.

## Vérifications effectivement observées

- Le précédent run GitHub Actions a exécuté et réussi le validateur de paquet.
- Le contrôle syntaxique JavaScript a réussi.
- Le job a échoué à l'étape de compilation Python, car le workflow appelait un chemin de tests inexistant : `integrations/monolith-france/tests/*.py`.
- Le test a ensuite été déplacé/maintenu dans `integrations/monolith-france/scripts/test_android_installer.py`, et le workflow corrigé pour utiliser ce chemin.
- Un nouvel essai Actions reste à examiner avant de déclarer la CI verte.

## Tests non réputés exécutés

- Compilation Gradle réelle de l'APK France.
- Vérification de signature de l'APK final par `apksigner`.
- Installation sur appareil ou émulateur Android.
- Test interactif des couches WMTS et des appels de recherche depuis la WebView.
- Validation de bout en bout de l'import/export GeoJSON depuis Android.

## Capacités et limites actuelles

- La carte France, les fonds IGN/OSM, les commandes des couches LiDAR et le carnet local sont présents dans le module.
- Les identifiants de couches WMTS n'ont pas encore été validés par une recette Android réelle.
- La recherche géographique IGN doit être testée avec le service réel depuis WebView.
- La recherche spécifique du sous-type POI mégalithe IGN est désactivée tant que la résolution catégorie/paramètre n'est pas confirmée.
- La recherche OSM est disponible à la demande mais nécessite réseau et une emprise suffisamment zoomée.
- Les observations sont stockées dans `localStorage` ; la persistance dépend de la configuration et du cycle de vie WebView, elle doit être testée sur appareil.
- Les icônes Leaflet du paquet sont des PNG de repli, pas les visuels de marque originaux ; ils doivent être remplacés par les ressources officielles Leaflet sous licence adéquate avant livraison UI finale.
- Aucun APK final n'est joint ou annoncé ici.

## Prochaine validation Android

Exécuter `scripts/integrate_and_build_codespace.sh` depuis un Codespace avec JDK 17 et Android SDK Platform 35 / Build Tools 35.0.0. Examiner les logs Gradle, vérifier les assets internes de l'APK, puis effectuer la recette appareil avant de sortir la PR du mode brouillon.
