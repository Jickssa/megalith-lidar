# État de validation — Monolith France

## 1.2.4 — build validé

- Branche : `feature/monolith-france-1.1.0`
- Commit source fonctionnel : `bcbbed71345df0ee7ee09eb53bbf58a3c87bb26b`
- Workflow GitHub Actions push #146 : succès complet — https://github.com/Jickssa/megalith-lidar/actions/runs/45154564962
- Validation du paquet, syntaxe JS/Python, tests Node et fixture de l'installateur : succès.
- Gradle `assembleDebug` : succès.
- Vérification du contenu APK, `zipalign` et `apksigner verify` : succès.
- APK : 19 024 313 octets, 97 entrées ZIP, aucune erreur CRC.
- SHA-256 APK : `34804ea112838dfced2260801b262f6e186e75af1d588427b3e113ea7654677a`.
- Artefact CI ID `14807004053`, taille archive 18 984 152 octets, digest SHA-256 `5fa1fad050c6a1f9e09dd1932679110e3541195351588a934071789147450bd6`.
- Artefact : https://github.com/Jickssa/megalith-lidar/actions/runs/45154564962/artifacts/14807004053

### Navigation et adaptation territoriale

- L'installateur règle le démarrage Android sur `/assets/web/atlas-home.html`.
- Sélecteur → Atlas France : `/assets/web/france/web/index.html`.
- Sélecteur → Atlas UK : `/assets/web/index.html`, interface cartographique historique.
- Atlas UK → sélecteur ; Atlas UK → Atlas France. Aucun lien ne recharge inutilement la carte UK.
- L'introduction UK (`uk-home.html`) est en français ; la carte UK historique reste en anglais.
- L'interface de l'Atlas France est en français.

### Recherche et couches

- Géocodage IGN direct filtré par `terr=METROPOLE`, avec plafond de 30 résultats contrôlé par configuration.
- Seuil minimal de zoom de la recherche OSM lu depuis la configuration ; valeur validée : 8.
- Les paramètres et les routes produites sont couverts par les tests unitaires JavaScript.
- Identifiants des couches Plan IGN v2 et LiDAR HD MNT/MNS/MNH recoupés dans la documentation actuelle de l'IGN/Géoplateforme.
- La couverture LiDAR HD reste progressive ; une couche sans tuiles sur une zone n'indique pas l'absence de données archéologiques.

### Durcissement Android

- PNG diagnostic : 8 Mio maximum par fichier, MIME et signature contrôlés, redirections désactivées.
- Cache diagnostic : 64 Mio maximum, 24 fichiers, expiration à 30 jours, nettoyage des temporaires.
- Pont d'export : taille et MIME bornés, écriture asynchrone et nom temporaire unique.

## Recette encore nécessaire

La compilation et les vérifications d'archive ne remplacent pas une recette sur téléphone. Aucun appareil Android ni émulateur n'était accessible dans l'environnement de développement. Restent à tester : démarrage réel, navigation tactile, géolocalisation, import/export GeoJSON, appels réseau IGN/OSM et comportements portrait/paysage.

La comparaison des certificats de signature entre l'APK installée et l'APK Debug n'est pas démontrée. Ne pas désinstaller l'application existante sans avoir sauvegardé les relevés ; une signature différente empêcherait une mise à jour par-dessus l'installation existante.

La PR #1 reste ouverte en brouillon, non fusionnée. La branche cible `main` est toujours au SHA `ba08b3346895472dd68c27ab5435d614cec64356` ; aucun commit n'y a été poussé.
