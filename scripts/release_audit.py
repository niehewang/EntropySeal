#!/usr/bin/env python3
"""Fail closed on common public-release leakage classes.

This file is excluded from content matching because it necessarily contains the
patterns it enforces. All other tracked text files are scanned.
"""
from __future__ import annotations
import re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SELF=Path(__file__).resolve()
TEXT_SUFFIX={'.py','.md','.json','.yml','.yaml','.toml','.txt','.csv','.sh','.cff'}
PATTERNS={
 'venue_metadata': re.compile(r'(?i)(target\s+venue|under\s+review|submission\s+history|ieee\s+transactions\s+on\s+image\s+processing|\bTIP\b)'),
 'internal_workflow': re.compile(r'(?i)(research\s*os|latest_handoff|current_decision|next_action|project_state|return_to_chatgpt|\bchatgpt\b|\bcodex\b|experiment_execution_master_policy|public_code_release_and_github_policy)'),
 'private_path': re.compile(r'(?i)(/data/|/home/|[A-Z]:\\Users\\|jx-vmlab|jxvmlab-KVM|my_workspace|school-gpu|school-relay)'),
 'credential': re.compile(r'(?i)(github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|(?:password|passwd|secret|token)\s*[:=]\s*["\'][^"\']{8,}["\'])'),
 'private_drive_id': re.compile(r'(?i)drive\.google\.com/(?:file/d|drive/folders)/[A-Za-z0-9_-]{20,}'),
 'internal_stage': re.compile(r'\b(?:A0Q|A1W|A2V2?|A3M|A3R|A4G|A5Q|A6C)\b'),
}
ALLOW_LARGE={'.csv'}
MAX_BYTES=5*1024*1024

def main():
 bad=[]
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file() or '.git' in p.parts or p.resolve()==SELF: continue
  rel=p.relative_to(ROOT).as_posix()
  if p.stat().st_size>MAX_BYTES and p.suffix.lower() not in ALLOW_LARGE: bad.append((rel,'large_artifact',str(p.stat().st_size)))
  if p.suffix.lower() not in TEXT_SUFFIX: continue
  try:s=p.read_text(encoding='utf-8')
  except UnicodeDecodeError: continue
  s_stage=s.replace('ENTROPYSEAL_A5Q_ORDER_V1','').replace('|A4G|','')
  for name,rx in PATTERNS.items():
   hay=s_stage if name=='internal_stage' else s
   m=rx.search(hay)
   if m: bad.append((rel,name,m.group(0)[:120]))
 if bad:
  for r in bad: print('RELEASE_AUDIT_FAIL',*r,sep='\t')
  raise SystemExit(2)
 print('RELEASE_AUDIT_PASS')
if __name__=='__main__':main()
