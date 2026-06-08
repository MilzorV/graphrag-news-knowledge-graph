# GraphRAG News Knowledge Graph Prototype

Prototype MVP for testing relationship-oriented retrieval over press/news articles. It can load a small article corpus, extract a lightweight knowledge graph, build a TF-IDF vector baseline, and compare retrieval modes from a CLI or Streamlit UI.

The current MVP is intentionally laptop-friendly:

- works immediately with heuristic extraction, no model download required;
- supports local Ollama extraction/answer generation when a chat model is available;
- includes optional LightRAG commands when installed with the extra dependency;
- preserves evidence snippets and source article metadata for every answer.

## Quick Start

```bash
uv sync --extra dev
uv run news-graphrag doctor
uv run news-graphrag ingest --extractor heuristic
uv run news-graphrag query "What connects Maria Nowak with GreenGrid Europe?" --mode hybrid
uv run news-graphrag eval
```

Corpus v1 (18 articles) and extended evaluation:

```bash
uv run news-graphrag ingest --input data/corpus_v1/corpus.json --output outputs/corpus_v1_index
uv run news-graphrag eval --index outputs/corpus_v1_index --questions data/questions_v1.json
```

Start the UI:

```bash
uv run streamlit run src/news_graphrag_demo/app.py
```

The app opens a small testbench where you can rebuild the sample index, ask questions, switch between retrieval modes, inspect evidence, and run the sample evaluation set.

## Local Models

Ollama is optional for the first smoke test, but recommended for the local-LLM part of the project.

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
uv run news-graphrag doctor
```

Use Ollama extraction:

```bash
uv run news-graphrag ingest --extractor ollama --model llama3.1:8b
```

Use Ollama for final answer wording:

```bash
uv run news-graphrag query "Where did the Vistula Flood Response happen?" --mode graph --ollama
```

## Retrieval Modes

- `keyword`: lexical overlap over chunks.
- `vector`: TF-IDF vector search over article chunks.
- `graph`: entity/event matching plus graph neighborhood evidence.
- `hybrid`: graph evidence plus vector and keyword fallback.
- `lightrag`: optional external LightRAG working directory, available through separate commands.

Optional LightRAG setup:

```bash
uv sync --extra lightrag --extra dev
uv run news-graphrag lightrag-index
uv run news-graphrag lightrag-query "What are the main relationships in the corpus?"
```

## Data

The bundled demo corpus is in `data/sample_articles/news_mini_corpus.json` (8 articles). The expanded evaluation corpus is `data/corpus_v1/corpus.json` (18 interconnected energy/climate articles) with questions in `data/questions_v1.json`. Optional MIND conversion: `scripts/prepare_mind_subset.py`.

Supported input formats:

- `.txt`
- `.md`
- `.json` with one article, a list of articles, or `{ "articles": [...] }`
- `.csv` with `title` and `text`/`body`/`content` columns

Article fields used by the loader:

```json
{
  "id": "article-id",
  "title": "Article title",
  "source": "Publisher or source",
  "published_at": "YYYY-MM-DD",
  "author": "Author",
  "text": "Article body"
}
```

## Outputs

Generated files are ignored by git and written to `outputs/demo_index/` by default:

- `index.json`: articles, chunks, entities, relations, and evidence snippets;
- `vector_index.pkl`: local TF-IDF vector index;
- `run_info.json`: indexing parameters and graph counts;
- `evaluation.csv`: comparison output from `news-graphrag eval` (includes `expected_overlap` per question/mode).

Use `--timestamped` on `eval` to write `evaluation_<UTC>.csv` for comparing runs (e.g. heuristic vs Ollama).

## Documentation

- [PROGRESS.md](PROGRESS.md) — milestone tracker and 5-week sprint checklist
- [docs/literature_review.md](docs/literature_review.md) — related work summary
- [docs/tool_comparison.md](docs/tool_comparison.md) — Microsoft GraphRAG vs LightRAG vs custom pipeline
- [docs/evaluation_report.md](docs/evaluation_report.md) — mode comparison on corpus_v1
- [docs/ollama_experiment.md](docs/ollama_experiment.md) — local LLM experiment design and baseline results
- [docs/report_draft.md](docs/report_draft.md) — semester report draft
- [docs/demo_script.md](docs/demo_script.md) — 5–10 minute demo walkthrough
- [resources/pdfs/SOURCES.txt](resources/pdfs/SOURCES.txt) — PDF manifest with source URLs

## Project Structure

```text
src/news_graphrag_demo/
  app.py              Streamlit UI
  cli.py              Typer CLI
  pipeline.py         ingest -> chunk -> extract -> graph/vector index
  extraction.py       heuristic + optional Ollama JSON extraction
  retrieval.py        keyword/vector/graph/hybrid retrieval
  lightrag_adapter.py optional LightRAG wrapper
  evaluation.py       fixed question evaluation runner
data/
  sample_articles/    bundled demo corpus (8 articles)
  corpus_v1/          expanded corpus (18 articles)
  sample_questions.json
  questions_v1.json
scripts/
  prepare_mind_subset.py
docs/
  literature_review.md, tool_comparison.md, evaluation_report.md, ...
```

## Tests

```bash
uv run pytest
```

Current tests cover sample article loading, chunking, index creation, graph counts, vector artifact creation, and a hybrid query smoke test.

## Current Limitations

- Heuristic extraction is intentionally simple and noisy; use it as a deterministic baseline, not a final information extraction system.
- Ollama quality depends heavily on the local model. The `doctor` command shows missing models.
- LightRAG is optional because it is heavier and more sensitive to model setup.
- Entity resolution is basic normalized string matching with small alias hints.
- The sample corpus is synthetic; replace it with MIND, GDELT, or manually collected articles for the final evaluation.
