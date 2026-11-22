# Fork GitHub et compilation dans Codespaces

Le fork `Jickssa/megalith-lidar` a été trouvé. Il était initialement identique à l'amont, commit `ba08b3346895472dd68c27ab5435d614cec64356`. La branche `feature/monolith-france-1.1.0` a été créée dans le fork à partir de ce commit ; `main` est laissée intacte.

## Procédure

Ouvrir un Codespace sur la branche `feature/monolith-france-1.1.0`, puis lancer :

```bash
python3 integrations/monolith-france/scripts/install_into_megalith_lidar_android.py "$PWD" --dry-run
bash integrations/monolith-france/scripts/integrate_and_build_codespace.sh "$PWD"
```

Le script vérifie la structure, les points d'insertion Android, la configuration France, les ressources, le test d'installation factice, puis modifie les sources et exécute `./android/gradlew assembleDebug`.

Prérequis : JDK 17, Python 3, Node.js, Android Command-line Tools, SDK Platform 35 et Build Tools 35.0.0 ; `Pillow` est installé dans un environnement Python isolé si nécessaire. Définir `ANDROID_HOME` ou `ANDROID_SDK_ROOT`.

Résultat attendu :

```text
dist/megalith-lidar-france-debug.apk
dist/megalith-lidar-france-debug.apk.sha256
```

La build Debug utilise une clé de debug locale. Elle ne remplace pas nécessairement une installation Release existante si les certificats diffèrent. Pour publier une Release compatible, le propriétaire doit fournir ses secrets de signature au système de build ; ils ne doivent jamais être committés.

La procédure n'effectue ni push, ni création de Release, ni fusion de PR. Les requêtes IGN et Overpass sont des services en ligne ; il ne faut pas annoncer de fonctionnement complet hors réseau.
