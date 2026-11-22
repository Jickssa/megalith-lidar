# Validation et recette

## Tests exécutés dans cet environnement

- JSON des trois configurations : parsable.
- Validation spécifique du paquet : réussie.
- `node --check web/app.js` : réussi.
- `py_compile` des scripts Python et du test : réussi.
- Test d'intégration factice : réussit sur dry-run, installation, START_URL France, ressources, hook Gradle et réinstallation forcée sans duplication.
- XML fragments Android : bien formés.
- PNG Leaflet : décodables.
- Archive ZIP : CRC OK.

## Tests non exécutés

- Construction Gradle réelle / APK.
- Validation cryptographique de signature via `apksigner`.
- Installation et parcours sur téléphone.
- Requêtes réelles IGN/Overpass depuis WebView Android : à vérifier avec la politique CORS des services.
- Qualité scientifique de détection de sites inconnus : non revendiquée, détecteur désactivé.

## Recette sur téléphone

1. Installer la build Debug sur appareil de test.
2. Vérifier l'écran France et le lien « Atlas initial ».
3. Activer successivement les couches MNT, MNS et MNH à plusieurs zooms et emprises.
4. Tester une recherche de mégalithe, une recherche de lieu et une recherche OSM.
5. Tester le refus puis l'octroi de permission de localisation.
6. Ajouter une observation, fermer/réouvrir l'application, exporter et réimporter le GeoJSON.
7. Tester réseau absent, lenteur, erreur 429/5xx et réponse CORS refusée ; vérifier qu'aucune erreur n'est présentée comme absence archéologique.
