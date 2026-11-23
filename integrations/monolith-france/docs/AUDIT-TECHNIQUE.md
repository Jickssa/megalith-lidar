# Audit technique — adaptation France du dépôt megalith-lidar

## Dépôt et périmètre

Dépôt amont étudié : `GlassOnTin/megalith-lidar`, branche `main`. Fork vérifié : `Jickssa/megalith-lidar`. Au moment de la comparaison, le fork était identique à l'amont, commit `ba08b3346895472dd68c27ab5435d614cec64356`.

L'arbre de l'amont contenait 85 fichiers suivis, dont environ 98,5 Mio sous `docs/`. Les principaux composants étaient `megalith_lidar/terrain_features.py`, `dataset.py`, `model.py`, `scanner.py`, `catalog.py`, `lidar_wcs.py`, `osm_context.py`, `arch_context.py`, les scripts nationaux, `index.html` et le projet Android Gradle.

## Architecture amont

- Six canaux de terrain multi-échelle calculés sur des MNT/MNS ; U-Net avec encodeur ResNet-34 et sorties spécialisées préhistorique, enclos et romain.
- Entraînement PyTorch, masques issus du registre NHLE, séparation spatiale par blocs BNG de 20 km, calibrage Platt et évaluation sur jeux tests anglais.
- Recoupements avec Historic England, OpenStreetMap, Megalithic Portal et cartes historiques Ordnance Survey.
- Interface Leaflet, inspecteur et exports GPX / OsmAnd.
- Application Android WebView avec permissions de localisation et sélecteur GeoJSON.

## Non-transposabilité France

Les modèles et jeux de données amont sont liés à l'Angleterre : British National Grid EPSG:27700, Environment Agency LiDAR, NHLE, OS historique et données OSM/Megalithic Portal. Les scores publiés dans le README ne sont pas des mesures de performances en France. Aucun poids de modèle prêt à l'inférence n'a été identifié dans l'arbre suivi. Les résultats anglais ne sont donc pas chargés ni réinterprétés comme des données françaises.

## Choix de l'adaptation

1. Utiliser WGS84/EPSG:4326 comme CRS d'échange.
2. Centrer la carte sur la France métropolitaine.
3. Utiliser Plan IGN v2 et les couches LiDAR HD MNT, MNS, MNH via WMTS Géoplateforme.
4. Filtrer le géocodage direct par `terr=METROPOLE`, cohérent avec le territoire couvert par cette interface ; plafonner les résultats à 30 et lire le seuil OSM depuis la configuration. Documentation Géoplateforme : https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/geocodage/.
4. Résoudre le filtre POI « mégalithe » par découverte dynamique de sa catégorie parente dans les capacités de l'API ; ne pas traiter « mégalithe » comme catégorie racine sans résolution.
5. Utiliser le géocodeur IGN pour les lieux/adresses, Overpass pour les éléments OSM et les données ouvertes du ministère de la Culture uniquement comme recoupement.
6. Sauvegarder les observations dans le WebView et permettre l'import/export GeoJSON.
7. Garder la détection IA désactivée jusqu'à constitution et validation d'un jeu français.

## Limites

- La couverture LiDAR HD est progressive et doit être contrôlée pour chaque emprise.
- Les POI IGN, OSM et les immeubles protégés ne sont pas exhaustifs de l'archéologie.
- Les services cartographiques et les recherches nécessitent une connexion. Le cache hors ligne n'est pas garanti.
- La compilation Android et le test sur appareil ne sont pas réputés effectués par cet audit.


## Audit de robustesse 1.2.1 — corrections appliquées

### Pont JavaScript Android

L'ancien pont `saveOrShareFile` écrivait un contenu de taille illimitée directement sur le thread UI, utilisait un nom de cache déterministe (risque d'écrasement d'un export encore utilisé) et acceptait le MIME transmis sans filtrage. La version 1.2.1 applique une limite de 25 Mio, borne les types MIME, écrit en arrière-plan et utilise un fichier temporaire unique.

### Sélecteur de fichiers

Le sélecteur Android ne reprenait pas les types réellement demandés par l'élément Web. Il normalise maintenant les extensions .json/.geojson et les MIME autorisés. Le callback est toujours libéré lorsque le sélecteur n'est pas disponible.

### Navigation WebView

La route appassets est maintenant acceptée uniquement pour HTTPS, l'hôte attendu, sans userinfo et avec un port absent ou 443. Les liens HTTP(S) externes sont transmis au navigateur externe. Les schémas non pris en charge (notamment intent:, file: et content:) sont bloqués.

### Import GeoJSON

Le parser validait déjà la structure FeatureCollection, les points WGS84 et les limites de taille/nombre. Le fichier est désormais aussi refusé avant lecture s'il n'a ni extension JSON/GeoJSON ni MIME JSON/GeoJSON connu.

### Ergonomie

