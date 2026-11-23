#!/usr/bin/env python3
"""Copie le module France dans le dossier assets d'une application hôte WebView."""
from pathlib import Path
import argparse,shutil
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('project_root',type=Path);p.add_argument('--destination',default='app/src/main/assets/monolith-france');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
 dst=a.project_root/a.destination
 if a.dry_run: print(f'{ROOT}/web -> {dst}');return 0
 if dst.exists():raise SystemExit(f'{dst} existe; déplacer ou supprimer explicitement avant installation.')
 dst.mkdir(parents=True)
 for f in ('web','config','docs'):shutil.copytree(ROOT/f,dst/f)
 print('Module copié:',dst);return 0
if __name__=='__main__':raise SystemExit(main())
