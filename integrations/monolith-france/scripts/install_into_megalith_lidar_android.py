#!/usr/bin/env python3
"""Installer idempotent du module France dans le projet Android megalith-lidar."""
from pathlib import Path
import argparse, re, shutil, sys
ROOT=Path(__file__).resolve().parents[1]
def backup(p):
 b=p.with_name(p.name+'.before-monolith-france.bak')
 if not b.exists(): shutil.copy2(p,b)
def patch(p,old,new,marker):
 s=p.read_text(encoding='utf-8')
 if marker in s or new in s:return
 if old not in s: raise RuntimeError(f'Ancre absente: {p}')
 backup(p); p.write_text(s.replace(old,new,1),encoding='utf-8')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('project_root',type=Path); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--force',action='store_true'); a=ap.parse_args(); r=a.project_root.resolve()
 activity=r/'android/app/src/main/java/uk/megalith/lidar/MainActivity.kt'; manifest=r/'android/app/src/main/AndroidManifest.xml'; leaf=r/'android/app/src/main/leaflet'; prep=r/'scripts/prepare_android_assets.py'; grad=r/'android/app/build.gradle.kts'; strings=r/'android/app/src/main/res/values/strings.xml'; target=r/'integrations/monolith-france'
 required=[activity,manifest,leaf/'leaflet.js',leaf/'leaflet.css',prep,grad,strings]
 missing=[str(x) for x in required if not x.exists()]
 if missing: print('Structure incompatible:\n'+'\n'.join(missing),file=sys.stderr); return 2
 at=activity.read_text(encoding='utf-8'); mf=manifest.read_text(encoding='utf-8'); ps=prep.read_text(encoding='utf-8')
 if 'addJavascriptInterface(AndroidBridge(), "MegalithAndroid")' not in at or 'fun saveOrShareFile' not in at or 'setGeolocationEnabled(true)' not in at: raise RuntimeError('Pont Android non reconnu')
 for perm in ('android.permission.INTERNET','android.permission.ACCESS_COARSE_LOCATION','android.permission.ACCESS_FINE_LOCATION'):
  if perm not in mf: raise RuntimeError(f'Permission amont absente: {perm}')
 anchor='    export_osmand_files(docs_out, updated_utc=updated_utc, include_obf=False)\n'
 if 'MONOLITH_FRANCE_INTEGRATION' not in ps and anchor not in ps: raise RuntimeError('Hook de préparation introuvable')
 if target.exists() and not a.force: raise RuntimeError('Le module existe déjà; utiliser --force après sauvegarde.')
 start=re.compile(r'(private\s+const\s+val\s+START_URL\s*=\s*\n?\s*)["\\']https://appassets\\.androidplatform\\.net/assets/web/index\\.html["\\']')
 url='https://appassets.androidplatform.net/assets/web/france/web/index.html'
 if url not in at and not start.search(at): raise RuntimeError('START_URL amont inattendue')
 if a.dry_run: print('DRY-RUN OK: structure, pont, permissions, hook assets et URL.'); return 0
 if target.exists(): shutil.rmtree(target)
 target.mkdir(parents=True)
 for folder in ('web','config','docs'): shutil.copytree(ROOT/folder,target/folder)
 # Leaflet CSS and JS remain in the upstream asset folder. Supply its missing PNG images.
 img=target/'web/vendor/images'; img.mkdir(parents=True,exist_ok=True)
 for f in ('layers.png','layers-2x.png','marker-icon.png','marker-icon-2x.png','marker-shadow.png'): shutil.copy2(ROOT/'web/vendor/images'/f,img/f)
 hook='''    # MONOLITH_FRANCE_INTEGRATION: recopier après génération des assets Android.
    fr_src = REPO_ROOT / "integrations" / "monolith-france"
    if fr_src.is_dir():
        fr_out = web_out / "france"
        if fr_out.exists(): shutil.rmtree(fr_out)
        for folder in ("web", "config", "docs"): shutil.copytree(fr_src / folder, fr_out / folder)
        img_src = fr_src / "web" / "vendor" / "images"
        img_dst = web_out / "leaflet" / "images"
        if img_src.is_dir(): shutil.copytree(img_src, img_dst, dirs_exist_ok=True)
'''
 patch(prep,anchor,anchor+hook,'MONOLITH_FRANCE_INTEGRATION')
 patch(grad,'    inputs.file(File(rootRepoDir, "scripts/export_osmand_plugin.py"))\n','    inputs.file(File(rootRepoDir, "scripts/export_osmand_plugin.py"))\n    inputs.dir(File(rootRepoDir, "integrations/monolith-france"))\n','inputs.dir(File(rootRepoDir, "integrations/monolith-france"))')
 if url not in at:
  updated,n=start.subn(lambda m:m.group(1)+'"'+url+'"',at,count=1)
  if n!=1: raise RuntimeError('Impossible de remplacer START_URL')
  backup(activity); activity.write_text(updated,encoding='utf-8')
 st=strings.read_text(encoding='utf-8')
 if 'Megalith LiDAR France' not in st:
  new=re.sub(r'(<string\s+name="app_name"[^>]*>).*?(</string>)',r'\1Megalith LiDAR France\2',st,count=1,flags=re.S)
  if new==st: raise RuntimeError('app_name introuvable')
  backup(strings); strings.write_text(new,encoding='utf-8')
 print('OK: module France installé; atlas britannique conservé; Activity et permissions réutilisées.')
 return 0
if __name__=='__main__': raise SystemExit(main())
