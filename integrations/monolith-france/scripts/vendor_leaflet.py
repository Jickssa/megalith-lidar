#!/usr/bin/env python3
"""Télécharge Leaflet 1.9.4 depuis unpkg et vérifie les empreintes SRI du dépôt."""
from pathlib import Path
import base64,hashlib,urllib.request
ROOT=Path(__file__).resolve().parents[1]
FILES={'leaflet.js':('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js','20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo='),'leaflet.css':('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css','p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=')}
def main():
 d=ROOT/'web/vendor';d.mkdir(parents=True,exist_ok=True)
 for name,(url,expected) in FILES.items():
  data=urllib.request.urlopen(url,timeout=30).read(); got=base64.b64encode(hashlib.sha256(data).digest()).decode()
  if got!=expected:raise SystemExit('SRI invalide: '+name)
  (d/name).write_bytes(data);print(name,len(data),'OK')
if __name__=='__main__':main()
