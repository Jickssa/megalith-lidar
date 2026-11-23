#!/usr/bin/env python3
"""Install Monolith France in the upstream Android project, idempotently."""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
IMAGE_NAMES = (
    "layers.png",
    "layers-2x.png",
    "marker-icon.png",
    "marker-icon-2x.png",
    "marker-shadow.png",
)
START_URL = "https://appassets.androidplatform.net/assets/web/france/web/index.html"
OLD_START_URL = "https://appassets.androidplatform.net/assets/web/index.html"
START_URL_PATTERN = re.compile(
    r'(private\s+const\s+val\s+START_URL\s*=\s*)(["\'])'
    + re.escape(OLD_START_URL)
    + r'\2'
)


FILE_CHOOSER_CATCH_OLD = """                } catch (_: ActivityNotFoundException) {
                    fileUploadCallback = null
                    false
                }"""
FILE_CHOOSER_CATCH_NEW = """                } catch (_: ActivityNotFoundException) {
                    fileUploadCallback?.onReceiveValue(null)
                    fileUploadCallback = null
                    false
                }"""

def backup_once(path: Path, repo: Path) -> None:
    # Keep backups out of Android source/resource trees: AGP scans res/values.
    relative = path.resolve().relative_to(repo.resolve())
    backup = repo / ".monolith-france-backups" / relative
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        shutil.copy2(path, backup)


def replace_text_once(path: Path, repo: Path, old: str, new: str, marker: str) -> None:
    content = path.read_text(encoding="utf-8")
    if marker in content:
        return
    if old not in content:
        raise RuntimeError(f"Anchor not found in {path}: {old!r}")
    backup_once(path, repo)
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


