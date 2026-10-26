# RQ1 public-skill primary-document field distribution

Frozen source frame: 29,292 canonical public `SKILL.original.md` files.

For each source, an agent made a simple binary judgment for each candidate information field across the complete primary skill document: YAML frontmatter (including `name` and `description`) plus every Markdown section, table, and example. A field received `1` if it was expressed anywhere in that primary file and `0` otherwise. Attached scripts, references, and other non-primary files were not read. These are descriptive occurrence counts, not a claim that every field is required by every skill, a document-quality score, or a retrieval-effect result.

| Candidate information field | Primary-document-present skills | Share of 29,292 |
|---|---:|---:|
| Use condition | 23,634 | 80.68% |
| Input / precondition | 20,618 | 70.39% |
| Output / artifact | 23,363 | 79.76% |
| Workflow / procedure | 24,412 | 83.34% |
| Success / verification | 20,968 | 71.58% |
| Boundary / not-for | 19,543 | 66.72% |
| Dependency / resource | 22,064 | 75.32% |
| Few-shot example | 19,013 | 64.91% |

## RQ1 interpretation

Prior literature motivates candidate operational information fields. Independently, this full-primary-document distribution shows that the same categories recur in naturally authored public skills at different frequencies. Together, these provide a non-arbitrary basis for selecting candidate fields for RQ1. The distribution does not establish that any field improves routing or retrieval; that remains the question for controlled RQ1 comparisons.

This census treats short descriptions and names as part of the agent-visible primary skill document. It therefore measures whether information occurs somewhere in the complete document, not whether the same information occurs specifically in the Markdown body. If RQ1 later needs a body-origin claim for a particular intervention, that origin must be stated and assessed separately.
