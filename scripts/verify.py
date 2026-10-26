#!/usr/bin/env python3
"""Verify a release inventory, including optional Git LFS objects."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify(root=ROOT, require_embeddings=False):
    manifest = json.loads((root / "release_manifest.json").read_text())
    errors, pointers = [], []
    expected = set(manifest["files"]) | {"release_manifest.json"}
    for parent, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {".git", ".venv", "__pycache__", "output"}]
        for name in files:
            path = Path(parent) / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or relative not in expected:
                errors.append("Unexpected file: " + relative)
            if (name.startswith(".env") and name != ".env.example") or name.lower().endswith((".pem", ".key", ".p12")):
                errors.append("Disallowed sensitive filename: " + relative)
    for relative, item in manifest["files"].items():
        path = root / relative
        if not path.is_file() or path.is_symlink():
            errors.append("Missing or unsafe file: " + relative)
            continue
        size = path.stat().st_size
        if item["lfs"] and size < 1024:
            text = path.read_text(errors="replace")
            match = re.fullmatch(r"version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n", text)
            if not match or match[1] != item["sha256"] or int(match[2]) != item["bytes"]:
                errors.append("LFS pointer mismatch: " + relative)
            else:
                pointers.append(relative)
            continue
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        if size != item["bytes"] or digest.hexdigest() != item["sha256"]:
            errors.append("Hash/size mismatch: " + relative)
    if require_embeddings and pointers:
        errors.append("Embeddings were not downloaded: " + str(len(pointers)) + " LFS pointers remain")
    return {"status": "FAIL" if errors else "PASS", "files": len(manifest["files"]), "lfs_pointers_not_downloaded": len(pointers), "vector_bytes_verified": not pointers, "errors": errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-embeddings", action="store_true")
    args = parser.parse_args()
    report = verify(require_embeddings=args.require_embeddings)
    print(json.dumps(report, indent=2))
    raise SystemExit(report["status"] != "PASS")
