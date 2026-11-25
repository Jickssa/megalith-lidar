# Validation et recette — Monolith International 2.0

## Périmètre livré dans cette tranche

L'Atlas France comprend trois espaces fonctionnels : Carte & LiDAR, Liste des candidats, Détails du site et carnet de terrain. Les résultats IGN/OSM et les observations locales alimentent un modèle d'affichage commun, avec source, catégorie, nature et état de vérification. La sélection relie la liste, la carte et l'inspecteur. Aucun score ou verdict archéologique n'est fabriqué.

## Validation automatisée initiale — HEAD a6b634fe760998a8dc9cf870a8dab10bb5650e60

Deux workflows GitHub Actions ont réussi sur le même HEAD :
- Push : [45381106088](https://github.com/Jickssa/megalith-lidar/actions/runs/45381106088).
- Pull request #2 : [45381119538](https://github.com/Jickssa/megalith-lidar/actions/runs/45381119538).

Les étapes suivantes ont réussi dans les deux runs :
- `python integrations/monolith-france/scripts/validate_package.py`
- `node --check integrations/monolith-france/web/app.js`
- `node integrations/monolith-france/scripts/test_web_logic.js`
- `python -m py_compile integrations/monolith-france/scripts/*.py`
- `python integrations/monolith-france/scripts/test_android_installer.py`
- Build Gradle `assembleDebug`
- Vérification des assets internationaux et France dans l'APK.
- CRC ZIP, `zipalign` et `apksigner`.

SHA-256 de l'APK Debug, identique pour les deux workflows :

`09303ed07eb77cdcea2576facf983734045f10c1913f7df0c984726c8eaaf972`

Artefacts :
- Push : [14912074868](https://github.com/Jickssa/megalith-lidar/actions/runs/45381106088/artifacts/14912074868).
- PR : [14914890180](https://github.com/Jickssa/megalith-lidar/actions/runs/45381119538/artifacts/14914890180).

## Recette fonctionnelle restante

- Parcours des trois onglets sur appareil Android physique, y compris retour liste ↔ carte ↔ inspecteur.
- Import/export GeoJSON, création d'observations et vérification du rattachement à un candidat.
- Écrans 360–430 px en portrait et paysage sur appareil réel.
- Chargement WMTS IGN et comportement hors ligne.
- Diagnostic réel du rectangle sombre observé dans la capture précédente.
- Vérification du fonctionnement des couches LiDAR sur des emprises de référence.
- Validation en direct des services externes et du comportement réseau.

## Limites architecturales et scientifiques

- L'interface source UK n'est pas refactorisée en composants JavaScript communs ; elle reste préservée.
- La présente livraison établit la structure STEP 1–3 côté France et le modèle de sélection associé ; elle ne constitue pas encore un shell de composants partagé au niveau du code UK/FR.
- L'agrégation des marqueurs UK et la suppression du ratio national fixe sont désormais livrées. La cause complète de l'ancien dépassement de 100 % reste à vérifier au niveau des surfaces géographiques et recouvrements éventuels.
- La cause du rectangle sombre de la carte France n'est pas établie par capture seule.
- POI IGN et IA France restent désactivés.
- Aucun test physique Android ni test de mise à jour d'une application déjà installée avec vérification de certificat n'est revendiqué.


## Contrôles supplémentaires

- Regroupement cartographique UK par cellule écran avec catégories séparées, indicateur de sélection et retour aux marqueurs individuels à partir du zoom 11.
- Suppression du ratio fondé sur la constante 130279.0 ; seules les surfaces et quantités provenant du résumé de campagne sont présentées.
- Distinction explicite entre profil territorial GB et emprise de la campagne publiée (Angleterre).
- Les erreurs de tuiles IGN, OSM et LiDAR sont désormais signalées. La cause du rectangle sombre reste à confirmer par un essai visuel réel sur les services et emprises ciblés.


## Installateur transactionnel

Un test injecte une erreur lors du remplacement de `config` après le remplacement de `web`. La procédure doit restaurer les contenus précédents de `web`, `config` et `docs`. Le test ne simule pas une coupure électrique ou un arrêt forcé du processus ; la garantie porte sur les exceptions remontées pendant l'exécution.


## Validation de la tranche suivante — HEAD 1ce620e

Push : [45535520209](https://github.com/Jickssa/megalith-lidar/actions/runs/45535520209) — succès.  
PR #2 : [45535526503](https://github.com/Jickssa/megalith-lidar/actions/runs/45535526503) — succès.

Les deux runs valident :
- Tests de logique Web et fonctions de diagnostic des tuiles.
- Tests du contrat international et exécution de `node --check` sur le script inline UK.
- Test de remplacement transactionnel : l'échec injecté au remplacement de `config` restaure les trois arbres runtime précédents.
- Build Android Debug, présence des assets France et routes internationales, intégrité ZIP, alignement et signature v2.

Le renommage des dossiers garantit une atomicité par dossier et une restauration pour les exceptions interceptées. Il ne prétend pas couvrir une coupure brutale du processus ou de l'alimentation au milieu de la transaction.


## Cycle de vie Android

`MainActivity.onDestroy()` neutralise les callbacks de permission et de sélecteur de fichier, arrête les chargements et détruit le WebView. Les exports en cours peuvent terminer leur écriture sur le thread dédié, mais le résultat est supprimé au lieu d'être partagé ou affiché si l'activité a été détruite. Le validateur vérifie les contrats de nettoyage et le build Gradle confirme la compilation Kotlin ; cela ne remplace pas un essai sur appareil Android physique.

- Le rendu agrégé est recalculé sur `moveend` ; les cellules écran suivent ainsi le viewport après un déplacement à zoom constant.


## Résultats de validation finaux — HEAD 3248ec2

- Push : [45536266046](https://github.com/Jickssa/megalith-lidar/actions/runs/45536266046) — succès.
- PR #2 : [45536272196](https://github.com/Jickssa/megalith-lidar/actions/runs/45536272196) — succès.
- Les tests internationaux vérifient la réagrégation UK après `moveend` ainsi que le re-rendu détaillé au zoom 11.
- Le validateur et la régression installateur contrôlent maintenant l'état de destruction de `MainActivity`, la destruction du WebView et la neutralisation des callbacks.
- Les deux builds APK passent l'intégrité, `zipalign` et la vérification de signature v2.

Les essais physiques Android, la mise à jour d'une installation existante et le contrôle visuel en direct des tuiles LiDAR restent hors validation automatisée.
