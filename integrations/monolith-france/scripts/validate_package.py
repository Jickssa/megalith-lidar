#!/usr/bin/env python3
"""Contrôles statiques avant intégration."""
import json,sys
from pathlib import Path
from xml.etree import ElementTree as ET
R=Path(__file__).resolve().parents[1]; errors=[]
def load(p):
 try:return json.loads((R/p).read_text(encoding='utf-8'))
 except Exception as e:errors.append(f'{p}: {e}');return {}
c=load('config/france-config.json'); s=load('config/data-sources.json'); load('config/archaeology-taxonomy.fr.json')
h=(R/'web/index.html').read_text(); j=(R/'web/app.js').read_text()
if c.get('country')!='FR' or c.get('locale')!='fr-FR':errors.append('Territoire/langue incorrects')
if c.get('detector',{}).get('enabled') is not False:errors.append('Détection IA doit rester désactivée')
for k in ('IGNF_LIDAR-HD_MNT','IGNF_LIDAR-HD_MNS','IGNF_LIDAR-HD_MNH'):
 if k not in json.dumps(s):errors.append('Couche manquante '+k)
for p in ('/assets/web/leaflet/leaflet.css','/assets/web/leaflet/leaflet.js'):
 if p not in h:errors.append('Ressource absente '+p)
if '/assets/web/france/config/france-config.json' not in j:errors.append('URL config absente')
if 'overpass-api.de' not in j or 'saveOrShareFile' not in j:errors.append('Recherche OSM / export absent')
for p in ('android/AndroidManifest-fragment.xml','android/file-provider-manifest-snippet.xml','android/res/xml/monolith_france_file_paths.xml'):
 try:ET.parse(R/p)
 except Exception as e:errors.append(f'XML {p}: {e}')
if errors:print('ECHEC\n'+'\n'.join(errors));sys.exit(1)
print('OK — configs, sources IGN, ressources, UI, export et XML.')
