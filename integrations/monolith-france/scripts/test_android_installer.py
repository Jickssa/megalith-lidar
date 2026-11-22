#!/usr/bin/env python3
"""Test d'intégration Android déterministe sur fixture, sans SDK ni accès réseau."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/install_into_megalith_lidar_android.py"
IMAGE_NAMES = ("layers.png", "layers-2x.png", "marker-icon.png",
               "marker-icon-2x.png", "marker-shadow.png")


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def run(repo, *args):
    p = subprocess.run([sys.executable, str(INSTALLER), str(repo), *args],
                       capture_output=True, text=True)
    if p.returncode:
        raise AssertionError(p.stdout + p.stderr)
    return p.stdout


def main():
    with tempfile.TemporaryDirectory(prefix="monolith-france-fixture-") as tmp:
        repo = Path(tmp) / "megalith-lidar"
        activity = repo / "android/app/src/main/java/uk/megalith/lidar/MainActivity.kt"
        manifest = repo / "android/app/src/main/AndroidManifest.xml"
        leaflet = repo / "android/app/src/main/leaflet"
        prepare = repo / "scripts/prepare_android_assets.py"
        gradle = repo / "android/app/build.gradle.kts"
        strings = repo / "android/app/src/main/res/values/strings.xml"
        write(activity, '''package uk.megalith.lidar
class MainActivity {
 fun saveOrShareFile(filename: String, mimeType: String, content: String) {}
 fun setup() { setGeolocationEnabled(true); webView.addJavascriptInterface(AndroidBridge(), "MegalithAndroid") }
 companion object { private const val START_URL = "https://appassets.androidplatform.net/assets/web/index.html" }
}
''')
        write(manifest, '''<manifest xmlns:android="http://schemas.android.com/apk/res/android">
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
</manifest>''')
        write(leaflet / "leaflet.js", "/* Leaflet 1.9.4 */\n")
        write(leaflet / "leaflet.css", "/* Leaflet css */\n")
        write(prepare, "    export_osmand_files(docs_out, updated_utc=updated_utc, include_obf=False)\n")
        write(gradle, '    inputs.file(File(rootRepoDir, "scripts/export_osmand_plugin.py"))\n')
        write(strings, '<resources><string name="app_name">Megalith LiDAR</string></resources>\n')

        assert "DRY-RUN OK" in run(repo, "--dry-run")
        assert not (repo / "integrations/monolith-france").exists()
        run(repo)
        dest = repo / "integrations/monolith-france"
        assert (dest / "web/index.html").is_file()
        assert (dest / "config/france-config.json").is_file()
        for name in IMAGE_NAMES:
            png = dest / "web/vendor/images" / name
            assert png.is_file() and png.read_bytes().startswith(b"\\x89PNG\\r\\n\\x1a\\n"), name
            copied = repo / "android/app/src/main/assets/web/leaflet/images" / name
            assert copied.is_file() and copied.read_bytes() == png.read_bytes(), name
        assert "/assets/web/france/web/index.html" in activity.read_text(encoding="utf-8")
        assert "integrations/monolith-france" in gradle.read_text(encoding="utf-8")
        prep_text = prepare.read_text(encoding="utf-8")
        assert prep_text.count("MONOLITH_FRANCE_INTEGRATION") == 1
        assert "france_out" in prep_text and "image_dst" in prep_text
        assert "Megalith LiDAR France" in strings.read_text(encoding="utf-8")
        assert activity.with_name(activity.name + ".before-monolith-france.bak").exists()
        run(repo, "--force")
        assert prepare.read_text(encoding="utf-8").count("MONOLITH_FRANCE_INTEGRATION") == 1
        print("PASS — dry-run, installation, PNG, sauvegardes et idempotence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
