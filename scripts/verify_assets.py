#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'configs/reproduction.json').read_text())
def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--checkpoint',type=Path,required=True);ap.add_argument('--upstream',type=Path,required=True);a=ap.parse_args()
 exp=CFG['upstream']; bad=[]
 got=sha256(a.checkpoint)
 if got!=exp['source_checkpoint_sha256']:bad.append(f'checkpoint sha256 {got}')
 for rec in exp['tracked_source_files']:
  p=a.upstream/rec['path']; g=sha256(p) if p.is_file() else 'MISSING'
  if g!=rec['sha256']:bad.append(f"{rec['path']}: {g}")
 if bad: raise SystemExit('asset verification failed\n  ' + '\n  '.join(bad))
 print('ASSET_VERIFY_PASS')
if __name__=='__main__':main()
