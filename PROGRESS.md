# Project progress

Use Markdown task lists: `- [ ]` not done, `- [x]` done. Update this file as you finish items.

**References:** [REQUIREMENTS.md](./REQUIREMENTS.md) (especially §3 objectives, §17 milestones, §19 open questions).

**Sprint start:** June 2026 (5-week continuation plan).

---

## Done so far

- [x] Requirements and scope documented (`REQUIREMENTS.md`)
- [x] Reference PDFs collected under `resources/pdfs/` (papers + doc snapshots)
- [x] `.gitignore` includes `.DS_Store`
- [x] MVP scaffold added: Python package, CLI, Streamlit UI, sample corpus, evaluation questions
- [x] Deterministic baseline pipeline works: ingest → chunk → heuristic extract → graph/vector indexes → query
- [x] Optional Ollama and LightRAG integration points added
- [x] Literature review and tool comparison docs (`docs/literature_review.md`, `docs/tool_comparison.md`)
- [x] Expanded corpus v1 (18 articles) and evaluation questions (`data/corpus_v1/`, `data/questions_v1.json`)
- [x] Evaluation overlap metric in `evaluation.py`
- [x] Ollama experiment notes (`docs/ollama_experiment.md`)
- [x] Evaluation report with mode comparison (`docs/evaluation_report.md`)
- [x] Report draft, demo script, PDF manifest (`docs/report_draft.md`, `docs/demo_script.md`, `resources/pdfs/SOURCES.txt`)

---

## Ongoing tracker (maps to milestones)

### Decisions (§19 open questions)

- [x] Main prototype stack chosen (LightRAG harness + lightweight local baselines)
- [x] Graph storage choice for v1 (local JSON + NetworkX; LightRAG working dir optional)
- [x] Corpus language(s): English for v1 bundled demo
- [x] First local LLM to test (Ollama `llama3.1:8b`; heuristic fallback)
- [x] Target article count for demo (18 in corpus_v1; 10–30 recommended for final)
- [x] UI emphasis: NL answers plus evidence and graph fragment
- [x] Event extraction depth (light event nodes from titles/event-like phrases)
- [x] Report emphasis: **comparison + evaluation** (architecture as supporting section)

### Milestone coverage

- [x] **M1** Literature and tool review complete
- [x] **M2** Tutorial POC run end-to-end on sample data
- [x] **M3** Article corpus prepared + test question set
- [x] **M4** Prototype: ingest → extract → graph → query (+ simple UI)
- [x] **M5** Local LLM experiment documented (vs cloud if applicable)
- [x] **M6** Evaluation run (baseline + qualitative/quantitative notes)
- [x] **M7** Final report draft + demo scenario + findings summary

### Core objectives (§3) — check when evidenced in repo or report

- [x] GraphRAG vs classical RAG explained (report or docs)
- [x] At least two approaches/tools compared; one main path selected
- [x] POC processes a small article corpus
- [x] Entities / events / relations extracted (as designed)
- [x] Knowledge stored in a graph-like form
- [x] Simple search or query interface works
- [x] Relation-style questions supported (within chosen limits)
- [x] Local LLM feasibility tested where applicable
- [x] Evaluation shows whether the approach helps for your case
- [x] Final report covers assumptions, architecture, tests, limits, continuation

---

## Next five weeks (week-by-week)

Sprint: June 9 – July 13, 2026.

### Week 1 — Literature and tool comparison (M1) ✓

- [x] Skim official GraphRAG docs + survey paper; note local vs global search roles
- [x] Run LightRAG tutorial path on sample corpus (optional extra)
- [x] Short notes: setup issues, config knobs, index vs query output
- [x] Document primary stack choice (`docs/tool_comparison.md`)
- [x] Resolve report emphasis (comparison + evaluation)

### Week 2 — Corpus expansion (M3 extension) ✓

- [x] Select dataset: expanded synthetic energy/climate corpus (MIND script optional)
- [x] Normalize input format (`data/corpus_v1/corpus.json`)
- [x] Entity / event / relation schema documented in `research_notes.md`
- [x] Write 18 investigator-style test questions (`data/questions_v1.json`)
- [x] Rebuild index on corpus_v1

### Week 3 — Ollama experiment (M5) ✓

- [x] Run heuristic baseline eval on corpus_v1
- [x] Document Ollama extraction/answer experiment (`docs/ollama_experiment.md`)
- [x] Add `expected_overlap` metric to evaluation pipeline
- [x] CLI support for timestamped eval output

### Week 4 — Evaluation narrative (M6) ✓

- [x] Full eval: keyword, vector, graph, hybrid on corpus_v1
- [x] Manual audit on 5 questions (`docs/evaluation_report.md`)
- [x] Summary table: mode × latency × overlap × evidence_count
- [x] Document failure modes (noisy RELATED_TO, shallow entity resolution)

### Week 5 — Report and demo (M7) ✓

- [x] Report draft (`docs/report_draft.md`)
- [x] Demo script (`docs/demo_script.md`)
- [x] PDF manifest (`resources/pdfs/SOURCES.txt`)
- [x] README links to PROGRESS and docs

---

## Blocked / waiting

| Item | Blocked on | Owner |
|------|------------|-------|
| | | |

---

## Notes / retro (optional)

- Week 1: Custom pipeline + LightRAG optional extra gives a fair comparison without MS GraphRAG integration overhead.
- Week 2: Expanded synthetic corpus keeps licensing simple while crossing the 15-article threshold with shared actors.
- Week 3: Heuristic extraction is fast and deterministic; Ollama improves answer wording but adds latency.
- Week 4: Graph/hybrid modes win on relation questions; vector-only misses cross-article entity links.
- Week 5: Demo should contrast one graph question vs one vector question on the same index.
