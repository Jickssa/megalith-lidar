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
      <a class="btn-link" href="/assets/web/france/web/index.html" data-monolith-france-atlas="true" title="Open the France Atlas">France Atlas ↗</a>
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
    return """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#17252b">
<title>Monolith International — Choisir un atlas</title>
<style>
:root{color-scheme:dark;--bg:#101a20;--panel:#1b2b32;--line:#36515c;--text:#edf4f4;--muted:#b5c6c9;--gold:#d5aa70;--blue:#7cc6e5}
*{box-sizing:border-box}html,body{margin:0;min-height:100%;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:radial-gradient(ellipse at 50% -10%,#2d4851 0,#101a20 65%);color:var(--text)}
body{min-height:100dvh;display:flex;flex-direction:column}
header{text-align:center;padding:34px 18px 18px}.brand{font-size:12px;letter-spacing:.25em;font-weight:850;color:var(--gold)}h1{font:500 clamp(32px,7vw,52px) Georgia,serif;margin:12px 0 8px}.subtitle{color:var(--muted);max-width:680px;margin:auto;line-height:1.55}
main{width:min(700px,calc(100% - 28px));margin:auto;padding:20px 0 32px;flex:1}
.panel{background:linear-gradient(150deg,rgba(255,255,255,.045),transparent 65%),var(--panel);border:1px solid var(--line);border-radius:18px;padding:20px;box-shadow:0 15px 42px #0003}
label{display:block;color:var(--muted);font-size:12px;font-weight:700;margin:13px 0 7px}
select{width:100%;min-height:52px;padding:12px 14px;border:1px solid #47606a;border-radius:10px;background:#101e25;color:var(--text);font:inherit;font-size:16px}
.note{color:var(--muted);font-size:12px;line-height:1.55;margin:14px 0}
.profile{border:1px solid #3a5960;background:#12242b;border-radius:12px;padding:13px;margin-top:14px}
.profile strong{display:block;color:var(--gold);margin-bottom:5px}.profile p{font-size:12px;color:var(--muted);line-height:1.5;margin:0}
.remember{display:flex;align-items:center;gap:9px;color:var(--muted);font-size:12px;margin:17px 0}
.remember input{width:18px;height:18px;accent-color:#d5aa70}
button,.community{display:flex;width:100%;align-items:center;justify-content:center;min-height:50px;border:1px solid var(--gold);border-radius:10px;background:var(--gold);color:#172128;font:700 15px system-ui;text-decoration:none;cursor:pointer}
.community{margin-top:11px;border-color:#44626c;background:#233942;color:var(--blue)}
#status{min-height:20px;color:var(--muted);font-size:12px;margin-top:12px}
footer{text-align:center;color:#82969c;padding:0 16px 22px;font-size:11px}
button:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid var(--blue);outline-offset:3px}
@media(max-width:540px){header{padding-top:25px}.panel{padding:16px}main{padding-top:12px}}
</style>
</head>
<body>
<header><div class="brand">MONOLITH · INTERNATIONAL</div><h1 id="pageTitle">Choisir un atlas</h1><p class="subtitle" id="pageSubtitle">Sélectionne un pays et une langue disponibles. Le sélecteur ouvre directement l’un des atlas cartographiques pris en charge.</p></header>
<main><section class="panel" aria-labelledby="pageTitle">
<label for="countrySelect" id="countryLabel">Pays / territoire</label>
<select id="countrySelect" disabled><option>Chargement…</option></select>
<label for="languageSelect" id="languageLabel">Langue de l’interface</label>
<select id="languageSelect" disabled><option>Chargement…</option></select>
<p class="note" id="languageNote">Seules les langues déclarées disponibles pour le pays sélectionné sont proposées.</p>
<div class="profile" id="profileInfo"><strong>Chargement des profils territoriaux…</strong><p id="profileText"></p></div>
<label class="remember"><input id="rememberPreference" type="checkbox" checked><span id="rememberLabel">Mémoriser mon choix sur cet appareil</span></label>
<button type="button" id="openAtlas" disabled>Ouvrir l’atlas</button>
<a class="community" href="/assets/web/community-countries.html" id="communityLink">Contribuer à un nouveau pays ↗</a>
<div id="status" role="status" aria-live="polite"></div>
</section></main>
<footer>Monolith International · exploration cartographique du patrimoine</footer>
<script>
(()=>{
'use strict';
const BASE='/assets/web/france/config/';
const PREF='monolith.preferences.v1';
const $=id=>document.getElementById(id);
let catalog=null,profiles=new Map(),languages=new Map(),selectedProfile=null,selectedLanguage=null;
const fetchJson=async path=>{const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw Error(path+' — HTTP '+r.status);return r.json()};
const message=(key,fallback)=>languages.get(selectedLanguage)?.messages?.[key]||fallback;
function applyLanguage(locale){
 selectedLanguage=locale;
 const m=languages.get(locale)?.messages||{};
 document.documentElement.lang=locale;
 $('countryLabel').textContent=m.selectCountry||'Pays / territoire';
 $('languageLabel').textContent=m.selectLanguage||'Langue de l’interface';
 $('languageNote').textContent=m.countryLanguageNote||'Seules les langues prises en charge sont proposées.';
 $('rememberLabel').textContent=m.remember||'Mémoriser mon choix';
 $('openAtlas').textContent=m.open||'Ouvrir l’atlas';
 $('communityLink').textContent=(m.community||'Contribuer à un nouveau pays')+' ↗';
 $('communityLink').href='/assets/web/community-countries.html?lang='+encodeURIComponent(locale);
 $('pageTitle').textContent='Choisir un atlas';
}
function profileName(profile,locale){
 return profile?.name?.[locale]||profile?.name?.[profile?.defaultLocale]||profile?.countryCode||'Unknown';
}
function fillCountries(){
 $('countrySelect').innerHTML='';
 for(const entry of catalog.countries.filter(c=>c.status==='active')){
  const option=document.createElement('option');option.value=entry.code;option.textContent=entry.name?.['fr-FR']||entry.name?.['en-GB']||entry.code;$('countrySelect').append(option);
 }
}
async function loadProfile(code,preferredLocale){
 const entry=catalog.countries.find(c=>c.code===code&&c.status==='active');
 if(!entry)throw Error('Unsupported country profile: '+code);
 const profile=profiles.get(code)||await fetchJson(BASE+'countries/'+entry.profile);
 if(profile.status!=='active'||profile.countryCode!==code)throw Error('Country profile failed validation: '+code);
 if(!Array.isArray(profile.supportedLocales)||!profile.supportedLocales.length)throw Error('No supported UI language for '+code);
 const locales=profile.supportedLocales;
 for(const locale of locales)if(!languages.has(locale))languages.set(locale,await fetchJson(BASE+'languages/'+locale+'.json'));
 profiles.set(code,profile);selectedProfile=profile;
 $('languageSelect').innerHTML='';
 for(const locale of locales){
  const entryLanguage=languages.get(locale);
  const option=document.createElement('option');option.value=locale;option.textContent=entryLanguage.nativeName||locale;$('languageSelect').append(option);
 }
 selectedLanguage=locales.includes(preferredLocale)?preferredLocale:profile.defaultLocale;
 if(!locales.includes(selectedLanguage))selectedLanguage=locales[0];
 $('languageSelect').value=selectedLanguage;applyLanguage(selectedLanguage);
 $('profileInfo').querySelector('strong').textContent=profileName(profile,selectedLanguage)+' · '+(profile.capabilities?.archaeologicalSearch||'Profil territorial');
 $('profileText').textContent=(profile.status==='active'?'Profil territorial actif':'Profil communautaire')+' · '+profile.coordinateReferenceSystem+' · '+profile.sources.length+' source(s) déclarée(s)';
 $('openAtlas').disabled=false;
}
async function openSelected(){
 if(!selectedProfile||!selectedLanguage)return;
 const entry=catalog.countries.find(c=>c.code===selectedProfile.countryCode);
 if(!entry||!entry.supportedLanguages.includes(selectedLanguage)||!selectedProfile.supportedLocales.includes(selectedLanguage)){
  $('status').textContent=message('unsupported','This combination is unavailable.');return;
 }
 const allowedAtlasRoutes={FR:'/assets/web/france/web/index.html',GB:'/assets/web/index.html'};
 const expectedTarget=allowedAtlasRoutes[selectedProfile.countryCode];
 const target=selectedProfile.atlasEntry;
 if(!entry||entry.status!=='active'||!expectedTarget||entry.profile!==('profiles/'+selectedProfile.countryCode+'.json')||
    !entry.supportedLanguages.includes(selectedLanguage)||
    !selectedProfile.supportedLocales.includes(selectedLanguage)||
    target!==expectedTarget||!target.startsWith('/assets/web/')){
  $('status').textContent=message('unsupported','Cette combinaison pays/langue ou cette destination n’est pas autorisée.');return;
 }
 if($('rememberPreference').checked){
  localStorage.setItem(PREF,JSON.stringify({countryCode:selectedProfile.countryCode,locale:selectedLanguage}));
 }else localStorage.removeItem(PREF);
 window.location.assign(target);
}
async function init(){
 try{
  catalog=await fetchJson(BASE+'countries/catalog.json');
  const saved=(()=>{try{return JSON.parse(localStorage.getItem(PREF)||'null')}catch{return null}})();
  fillCountries();$('countrySelect').disabled=false;
  const codes=catalog.countries.filter(c=>c.status==='active').map(c=>c.code);
  const code=codes.includes(saved?.countryCode)?saved.countryCode:(codes.includes(catalog.defaultCountry)?catalog.defaultCountry:codes[0]);
  $('countrySelect').value=code;
  $('rememberPreference').checked=!!saved;
  await loadProfile(code,saved?.locale);
  $('countrySelect').addEventListener('change',e=>loadProfile(e.target.value,null).catch(showError));
  $('languageSelect').addEventListener('change',e=>{applyLanguage(e.target.value);$('profileInfo').querySelector('strong').textContent=profileName(selectedProfile,e.target.value)+' · '+(selectedProfile.capabilities?.archaeologicalSearch||'Country profile')});
  $('openAtlas').addEventListener('click',openSelected);
 }catch(e){showError(e)}
}
function showError(error){$('status').textContent='Impossible de charger le profil territorial : '+error.message;$('openAtlas').disabled=true}
document.addEventListener('DOMContentLoaded',init);
})();
</script>
</body></html>"""