def validate_png(path: Path) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required to validate Leaflet PNG assets.") from exc
    try:
        with Image.open(path) as image:
            image.verify()
    except Exception as exc:
        raise RuntimeError(f"Invalid Leaflet PNG asset: {path}: {exc}") from exc


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

    required = (
        activity, manifest, leaflet / "leaflet.js", leaflet / "leaflet.css",
        prepare, gradle, strings,
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print("Incompatible source project; missing:\n" + "\n".join(missing), file=sys.stderr)
        return 2

    activity_text = activity.read_text(encoding="utf-8")
    manifest_text = manifest.read_text(encoding="utf-8")
    prepare_text = prepare.read_text(encoding="utf-8")
    gradle_text = gradle.read_text(encoding="utf-8")

    js_header = (leaflet / "leaflet.js").read_text(encoding="utf-8", errors="replace")[:1000]
    if "Leaflet" not in js_header or "1.9.4" not in js_header:
        raise RuntimeError("Upstream Leaflet 1.9.4 could not be confirmed.")

    expected_activity_tokens = (
        'addJavascriptInterface(AndroidBridge(), "MegalithAndroid")',
        "fun saveOrShareFile",
        "setGeolocationEnabled(true)",
        "WebViewAssetLoader.Builder()",
        'addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))',
        "onShowFileChooser(",
        "fileUploadCallback",
    )
    for token in expected_activity_tokens:
        if token not in activity_text:
            raise RuntimeError(f"Expected Android WebView capability absent: {token}")
    if FILE_CHOOSER_CATCH_OLD not in activity_text and FILE_CHOOSER_CATCH_NEW not in activity_text:
        raise RuntimeError("Android file chooser cancellation callback anchor not recognized.")

    for permission in (
        "android.permission.INTERNET",
        "android.permission.ACCESS_COARSE_LOCATION",
        "android.permission.ACCESS_FINE_LOCATION",
    ):
        if permission not in manifest_text:
            raise RuntimeError(f"Upstream Android permission missing: {permission}")

    if "def prepare_android_assets()" not in prepare_text:
        raise RuntimeError("prepare_android_assets() was not found.")
    if "web_out = REPO_ROOT / \"android\"" not in prepare_text:
        raise RuntimeError("Expected Android web asset generation path not found.")
    if "export_osmand_files(docs_out, updated_utc=updated_utc, include_obf=False)" not in prepare_text:
        raise RuntimeError("Expected upstream asset-generation completion anchor not found.")

    if 'inputs.file(File(rootRepoDir, "scripts/prepare_android_assets.py"))' not in gradle_text:
        raise RuntimeError("Gradle prepareWebAssets task not recognized.")

    if START_URL not in activity_text and not START_URL_PATTERN.search(activity_text):
        raise RuntimeError("Unexpected MainActivity START_URL; refusing to modify it.")

    if integration.exists() and not args.force:
        raise RuntimeError(f"{integration} already exists; pass --force to replace it.")

    images = PACKAGE_ROOT / "web/vendor/images"
    for name in IMAGE_NAMES:
        image = images / name
        if not image.is_file():
            raise RuntimeError(f"Leaflet image missing: {image}")
        validate_png(image)

    if args.dry_run:
        print("DRY-RUN OK: Android host, WebView, permissions, Leaflet, Gradle, and PNG assets.")
        return 0

    # Stage the source before replacing the destination. This is essential when
    # PACKAGE_ROOT itself is integrations/monolith-france in the repository checkout.
    with tempfile.TemporaryDirectory(prefix="monolith-france-stage-") as staging_dir:
        staged = Path(staging_dir) / "monolith-france"
        staged.mkdir(parents=True)
        for folder in ("web", "config", "docs"):
            shutil.copytree(PACKAGE_ROOT / folder, staged / folder)

        # Replace only runtime trees. Preserve scripts, README, manifests and metadata
        # when the source package is also the destination directory.
        integration.mkdir(parents=True, exist_ok=True)
        for folder in ("web", "config", "docs"):
            destination = integration / folder
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(staged / folder, destination)

    # Inject the module at the very end of the upstream asset-generation function.
    hook_marker = "MONOLITH_FRANCE_INTEGRATION_V2"
    hook = '''
    # MONOLITH_FRANCE_INTEGRATION_V2: module recopié après le nettoyage/rebuild des assets.
    france_src = REPO_ROOT / "integrations" / "monolith-france"
    if france_src.is_dir():
        france_out = web_out / "france"
        if france_out.exists():
            shutil.rmtree(france_out)
        for folder in ("web", "config", "docs"):
            shutil.copytree(france_src / folder, france_out / folder)
        leaflet_images = web_out / "leaflet" / "images"
        leaflet_images.mkdir(parents=True, exist_ok=True)
        for image_name in ("layers.png", "layers-2x.png", "marker-icon.png",
                           "marker-icon-2x.png", "marker-shadow.png"):
            shutil.copy2(france_src / "web" / "vendor" / "images" / image_name,
                         leaflet_images / image_name)
'''
    if hook_marker not in prepare_text:
        anchor = "    export_osmand_files(docs_out, updated_utc=updated_utc, include_obf=False)\n"
        replace_text_once(prepare, repo, anchor, anchor + hook, hook_marker)

    # Register the module folder as a task input so Gradle rebuilds assets when it changes.
    gradle_text = gradle.read_text(encoding="utf-8")
    gradle_marker = 'inputs.dir(File(rootRepoDir, "integrations/monolith-france"))'
    if gradle_marker not in gradle_text:
        gradle_anchor = '    inputs.file(File(rootRepoDir, "scripts/export_osmand_plugin.py"))\n'
        replace_text_once(
            gradle,
            repo,
            gradle_anchor,
            gradle_anchor + "    " + gradle_marker + "\n",
            gradle_marker,
        )

    # Release the WebView callback when Android has no file-picker activity.
    if FILE_CHOOSER_CATCH_OLD in activity.read_text(encoding="utf-8"):
        replace_text_once(
            activity, repo, FILE_CHOOSER_CATCH_OLD, FILE_CHOOSER_CATCH_NEW,
            FILE_CHOOSER_CATCH_NEW,
        )

    # Change only the known upstream START_URL declaration.
    activity_text = activity.read_text(encoding="utf-8")
    if START_URL not in activity_text:
        changed, count = START_URL_PATTERN.subn(
            lambda match: match.group(1) + '"' + START_URL + '"',
            activity_text,
            count=1,
        )
        if count != 1:
            raise RuntimeError("Unable to update the expected START_URL declaration.")
        backup_once(activity, repo)
        activity.write_text(changed, encoding="utf-8")

    strings_text = strings.read_text(encoding="utf-8")
    if "Megalith LiDAR France" not in strings_text:
        pattern = re.compile(r'(<string\s+name="app_name"[^>]*>).*?(</string>)', re.S)
        changed, count = pattern.subn(
            lambda match: match.group(1) + "Megalith LiDAR France" + match.group(2),
            strings_text,
            count=1,
        )
        if count != 1:
            raise RuntimeError("Could not find app_name resource.")
        backup_once(strings, repo)
        strings.write_text(changed, encoding="utf-8")

    print("Installation completed. UK atlas remains accessible at /assets/web/index.html.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
