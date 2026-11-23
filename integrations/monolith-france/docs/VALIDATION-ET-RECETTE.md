# Validation 1.2.4 — navigation, sécurité et recherche territoriale

## Navigation embarquée

- Le sélecteur Android ouvre directement les deux interfaces cartographiques : `/assets/web/france/web/index.html` et `/assets/web/index.html`.
- Les pages `france-home.html` et `uk-home.html` sont des présentations secondaires, pas les cartes.
- Depuis l'Atlas UK, « Choose atlas » retourne au sélecteur et « France Atlas » mène à la carte France.
- L'Atlas UK historique reste en anglais ; sa page d'introduction est en français.

## Recherche territoriale France

- La recherche IGN utilise le paramètre `terr=METROPOLE` pour ne pas mélanger les résultats des DOM-TOM avec la carte de France métropolitaine.
- La limite de résultats vient de la configuration et est plafonnée à 30.
- Le seuil de zoom de recherche OSM est lu depuis la configuration (8 par défaut).
- Les tests vérifient l'URL produite, le filtre territorial, le plafonnement, les valeurs incorrectes et le seuil de zoom.

## Sécurité Android

- Images diagnostics limitées à 8 Mio, MIME et signature PNG validés, redirections interdites.
- Cache borné à 64 Mio et 24 fichiers, rétention maximale de 30 jours.
- Export natif plafonné et écrit hors du thread UI.
- Import GeoJSON validé en extension/MIME, structure FeatureCollection et coordonnées WGS84.

## CI 1.2.4

Workflow push #146 : succès complet — https://github.com/Jickssa/megalith-lidar/actions/runs/45154564962

- Validateur paquet : succès.
- Syntaxe JavaScript et Python : succès.
- Tests Node et fixture d'installateur : succès.
- Android Gradle `assembleDebug` : succès.
- Intégrité ZIP, `zipalign`, `apksigner verify` : succès.
- APK : 19 024 313 octets, 97 entrées, SHA-256 `34804ea112838dfced2260801b262f6e186e75af1d588427b3e113ea7654677a`.

## Limites

La recette physique sur téléphone Android reste non exécutée. La compatibilité de signature avec la version déjà installée n'a pas été établie ; sauvegarder les relevés GeoJSON avant toute tentative de remplacement.
