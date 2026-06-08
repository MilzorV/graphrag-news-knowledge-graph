# GraphRAG Prototype for Press Article Relationship Search

**Draft report** — semester project, AGH. Supervisor: Kamil Pietak.

English title: *Development of the GraphRAG prototype supporting the search for connections between objects and events occurring in press articles.*

---

## 1. Introduction and motivation

Press articles describe people, organizations, locations, and events in unstructured text. Keyword and vector search retrieve similar passages but do not explicitly model relationships (who participated in what, what connects two actors across articles).

**GraphRAG** augments retrieval with a knowledge graph: entities and relations extracted from documents support structured queries and evidence-backed answers. This project implements a laptop-friendly comparison testbench and documents how graph-enhanced retrieval behaves on a small news corpus.

## 2. Related work

See [`literature_review.md`](literature_review.md). Key points:

- Microsoft GraphRAG: local vs global vs DRIFT search; community summaries for corpus-wide questions.
- LightRAG: dual-level graph retrieval with lighter setup.
- Event-centric KG literature (EventKG, WikiEvents) and news datasets (MIND).
- Extraction tools (GLiNER, REBEL) and evaluation frameworks (Ragas) as future work.

Tool choice documented in [`tool_comparison.md`](tool_comparison.md).

## 3. Objectives

1. Explain GraphRAG vs classical RAG.
2. Compare at least two approaches (custom pipeline + optional LightRAG).
3. Build ingest → extract → graph → query pipeline on a small corpus.
4. Support relation-style investigator questions.
5. Test local LLM feasibility (Ollama).
6. Evaluate retrieval modes and document limitations.

All objectives are addressed in code and companion docs; see [`PROGRESS.md`](../PROGRESS.md).

## 4. Architecture

```text
Articles (JSON/txt/md/csv)
  → loaders → preprocessing/chunking
  → extraction (heuristic | Ollama JSON)
  → graph_store (NetworkX) + vector_index (TF-IDF)
  → storage (index.json, vector_index.pkl)
  → retrieval (keyword | vector | graph | hybrid)
  → generation (templates | Ollama)
  → CLI / Streamlit UI
```

**Entity types:** PERSON, ORGANIZATION, LOCATION, EVENT, DATE_TIME, OBJECT, TOPIC.  
**Storage:** JSON on disk; graph loaded in memory at query time.  
**Optional:** LightRAG in separate working directory.

## 5. Implementation

- **Package:** `src/news_graphrag_demo/` (Python 3.10+, `uv` / Hatchling).
- **Corpus v1:** 18 synthetic English energy/climate articles with recurring actors (`data/corpus_v1/corpus.json`).
- **Extraction:** Heuristic capitalization NER + regex relations (baseline); Ollama optional.
- **Retrieval:** Graph mode matches question entities, walks 2-hop neighborhood, merges evidence with vector/keyword in hybrid mode.
- **UI:** Streamlit app for index build, query, evidence table, graph fragment, eval runner.

## 6. Evaluation

See [`evaluation_report.md`](evaluation_report.md).

- 18 questions × 4 modes = 72 runs.
- Best average token overlap: **vector (0.520)**, then keyword, graph, hybrid.
- Graph modes add ~14 ms latency; value is in cross-article relationship evidence, not overlap score alone.
- Manual audit: graph wins on multi-entity questions (q8, q18); vector wins on simple facts (q3); q13 shows entity-resolution failure.

Local LLM notes: [`ollama_experiment.md`](ollama_experiment.md).

## 7. Limitations

- Heuristic extraction produces noisy `RELATED_TO` edges.
- No Microsoft GraphRAG or Neo4j integration in code.
- TF-IDF vector baseline, not embedding models (except via optional LightRAG).
- Template answers limit graph mode perceived quality.
- Synthetic corpus — MIND conversion script provided (`scripts/prepare_mind_subset.py`).
- No RAGAS or automated faithfulness metrics in v1.

## 8. Conclusions

The prototype demonstrates that **graph-enhanced retrieval is feasible on a laptop** and helps on relationship-heavy questions when evidence spans multiple articles. Classical vector/keyword retrieval remains strong for direct fact lookup. A **hybrid** design is justified; answer generation quality (Ollama or richer templates) is the next improvement lever.

**Report emphasis:** comparison of retrieval modes and evaluation outcomes, with architecture as supporting context.

## 9. Future work

- GLiNER / REBEL extraction backends.
- Embedding-based vector index (e.g. `nomic-embed-text`).
- Entity resolution and `SAME_AS` edges.
- Multi-hop path queries (“path between A and B”).
- RAGAS evaluation; larger MIND or GDELT subset.
- Polish-language corpus.

## 10. Reproduction

```bash
uv sync --extra dev
uv run news-graphrag doctor
uv run news-graphrag ingest --input data/corpus_v1/corpus.json --output outputs/corpus_v1_index
uv run news-graphrag eval --index outputs/corpus_v1_index --questions data/questions_v1.json
uv run streamlit run src/news_graphrag_demo/app.py
```

Demo walkthrough: [`demo_script.md`](demo_script.md).

## References

Local PDF copies listed in [`resources/pdfs/SOURCES.txt`](../resources/pdfs/SOURCES.txt).
