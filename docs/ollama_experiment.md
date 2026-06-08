# Ollama Local LLM Experiment (M5)

Documented comparison of heuristic vs Ollama paths for extraction and answer generation on `corpus_v1`.

## Environment

| Check | Status at experiment time |
|-------|---------------------------|
| Ollama server | Running (`news-graphrag doctor`) |
| `llama3.1:8b` | Not installed — run `ollama pull llama3.1:8b` |
| `nomic-embed-text` | Not installed — needed for LightRAG only |
| Heuristic baseline | Available without models |

## Experiment design

Three configurations on the same 18-question set (`data/questions_v1.json`) and index (`outputs/corpus_v1_index/`):

| Run | Index build | Query / eval |
|-----|-------------|--------------|
| **A — Heuristic baseline** | `--extractor heuristic` | `eval` (template answers) |
| **B — Ollama extraction** | `--extractor ollama --model llama3.1:8b` | `eval` |
| **C — Ollama answers** | `--extractor heuristic` | `eval --ollama` |

Compare: graph node/edge counts after ingest, average `expected_overlap`, average `latency_ms`, and 3–5 qualitative examples.

### Commands

```bash
# A — baseline (completed)
uv run news-graphrag ingest --input data/corpus_v1/corpus.json \
  --output outputs/corpus_v1_index --extractor heuristic
uv run news-graphrag eval --index outputs/corpus_v1_index \
  --questions data/questions_v1.json --timestamped

# B — Ollama extraction (run after: ollama pull llama3.1:8b)
uv run news-graphrag ingest --input data/corpus_v1/corpus.json \
  --output outputs/corpus_v1_ollama_index --extractor ollama --model llama3.1:8b
uv run news-graphrag eval --index outputs/corpus_v1_ollama_index \
  --questions data/questions_v1.json --timestamped

# C — Ollama answer wording on heuristic index
uv run news-graphrag eval --index outputs/corpus_v1_index \
  --questions data/questions_v1.json --ollama --timestamped
```

## Heuristic baseline results (Run A)

Index stats after heuristic ingest on 18 articles:

| Metric | Value |
|--------|-------|
| Nodes | 103 |
| Edges | 736 |
| `RELATED_TO` edges | 411 (noisy co-occurrence) |
| Ingest time | ~0.02 s |

Evaluation summary (`hybrid` mode not required — all modes below):

| Mode | Avg overlap | Avg latency (ms) |
|------|-------------|------------------|
| vector | 0.520 | 0 |
| keyword | 0.485 | 0 |
| graph | 0.400 | 14 |
| hybrid | 0.400 | 16 |

Full CSV: `outputs/corpus_v1_index/evaluation.csv`

## Expected Ollama effects (hypothesis)

**Extraction (Run B):** Fewer spurious `RELATED_TO` edges if JSON extraction is clean; risk of hallucinated entities on a small corpus. Latency increases to minutes for 18 articles on a laptop.

**Answer generation (Run C):** Template answers replaced by fluent prose grounded in evidence snippets; `expected_overlap` may rise for complex questions (q11, q13) where templates are generic. Latency per question typically 1–10 s depending on hardware.

## Qualitative examples (heuristic baseline)

| Question | Mode | Observation |
|----------|------|-------------|
| q1 — Maria Nowak ↔ GreenGrid | graph | Retrieves GreenGrid software article; overlap lower than vector because template emphasizes wrong evidence |
| q13 — Ewa Lewandowska role | graph | Overlap 0.0 — graph matched Warsaw summit, not port director context |
| q3 — Vistula Flood location | keyword/vector | Overlap 0.75 — correct article retrieved quickly |
| q18 — Climate Directorate scope | hybrid | Overlap 0.643 — deadline article matches resilience theme |

## Conclusion

- **Feasibility:** Ollama integration is wired (`--extractor ollama`, `--ollama` on eval/query); laptop use is practical once models are pulled.
- **Baseline value:** Heuristic path enables zero-model development and reproducible CI; quality ceiling is low for relation-heavy answers.
- **Recommendation:** Use heuristic for pipeline tests; use Ollama for demo and final report quality comparison when `llama3.1:8b` is available.

Re-run Runs B and C after `ollama pull llama3.1:8b` and append timestamped CSVs to this document.