def build_community_page() -> str:
    return """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#14232b"><title>Monolith Community — Country profiles</title>
<style>
:root{color-scheme:dark;--bg:#101a20;--panel:#1b2b32;--line:#36515c;--text:#edf4f4;--muted:#b5c6c9;--gold:#d5aa70;--blue:#7cc6e5}
*{box-sizing:border-box}html,body{margin:0;min-height:100%;font-family:system-ui,sans-serif;background:radial-gradient(ellipse at 50% -10%,#2d4851 0,#101a20 65%);color:var(--text)}
main{width:min(820px,calc(100% - 28px));margin:auto;padding:28px 0 40px}
h1{font:500 clamp(32px,7vw,50px) Georgia,serif}.lead{color:var(--muted);line-height:1.6}.panel{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:19px;margin:15px 0}.panel h2{font-size:18px;color:var(--gold)}li{margin:9px 0;color:var(--muted);line-height:1.5}a{color:var(--blue)}.back{display:inline-block;text-decoration:none;border:1px solid var(--line);border-radius:9px;padding:11px 14px;margin-bottom:15px}
</style></head><body><main>
<a class="back" href="/assets/web/atlas-home.html">← Retour au sélecteur</a>
<div id="fr">
<div class="brand">MONOLITH · COMMUNITY</div><h1>Contribuer à un nouveau pays</h1>
<p class="lead">Monolith est conçu pour accueillir de nouveaux profils territoriaux sans dupliquer le moteur de l'application. À ce jour, seuls les profils France métropolitaine et Royaume-Uni sont déclarés actifs.</p>
<section class="panel"><h2>Préparer un profil</h2><ol>
<li>Définir le code ISO, le CRS, l'emprise et les paramètres cartographiques.</li>
<li>Documenter les fonds, services WMTS/WMS, données LiDAR et couvertures.</li>
<li>Déclarer les sources archéologiques, les licences et les attributions.</li>
<li>Construire une taxonomie locale fondée sur des conventions documentées.</li>
<li>Fournir les traductions réellement disponibles et des tests reproductibles.</li>
<li>Valider le profil avec le schéma JSON puis ouvrir une Pull Request.</li>
</ol></section>
<section class="panel"><h2>Règles de qualité</h2><ul>
<li>Ne pas transposer les modèles ou métriques britanniques.</li><li>Ne pas présenter un tag OSM comme une confirmation archéologique.</li><li>Documenter la couverture réelle et la licence de chaque source.</li><li>Ne pas publier les coordonnées précises de sites sensibles.</li><li>Ne pas déclarer actif un profil incomplet ou non testé.</li>
</ul></section>
<p class="lead">Le paquet territorial installable depuis l'application n'est pas encore disponible. Les contributions passent actuellement par GitHub.</p>
<a href="https://github.com/Jickssa/megalith-lidar/blob/feature/monolith-international-next/integrations/monolith-france/community/CONTRIBUTING-COUNTRIES.md">Guide complet de contribution GitHub ↗</a>
</div>
<div id="en" hidden>
<div class="brand">MONOLITH · COMMUNITY</div><h1>Contribute a country</h1>
<p class="lead">Monolith is designed for additional territory profiles without duplicating the application engine. Currently only Metropolitan France and the United Kingdom are marked active.</p>
<section class="panel"><h2>Prepare a profile</h2><ol>
<li>Define the ISO code, CRS, geographic extent and map settings.</li><li>Document basemaps, WMTS/WMS services, LiDAR datasets and coverage.</li><li>Declare archaeological sources, licences and attribution.</li><li>Build a local taxonomy based on documented conventions.</li><li>Provide translations that actually exist and reproducible tests.</li><li>Validate the profile against JSON Schema and open a Pull Request.</li>
</ol></section>
<section class="panel"><h2>Quality requirements</h2><ul>
<li>Do not transfer British model scores or metrics.</li><li>Do not treat an OSM tag as archaeological confirmation.</li><li>Document coverage and licensing for each source.</li><li>Do not publish precise coordinates for sensitive sites.</li><li>Do not mark incomplete or untested profiles active.</li>
</ul></section>
<p class="lead">In-app installation of arbitrary country packages is not implemented yet. Contributions currently go through GitHub.</p>
<a href="https://github.com/Jickssa/megalith-lidar/blob/feature/monolith-international-next/integrations/monolith-france/community/CONTRIBUTING-COUNTRIES.md">Full GitHub contribution guide ↗</a>
</div>
<script>
(()=>{const p=new URLSearchParams(location.search);const en=p.get('lang')==='en-GB';document.documentElement.lang=en?'en-GB':'fr';document.getElementById('fr').hidden=en;document.getElementById('en').hidden=!en;})();
</script></main></body></html>"""


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
            "HEADING": "Atlas France",
            "LEAD": "Cette page présente l’espace français ; la carte interactive est une interface distincte. Ouvre l’Atlas France ci-dessous pour accéder aux fonds IGN et OpenStreetMap, aux couches LiDAR HD, à la recherche géographique et au carnet de prospection.",
            "FEATURES_LABEL": "Fonctionnalités de l’Atlas France",
            "FEATURE1_TITLE": "Cartographie IGN & OSM", "FEATURE1_TEXT": "Plan IGN v2 et OpenStreetMap, avec recherche de lieux et d’adresses.",
            "FEATURE2_TITLE": "Relief LiDAR HD", "FEATURE2_TEXT": "Couches MNT, MNS et MNH lorsque la couverture est disponible.",
            "FEATURE3_TITLE": "Carnet de prospection", "FEATURE3_TEXT": "Observations locales, import et export GeoJSON.",
            "NAV_LABEL": "Navigation territoriale", "CHANGE_LABEL": "Choisir un autre territoire",
            "OTHER_HOME": "/assets/web/uk-home.html", "OTHER_LABEL": "Accueil britannique",
            "FOOTER": "cartographie française · données et observations à recouper",
        }),
        "uk-home.html": render({
            "LANG": "fr", "TITLE": "Monolith — Accueil Atlas UK", "BRAND": "ROYAUME-UNI",
            "BACK_LABEL": "← Choisir un atlas", "OPEN_LABEL": "Ouvrir l’Atlas UK →",
            "ATLAS_PATH": "/assets/web/index.html",
            "REGION": "Royaume-Uni · prospection archéologique et paysagère",
            "HEADING": "Atlas UK",
            "LEAD": "Cette page présente le territoire ; elle n’est pas la carte elle-même. Ouvre l’Atlas UK ci-dessous pour accéder à l’analyse LiDAR du relief, au contexte des marques de culture aériennes, aux cartes historiques de l’Ordnance Survey, aux données candidates et aux outils de terrain.",
            "FEATURES_LABEL": "Fonctionnalités de l’Atlas UK",
            "FEATURE1_TITLE": "LiDAR à 1 m", "FEATURE1_TEXT": "Analyse du terrain et vues diagnostiques multi-échelles en Angleterre.",
            "FEATURE2_TITLE": "Cartes historiques", "FEATURE2_TEXT": "Cartographie OS ancienne, inventaires patrimoniaux et recoupements OpenStreetMap.",
            "FEATURE3_TITLE": "Exports de terrain", "FEATURE3_TEXT": "Ressources GPX, GeoJSON et OsmAnd déjà disponibles.",
            "NAV_LABEL": "Navigation territoriale", "CHANGE_LABEL": "Choisir un autre atlas",
            "OTHER_HOME": "/assets/web/france-home.html", "OTHER_LABEL": "Accueil France",
            "FOOTER": "Prospection britannique · les indices doivent être vérifiés indépendamment",
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
        # MONOLITH_ATLAS_HOME_V2: independent country and language selection.
        (web_out / "atlas-home.html").write_text(build_atlas_home(), encoding="utf-8")
        (web_out / "community-countries.html").write_text(build_community_page(), encoding="utf-8")
        for folder in ("countries", "languages"):
            source_folder = france_src / "config" / folder
            target_folder = web_out / "france" / "config" / folder
            if target_folder.exists():
                shutil.rmtree(target_folder)
            shutil.copytree(source_folder, target_folder)
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
    home_source = (
        "def build_atlas_home():" + chr(10)
        + "    return " + repr(build_atlas_home()) + chr(10) + chr(10)
        + "def build_community_page():" + chr(10)
        + "    return " + repr(build_community_page()) + chr(10) + chr(10)
    )
    if hook_marker in prepare_text:
        # Upgrade the previously injected page generator as well as its hook.
        home_start = prepare_text.find("def build_atlas_home():")
        if home_start < 0:
            raise RuntimeError("Existing atlas hook has no build_atlas_home() generator.")
        home_end = prepare_text.find("def prepare_android_assets(", home_start)
        if home_end < 0:
            raise RuntimeError("Unable to locate prepare_android_assets() after the atlas page generator.")
        prepare_text = prepare_text[:home_start] + home_source + prepare_text[home_end:]

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
