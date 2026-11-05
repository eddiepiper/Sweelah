#!/usr/bin/env python3
"""Verify all committed SweeLah! visual design files against the checked-in manifest."""
from pathlib import Path
import hashlib, json, sys

ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))
items=manifest["items"]
if len(items)!=21:
    raise SystemExit(f"Expected 21 original artifacts, got {len(items)}")
errors=[]
for item in items:
    rel=Path(item["path"]).relative_to("design/sweelah")
    file=ROOT/rel
    if not file.is_file():
        errors.append(f"Missing: {rel}")
        continue
    data=file.read_bytes()
    sha256=hashlib.sha256(data).hexdigest()
    git_sha=hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()
    if len(data)!=item["size"] or sha256!=item["sha256"] or git_sha!=item["git_sha"]:
        errors.append(f"Incorrect content: {rel}")
    if item["kind"]=="html" and not data.startswith(b"<!DOCTYPE html>"):
        errors.append(f"Invalid HTML: {rel}")
    if rel.suffix.lower()==".gif" and not data.startswith(b"GIF89a"):
        errors.append(f"Incorrect GIF type: {rel}")
    if rel.suffix.lower()==".webp" and not (data.startswith(b"RIFF") and data[8:12]==b"WEBP"):
        errors.append(f"Incorrect WebP type: {rel}")
    if rel.suffix.lower()==".png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
        errors.append(f"Incorrect PNG type: {rel}")
if errors:
    print("\n".join(errors),file=sys.stderr)
    sys.exit(1)
htmls=sum(x["kind"]=="html" for x in items)
assets=len(items)-htmls
print(f"SweeLah! design integrity PASS: {htmls} HTML prototypes, {assets} visual assets, 21/21 matching SHA256 and Git blob hashes.")
