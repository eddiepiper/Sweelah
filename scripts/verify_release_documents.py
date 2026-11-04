#!/usr/bin/env python3
"""Verify the committed RetirePilot v2.7 release-document bundle.

This only validates file integrity and presence. It is NOT financial,
security, legal or consumer acceptance certification.
"""
from pathlib import Path
import hashlib, json, sys, zipfile

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'docs_release/BINARY_DOCUMENT_MANIFEST_v2.7.json'

def main():
    m=json.loads(MANIFEST.read_text(encoding='utf-8'))
    issues=[]
    for artifact in m['artifacts']:
        p=ROOT/artifact['path']
        if not p.is_file():
            issues.append(f'MISSING {p}')
            continue
        data=p.read_bytes()
        sha=hashlib.sha256(data).hexdigest()
        if sha!=artifact['sha256']:
            issues.append(f'SHA256 MISMATCH {p}')
        if len(data)!=artifact['size_bytes']:
            issues.append(f'SIZE MISMATCH {p}')
        if p.suffix in ('.docx','.xlsx','.zip'):
            try:
                with zipfile.ZipFile(p) as z:
                    error=z.testzip()
                    if error: issues.append(f'ARCHIVE CRC FAILURE {p}: {error}')
            except zipfile.BadZipFile:
                issues.append(f'INVALID ZIP CONTAINER {p}')
        if p.suffix=='.pdf' and (not data.startswith(b'%PDF-') or b'%%EOF' not in data[-2048:]):
            issues.append(f'INVALID PDF ENVELOPE {p}')
    if m['pilot_go_no_go']!='NO-GO':
        issues.append('PILOT-GATE STATUS UNEXPECTEDLY NOT NO-GO')
    if len(m['artifacts'])!=9:
        issues.append('ARTIFACT COUNT MISMATCH')
    print(f'Verified {len(m["artifacts"])} release artifacts; errors={len(issues)}')
    for issue in issues: print('ERROR:',issue)
    return 1 if issues else 0

if __name__=='__main__': sys.exit(main())
