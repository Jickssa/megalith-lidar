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
    if config.get("search", {}).get("defaultMode") != "place":
        ERRORS.append("Le mode de recherche par défaut doit être le géocodage IGN pris en charge.")
    if config.get("detector", {}).get("enabled") is not False:
        ERRORS.append("La détection IA française doit rester désactivée.")
    storage = config.get("storage", {})
    if storage.get("maxImportBytes") != 20_971_520:
        ERRORS.append("Limite d'import GeoJSON inattendue.")
    if storage.get("maxFeatures") != 5000:
        ERRORS.append("Limite cumulée d'observations attendue : 5 000.")
    for contract in ("getStorageLimits", "isValidObservationFeature", "parseObservationImport", "persistObs", "isGeoJsonFile"):
        if contract not in js:
            ERRORS.append(f"Contrat de stockage/GeoJSON absent : {contract}")
    if not isinstance(taxonomy, dict) or not taxonomy:
        ERRORS.append("Taxonomie archéologique vide ou invalide.")

    source_text = json.dumps(sources, ensure_ascii=False)
    for layer in ("IGNF_LIDAR-HD_MNT", "IGNF_LIDAR-HD_MNS", "IGNF_LIDAR-HD_MNH"):
        if layer not in source_text:
            ERRORS.append(f"Couche de données absente : {layer}")

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
    if "Recherche du sous-type POI" not in js:
        ERRORS.append("Le mode POI mégalithe doit rester explicitement déclaré désactivé.")
    if "IGN — géocodage" not in js:
        ERRORS.append("Le chemin de recherche de géocodage IGN doit rester identifiable.")
    if "overpass-api.de" not in js:
        ERRORS.append("Endpoint Overpass primaire absent.")
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
