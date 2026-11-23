#!/usr/bin/env python3
"""Regression test for Monolith France Android installer."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/install_into_megalith_lidar_android.py"
IMAGE_NAMES = (
    "layers.png",
    "layers-2x.png",
    "marker-icon.png",
    "marker-icon-2x.png",
    "marker-shadow.png",
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def invoke(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(INSTALLER), str(repo), *args],
        capture_output=True,
        text=True,
    )
    if proc.returncode:
        raise AssertionError(proc.stdout + proc.stderr)
    return proc.stdout


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="monolith-france-installer-") as tmp:
        repo = Path(tmp) / "megalith-lidar"
        activity = repo / "android/app/src/main/java/uk/megalith/lidar/MainActivity.kt"
        manifest = repo / "android/app/src/main/AndroidManifest.xml"
        leaflet = repo / "android/app/src/main/leaflet"
        prepare = repo / "scripts/prepare_android_assets.py"
        gradle = repo / "android/app/build.gradle.kts"
        strings = repo / "android/app/src/main/res/values/strings.xml"
        web_out = repo / "android/app/src/main/assets/web"

        write(activity, '''package uk.megalith.lidar
class MainActivity {
    fun saveOrShareFile(filename: String, mimeType: String, content: String) {}
    private var fileUploadCallback: ValueCallback<Array<Uri>>? = null
    fun onShowFileChooser() {
        object {
            fun choose() {
                try {
                    startActivityForResult(Intent.createChooser(Intent(), "Choose"), 1002)
                    true
                } catch (_: ActivityNotFoundException) {
                    fileUploadCallback = null
                    false
                }
            }
        }
    }
    fun setup() {
        val assetLoader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()
        setGeolocationEnabled(true)
        webView.addJavascriptInterface(AndroidBridge(), "MegalithAndroid")
    }
    companion object {
        private const val START_URL =
            "https://appassets.androidplatform.net/assets/web/index.html"
    }
}
''')
        write(manifest, '''<manifest xmlns:android="http://schemas.android.com/apk/res/android">
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
</manifest>''')
        write(leaflet / "leaflet.js", "/* Leaflet 1.9.4 */\n")
        write(leaflet / "leaflet.css", "/* Leaflet CSS */\n")
        prepare_source = '''from pathlib import Path
import shutil
REPO_ROOT = Path(__file__).resolve().parent.parent
def export_osmand_files(*args, **kwargs):
    pass
def build_atlas_home():
    return "<html lang='fr'><title>Choisir un atlas</title><a href='/assets/web/france/web/index.html'>Atlas France</a><a href='/assets/web/index.html'>Atlas britannique</a>"
def prepare_android_assets():
    web_out = REPO_ROOT / "android" / "app" / "src" / "main" / "assets" / "web"
    updated_utc = "2026-01-01T00:00:00Z"
    docs_out = web_out / "docs"
    leaflet_out = web_out / "leaflet"
    if web_out.exists():
        shutil.rmtree(web_out)
    docs_out.mkdir(parents=True, exist_ok=True)
    leaflet_out.mkdir(parents=True, exist_ok=True)
    (web_out / "index.html").write_text("<html>UK atlas</html>", encoding="utf-8")
    export_osmand_files(docs_out, updated_utc=updated_utc, include_obf=False)
    # MONOLITH_ATLAS_HOME_V1: separate atlas chooser, preserving UK index.
    (web_out / "atlas-home.html").write_text(build_atlas_home(), encoding="utf-8")
    # MONOLITH_FRANCE_INTEGRATION_V2: module copied after the asset reset.
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
if __name__ == "__main__":
    prepare_android_assets()
'''
        write(prepare, prepare_source)
        write(gradle, '''val prepareWebAssets by tasks.registering(Exec::class) {
    val rootRepoDir = rootProject.projectDir.parentFile
    inputs.file(File(rootRepoDir, "scripts/prepare_android_assets.py"))
    inputs.file(File(rootRepoDir, "scripts/export_osmand_plugin.py"))
    outputs.dir(file("src/main/assets/web"))
}
''')
        write(strings, '<resources><string name="app_name">Megalith LiDAR</string></resources>\n')

        # Real image files are read from the checked-in package and must decode.
        dry = invoke(repo, "--dry-run")
        assert "DRY-RUN OK" in dry
        assert not (repo / "integrations/monolith-france").exists()

        invoke(repo)
        # Test --force with source == destination in a separate self-hosted fixture.
        self_host = Path(tmp) / "self-hosted"
        shutil.copytree(repo, self_host)
        self_integration = self_host / "integrations/monolith-france"
        if self_integration.exists():
            shutil.rmtree(self_integration)
        shutil.copytree(ROOT, self_integration)
        self_installer = self_integration / "scripts/install_into_megalith_lidar_android.py"
        subprocess.run([sys.executable, str(self_installer), str(self_host), "--force"], check=True)
        for preserved in ("scripts/install_into_megalith_lidar_android.py", "README-INTEGRATION-FR.md", ".gitignore", "web/index.html"):
            assert (self_integration / preserved).is_file(), preserved
        assert not list((self_host / "android/app/src/main/res").rglob("*.bak"))
        self_hook = (self_host / "scripts/prepare_android_assets.py").read_text(encoding="utf-8")
        assert self_hook.count("MONOLITH_FRANCE_INTEGRATION_V2") == 1
        patched_activity = activity.read_text(encoding="utf-8")
        assert "/assets/web/atlas-home.html" in patched_activity
        assert "fileUploadCallback?.onReceiveValue(null)\n                    fileUploadCallback = null" in patched_activity
        assert "Megalith LiDAR France" in strings.read_text(encoding="utf-8")
        backup_root = repo / ".monolith-france-backups"
        assert (backup_root / "android/app/src/main/java/uk/megalith/lidar/MainActivity.kt").is_file()
        assert (backup_root / "android/app/src/main/res/values/strings.xml").is_file()
        assert not list((repo / "android/app/src/main/res").rglob("*.bak"))
        assert "integrations/monolith-france" in gradle.read_text(encoding="utf-8")
        prep_text = prepare.read_text(encoding="utf-8")
        assert prep_text.count("MONOLITH_FRANCE_INTEGRATION_V2") == 1
        assert "france_out" in prep_text and "leaflet_images" in prep_text
        assert prep_text.count("MONOLITH_ATLAS_HOME_V1") == 1
        assert "build_atlas_home" in prep_text
        repo_ignore = ROOT.parents[1] / ".gitignore"
        assert ".monolith-france-backups/" in repo_ignore.read_text(encoding="utf-8")

        # Execute the same source preparation logic after the installer has patched it.
        invoke(repo, "--force")
        subprocess.run([sys.executable, str(prepare)], check=True)
        assets = repo / "android/app/src/main/assets/web"
        home = (assets / "atlas-home.html").read_text(encoding="utf-8")
        assert "Choisir un atlas" in home
        assert "/assets/web/france/web/index.html" in home
        assert "/assets/web/index.html" in home
        assert (assets / "index.html").read_text(encoding="utf-8") == "<html>UK atlas</html>"
        france_html = (assets / "france/web/index.html").read_text(encoding="utf-8")
        assert "/assets/web/atlas-home.html" in france_html
        assert "/assets/web/index.html" in france_html
        assert (assets / "france/web/index.html").is_file()
        assert (assets / "france/config/france-config.json").is_file()
        expected_sizes = {
            "layers.png": (26, 26),
            "layers-2x.png": (52, 52),
            "marker-icon.png": (25, 41),
            "marker-icon-2x.png": (50, 82),
            "marker-shadow.png": (41, 41),
        }
        from PIL import Image
        for name, expected_size in expected_sizes.items():
            target = assets / "leaflet/images" / name
            assert target.is_file(), name
            with Image.open(target) as image:
                assert image.size == expected_size, (name, image.size, expected_size)
                image.load()
                assert image.convert("RGBA").getchannel("A").getbbox() is not None, name
        assert prep_text.count("MONOLITH_FRANCE_INTEGRATION_V2") == 1
        print("PASS — dry-run, backups, chooser routes, preserved UK index, forced re-install and regenerated assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
