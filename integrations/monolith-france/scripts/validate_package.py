#!/usr/bin/env python3
"""Validate Monolith France package structure, metadata and local assets."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []


def read_text(relative: str) -> str:
    path = ROOT / relative
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        ERRORS.append(f"{relative}: {exc}")
        return ""


def read_json(relative: str):
    try:
        return json.loads(read_text(relative))
    except Exception as exc:
        ERRORS.append(f"{relative}: JSON invalide ({exc})")
        return {}


def main() -> int:
    config = read_json("config/france-config.json")
    sources = read_json("config/data-sources.json")
    taxonomy = read_json("config/archaeology-taxonomy.fr.json")
    html = read_text("web/index.html")
    js = read_text("web/app.js")
    css = read_text("web/styles.css")

    if config.get("country") != "FR" or config.get("locale") != "fr-FR":
        ERRORS.append("Territoire ou locale incorrects.")
    if config.get("coordinateReferenceSystem") != "EPSG:4326":
        ERRORS.append("Le CRS attendu pour l'interface doit être EPSG:4326.")
    search_config = config.get("search", {})
    if search_config.get("defaultMode") != "place":
        ERRORS.append("Le mode de recherche par défaut doit être le géocodage IGN pris en charge.")
    if search_config.get("territory") != "METROPOLE":
        ERRORS.append("Le géocodage doit être borné à la France métropolitaine.")
    if search_config.get("maxResults") != 30:
        ERRORS.append("Le géocodage doit être limité à 30 résultats.")
    if search_config.get("osmMinimumZoom") != 8:
        ERRORS.append("Le seuil de zoom OSM attendu est 8.")
    if config.get("detector", {}).get("enabled") is not False:
        ERRORS.append("La détection IA française doit rester désactivée.")
    storage = config.get("storage", {})
    if storage.get("maxImportBytes") != 20_971_520:
        ERRORS.append("Limite d'import GeoJSON inattendue.")
    if storage.get("maxFeatures") != 5000:
        ERRORS.append("Limite cumulée d'observations attendue : 5 000.")
    for contract in ("getStorageLimits", "isValidObservationFeature", "parseObservationImport", "persistObs", "isGeoJsonFile", "getSearchSettings", "buildPlaceSearchUrl"):
        if contract not in js:
            ERRORS.append(f"Contrat de stockage/GeoJSON absent : {contract}")
    if not isinstance(taxonomy, dict) or not taxonomy:
        ERRORS.append("Taxonomie archéologique vide ou invalide.")
    categories = taxonomy.get("categories", [])
    if not isinstance(categories, list) or len(categories) < 5:
        ERRORS.append("La taxonomie française doit exposer au moins cinq familles.")
    else:
        category_ids = [c.get("id") for c in categories if isinstance(c, dict)]
        if len(category_ids) != len(set(category_ids)):
            ERRORS.append("Identifiants de taxonomie dupliqués.")
        if any(not isinstance(c.get("osm"), list) or not c["osm"] for c in categories if isinstance(c, dict)):
            ERRORS.append("Chaque famille de recherche doit documenter ses règles OSM.")
        if any(not isinstance(c.get("queryFields"), list) or not c["queryFields"] for c in categories if isinstance(c, dict)):
            ERRORS.append("Chaque famille doit définir ses champs de recherche textuelle.")

    source_text = json.dumps(sources, ensure_ascii=False)
    for layer in ("IGNF_LIDAR-HD_MNT", "IGNF_LIDAR-HD_MNS", "IGNF_LIDAR-HD_MNH"):
        if layer not in source_text:
            ERRORS.append(f"Couche de données absente : {layer}")

    # Validate only explicitly declared territory/language combinations.
    try:
        from jsonschema import validate
        from jsonschema.exceptions import ValidationError
    except ImportError:
        ERRORS.append("jsonschema absent : impossible de valider les profils pays.")
    else:
        country_root = ROOT / "config/countries"
        schema_path = country_root / "country-profile.schema.json"
        catalog_path = country_root / "catalog.json"
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            country_entries = catalog.get("countries", [])
            active = [entry for entry in country_entries if entry.get("status") == "active"]
            active_codes = {entry.get("code") for entry in active}
            if catalog.get("defaultCountry") not in active_codes:
                ERRORS.append("Le pays par défaut doit être déclaré actif dans le catalogue.")
            if active_codes != {"FR", "GB"}:
                ERRORS.append("Seuls FR et GB peuvent être actifs tant qu'aucun autre profil n'est validé.")
            if len(active_codes) != len(active):
                ERRORS.append("Codes pays actifs dupliqués.")
            for entry in active:
                code = entry.get("code")
                locales = entry.get("supportedLanguages")
                profile_rel = entry.get("profile")
                if not isinstance(code, str) or not isinstance(locales, list) or not locales or len(locales) != len(set(locales)):
                    ERRORS.append(f"Catalogue {code!r} : langues déclarées invalides ou dupliquées.")
                    continue
                if not isinstance(profile_rel, str) or not re.fullmatch(r"profiles/[A-Z]{2,3}\.json", profile_rel):
                    ERRORS.append(f"Catalogue {code} : chemin de profil invalide.")
                    continue
                profile_path = (country_root / profile_rel).resolve()
                if country_root.resolve() not in profile_path.parents or not profile_path.is_file():
                    ERRORS.append(f"Catalogue {code} : profil absent ou hors du répertoire autorisé.")
                    continue
                profile = json.loads(profile_path.read_text(encoding="utf-8"))
                try:
                    validate(instance=profile, schema=schema)
                except ValidationError as exc:
                    ERRORS.append(f"Profil {code} hors schéma : {exc.message}")
                if profile.get("countryCode") != code or profile.get("status") != "active":
                    ERRORS.append(f"Profil {code} : code ou statut incohérent.")
                if profile.get("supportedLocales") != locales:
                    ERRORS.append(f"Profil {code} : supportedLocales diffère du catalogue.")
                if profile.get("defaultLocale") not in locales:
                    ERRORS.append(f"Profil {code} : langue par défaut non déclarée.")
                routes = {"FR": "/assets/web/france/web/index.html", "GB": "/assets/web/index.html"}
                if profile.get("atlasEntry") != routes.get(code):
                    ERRORS.append(f"Profil {code} : route Atlas absente ou non autorisée.")
                for locale in locales:
                    if not isinstance(locale, str) or not re.fullmatch(r"[a-z]{2}-[A-Z]{2}", locale):
                        ERRORS.append(f"Profil {code} : identifiant de langue invalide.")
                        continue
                    language_path = ROOT / "config/languages" / (locale + ".json")
                    if not language_path.is_file():
                        ERRORS.append(f"Langue absente pour {code} : {locale}.")
                        continue
                    language = json.loads(language_path.read_text(encoding="utf-8"))
                    if language.get("locale") != locale or not language.get("nativeName"):
                        ERRORS.append(f"Catalogue de langue incohérent : {locale}.")
                    if not isinstance(language.get("messages"), dict) or not language["messages"]:
                        ERRORS.append(f"Catalogue de langue vide : {locale}.")
            expected_language_pairs = {("FR", "fr-FR"), ("GB", "en-GB")}
            actual_language_pairs = {(entry.get("code"), locale) for entry in active for locale in entry.get("supportedLanguages", [])}
            if actual_language_pairs != expected_language_pairs:
                ERRORS.append("Combinaisons pays/langue actives différentes du catalogue testé FR/GB.")
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            ERRORS.append(f"Catalogue/profils pays illisibles ou incomplets : {exc}")

    # Assert every internal URL used in HTML is present in the known runtime layout.
    for required in (
        "/assets/web/leaflet/leaflet.css",
        "/assets/web/france/web/styles.css",
        "/assets/web/leaflet/leaflet.js",
        "/assets/web/france/web/app.js",
        "/assets/web/france/config/france-config.json",
    ):
        if required not in html and required not in js:
            ERRORS.append(f"Référence locale attendue absente : {required}")

    for local in (
        "web/index.html",
        "web/app.js",
        "web/styles.css",
        "config/france-config.json",
        "config/data-sources.json",
        "config/archaeology-taxonomy.fr.json",
        "docs/AUDIT-TECHNIQUE.md",
    ):
        if not (ROOT / local).is_file():
            ERRORS.append(f"Fichier requis absent : {local}")

    # All local CSS/JS/image references in the France module must resolve.
    for source, text in (("web/index.html", html), ("web/app.js", js), ("web/styles.css", css)):
        if source == "web/index.html":
            refs = re.findall(r'''(?:src|href)=["']([^"']+)["']''', text)
        elif source == "web/styles.css":
            refs = re.findall(r'''url\(["']?([^"')]+)''', text)
        else:
            refs = []
        for ref in refs:
            if ref.startswith(("https://", "http://", "data:", "#", "/assets/web/leaflet/")):
                continue
            if ref in (
                "/assets/web/index.html",
                "/assets/web/atlas-home.html",
                "/assets/web/france-home.html",
                "/assets/web/uk-home.html",
            ):
                # Deliberate shared entry routes in the host APK.
                continue
            if ref.startswith("/assets/web/france/"):
                relative = ref.removeprefix("/assets/web/france/")
                if not (ROOT / relative).exists():
                    ERRORS.append(f"{source}: ressource référencée absente : {ref}")
            elif ref.startswith("/"):
                ERRORS.append(f"{source}: chemin absolu hors périmètre du module : {ref}")
            elif not ref.startswith(("mailto:", "tel:", "javascript:")):
                candidate = (ROOT / source).parent / ref
                if not candidate.exists():
                    ERRORS.append(f"{source}: ressource relative absente : {ref}")

    # Leaflet PNG placeholders are checked with an actual decoder, not only a magic header.
    try:
        from PIL import Image
    except ImportError:
        ERRORS.append("Pillow absent : impossible de valider réellement les PNG.")
    else:
        expected_sizes = {
            "layers.png": (26, 26),
            "layers-2x.png": (52, 52),
            "marker-icon.png": (25, 41),
            "marker-icon-2x.png": (50, 82),
            "marker-shadow.png": (41, 41),
        }
        for name, expected_size in expected_sizes.items():
            path = ROOT / "web/vendor/images" / name
            if not path.is_file():
                ERRORS.append(f"Image Leaflet absente : {path.relative_to(ROOT)}")
                continue
            try:
                with Image.open(path) as image:
                    if image.size != expected_size:
                        ERRORS.append(
                            f"Dimensions PNG Leaflet incorrectes {name}: "
                            f"{image.size}, attendu {expected_size}"
                        )
                    image.load()
                    if image.convert("RGBA").getchannel("A").getbbox() is None:
                        ERRORS.append(f"Image Leaflet entièrement transparente : {name}")
            except Exception as exc:
                ERRORS.append(f"PNG illisible {name}: {exc}")

    for relative in (
        "android/AndroidManifest-fragment.xml",
        "android/file-provider-manifest-snippet.xml",
        "android/res/xml/monolith_france_file_paths.xml",
    ):
        path = ROOT / relative
        try:
            ElementTree.parse(path)
        except Exception as exc:
            ERRORS.append(f"XML invalide {relative}: {exc}")

    if 'option value="megalith"' in html or "value='megalith'" in html:
        ERRORS.append("Le mode POI mégalithe IGN non validé ne doit pas être exposé dans l’interface.")
    if "Mégalithes IGN" in html:
        ERRORS.append("L’interface ne doit pas présenter la recherche POI mégalithe comme disponible.")
    if "geocodage/completion/" not in source_text:
        ERRORS.append("L'endpoint d'autocomplétion POI IGN doit être déclaré distinctement.")
    if "buildPoiAutocompleteUrl" not in js or "poiType" not in js:
        ERRORS.append("Le contrat de construction des requêtes POI IGN est absent.")
    if "IGN / Géoplateforme" not in js or "buildPlaceSearchUrl" not in js:
        ERRORS.append("Le géocodage direct IGN doit rester identifiable.")
    if "queryFields" not in js or "buildOverpassQuery" not in js or "escapeOverpassRegex" not in js:
        ERRORS.append("Les champs textuels configurables et le générateur Overpass sont requis.")
    if "osmElementToItem" not in js or "AbortController" not in js:
        ERRORS.append("La normalisation OSM et l'annulation des recherches sont requises.")
    if "overpass-api.de" not in js:
        ERRORS.append("Endpoint Overpass primaire absent.")
    for search_contract in ("buildOverpassQuery", "normalizeTaxonomy", "osmElementToItem", "archaeologyCategory", "AbortController"):
        if search_contract not in js and search_contract not in html:
            ERRORS.append(f"Contrat du moteur de recherche absent : {search_contract}")
    for search_contract in ("escapeOverpassRegex", "buildOverpassTagSelector"):
        if search_contract not in js:
            ERRORS.append(f"Contrat de sécurité des requêtes absent : {search_contract}")
    if "deduplicateOsmItems" not in js:
        ERRORS.append("La déduplication des résultats OSM est absente.")
    if "queryFields" not in js:
        ERRORS.append("Les champs de recherche par sous-type ne sont pas utilisés.")
    if "tags" not in taxonomy.get("categories", [{}])[0].get("osm", [{}])[0]:
        ERRORS.append("La taxonomie doit pouvoir exprimer des conjonctions de tags OSM.")
    if "geocodage/completion/" not in source_text:
        ERRORS.append("L'endpoint d'autocomplétion POI IGN doit être distinct du géocodeur direct.")
    if "saveOrShareFile" not in js:
        ERRORS.append("Pont d'export natif non utilisé par le module.")
    android_activity = ROOT.parents[1] / "android/app/src/main/java/uk/megalith/lidar/MainActivity.kt"
    if android_activity.is_file():
        native_text = android_activity.read_text(encoding="utf-8")
        for native_contract in (
            "MAX_EXPORT_BYTES",
            "File.createTempFile",
            "fileChooserParams.acceptTypes",
            "uri.userInfo == null",
            "MAX_DIAGNOSTIC_FILE_BYTES",
            "MAX_DIAGNOSTIC_CACHE_BYTES",
            "MAX_DIAGNOSTIC_CACHE_FILES",
            "instanceFollowRedirects = false",
            "isValidDiagnosticPng",
            "trimDiagnosticCache",
        ):
            if native_contract not in native_text:
                ERRORS.append(f"Contrôle Android de sécurité absent : {native_contract}")
    else:
        ERRORS.append("MainActivity.kt introuvable : contrôle du pont Android impossible.")
    if ERRORS:
        print("VALIDATION ÉCHOUÉE")
        print("\n".join(f"- {error}" for error in ERRORS))
        return 1
    print("VALIDATION STATIQUE OK")
    if WARNINGS:
        print("AVERTISSEMENTS")
        print("\n".join(f"- {warning}" for warning in WARNINGS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