Les zones tactiles sont portées à 40 px minimum pour les commandes principales ; l'en-tête peut se replier sur petit écran et la carte reçoit une hauteur dédiée en mode paysage.

### Limites résiduelles à traiter

- Les téléchargements PNG de diagnostic sont maintenant limités à 8 Mio par fichier ; le type MIME et la signature binaire PNG sont vérifiés. Les redirections sont désactivées pour la source fixe ; le cache est borné à 64 Mio, 24 fichiers et 30 jours, avec éviction par date de dernier accès.
- Le pont `addJavascriptInterface` est visible dans tous les frames d'une page WebView selon Android ; les pages actuelles ne contiennent pas d'iframe distante identifiée, mais l'ajout futur de contenu embarqué non fiable devra être interdit ou isolé.
- Le bouton Retour reste implémenté via la méthode historique `onBackPressed` ; il doit être testé sur versions Android récentes avec navigation prédictive.
- L'identifiant d'application est resté `uk.megalith.lidar`. L'APK de base et l'APK Debug ont le même applicationId ; la compatibilité de signature n'a pas été démontrée par la seule inspection des archives.


## Audit de suivi 1.3.0 — moteur de recherche français

### Défauts observés

- La fonction `searchIgn()` était un stub levant une exception.
- La requête Overpass fixe ne tenait pas compte du texte saisi.
- La taxonomie JSON n'était pas utilisée pour produire les requêtes.
- Les objets OSM étaient réduits à un titre/type et un point, sans identifiant stable ni URL source.
- Les recherches asynchrones ne comportaient pas de mécanisme d'annulation ni de protection contre les réponses tardives.
- Le manifeste POI IGN associait à tort le type POI au géocodeur direct.

### Corrections 1.3.0

- Taxonomie OSM déclarative reliée à six catégories de prospection.
- Construction des requêtes par catégorie, terme saisi et bbox.
- Prise en charge nodes, ways et relations.
- Normalisation des résultats et identifiants OSM.
- Limitation d'emprise, annulation et identité de recherche.
- Endpoint POI documenté comme autocomplétion ; activation différée jusqu'à validation de GetCapabilities.
- CI couvrant aussi les fichiers Android et la source UK.

### Limites

Cette recherche interroge les objets déjà cartographiés dans OSM. Elle ne détecte pas de structures inconnues. La présence d'un objet OSM n'atteste pas sa validité archéologique. Les familles de recherche génériques peuvent retourner des résultats ambigus qui exigent un recoupement.


## Audit 1.3.1 — précision du moteur OSM

Les tags OSM ont été vérifiés dans la documentation actuelle. Pour les mégalithes, la combinaison recommandée est `historic=archaeological_site` avec `archaeological_site=megalith`, et le sous-type peut être précisé par `megalith_type=*`. Les villas romaines et fortifications archéologiques s'expriment également par `historic=archaeological_site` et `archaeological_site=roman_villa` / `fortification`. Les valeurs génériques ne doivent pas être prises comme preuves archéologiques.

La recherche texte interroge maintenant des champs configurés par catégorie (nom, nom français, référence, sous-type) et déduplique les mêmes objets. Les tags trop génériques ou documentés comme confondeurs ont été retirés des recherches automatiques.

Limite : les catégories « patrimoine médiéval » comportent volontairement des objets bâtis visibles, pas uniquement des sites archéologiques enfouis. L'interface doit conserver cette distinction dans les fiches et filtres.


## Audit de précision 1.3.1 — taxonomie et recherche OSM

Vérification des conventions OSM actuelles :

- Les mégalithes se décrivent par `historic=archaeological_site` + `archaeological_site=megalith`; les sous-types sont décrits par `megalith_type=*`.
- Les villas romaines utilisent `historic=archaeological_site` + `archaeological_site=roman_villa`.
- Les fortifications archéologiques utilisent `historic=archaeological_site` + `archaeological_site=fortification`, éventuellement avec `fortification_type=*`.
- `archaeological_site=settlement` est documenté comme sous-type de site archéologique.
- `man_made=cairn` peut concerner un cairn servant de repère ou d'importance topographique ; il n'est pas assimilé systématiquement à un site archéologique.
- `highway=track` est un type de voie générique, impropre comme filtre automatique de voie antique.

La taxonomie prend maintenant en charge les conjonctions de tags et les champs de recherche textuelle par catégorie. Les doublons d'objets OSM sont dédupliqués par identifiant stable. Les règles restent des filtres de rappel documentaire, non des détecteurs archéologiques.

Références consultées :
https://wiki.openstreetmap.org/wiki/Tag:archaeological_site%3Dmegalith
https://wiki.openstreetmap.org/wiki/Tag:archaeological_site%3Droman_villa
https://wiki.openstreetmap.org/wiki/Tag:archaeological_site%3Dfortification
https://wiki.openstreetmap.org/wiki/Tag:historic%3Darchaeological_site
https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dcairn
