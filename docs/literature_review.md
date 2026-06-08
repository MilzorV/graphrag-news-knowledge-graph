# Literature Review

Short review aligned with the semester GraphRAG prototype for press-article relationship search. Full PDFs are in [`resources/pdfs/`](../resources/pdfs/).

## 1. GraphRAG vs classical RAG

Classical RAG retrieves semantically similar text chunks from a vector index. It works well for paraphrase-style questions but weakly represents explicit relations (who met whom, where an event occurred, which organization funded what).

**Microsoft GraphRAG** (Edge et al., 2024 — *From Local to Global*) builds a knowledge graph from documents using LLM extraction, then clusters entities into communities and generates community summaries. Query time offers:

- **Local search** — entity-centric neighborhood retrieval for questions about specific actors or events.
- **Global search** — community-summary retrieval for corpus-wide themes (“what are the main topics?”).
- **DRIFT search** — hybrid refinement starting from local context.

For news investigation, local search maps naturally to questions like “what connects person X and organization Y?” Global search matters when the corpus is large enough for meaningful communities; our MVP prioritizes local/relationship queries.

The **Graph RAG survey** (2024) and **Retrieval-Augmented Generation with Graphs** (2025) confirm the trend: graphs help multi-hop and structured questions; vector-only baselines remain important for lexical/semantic recall.

## 2. LightRAG and lighter alternatives

**LightRAG** (Guo et al., 2024) indexes entities and relations with dual-level retrieval (low-level entity detail + high-level theme). It is lighter to run than full Microsoft GraphRAG and fits laptop-scale experiments. This project keeps LightRAG as an optional external stack (`lightrag-index` / `lightrag-query`) while the main pipeline is a custom NetworkX + TF-IDF testbench.

**PathRAG** and **HippoRAG 2** (2025) explore path-based and memory-inspired graph retrieval; they are relevant for future work but not integrated in v1.

## 3. Event-centric knowledge graphs

News graphs should treat **events as first-class nodes**, not only people and organizations.

- **EventKG** models events linked to actors, places, and times in knowledge bases.
- **WikiEvents** provides an event extraction benchmark from Wikipedia; useful background for schema design.
- **MIND** (Microsoft News Dataset) offers real news articles with impressions metadata; suitable for scaling beyond the synthetic demo corpus.

Our MVP creates event nodes from article titles and event-like phrases, linking people, organizations, locations, and dates with evidence snippets.

## 4. Information extraction for news

- **GLiNER** — flexible zero-shot NER with custom labels; good next step beyond heuristics.
- **REBEL** — seq2seq relation extraction; higher quality but heavier runtime.
- **Ragas** (EACL 2024 demo) — systematic RAG evaluation metrics; deferred in favor of a fixed question set and overlap scoring for the semester MVP.

Current extraction: deterministic heuristics (baseline) + optional Ollama JSON extraction.

## 5. Stack choice for this project

| Need | Choice |
|------|--------|
| Main prototype | Custom pipeline (ingest → graph → hybrid retrieval) |
| Second approach | Optional LightRAG |
| Graph storage | JSON + NetworkX in-memory |
| Vector baseline | TF-IDF over chunks |
| Local LLM | Ollama (`llama3.1:8b`) |
| Corpus v1 | 18 English energy/climate articles (synthetic, interconnected) |

Microsoft GraphRAG is documented comparatively in [`tool_comparison.md`](tool_comparison.md) but not embedded in code — setup cost and API/indexing requirements exceed semester scope for integration.

## References (local copies)

- `resources/pdfs/papers/graphrag-from-local-to-global-arxiv-2404.16130.pdf`
- `resources/pdfs/papers/graphrag-survey-arxiv-2408.08921.pdf`
- `resources/pdfs/papers/lightrag-arxiv-2410.05779.pdf`
- `resources/pdfs/papers/mind-acl-2020.pdf`
- `resources/pdfs/papers/eventkg-arxiv-1804.04526.pdf`
- `resources/pdfs/papers/gliner-arxiv-2311.08526.pdf`
- `resources/pdfs/papers/ragas-eacl-2024-demo.pdf`
