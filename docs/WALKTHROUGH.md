# Walkthrough

## 1. Check the release

Run `python3 scripts/verify.py` from the repository root. It verifies the file inventory
and SHA-256 values, rejects unexpected files and unsafe names, and checks the Git LFS
pointers when large vectors have not been downloaded. A pointer-only PASS does not
claim that vector bytes were checked. No `.env` is needed.

## 2. Recompute larger-library scores

Run `python3 scripts/replay.py`. For every request in every condition, it checks that
the reranked list is a permutation of the frozen 20 candidates, applies the expanded
approved acceptable set, and recomputes Candidate@20, Hit@1, MRR@20, set recall, and
label coverage. It compares all recomputed values with the retained scored rows and
checks the primary means against the canonical report. Any mismatch fails the command.

This does not generate new labels, rerun models, or establish independent human truth.
Bootstrap confidence intervals are retained in the canonical report but are not re-estimated
by this lightweight command. Smaller-library aggregate results can be inspected, not fully
reconstructed from the original missing intermediates in this release.

## 3. Inspect results in the browser

Run `python3 -m http.server 8000 --bind 127.0.0.1` and open `/demo/` at that address.
Filter by library, representation, retriever, and reranker. Values come directly from
the frozen matrices. Different library sizes use their own approved acceptable answers.
MRR@20 is zero when no approved answer occurs in the Top-20; otherwise it is the
reciprocal rank of the first approved answer. Hit@1 credits any approved first answer.

## 4. Optionally inspect or replay cached vectors

Download the LFS objects as described in README, install NumPy, then run
`python3 scripts/verify.py --require-embeddings`. Run `scripts/replay_vectors.py --help`
to select one query, model, and representation. Scores use cosine similarity and a
maximum over non-truncated document chunks. Exact ties use source identity for a stable
display order. The original model-call pipeline and its numerical implementation are
not re-executed. A mismatch is reported, never substituted into the frozen matrix.

## 5. A fresh provider experiment is separate

The scripts intentionally do not contain provider authentication or execution code.
New model calls would require separately approved data access, model availability,
credentials, runtime settings, and a budget. This release supports examination and
offline replay of retained evidence, not a claim that hosted providers are immutable.
