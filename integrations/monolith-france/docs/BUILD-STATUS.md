# État de validation — Monolith France

## État GitHub

- Branche : `feature/monolith-france-1.1.0`.
- PR #1 : ouverte, en brouillon, non fusionnée ; cible `main`.
- Aucun changement poussé sur `main`.
- Tête actuelle documentée : `70bf0efe0e518cc2616763218002ec5b71aa4cff`.
- Évolution de navigation 1.1.3 en cours de validation.

## Navigation commune 1.1.3

- Démarrage Android : `/assets/web/atlas-home.html`.
- Atlas France : `/assets/web/france/web/index.html`.
- Atlas britannique : `/assets/web/index.html`, chemin historique conservé.
- L'installateur écrit l'accueil dans un fichier séparé après le nettoyage des assets.
- L'index britannique n'est ni déplacé ni écrasé, afin de préserver ses chemins relatifs et références aux datasets.
- L'en-tête France permet le retour à l'écran commun et le passage direct vers l'atlas britannique.
- L'installateur migre l'URL START_URL depuis l'ancien démarrage britannique ou l'ancien démarrage France.

## CI de la nouvelle navigation

- Runs #92/#93 : échec du fixture sur assertion HTML ; le job Android a été ignoré.
- Runs #94/#95 : échec du validateur, qui n'autorisait pas l'URL commune `/assets/web/atlas-home.html`.
- Corrections : page d'accueil séparée, index UK préservé, allowlist du validateur limitée aux routes communes documentées, fixture étendu.
- Run push #96 : validation statique, syntaxe, tests Node et fixture installateur réussis.
- Le job Android du run #96 était en file d'attente au moment de la mise à jour initiale. Aucun APK 1.1.3 n'est déclaré construit ou inspecté ici.

## Build de référence historique

L'APK du run PR #89 sur le commit applicatif `fd1d68e` a été téléchargée et inspectée. Elle ne contient pas l'écran d'accueil 1.1.3.

- Run : https://github.com/Jickssa/megalith-lidar/actions/runs/45095513607
- APK Debug : 19 010 059 octets.
- SHA-256 : `8c6de9c70e0a6c5da85f7c1818c98ddffa2ddf70320c04550529b540b478bcb1`.
- Artefact ID : `14783575119`.
- Cette APK est uniquement un build de référence antérieur.

## Correctifs antérieurs toujours présents

- Observations GeoJSON validées en WGS84 ; plafond cumulé 5 000 et import 20 Mio.
- État mémoire conservé si l'écriture locale échoue.
- Tests Node dans `scripts/test_web_logic.js`.
- Images Leaflet officielles 1.9.4, dimensions et alpha contrôlés.
- Callback WebView annulé proprement si le sélecteur Android est indisponible.
- Dossier de sauvegarde installateur exclu de Git.
- POI IGN mégalithe et détecteur IA français toujours désactivés faute de validation.

## Recette appareil non réalisée

Il reste à vérifier sur appareil : lancement sur l'écran commun, les quatre parcours entre les deux atlas, chargement de l'index UK et de ses datasets, rendu des WMTS, géocodage IGN, Overpass, géolocalisation, stockage, import/export et annulation du sélecteur.
