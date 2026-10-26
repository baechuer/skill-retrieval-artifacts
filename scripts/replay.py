#!/usr/bin/env python3
"""Recompute frozen larger-library scores without calling any model."""
import gzip
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ("acceptable_hit_at_1", "candidate_hit_at_20", "mrr_at_20", "set_recall_at_20", "unjudged_at_1")


def read_rows(path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        yield from (json.loads(line) for line in handle if line.strip())


def rank_metrics(ranking, candidates, acceptable, judged):
    if len(ranking) != 20 or len(set(ranking)) != 20 or set(ranking) != set(candidates) or len(candidates) != 20:
        raise ValueError("Expected a permutation of 20 unique frozen candidates")
    if not acceptable:
        raise ValueError("Empty acceptable set")
    first_rank = next((i for i, s in enumerate(ranking, 1) if s in acceptable), None)
    return {"acceptable_hit_at_1": float(ranking[0] in acceptable), "candidate_hit_at_20": float(bool(set(candidates) & acceptable)), "mrr_at_20": 0.0 if first_rank is None else 1.0 / first_rank, "set_recall_at_20": len(set(candidates) & acceptable) / len(acceptable), "unjudged_at_1": float(ranking[0] not in judged)}


def main():
    from verify import verify
    checked = verify()
    if checked["status"] != "PASS":
        raise ValueError("Verify the release before replay: " + str(checked["errors"]))
    labels = {r["prompt_id"]: r for r in read_rows(ROOT / "benchmark/acceptable_sets.jsonl.gz")}
    expected = {(r["condition_id"], r["prompt_id"]): r for r in read_rows(ROOT / "results/larger_library/scored_rows.jsonl.gz")}
    if len(labels) != 1077 or len(expected) != 42 * 1077:
        raise ValueError("Frozen scope mismatch")
    report = json.loads((ROOT / "results/larger_library/report.json").read_text())
    recomputed, seen = {}, set()
    for path in sorted((ROOT / "rankings/larger_library").glob("*.jsonl.gz")):
        primary = []
        condition_ids = set()
        for row in read_rows(path):
            condition, prompt = row["condition_id"], row["prompt_id"]
            condition_ids.add(condition)
            key = (condition, prompt)
            if key in seen or key not in expected:
                raise ValueError("Duplicate or unexpected ranking identity")
            seen.add(key)
            label = labels[prompt]
            if row["prompt_sha256"] != label["prompt_sha256"]:
                raise ValueError("Prompt hash mismatch")
            values = rank_metrics(row["ranking"], row["candidates"], set(label["larger_acceptable_sources"]), set(label["larger_judged_sources"]))
            for metric in METRICS:
                if not math.isclose(values[metric], expected[key]["final_" + metric], abs_tol=1e-12):
                    raise ValueError("Per-query score mismatch: " + condition + "/" + prompt + "/" + metric)
            if label["primary_714"]:
                primary.append(values)
        if len(condition_ids) != 1 or len(primary) != 714:
            raise ValueError("Condition or primary scope mismatch")
        condition = next(iter(condition_ids))
        summary = {metric: sum(r[metric] for r in primary) / len(primary) for metric in METRICS}
        for metric in METRICS:
            if not math.isclose(summary[metric], report["conditions"][condition]["primary_714"][metric], abs_tol=1e-12):
                raise ValueError("Aggregate mismatch: " + condition + "/" + metric)
        recomputed[condition] = summary
    if seen != set(expected) or len(recomputed) != 42:
        raise ValueError("Incomplete ranking coverage")
    print(json.dumps({"status": "PASS", "conditions": len(recomputed), "scored_rows_verified": len(seen), "primary_requests_per_condition": 714, "provider_calls": 0, "smaller_library": "aggregate inspection only", "bootstrap_intervals": "retained, not re-estimated"}, indent=2))


if __name__ == "__main__":
    main()
