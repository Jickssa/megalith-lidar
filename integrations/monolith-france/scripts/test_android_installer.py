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
    fun setup() {
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
def prepare_android_assets():
    web_out = REPO_ROOT / "android/app/src/main/assets/web"
    docs_out = web_out / "docs"
    leaflet_out = web_out / "leaflet"
    if web_out.exists():
        shutil.rmtree(web_out)
    docs_out.mkdir(parents=True, exist_ok=True)
    leaflet_out.mkdir(parents=True, exist_ok=True)
    (web_out / "index.html").write_text("<html>UK atlas</html>", encoding="utf-8")
    export_osmand_files(docs_out, updated_utc="2026-01-01T00:00:00Z", include_obf=False)
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
    outputs.dir(file("src/main/assets/web"))
}
''')
        write(strings, '<resources><string name="app_name">Megalith LiDAR</string></resources>\n')

        # Real image files are read from the checked-in package and must decode.
        dry = invoke(repo, "--dry-run")
        assert "DRY-RUN OK" in dry
        assert not (repo / "integrations/monolith-france").exists()

        invoke(repo)
        assert "/assets/web/france/web/index.html" in activity.read_text(encoding="utf-8")
        assert "Megalith LiDAR France" in strings.read_text(encoding="utf-8")
        assert activity.with_name(activity.name + ".before-monolith-france.bak").exists()
        assert strings.with_name(strings.name + ".before-monolith-france.bak").exists()
        assert "integrations/monolith-france" in gradle.read_text(encoding="utf-8")
        prep_text = prepare.read_text(encoding="utf-8")
        assert prep_text.count("MONOLITH_FRANCE_INTEGRATION_V2") == 1
        assert "france_out" in prep_text and "leaflet_images" in prep_text

        # Execute the same source preparation logic after the installer has patched it.
        invoke(repo, "--force")
        module_target = repo / "integrations/monolith-france"
        module_target.mkdir(parents=True, exist_ok=True)
        for folder in ("web", "config", "docs"):
            shutil.copytree(ROOT / folder, module_target / folder)
        subprocess.run([sys.executable, str(prepare)], check=True)
        assets = repo / "android/app/src/main/assets/web"
        assert (assets / "index.html").read_text(encoding="utf-8") == "<html>UK atlas</html>"
        assert (assets / "france/web/index.html").is_file()
        assert (assets / "france/config/france-config.json").is_file()
        for name in IMAGE_NAMES:
            target = assets / "leaflet/images" / name
            assert target.is_file() and target.stat().st_size > 60
            from PIL import Image
            with Image.open(target) as image:
                image.verify()
        assert prep_text.count("MONOLITH_FRANCE_INTEGRATION_V2") == 1
        print("PASS — dry-run, backups, START_URL, forced re-install, post-cleanup asset generation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
