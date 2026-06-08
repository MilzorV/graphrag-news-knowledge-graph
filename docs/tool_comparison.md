# Tool Comparison: Microsoft GraphRAG vs LightRAG vs Custom Pipeline

Comparison for the semester prototype. Integration status reflects this repository, not general product maturity.

## Summary table

| Criterion | Microsoft GraphRAG | LightRAG | Custom pipeline (this repo) |
|-----------|-------------------|----------|----------------------------|
| **Integration** | Not integrated; docs/PDFs only | Optional CLI (`--extra lightrag`) | Primary path |
| **Setup** | `graphrag init`, settings YAML, LLM API or local | Ollama + `lightrag-hku` extra | `uv sync`; works with heuristics, no models |
| **Indexing** | LLM entity/relation extraction, community detection, parquet tables | Entity/relation graph + vector store in working dir | Heuristic or Ollama JSON extract → JSON index + TF-IDF pickle |
| **Graph storage** | Parquet + LanceDB (default) | LightRAG internal store | `index.json` + NetworkX at query time |
| **Query modes** | Local, global, DRIFT | naive/local/global/hybrid/mix | keyword, vector, graph, hybrid |
| **Local LLM** | Supported via config | Ollama via adapter | Ollama for extract + answer |
| **Laptop-friendly** | Heavy; indexing costly | Moderate | Light (heuristic mode) |
| **Evidence / sources** | Built into search context | Returned in query response | Evidence snippets per retrieval hit |
| **Best for** | Large corpora, thematic/global questions | Fast graph-RAG experiments | Controlled comparison, teaching, deterministic baseline |

## Microsoft GraphRAG (reference only)

**Pros:** Mature documentation; community summaries enable global search; industry reference implementation.

**Cons for this project:** Separate project layout (`graphrag init`); indexing pipeline tied to its config and storage layout; heavier dependencies and runtime than a custom MVP; not merged into our CLI/UI without significant adapter work.

**Decision:** Use collected PDFs and doc snapshots for the literature review and report. Run a standalone tutorial separately if needed; do not block the semester deliverable on MS GraphRAG integration.

## LightRAG (optional second stack)

**Pros:** Closer to “graph-enhanced RAG” with reasonable setup; already wrapped in `lightrag_adapter.py`; uses Ollama models consistent with M5 experiments.

**Cons:** Extra install (`uv sync --extra lightrag`); separate working directory from main index; quality depends on pulled models.

**Decision:** Keep optional. Satisfies REQUIREMENTS “compare at least two approaches” alongside the custom keyword/vector/graph/hybrid modes.

## Custom pipeline (primary)

**Pros:** Full control over schema, retrieval weights, and evaluation; deterministic heuristic path needs no GPU/models; Streamlit UI and CSV eval built in; transparent evidence for demo and report.

**Cons:** Heuristic extraction is noisy; no community/global search; TF-IDF vector mode is not embedding-based; entity resolution is basic string matching.

**Decision:** Primary prototype. LightRAG and documented MS GraphRAG comparison provide the multi-tool narrative for M1 and the final report.

## Retrieval mode mapping

| Question type | Best mode in custom pipeline | GraphRAG analogue |
|---------------|----------------------------|-------------------|
| “What connects X and Y?” | `graph` or `hybrid` | Local search |
| “Summarize main themes in corpus” | `vector` (weak) | Global search |
| Keyword-heavy fact lookup | `keyword` | Chunk retrieval |
| General investigator question | `hybrid` | Local + chunk fallback |

## Primary stack (documented choice)

**Custom pipeline + optional LightRAG**, graph in JSON/NetworkX, evaluation via fixed questions and `expected_overlap` metric. Report emphasis: **comparison and evaluation**, with architecture described as supporting context.
