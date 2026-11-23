# Validation et recette — Monolith France 1.2.0

## Parcours cible

- Démarrage → `assets/web/atlas-home.html` (sélecteur commun).
- Sélecteur → `assets/web/france-home.html` → `assets/web/france/web/index.html` (Atlas France).
- Sélecteur → `assets/web/uk-home.html` → `assets/web/index.html` (Atlas britannique original).
- Les pages territoriales offrent un retour au sélecteur et un accès à l'accueil de l'autre territoire.
- La copie embarquée de l'Atlas britannique ajoute un lien `Choose atlas` vers le sélecteur ; sa source est contrôlée comme immuable.

## Contrôles 1.2.0

- Tests de génération des trois pages et des liens entre elles.
- Contrôle des CTA vers les deux interfaces cartographiques complètes.
- Vérification du lien de retour injecté une seule fois dans l'Atlas britannique embarqué.
- Vérification de l'absence de modification du fichier source britannique.
- Vérification de la mise à niveau/réinstallation du hook existant.
- Résultats CI et compilation APK : à compléter après exécution du workflow.

## Écart documentaire avec l'APK originale fournie

L'APK inspectée (SHA-256 `cf6362d6c5513c08740f2b0f58ac3178f29b11f0584117a2b3bd2911d6bdd3dd`) contient une unique page Web `assets/web/index.html`, directement chargée par Android. Le DEX référence `https://appassets.androidplatform.net/assets/web/index.html`. Aucun second HTML et aucun bouton « Atlas britannique » n'ont été trouvés dans cette APK. Le parcours à trois niveaux est donc une évolution nouvelle de Monolith, non une reproduction démontrée d'une navigation absente de ce binaire.

---

# Historique — validation et recette Monolith France 1.1.3 / build #110

## CI automatisée

- Push #110 : succès complet — https://github.com/Jickssa/megalith-lidar/actions/runs/45097292720
- Pull request #111 : succès complet — https://github.com/Jickssa/megalith-lidar/actions/runs/45097297817
- Validation paquet : réussie.
- Syntaxe JS : réussie.
- Tests Node GeoJSON : réussis.
- Syntaxe Python : réussie.
- Fixture installateur : réussie ; génération synthétique et contrôle du hook dans le préparateur upstream réel.
- Installateur dans le checkout Android : réussi.
- Gradle `assembleDebug` : réussi.
- Contrôle CRC APK : réussi.
- `zipalign` : réussi.
- `apksigner verify` : réussi, signature APK v2.

## Contrôle de la navigation

Routes embarquées :
- accueil : `assets/web/atlas-home.html`
- Royaume-Uni : `assets/web/index.html` (chemin historique)
- France : `assets/web/france/web/index.html`

Contenu confirmé directement :
- l'accueil affiche « Atlas France » et « Atlas britannique » ;
- le lien France cible `/assets/web/france/web/index.html` ;
- le lien UK cible `/assets/web/index.html` ;
- la page France propose `/assets/web/atlas-home.html` et le lien UK.
- l'index UK n'est pas remplacé par l'accueil.

## Contrôle APK direct

- APK Debug extraite de l'artefact GitHub run #110.
- Archive zip artefact : CRC valide.
- APK interne : CRC valide, 95 entrées.
- Taille APK : 19 010 091 octets.
- SHA-256 : `4ef84499c4e3a5d26515d5bc991cb3fd7f5c1695232a67539de03af92517956c`.
- Checksum de l'artefact : concordant.
- Artefact GitHub : ID `14783892920`.
- URL : https://github.com/Jickssa/megalith-lidar/actions/runs/45097292720/artifacts/14783892920

## Recette sur appareil non réalisée pour la nouvelle navigation

L'utilisateur a déjà testé une APK antérieure, mais l'écran commun vient d'être ajouté après son test. Il reste à valider sur son appareil :
1. Lancement → « Choisir un atlas ».
2. Accueil → Atlas France.
3. France → « Choisir un atlas ».
4. Accueil → Atlas britannique.
5. France → Atlas britannique.
6. Vérifier que les datasets et ressources de l'atlas britannique continuent de fonctionner.
7. Tester retour arrière Android, absence d'écran blanc et absence de boucle.
8. Tester le reste des fonctions réseau et terrain séparément.

## Limites connues

- Aucune détection IA française active.
- POI IGN « mégalithe » désactivé faute de schéma API validé.
- Couverture LiDAR HD progressive et dépendante des emprises.
- Les observations OSM et catalogues patrimoniaux sont non exhaustifs.
