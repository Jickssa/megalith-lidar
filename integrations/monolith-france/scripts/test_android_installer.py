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
        prepare_source = "#!/usr/bin/env python3\n\"\"\"Deterministically prepare bundled offline web assets for the Android APK.\n\nPopulates android/app/src/main/assets/web/ from the repository's source HTML,\nvendored Leaflet 1.9.4 assets, and survey JSON/GeoJSON datasets, while:\n  - Replacing CDN Leaflet tags with local bundled leaflet/leaflet.css & leaflet.js\n  - Stripping the web-only GoatCounter analytics script tag\n  - Deduplicating repeated NHLE/OSM features across domain GeoJSONs so the\n    bundled Android dataset loads quickly offline with identical tab counts\n  - Generating a pure-source OsmAnd plugin (.osf) and GPX waypoint export\n\"\"\"\n\nfrom __future__ import annotations\n\nimport json\nimport re\nimport shutil\nimport sys\nfrom pathlib import Path\nfrom typing import Any, Dict, List\n\nREPO_ROOT = Path(__file__).resolve().parent.parent\nSCRIPTS_DIR = REPO_ROOT / \"scripts\"\nif str(SCRIPTS_DIR) not in sys.path:\n    sys.path.insert(0, str(SCRIPTS_DIR))\n\nfrom export_osmand_plugin import export_osmand_files  # noqa: E402\n\n\ndef _clean_grid_id(val: Any) -> str:\n    return re.sub(r\"[^A-Z0-9]\", \"\", str(val or \"\").upper())\n\n\ndef _dedup_key(p: Dict[str, Any], mode: str) -> str:\n    k = _clean_grid_id(p.get(\"os_grid_ref\"))\n    if mode == \"known\":\n        mm = p.get(\"matched_monument\")\n        if isinstance(mm, dict) and mm.get(\"list_entry\"):\n            return f\"nhle_{mm['list_entry']}\"\n        osm = p.get(\"osm_archaeology_matches\")\n        if isinstance(osm, list) and osm and isinstance(osm[0], dict) and osm[0].get(\"osm_id\"):\n            return f\"osm_{osm[0]['osm_id']}\"\n    if not k:\n        k = f\"{p.get('os_grid_ref')}_{p.get('easting')}_{p.get('northing')}_{p.get('predicted_class', '')}\"\n    return k\n\n\ndef _deduplicate_features(features: List[Dict[str, Any]], mode: str) -> List[Dict[str, Any]]:\n    by_id: Dict[str, Dict[str, Any]] = {}\n    for f in features:\n        p = (f or {}).get(\"properties\") or {}\n        dk = _dedup_key(p, mode)\n        prev = by_id.get(dk)\n        if prev is None:\n            by_id[dk] = f\n        else:\n            prev_p = prev.get(\"properties\") or {}\n            prev_png = 1 if prev_p.get(\"diagnostic_png\") else 0\n            cur_png = 1 if p.get(\"diagnostic_png\") else 0\n            if cur_png > prev_png or (\n                cur_png == prev_png\n                and float(p.get(\"confidence\") or 0.0) > float(prev_p.get(\"confidence\") or 0.0)\n            ):\n                by_id[dk] = f\n    return list(by_id.values())\n\n\ndef _compact_feature(f: Dict[str, Any]) -> Dict[str, Any]:\n    p = dict((f or {}).get(\"properties\") or {})\n    if isinstance(p.get(\"nearby_nhle_monuments\"), list):\n        p[\"nearby_nhle_monuments\"] = p[\"nearby_nhle_monuments\"][:3]\n    if isinstance(p.get(\"megalithic_portal_matches\"), list):\n        p[\"megalithic_portal_matches\"] = p[\"megalithic_portal_matches\"][:3]\n    if isinstance(p.get(\"osm_archaeology_matches\"), list):\n        p[\"osm_archaeology_matches\"] = p[\"osm_archaeology_matches\"][:1]\n    if isinstance(p.get(\"osm_confounder_matches\"), list):\n        p[\"osm_confounder_matches\"] = p[\"osm_confounder_matches\"][:1]\n    if isinstance(p.get(\"environmental_confounder_hints\"), list):\n        p[\"environmental_confounder_hints\"] = p[\"environmental_confounder_hints\"][:2]\n    return {\n        \"type\": \"Feature\",\n        \"geometry\": f.get(\"geometry\"),\n        \"properties\": p,\n    }\n\n\ndef _compact_summary(summary: Dict[str, Any]) -> Dict[str, Any]:\n    out = dict(summary)\n    if isinstance(out.get(\"scanned_squares\"), list):\n        keep_sq_keys = (\n            \"square_id\",\n            \"sampling_stream\",\n            \"os_grid_ref\",\n            \"bounds_latlon\",\n            \"center_lat\",\n            \"center_lon\",\n            \"area_km2\",\n            \"rediscovered_nhle_scheduled_count\",\n            \"flagged_modern_or_karst_confounders_count\",\n            \"unidentified_candidates_count\",\n            \"unidentified_candidates_fpr_0_01_count\",\n        )\n        out[\"scanned_squares\"] = [\n            {k: sq[k] for k in keep_sq_keys if k in sq}\n            for sq in out[\"scanned_squares\"]\n            if isinstance(sq, dict)\n        ]\n    return out\n\n\ndef _write_compact_json(path: Path, payload: Any) -> None:\n    path.write_text(\n        json.dumps(payload, separators=(\",\", \":\"), ensure_ascii=False),\n        encoding=\"utf-8\",\n    )\n\n\ndef prepare_android_assets() -> None:\n    docs_src = REPO_ROOT / \"docs\"\n    leaflet_src = REPO_ROOT / \"android\" / \"app\" / \"src\" / \"main\" / \"leaflet\"\n    web_out = REPO_ROOT / \"android\" / \"app\" / \"src\" / \"main\" / \"assets\" / \"web\"\n    docs_out = web_out / \"docs\"\n    leaflet_out = web_out / \"leaflet\"\n\n    if web_out.exists():\n        shutil.rmtree(web_out)\n    docs_out.mkdir(parents=True, exist_ok=True)\n    leaflet_out.mkdir(parents=True, exist_ok=True)\n\n    # 1. Copy vendored Leaflet 1.9.4 assets\n    shutil.copyfile(leaflet_src / \"leaflet.css\", leaflet_out / \"leaflet.css\")\n    shutil.copyfile(leaflet_src / \"leaflet.js\", leaflet_out / \"leaflet.js\")\n\n    # 2. Transform index.html for local offline WebView execution (no CDN, no GoatCounter)\n    html = (REPO_ROOT / \"index.html\").read_text(encoding=\"utf-8\")\n    html = re.sub(\n        r'<link\\s+rel=\"stylesheet\"\\s+href=\"https://unpkg\\.com/leaflet@1\\.9\\.4/dist/leaflet\\.css\"[^>]*/>',\n        '<link rel=\"stylesheet\" href=\"leaflet/leaflet.css\" />',\n        html,\n    )\n    html = re.sub(\n        r'<script\\s+src=\"https://unpkg\\.com/leaflet@1\\.9\\.4/dist/leaflet\\.js\"[^>]*></script>',\n        '<script src=\"leaflet/leaflet.js\"></script>',\n        html,\n    )\n    html = re.sub(\n        r'\\s*<script[^>]*data-goatcounter=[^>]*></script>',\n        \"\",\n        html,\n    )\n    (web_out / \"index.html\").write_text(html, encoding=\"utf-8\")\n\n    # 3. Compact and copy summary JSONs and static overlays\n    summary_raw = json.loads((docs_src / \"survey_summary.json\").read_text(encoding=\"utf-8\"))\n    updated_utc = str(summary_raw.get(\"updated_at_utc\") or \"2026-01-01T00:00:00Z\").strip()\n    _write_compact_json(docs_out / \"survey_summary.json\", _compact_summary(summary_raw))\n\n    for opt_json in (\"roman_summary.json\", \"enclosure_summary.json\"):\n        src_p = docs_src / opt_json\n        if src_p.exists():\n            obj = json.loads(src_p.read_text(encoding=\"utf-8\"))\n            _write_compact_json(docs_out / opt_json, _compact_summary(obj))\n\n    for copy_json in (\n        \"uk_counties.geojson\",\n        \"roman_and_ancient_roads.geojson\",\n        \"community_annotations.json\",\n    ):\n        src_p = docs_src / copy_json\n        if src_p.exists():\n            obj = json.loads(src_p.read_text(encoding=\"utf-8\"))\n            _write_compact_json(docs_out / copy_json, obj)\n\n    if (docs_src / \"osmand_qr.svg\").exists():\n        shutil.copyfile(docs_src / \"osmand_qr.svg\", docs_out / \"osmand_qr.svg\")\n\n    # 4. Deduplicate & compact candidate GeoJSONs while preserving 100% of tab features\n    c_gj = json.loads((docs_src / \"candidates.geojson\").read_text(encoding=\"utf-8\"))\n    r_gj = json.loads((docs_src / \"roman_candidates.geojson\").read_text(encoding=\"utf-8\"))\n    e_gj = json.loads((docs_src / \"enclosure_candidates.geojson\").read_text(encoding=\"utf-8\"))\n\n    c_feats = [_compact_feature(f) for f in (c_gj.get(\"features\") or [])]\n    r_feats = [_compact_feature(f) for f in (r_gj.get(\"features\") or [])]\n    e_feats = [_compact_feature(f) for f in (e_gj.get(\"features\") or [])]\n    all_feats = c_feats + r_feats + e_feats\n\n    known_winners = _deduplicate_features(\n        [\n            f\n            for f in all_feats\n            if (f.get(\"properties\") or {}).get(\"context_category\")\n            in (\"rediscovered_nhle_scheduled\", \"rediscovered_osm_archaeology\")\n        ],\n        \"known\",\n    )\n    conf_winners = _deduplicate_features(\n        [\n            f\n            for f in all_feats\n            if (f.get(\"properties\") or {}).get(\"context_category\")\n            == \"flagged_modern_or_karst_confounder\"\n        ],\n        \"confounders\",\n    )\n\n    c_unid = [\n        f\n        for f in c_feats\n        if (f.get(\"properties\") or {}).get(\"context_category\") == \"unidentified_candidate\"\n    ]\n    r_unid = [\n        f\n        for f in r_feats\n        if (f.get(\"properties\") or {}).get(\"context_category\") == \"unidentified_candidate\"\n    ]\n    e_unid = [\n        f\n        for f in e_feats\n        if (f.get(\"properties\") or {}).get(\"context_category\") == \"unidentified_candidate\"\n    ]\n\n    _write_compact_json(\n        docs_out / \"candidates.geojson\",\n        {\"type\": \"FeatureCollection\", \"features\": c_unid + known_winners + conf_winners},\n    )\n    _write_compact_json(\n        docs_out / \"roman_candidates.geojson\",\n        {\"type\": \"FeatureCollection\", \"features\": r_unid},\n    )\n    _write_compact_json(\n        docs_out / \"enclosure_candidates.geojson\",\n        {\"type\": \"FeatureCollection\", \"features\": e_unid},\n    )\n\n    # 5. Generate pure-source OsmAnd .osf, .gpx, MapRoulette GeoJSON, and JOSM .osm in docs_out\n    export_osmand_files(docs_out, updated_utc=updated_utc, include_obf=False)\n\n\nif __name__ == \"__main__\":\n    prepare_android_assets()\n"
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
        # Exercise the installer against a copy of the real upstream asset preparer.
        real_repo = Path(tmp) / "real-upstream-fixture"
        shutil.copytree(repo, real_repo)
        real_prepare = real_repo / "scripts/prepare_android_assets.py"
        real_installer = real_repo / "integrations/monolith-france/scripts/install_into_megalith_lidar_android.py"
        subprocess.run([sys.executable, str(real_installer), str(real_repo), "--force"], check=True)
        real_text = real_prepare.read_text(encoding="utf-8")
        assert real_text.count("MONOLITH_ATLAS_HOME_V1") == 1
        assert real_text.count("export_osmand_files(docs_out, updated_utc=updated_utc, include_obf=False)") == 1
        assert "atlas-home.html" in real_text
        print("PASS — dry-run, backups, chooser routes, preserved UK index, re-install, fixture and real-upstream hook.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
