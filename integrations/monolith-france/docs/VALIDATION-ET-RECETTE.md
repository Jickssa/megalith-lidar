# Validation et recette — Monolith International

## CI et construction Android

L’exécution de référence est le run [45316298442](https://github.com/Jickssa/megalith-lidar/actions/runs/45316298442), commit `db2a542a683f11fc15bb47f294726ed8ac63fff6`, branche `feature/monolith-international-next`.

- Validation statique et fixture installateur : succès.
- Validation du paquet et profils pays/langue via `country-profile.schema.json` : succès.
- Vérification syntaxique JavaScript : succès.
- Tests de logique Web : succès.
- Compilation syntaxique Python : succès.
- Fixture installateur Android : succès.
- Compilation Debug Android avec JDK 17 / SDK 35 : succès.
- Contrôle des CRC ZIP et des assets internationaux requis : succès.
- `zipalign -c -v 4` : succès.
- `apksigner verify --verbose` : succès.
- Upload de l’APK Debug et du checksum : succès.

Artefact CI : [megalith-lidar-france-debug](https://github.com/Jickssa/megalith-lidar/actions/runs/45316298442/artifacts/14884244756), ID `14884244756`. Taille de l’archive : 18 997 547 octets. Digest d’archive GitHub : `sha256:5715b76917673844cd76e2346089625e11a6c7bc3c9012af4e884c00ff5f3fa3`. Ce digest est celui de l’archive d’artefact, pas le SHA-256 recalculé du fichier APK interne.

## Navigation et profils

Architecture conservée :

1. Sélecteur commun : `/assets/web/atlas-home.html`.
2. Pages de territoire : `/assets/web/france-home.html` et `/assets/web/uk-home.html`.
3. Atlas réels : France `/assets/web/france/web/index.html`, Royaume-Uni `/assets/web/index.html`.

Seules les combinaisons actives FR/fr-FR et GB/en-GB sont admises. Le profil FR ne reprend ni modèle, ni score, ni jeu de données analytique britannique. Les chemins de destination sont soumis à une liste exacte FR/GB. Les assets de profil et de langue sont embarqués dans l’application ; leur lecture passe par les chemins internes de l’AssetLoader, sans besoin d’un service distant.

La fixture vérifie les deux pages de territoire séparément des Atlas réels, les liens de retour, les routes, le hook préparateur unique, la réinstallation forcée et l’immutabilité du fichier source britannique `index.html`.

## Moteur France et limites scientifiques

- Taxonomie française distincte, six familles de recherche OSM avec règles de tags composées et champs de recherche.
- Requêtes liées à l’emprise cartographique, plafonnées et annulables ; les réponses périmées sont ignorées.
- Echappement des termes utilisateur dans les expressions régulières et dans Overpass QL.
- Déduplication par identifiant d’objet OSM.
- Les données OSM décrivent des objets contributifs existants et non des découvertes archéologiques certaines.
- Les anomalies visuelles LiDAR ne sont pas classées comme découvertes.
- Aucun modèle IA français n’est déclaré opérationnel.
- Les services POI IGN ne sont pas activés avant validation réelle de GetCapabilities et du paramètre de type.

## Recette restant à réaliser

Les éléments suivants ne sont pas couverts par la CI et restent à tester :

- Requêtes réseau réelles vers la Géoplateforme IGN, Overpass et WMTS.
- Couverture/continuité des couches IGN LiDAR HD sur plusieurs emprises de référence.
- Recette sur téléphone Android physique : WebView, AssetLoader, GPS, rotation, reprise, fonctionnement hors réseau.
- Import/export GeoJSON réel et limites sur appareil.
- Téléchargement des diagnostics, sélecteur de fichiers et URI internes sur versions Android cibles.
- Compatibilité de signature avec une version déjà installée et test de mise à jour.
- Test de contribution communautaire ; aucun installateur sécurisé de paquet pays arbitraire n’est disponible.

Aucun résultat de test réseau ou physique n’est revendiqué ici.
