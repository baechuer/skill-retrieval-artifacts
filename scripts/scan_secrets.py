#!/usr/bin/env python3
"""Scan release files without printing any matched credential value."""
import argparse
import gzip
import json
import os
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "github_token": re.compile(rb"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})"),
    "provider_token": re.compile(rb"(?:hf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,})"),
    "aws_access_id": re.compile(rb"(?:AKIA|ASIA)[A-Z0-9]{16}"),
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential_in_url": re.compile(rb"https?://[^\s/:]+:[^\s/@]+@"),
    "sensitive_assignment": re.compile(rb'''(?i)["']?(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|client[_-]?secret)["']?\s*[:=]\s*["'][A-Za-z0-9_+/.=-]{16,}["']'''),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-env", type=Path, help="Optional local comparison only; its contents are never copied or printed")
    args = parser.parse_args()
    known = []
    if args.private_env:
        for line in args.private_env.read_text().splitlines():
            if "=" not in line or line.lstrip().startswith("#"):
                continue
            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            if re.search("token|key|secret|password", key, re.I) and len(value) >= 8:
                known.append(value.encode())
    findings, count = [], 0
    for parent, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in {".git", ".venv", "__pycache__", "output"}]
        for name in files:
            path = Path(parent) / name
            relative = path.relative_to(ROOT).as_posix()
            count += 1
            if path.is_symlink() or (name.startswith(".env") and name != ".env.example") or name.lower().endswith((".pem", ".key", ".p12")):
                findings.append({"path": relative, "type": "disallowed_file"})
                continue
            if path.suffix == ".npz":
                if path.stat().st_size < 1024:
                    continue  # LFS pointer identity is checked by verify.py.
                with zipfile.ZipFile(path) as archive:
                    if set(archive.namelist()) != {"text_ids.npy", "embeddings.npy"}:
                        findings.append({"path": relative, "type": "unexpected_archive_member"})
                continue
            raw = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
            for kind, pattern in PATTERNS.items():
                if pattern.search(raw):
                    findings.append({"path": relative, "type": kind})
            if any(value in raw for value in known):
                findings.append({"path": relative, "type": "matches_private_local_credential"})
    print(json.dumps({"status": "FAIL" if findings else "PASS", "files_scanned": count, "private_value_comparison_enabled": bool(args.private_env), "findings": findings}, indent=2))
    raise SystemExit(bool(findings))


if __name__ == "__main__":
    main()
