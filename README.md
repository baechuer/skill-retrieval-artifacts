# Skill Retrieval: Results and Reproducibility Artifacts

Public artifact release 1.0.1 for Jacky Zhang's University of Sydney Honours thesis,
*Skill Representation for Scalable Agent Skill Retrieval under Semantic Confusability*.

Repository: https://github.com/baechuer/skill-retrieval-artifacts

This is the reader-facing release, not the research working tree. It contains
frozen results, approved scoring labels, portable offline checks, and optional
Git LFS embeddings. No script here calls a paid model or changes benchmark labels.
The repository is public. Version 1.0.1 updates access documentation only;
the scientific data and vectors are unchanged from version 1.0.0.

## Quick start: no API keys or GPU

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone --branch v1.0.1 https://github.com/baechuer/skill-retrieval-artifacts.git
cd skill-retrieval-artifacts
python3 scripts/verify.py
python3 scripts/replay.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open http://127.0.0.1:8000/demo/ to compare the two library matrices.
No GitHub account or API model credentials are required for the public clone.
The default clone skips large vector objects. Verification still checks their pointer
identity against the manifest and states explicitly that their bytes were not downloaded.

## What is included

- **RQ1:** retained result and source-presence summaries; these are inspection artifacts,
  not a new row-level human annotation dataset or complete independent rerun.
- **RQ2 matched-content experiment:** frozen confirmatory analysis and input protocol.
- **Smaller library (3,798 skills):** all 42 aggregate conditions and the historical receipt.
  Thirty-one Qwen cells were excluded under the approved complete-case rule. Original
  smaller-library analysis prerequisites are incomplete: do not describe its aggregate
  inspection as a full ranking/statistical replay.
- **Larger library (10,000 skills):** all 42 frozen ranking conditions, both the inherited
  smaller-library and expanded acceptable sets, per-query scoring, and the canonical report.
  Scores use 1,077 requests, including 714 primary semantically confusable requests.
- **Costs:** selected aggregate rate assumptions and paired comparisons, not account bills.
- **Embeddings:** optional lossless float64 exports of retained JSON vectors, with model
  metadata and query/document chunk maps. They are data, not downloaded model weights.

Representations are Skill Metadata, Full Skill Text, Extracted Skill Profile, and Profile
without Headings. Internal IDs remain only to join frozen records. Acceptable answers
are library-specific; never apply the expanded set to the smaller-library matrix.

## Optional: download and check embeddings

Install Git LFS, then:

```sh
git lfs install --local
git lfs pull --include="embeddings/**/*.npz"
python3 -m pip install -r requirements.txt
python3 scripts/verify.py --require-embeddings
python3 scripts/replay_vectors.py --provider qwen --representation I3C-fielded
```

Vector replay inspects one cached query by default and compares the reconstructed Top-20
with the frozen first-stage list. Its report is a numerical replay check, not a new thesis
result. Git LFS downloads consume repository-owner bandwidth. Do not enable paid reruns
or assume storage/downloads are unlimited.

Read [the walkthrough](docs/WALKTHROUGH.md), [scope and data notes](docs/DATA_AND_LIMITS.md),
and `provenance/release_scope.json` before interpreting a PASS. File identities are bound
by `release_manifest.json`; original source bindings are in `provenance/source_bindings.json`.

## Citation

Jacky Zhang (2026). *Skill Representation for Scalable Agent Skill Retrieval under Semantic
Confusability: Reproducibility Artifacts*. Version 1.0.1.
https://github.com/baechuer/skill-retrieval-artifacts/tree/v1.0.1

No new blanket licence is assigned to third-party data. Third-party full documents
and model weights are not included. Public access does not certify unrestricted
reuse rights; applicable upstream terms and third-party rights remain unchanged.
