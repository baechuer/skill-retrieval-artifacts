#!/usr/bin/env python3
"""Inspect one cached-vector query and compare with its frozen first-stage list."""
import argparse
import json
from pathlib import Path

import numpy as np

from replay import read_rows, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["qwen", "skillrouter"], default="qwen")
    parser.add_argument("--representation", choices=["I1-discovery", "I2-original", "I3C-fielded", "I3-flat"], default="I3C-fielded")
    parser.add_argument("--prompt-id")
    args = parser.parse_args()
    from verify import verify
    if verify(require_embeddings=True)["status"] != "PASS":
        raise SystemExit("Run git lfs pull and verify.py --require-embeddings first.")
    query = next((r for r in read_rows(ROOT / "embeddings/queries.jsonl.gz") if args.prompt_id is None or r["prompt_id"] == args.prompt_id), None)
    if query is None:
        raise ValueError("Unknown prompt")
    documents = [r for r in read_rows(ROOT / f"embeddings/{args.provider}/documents.jsonl.gz") if r["representation"] == args.representation]
    query_id = query[args.provider + "_text_id"]
    needed = {query_id} | {t for r in documents for t in r["chunk_text_ids"]}
    manifest = json.loads((ROOT / "embeddings/manifest.json").read_text())
    vectors = {}
    for item in manifest["models"][args.provider]["shards"]:
        with np.load(ROOT / item["path"], allow_pickle=False) as data:
            if set(data.files) != {"text_ids", "embeddings"}:
                raise ValueError("Unexpected vector archive member")
            for text_id, vector in zip(data["text_ids"], data["embeddings"]):
                if str(text_id) in needed:
                    vectors[str(text_id)] = vector
    if set(vectors) != needed or len(documents) != 10000:
        raise ValueError("Incomplete vector or document map")
    q = vectors[query_id]
    scores = []
    for row in documents:
        value = max(float(np.dot(q, vectors[t]) / (np.linalg.norm(q) * np.linalg.norm(vectors[t]))) for t in row["chunk_text_ids"])
        scores.append((row["source_sha256"], value))
    scores.sort(key=lambda p: (-p[1], p[0]))
    rep_index = ["I1-discovery", "I2-original", "I3C-fielded", "I3-flat"].index(args.representation)
    condition = f"B{rep_index * 3 + (2 if args.provider == 'qwen' else 3):02d}-G0"
    frozen = next(r for r in read_rows(ROOT / f"rankings/larger_library/{condition}.jsonl.gz") if r["prompt_id"] == query["prompt_id"])
    actual = [r[0] for r in scores[:20]]
    print(json.dumps({"prompt_id": query["prompt_id"], "condition": condition, "candidate_overlap_at_20": len(set(actual) & set(frozen["ranking"])), "exact_order_match": actual == frozen["ranking"], "note": "Cached-vector numerical diagnostic; no frozen ranking or thesis result is changed.", "top20": actual}, indent=2))


if __name__ == "__main__":
    main()
