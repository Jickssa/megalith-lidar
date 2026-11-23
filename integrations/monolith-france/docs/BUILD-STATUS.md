# État de validation — Monolith France

## Navigation 1.2.2 — correction de destination

Le retour utilisateur a révélé que les pages d'introduction avaient été présentées à tort comme des Atlas. Le sélecteur commun ouvre maintenant directement les cartes France et Royaume-Uni. Les pages territoriales restent disponibles comme introductions secondaires, dont le CTA cible la véritable carte correspondante.

Workflow push 1.2.2 : à confirmer après commit.

---

## Audit approfondi 1.2.1 — correctifs préparés

- Pont Android : export plafonné à 25 Mio, encodage UTF-8 borné, écriture hors thread UI, fichier temporaire unique, liste MIME autorisée.
- File chooser : types demandés par le champ Web normalisés et utilisés pour le sélecteur Android.
- WebView : appassets limité à HTTPS/hôte attendu/port standard/sans userinfo ; schémas inconnus bloqués.
- Import France : contrôle extension/MIME JSON/GeoJSON avant lecture.
- CSS : commandes tactiles et comportement paysage améliorés.
- Tests : assertions MIME/extension, contrats natifs dans la fixture et contrôles du validateur.
- Résultats CI / APK 1.2.1 : à compléter après exécution des workflows.
- Recette physique : non réalisée dans cet environnement, faute d'ADB et d'appareil Android accessible.

