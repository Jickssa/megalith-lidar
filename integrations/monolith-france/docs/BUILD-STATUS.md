# État de validation — Monolith France

## 1.2.3 — build validé

- Branche : `feature/monolith-france-1.1.0`
- Commit source : `f44e3b29ef1647e937cdf3c35102ba847cbdb7d6`
- Workflow GitHub Actions push #133 : succès complet — https://github.com/Jickssa/megalith-lidar/actions/runs/45153246084
- Job « Static validation and installer regression » : succès.
- Job « Android Debug APK build » : succès.
- APK vérifiée dans la CI avec contrôle ZIP/CRC, `zipalign` et `apksigner verify`.
- APK récupérée et inspectée localement : 19 023 125 octets, 97 entrées, aucun défaut CRC.
- Présence dans l'APK : sélecteur, introductions France/UK, carte UK historique, carte France et logique JavaScript France.
- SHA-256 APK : `bcba308cc3540c7da51d57d1c9c7ab5d37f848bd4e17ebcf57b468a52b690157`.
- Artefact CI ID `14807357234`, taille archive 18 982 976 octets ; digest archive `f30c54f4f765ae22b23cc0dd2cbbd7e74e3a5910e60f50fde675c7a88438164b`.
- Artefact : https://github.com/Jickssa/megalith-lidar/actions/runs/45153246084/artifacts/14807357234

### Navigation effectivement embarquée

- L'installateur règle le `START_URL` de la copie Android sur `/assets/web/atlas-home.html`. Le fichier source de l'upstream n'est pas modifié par ce changement dans le dépôt.
- Sélecteur → Atlas France : `/assets/web/france/web/index.html`.
- Sélecteur → Atlas UK : `/assets/web/index.html`, interface cartographique historique.
- Atlas UK → sélecteur ; Atlas UK → Atlas France. Le lien qui rechargeait inutilement la page UK a été supprimé.
- L'introduction territoriale UK (`uk-home.html`) est désormais en français. La carte UK historique elle-même reste en anglais ; sa traduction complète n'est pas incluse.
- L'interface cartographique France est en français.

### Durcissement Android

- Téléchargement d'une image diagnostic PNG plafonné à 8 Mio.
- Validation du MIME `image/png` et de la signature binaire PNG.
- Redirections HTTP désactivées pour la source distante fixe.
- Cache diagnostics borné à 64 Mio et 24 fichiers, avec expiration à 30 jours et nettoyage des temporaires.
- Tests statiques et tests de fixture de l'installateur passés.

## Recette encore nécessaire

La compilation et les vérifications d'archive ne remplacent pas une recette sur téléphone. Aucun appareil Android ni émulateur n'était accessible dans l'environnement de développement. Restent à tester : démarrage réel, navigation tactile, géolocalisation, import/export GeoJSON, appels réseau IGN/OSM et comportements portrait/paysage.

La comparaison des certificats de signature entre l'APK installée et l'APK Debug n'est pas démontrée. Ne pas désinstaller l'application existante sans avoir sauvegardé les relevés ; une signature différente empêcherait une mise à jour par-dessus l'installation existante.

La PR #1 reste ouverte en brouillon, non fusionnée. La branche cible `main` est toujours au SHA `ba08b3346895472dd68c27ab5435d614cec64356` ; aucun commit n'y a été poussé.
