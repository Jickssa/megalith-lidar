# Inspection de l'APK fourni — uk.megalith.lidar.apk

- Taille : 13 987 047 octets.
- SHA-256 : `cf6362d6c5513c08740f2b0f58ac3178f29b11f0584117a2b3bd2911d6bdd3dd`.
- Package : `uk.megalith.lidar`.
- Version : 3.2.0 (`versionCode` 320).
- `minSdk` 26 ; `targetSdk` 35 ; `compileSdk` déclaré 35.
- Activity de lancement : `uk.megalith.lidar.MainActivity`.
- Permissions : INTERNET, ACCESS_COARSE_LOCATION, ACCESS_FINE_LOCATION.

L'APK contient `assets/web/index.html`, `assets/web/leaflet/leaflet.js` et `leaflet.css`. La bibliothèque est Leaflet 1.9.4. Le HTML utilise ces deux chemins relatifs. Le dossier d'images PNG référencé par la feuille de style ne se trouve pas dans l'APK fourni ; le module ajoute des images de repli décodables à l'emplacement attendu.

Le manifeste Android est un binaire AXML, pas un XML texte. La signature contient des marqueurs de schéma v2/v3 ; la validation cryptographique complète avec `apksigner` n'a pas été exécutée dans l'environnement d'analyse.

Le binaire n'est pas modifié par l'intégrateur. Une reconstruction depuis les sources est nécessaire. Une APK reconstruite avec un certificat différent ne peut pas mettre à jour en place une APK existante portant une autre signature.
