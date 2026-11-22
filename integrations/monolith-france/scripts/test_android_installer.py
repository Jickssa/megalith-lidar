#!/usr/bin/env python3
"""Test de l'installateur sur un projet Android factice."""
from pathlib import Path
import tempfile,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]; SCRIPT=ROOT/'scripts/install_into_megalith_lidar_android.py'
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def main():
 with tempfile.TemporaryDirectory() as td:
  r=Path(td); a=r/'android/app/src/main/java/uk/megalith/lidar/MainActivity.kt'; m=r/'android/app/src/main/AndroidManifest.xml'; l=r/'android/app/src/main/leaflet'; p=r/'scripts/prepare_android_assets.py'; g=r/'android/app/build.gradle.kts'; st=r/'android/app/src/main/res/values/strings.xml'
  write(a,'class MainActivity { fun saveOrShareFile(filename: String,mimeType: String,content: String){}; fun x(){ addJavascriptInterface(AndroidBridge(), "MegalithAndroid"); setGeolocationEnabled(true) }; companion object { private const val START_URL = "https://appassets.androidplatform.net/assets/web/index.html" } }')
  write(m,'<manifest><uses-permission android:name="android.permission.INTERNET"/><uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/><uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/></manifest>')
  write(l/'leaflet.js','/* Leaflet */');write(l/'leaflet.css','/* Leaflet */');write(p,'    export_osmand_files(docs_out, updated_utc=updated_utc, include_obf=False)\n');write(g,'    inputs.file(File(rootRepoDir, "scripts/export_osmand_plugin.py"))\n');write(st,'<resources><string name="app_name">Megalith LiDAR</string></resources>')
  def run(*args):
   x=subprocess.run([sys.executable,str(SCRIPT),str(r),*args],capture_output=True,text=True)
   if x.returncode:raise RuntimeError(x.stdout+x.stderr)
  run('--dry-run');run();run('--force')
  assert '/assets/web/france/web/index.html' in a.read_text()
  assert p.read_text().count('MONOLITH_FRANCE_INTEGRATION')==1
  assert 'integrations/monolith-france' in g.read_text()
 print('PASS: dry-run, installation et réinstallation idempotente.')
if __name__=='__main__':main()
