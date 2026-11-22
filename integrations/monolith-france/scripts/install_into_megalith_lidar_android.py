#!/usr/bin/env python3
"""Installe Monolith France dans un clone source compatible de megalith-lidar."""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import shutil
import sys

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
IMAGE_NAMES = ("layers.png", "layers-2x.png", "marker-icon.png",
               "marker-icon-2x.png", "marker-shadow.png")


def backup_once(path: Path) -> None:
    backup = path.with_name(path.name + ".before-monolith-france.bak")
    if not backup.exists():
        shutil.copy2(path, backup)


def replace_once(path: Path, old: str, new: str, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text or new in text:
        return
    if old not in text:
        raise RuntimeError(f"Ancre absente dans {path}: {old!r}")
    backup_once(path)
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    repo = args.project_root.expanduser().resolve()

    activity = repo / "android/app/src/main/java/uk/megalith/lidar/MainActivity.kt"
    manifest = repo / "android/app/src/main/AndroidManifest.xml"
    leaflet = repo / "android/app/src/main/leaflet"
    prepare = repo / "scripts/prepare_android_assets.py"
    gradle = repo / "android/app/build.gradle.kts"
    strings = repo / "android/app/src/main/res/values/strings.xml"
    integration = repo / "integrations/monolith-france"
    required = (activity, manifest, leaflet / "leaflet.js", leaflet / "leaflet.css",
                prepare, gradle, strings)
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        print("Structure source incompatible :\n" + "\n".join(missing), file=sys.stderr)
        return 2

    at = activity.read_text(encoding="utf-8")
    mf = manifest.read_text(encoding="utf-8")
    prep = prepare.read_text(encoding="utf-8")
    grad = gradle.read_text(encoding="utf-8")
    leaf_header = (leaflet / "leaflet.js").read_text(encoding="utf-8", errors="replace")[:500]
    if "Leaflet 1.9.4" not in leaf_header:
        raise RuntimeError("Leaflet source 1.9.4 non confirmé; arrêt préventif.")
    for token in ('addJavascriptInterface(AndroidBridge(), "MegalithAndroid")',
                  "fun saveOrShareFile", "setGeolocationEnabled(true)"):
        if token not in at:
            raise RuntimeError(f"Capacité WebView attendue absente : {token}")
    for permission in ("android.permission.INTERNET", "android.permission.ACCESS_COARSE_LOCATION",
                       "android.permission.ACCESS_FINE_LOCATION"):
        if permission not in mf:
            raise RuntimeError(f"Permission amont absente : {permission}")
    anchor = "    export_osmand_files(docs_out, updated_utc=updated_utc, include_obf=False)\n"
    if "MONOLITH_FRANCE_INTEGRATION" not in prep and anchor not in prep:
        raise RuntimeError("Hook de préparation Android introuvable.")
    if 'inputs.dir(File(rootRepoDir, "integrations/monolith-france"))' not in grad and \
       'inputs.file(File(rootRepoDir, "scripts/export_osmand_plugin.py"))' not in grad:
        raise RuntimeError("Point d'entrée des inputs Gradle non reconnu.")
    start_re = re.compile(
        r'(private\\s+const\\s+val\\s+START_URL\\s*=\\s*\\n?\\s*)'
        r'"https://appassets\\.androidplatform\\.net/assets/web/index\\.html"'
    )
    start_url = "https://appassets.androidplatform.net/assets/web/france/web/index.html"
    if start_url not in at and not start_re.search(at):
        raise RuntimeError("START_URL amont inattendue; arrêt sans modification.")
    if integration.exists() and not args.force:
        raise RuntimeError(f"{integration} existe; utiliser --force pour remplacer explicitement.")

    source_images = PACKAGE_ROOT / "web/vendor/images"
    for name in IMAGE_NAMES:
        p = source_images / name
        if not p.is_file() or p.stat().st_size < 60 or p.read_bytes()[:8] != b"\\x89PNG\\r\\n\\x1a\\n":
            raise RuntimeError(f"Image Leaflet absente ou invalide : {p}")
    if args.dry_run:
        print("DRY-RUN OK : source, Activity, permissions, Leaflet, hook et Gradle.")
        return 0

    if integration.exists():
        shutil.rmtree(integration)
    integration.mkdir(parents=True)
    for folder in ("web", "config", "docs"):
        shutil.copytree(PACKAGE_ROOT / folder, integration / folder)

    # The upstream app ships its own Leaflet 1.9.4 CSS/JS. Supply its image
    # assets beside that CSS because the upstream APK omitted them.
    image_out = repo / "android/app/src/main/assets/web/leaflet/images"
    image_out.mkdir(parents=True, exist_ok=True)
    for name in IMAGE_NAMES:
        shutil.copy2(source_images / name, image_out / name)

    hook = '''    # MONOLITH_FRANCE_INTEGRATION: réinstaller les assets après leur génération.
    france_src = REPO_ROOT / "integrations" / "monolith-france"
    if france_src.is_dir():
        france_out = web_out / "france"
        if france_out.exists():
            shutil.rmtree(france_out)
        for folder in ("web", "config", "docs"):
            shutil.copytree(france_src / folder, france_out / folder)
        image_src = france_src / "web" / "vendor" / "images"
        image_dst = web_out / "leaflet" / "images"
        image_dst.mkdir(parents=True, exist_ok=True)
        for image_name in ("layers.png", "layers-2x.png", "marker-icon.png",
                           "marker-icon-2x.png", "marker-shadow.png"):
            shutil.copy2(image_src / image_name, image_dst / image_name)
'''
    replace_once(prepare, anchor, anchor + hook, "MONOLITH_FRANCE_INTEGRATION")
    grad_anchor = '    inputs.file(File(rootRepoDir, "scripts/export_osmand_plugin.py"))\n'
    if 'inputs.dir(File(rootRepoDir, "integrations/monolith-france"))' not in grad:
        replace_once(gradle, grad_anchor, grad_anchor +
                     '    inputs.dir(File(rootRepoDir, "integrations/monolith-france"))\n',
                     'inputs.dir(File(rootRepoDir, "integrations/monolith-france"))')

    at_now = activity.read_text(encoding="utf-8")
    if start_url not in at_now:
        patched, count = start_re.subn(lambda m: m.group(1) + '"' + start_url + '"', at_now, count=1)
        if count != 1:
            raise RuntimeError("START_URL impossible à remplacer après validation.")
        backup_once(activity)
        activity.write_text(patched, encoding="utf-8")
    st = strings.read_text(encoding="utf-8")
    if "Megalith LiDAR France" not in st:
        updated, count = re.subn(r'(<string\\s+name="app_name"[^>]*>).*?(</string>)',
                                 r'\\1Megalith LiDAR France\\2', st, count=1, flags=re.S)
        if count != 1:
            raise RuntimeError("Ressource app_name introuvable.")
        backup_once(strings)
        strings.write_text(updated, encoding="utf-8")
    print("Installation terminée. Atlas britannique conservé; Activity et permissions réutilisées.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
