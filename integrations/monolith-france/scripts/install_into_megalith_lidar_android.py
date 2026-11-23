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
UK_NAV_ANCHOR = """      <a class="btn-link" href="https://github.com/GlassOnTin/megalith-lidar" target="_blank" rel="noopener" title="Source code, model checkpoints, and documentation (AGPL-3.0)">
        GitHub ↗
      </a>"""
UK_NAV_LINK = """      <a class="btn-link" href="/assets/web/atlas-home.html" data-monolith-atlas-home="true" title="Choose another atlas">Choose atlas ↗</a>
"""
START_URL = "https://appassets.androidplatform.net/assets/web/atlas-home.html"
OLD_START_URLS = (
    "https://appassets.androidplatform.net/assets/web/index.html",
    "https://appassets.androidplatform.net/assets/web/france/web/index.html",
)
START_URL_PATTERN = re.compile(
    r'(private\s+const\s+val\s+START_URL\s*=\s*)(["\'])('
    + "|".join(re.escape(url) for url in OLD_START_URLS)
    + r')\2'
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

def build_atlas_home() -> str:
    return "<!doctype html>\n<html lang=\"fr\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n<meta name=\"theme-color\" content=\"#17252b\">\n<title>Monolith — Choisir un atlas</title>\n<style>\n:root{color-scheme:dark;--bg:#101a20;--panel:#1b2b32;--line:#36515c;--text:#edf4f4;--muted:#b5c6c9;--gold:#d5aa70;--blue:#7cc6e5}\n*{box-sizing:border-box}html,body{margin:0;min-height:100%;font-family:system-ui,-apple-system,\"Segoe UI\",sans-serif;background:radial-gradient(ellipse at 50% -10%,#2d4851 0,#101a20 60%);color:var(--text)}\nbody{min-height:100dvh;display:flex;flex-direction:column}header{padding:26px 20px 14px;text-align:center}.brand{font-size:13px;letter-spacing:.24em;color:var(--gold);font-weight:800}h1{font-family:Georgia,serif;font-size:clamp(30px,7vw,48px);font-weight:500;margin:10px 0 5px}.subtitle{max-width:640px;margin:auto;color:var(--muted);line-height:1.5}\nmain{width:min(880px,calc(100% - 28px));margin:auto;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;padding:28px 0 34px}\n.atlas{display:flex;flex-direction:column;min-height:270px;text-decoration:none;color:inherit;background:linear-gradient(155deg,rgba(255,255,255,.045),transparent 60%),var(--panel);border:1px solid var(--line);border-radius:18px;overflow:hidden;transition:transform .18s,border-color .18s,box-shadow .18s}.atlas:hover,.atlas:focus-visible{transform:translateY(-3px);border-color:var(--gold);box-shadow:0 15px 40px #0005;outline:none}\n.art{height:128px;display:grid;place-items:center;position:relative;overflow:hidden;background:linear-gradient(135deg,#203c42,#15282e)}.art:before,.art:after{content:\"\";position:absolute;width:230px;height:110px;border:1px solid #d5aa7040;border-radius:50%;transform:rotate(-16deg)}.art:after{width:180px;height:80px;transform:rotate(21deg)}.art span{font-size:56px;color:var(--gold);position:relative;z-index:1;font-family:Georgia,serif}\n.france .art{background:linear-gradient(135deg,#183c53,#1d4c50 58%,#213b37)}.uk .art{background:linear-gradient(135deg,#303b50,#2a4850 58%,#394435)}\n.content{padding:19px 20px 20px;display:flex;flex-direction:column;flex:1}.kicker{font-size:10px;letter-spacing:.17em;font-weight:800;color:var(--gold);text-transform:uppercase}h2{font-family:Georgia,serif;font-size:25px;margin:7px 0 8px;font-weight:500}p{color:var(--muted);font-size:13px;line-height:1.55;margin:0 0 18px}.go{margin-top:auto;display:flex;align-items:center;justify-content:space-between;color:var(--blue);font-weight:700;font-size:13px}.go b{font-size:22px;font-weight:400}footer{text-align:center;padding:0 18px 20px;color:#82969c;font-size:11px}\n@media(max-width:620px){header{padding-top:24px}main{grid-template-columns:1fr;gap:13px;max-width:500px;padding-top:17px}.atlas{min-height:220px}.art{height:94px}.art span{font-size:44px}.content{padding:15px 17px 17px}h2{font-size:23px}}\n</style></head><body>\n<header><div class=\"brand\">MONOLITH · ATLAS</div><h1>Choisir un atlas</h1><p class=\"subtitle\">Deux territoires, deux espaces de prospection. Sélectionne la cartographie à ouvrir.</p></header>\n<main>\n<a class=\"atlas france\" href=\"/assets/web/france-home.html\" aria-label=\"Ouvrir l’accueil France\"><div class=\"art\" aria-hidden=\"true\"><span>FR</span></div><div class=\"content\"><div class=\"kicker\">France métropolitaine</div><h2>Atlas France</h2><p>Cartographie IGN, relief LiDAR HD, fonds topographiques et carnet de prospection français.</p><div class=\"go\">Découvrir l’espace français <b>→</b></div></div></a>\n<a class=\"atlas uk\" href=\"/assets/web/uk-home.html\" aria-label=\"Ouvrir l’accueil britannique\"><div class=\"art\" aria-hidden=\"true\"><span>UK</span></div><div class=\"content\"><div class=\"kicker\">Royaume-Uni</div><h2>Atlas britannique</h2><p>Atlas historique et archéologique britannique, jeux de données, analyses et outils de terrain existants.</p><div class=\"go\">Découvrir l’espace britannique <b>→</b></div></div></a>\n</main><footer>Monolith · Exploration patrimoniale et cartographie de terrain</footer></body></html>"


def build_territory_homes() -> dict[str, str]:
    """Build the two territory landing pages without duplicating either atlas."""
    template = """<!doctype html>
<html lang="@@LANG@@">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#14232b">
<title>@@TITLE@@</title>
<style>
:root{color-scheme:dark;--bg:#101a20;--panel:#1b2b32;--line:#36515c;--text:#edf4f4;--muted:#b5c6c9;--gold:#d5aa70;--blue:#7cc6e5}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:radial-gradient(ellipse at 50% -10%,#2d4851 0,#101a20 65%);color:var(--text)}
body{min-height:100dvh;display:flex;flex-direction:column}
.topbar{width:min(1040px,calc(100% - 32px));margin:0 auto;padding:22px 0;display:flex;align-items:center;justify-content:space-between;gap:12px}
.brand{font-size:12px;letter-spacing:.18em;font-weight:800;color:var(--gold);white-space:nowrap}
.back,.top-action,.secondary a{border:1px solid var(--line);border-radius:10px;padding:10px 13px;color:var(--text);text-decoration:none;font-size:13px;font-weight:650}
.back{color:var(--muted)}
.top-action{background:var(--gold);border-color:var(--gold);color:#172128;white-space:nowrap}
main{width:min(900px,calc(100% - 32px));margin:auto;flex:1;display:flex;flex-direction:column;justify-content:center;padding:30px 0 42px}
.kicker{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);font-weight:800}
h1{font-family:Georgia,"Iowan Old Style",serif;font-weight:500;font-size:clamp(34px,7vw,62px);line-height:1.06;max-width:780px;margin:13px 0 16px}
.lead{max-width:720px;color:var(--muted);font-size:clamp(15px,2vw,18px);line-height:1.65;margin:0}
.features{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:34px 0 30px}
.feature{background:linear-gradient(145deg,rgba(255,255,255,.05),transparent 70%),var(--panel);border:1px solid var(--line);border-radius:14px;padding:17px 16px;min-height:112px}
.feature strong{display:block;font-size:14px;margin-bottom:7px;color:var(--text)}
.feature span{display:block;color:var(--muted);font-size:12px;line-height:1.5}
.secondary{display:flex;flex-wrap:wrap;gap:10px}
.secondary a{color:var(--blue)}
footer{text-align:center;padding:14px 16px 22px;color:#82969c;font-size:11px}
a:focus-visible{outline:3px solid var(--blue);outline-offset:3px}
@media(max-width:640px){
 .topbar{width:calc(100% - 24px);padding:15px 0;flex-wrap:wrap}
 .brand{order:-1;width:100%}
 .back,.top-action{flex:1;text-align:center}
 main{width:calc(100% - 28px);padding:24px 0 30px}
 h1{font-size:clamp(34px,10vw,48px)}
 .features{grid-template-columns:1fr;gap:9px;margin:25px 0}
 .feature{min-height:0;padding:14px}
 .secondary a{flex:1;text-align:center}
}
</style>
</head>
<body>
<header class="topbar">
<a class="back" href="/assets/web/atlas-home.html">@@BACK_LABEL@@</a>
<span class="brand">MONOLITH · @@BRAND@@</span>
<a class="top-action" href="@@ATLAS_PATH@@">@@OPEN_LABEL@@</a>
</header>
<main>
<div class="kicker">@@REGION@@</div>
<h1>@@HEADING@@</h1>
<p class="lead">@@LEAD@@</p>
<section class="features" aria-label="@@FEATURES_LABEL@@">
<div class="feature"><strong>@@FEATURE1_TITLE@@</strong><span>@@FEATURE1_TEXT@@</span></div>
<div class="feature"><strong>@@FEATURE2_TITLE@@</strong><span>@@FEATURE2_TEXT@@</span></div>
<div class="feature"><strong>@@FEATURE3_TITLE@@</strong><span>@@FEATURE3_TEXT@@</span></div>
</section>
<nav class="secondary" aria-label="@@NAV_LABEL@@">
<a href="/assets/web/atlas-home.html">@@CHANGE_LABEL@@</a>
<a href="@@OTHER_HOME@@">@@OTHER_LABEL@@</a>
</nav>
</main>
<footer>MONOLITH · @@FOOTER@@</footer>
</body>
</html>
"""
    def render(values: dict[str, str]) -> str:
        result = template
        for key, value in values.items():
            result = result.replace("@@" + key + "@@", value)
        return result

    return {
        "france-home.html": render({
            "LANG": "fr", "TITLE": "Monolith — Accueil France", "BRAND": "FRANCE",
            "BACK_LABEL": "← Choisir un territoire", "OPEN_LABEL": "Ouvrir l’Atlas France →",
            "ATLAS_PATH": "/assets/web/france/web/index.html",
            "REGION": "France métropolitaine · cartographie de prospection",
            "HEADING": "Explorer l’Atlas France",
            "LEAD": "Un espace cartographique dédié au repérage et à la documentation du patrimoine : fonds IGN, relief LiDAR HD, recherche géographique et carnet de terrain. Les observations et les hypothèses restent clairement distinguées des sites documentés.",
            "FEATURES_LABEL": "Fonctionnalités de l’Atlas France",
            "FEATURE1_TITLE": "Cartographie IGN & OSM", "FEATURE1_TEXT": "Plan IGN v2 et OpenStreetMap, avec recherche de lieux et d’adresses.",
            "FEATURE2_TITLE": "Relief LiDAR HD", "FEATURE2_TEXT": "Couches MNT, MNS et MNH lorsque la couverture est disponible.",
            "FEATURE3_TITLE": "Carnet de prospection", "FEATURE3_TEXT": "Observations locales, import et export GeoJSON.",
            "NAV_LABEL": "Navigation territoriale", "CHANGE_LABEL": "Choisir un autre territoire",
            "OTHER_HOME": "/assets/web/uk-home.html", "OTHER_LABEL": "Accueil britannique",
            "FOOTER": "cartographie française · données et observations à recouper",
        }),
        "uk-home.html": render({
            "LANG": "en-GB", "TITLE": "Monolith — UK Atlas Home", "BRAND": "UNITED KINGDOM",
            "BACK_LABEL": "← Choose a territory", "OPEN_LABEL": "Open the UK Atlas →",
            "ATLAS_PATH": "/assets/web/index.html",
            "REGION": "United Kingdom · archaeological and landscape survey",
            "HEADING": "Explore the UK Atlas",
            "LEAD": "Open the original British survey interface for LiDAR terrain analysis, aerial cropmark context, historic Ordnance Survey mapping and field-oriented datasets. This landing page is an additional entry point; the existing atlas and its resources remain in their original locations.",
            "FEATURES_LABEL": "UK Atlas features",
            "FEATURE1_TITLE": "1 m LiDAR survey", "FEATURE1_TEXT": "Terrain screening and multi-scale diagnostic views across England.",
            "FEATURE2_TITLE": "Historic map context", "FEATURE2_TEXT": "Historic OS mapping, heritage records and OpenStreetMap cross-references.",
            "FEATURE3_TITLE": "Field data exports", "FEATURE3_TEXT": "Existing GPX, GeoJSON and OsmAnd resources.",
            "NAV_LABEL": "Territory navigation", "CHANGE_LABEL": "Choose another territory",
            "OTHER_HOME": "/assets/web/france-home.html", "OTHER_LABEL": "France Atlas home",
            "FOOTER": "British survey · candidates require independent verification",
        }),
    }


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
    # Keep generated territory pages upgrade-safe across repeated installations.
    hook_marker = "MONOLITH_FRANCE_INTEGRATION_V2"
    hook = f'''
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
        # MONOLITH_ATLAS_HOME_V1: shared territory chooser.
        (web_out / "atlas-home.html").write_text(build_atlas_home(), encoding="utf-8")
        # MONOLITH_TERRITORY_HOMES_V1: separate French and British entry pages.
        territory_homes = {build_territory_homes()!r}
        for page_name, page_html in territory_homes.items():
            (web_out / page_name).write_text(page_html, encoding="utf-8")
        # MONOLITH_UK_ATLAS_NAV_V1: return to the common chooser without changing the source.
        uk_index = web_out / "index.html"
        uk_html = uk_index.read_text(encoding="utf-8")
        if "data-monolith-atlas-home" not in uk_html:
            uk_anchor = {UK_NAV_ANCHOR!r}
            uk_link = {UK_NAV_LINK!r}
            if uk_html.count(uk_anchor) != 1:
                raise RuntimeError("Unable to locate the unique UK header GitHub link for atlas navigation.")
            uk_index.write_text(uk_html.replace(uk_anchor, uk_link + uk_anchor, 1), encoding="utf-8")
'''
    if hook_marker in prepare_text:
        marker_line = "    # MONOLITH_FRANCE_INTEGRATION_V2:"
        start = prepare_text.find(marker_line)
        if start < 0:
            raise RuntimeError("Existing Monolith France hook marker has an unexpected format.")
        next_main = prepare_text.find("\nif __name__ ==", start)
        suffix = "" if next_main < 0 else prepare_text[next_main + 1:]
        updated_prepare = prepare_text[:start] + hook.strip("\n") + "\n" + suffix
        if updated_prepare != prepare_text:
            backup_once(prepare, repo)
            prepare.write_text(updated_prepare, encoding="utf-8")
    else:
        source_lines = prepare_text.splitlines(keepends=True)
        function_indexes = [
            index for index, line in enumerate(source_lines)
            if line.lstrip().startswith("def prepare_android_assets(")
        ]
        if len(function_indexes) != 1:
            raise RuntimeError("Expected exactly one prepare_android_assets() definition.")
        home_source = (
            "def build_atlas_home():" + chr(10)
            + "    return " + repr(build_atlas_home()) + chr(10) + chr(10)
        )
        if "def build_atlas_home():" not in prepare_text:
            function_index = function_indexes[0]
            source_lines = source_lines[:function_index] + [home_source] + source_lines[function_index:]
        anchor_indexes = [
            index for index, line in enumerate(source_lines)
            if "export_osmand_files(docs_out, updated_utc=updated_utc, include_obf=False)" in line
        ]
        if len(anchor_indexes) != 1:
            raise RuntimeError("Expected exactly one OsmAnd export anchor in prepare_android_assets.py.")
        anchor_index = anchor_indexes[0]
        source_lines = source_lines[:anchor_index + 1] + [hook] + source_lines[anchor_index + 1:]
        updated_prepare = "".join(source_lines)
        backup_once(prepare, repo)
        prepare.write_text(updated_prepare, encoding="utf-8")

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
