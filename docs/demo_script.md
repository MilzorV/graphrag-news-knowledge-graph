# Demo Script (5–10 minutes)

Audience: supervisor / seminar. Goal: show corpus → index → relationship query → evidence → graph peek.

## Prerequisites

```bash
cd graphrag-news-knowledge-graph
uv sync --extra dev
uv run news-graphrag doctor
uv run news-graphrag ingest --input data/corpus_v1/corpus.json \
  --output outputs/corpus_v1_index --extractor heuristic
```

Optional: `ollama pull llama3.1:8b` for fluent answers (`--ollama`).

---

## 1. Context (1 min)

- **Problem:** find connections between people, orgs, and events across news articles.
- **Approach:** lightweight GraphRAG testbench — graph + TF-IDF + keyword modes, optional LightRAG.
- **Corpus:** 18 synthetic energy/climate articles, shared actors (Maria Nowak, GreenGrid Europe, Amber Analytics, etc.).

## 2. Index snapshot (1 min)

```bash
uv run news-graphrag summary --index outputs/corpus_v1_index
```

Mention: ~103 nodes, ~736 edges; events as first-class nodes; evidence stored per relation.

## 3. Vector vs graph — same question (3 min)

**Question A (relationship):**

```bash
uv run news-graphrag query \
  "How is NordicGrid connected to Vilnius?" \
  --index outputs/corpus_v1_index --mode vector

uv run news-graphrag query \
  "How is NordicGrid connected to Vilnius?" \
  --index outputs/corpus_v1_index --mode graph
```

**Talking points:** Compare evidence titles/snippets. Graph mode should emphasize Vilnius talks and operations center articles.

**Question B (simple fact):**

```bash
uv run news-graphrag query \
  "Where did the Vistula Flood Response happen?" \
  --index outputs/corpus_v1_index --mode vector

uv run news-graphrag query \
  "Where did the Vistula Flood Response happen?" \
  --index outputs/corpus_v1_index --mode graph
```

**Talking points:** Vector/keyword often sufficient for “where” questions; show eval overlap scores from `evaluation_report.md`.

## 4. Streamlit UI (2 min)

```bash
uv run streamlit run src/news_graphrag_demo/app.py
```

In browser:

1. Point index path to `outputs/corpus_v1_index`.
2. Ask: *What connects Maria Nowak with GreenGrid Europe?* — mode **hybrid**.
3. Show evidence table and graph fragment plot.
4. Optionally run evaluation tab / show CSV summary.

## 5. Evaluation headline (1 min)

```bash
uv run news-graphrag eval --index outputs/corpus_v1_index \
  --questions data/questions_v1.json
```

**One-liner:** Vector highest average overlap; graph adds structured evidence for cross-article links; hybrid combines both; heuristic extraction is fast but noisy.

## 6. Optional — LightRAG (1 min, if installed)

```bash
uv sync --extra lightrag --extra dev
uv run news-graphrag lightrag-index --input data/corpus_v1/corpus.json
uv run news-graphrag lightrag-query "What are the main relationships in the corpus?"
```

Position as second external stack vs custom pipeline.

## 7. Close — limitations & next steps (1 min)

- Noisy heuristic edges; Ollama improves quality when models available.
- Synthetic corpus; MIND script ready for real data.
- Future: GLiNER, path queries, RAGAS metrics.

**Docs:** `docs/report_draft.md`, `PROGRESS.md`, `docs/evaluation_report.md`.
