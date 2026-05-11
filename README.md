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

The bundled corpus is in `data/sample_articles/news_mini_corpus.json`. It contains synthetic news-style articles with repeated entities, events, locations, dates, and organizations. This avoids scraping/licensing friction while still giving the graph enough cross-document structure for a demo.

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
- `evaluation.csv`: comparison output from `news-graphrag eval`.

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
  sample_articles/    bundled demo corpus
  sample_questions.json
docs/
  research_notes.md   short notes from collected papers/docs
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
