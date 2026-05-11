# Project progress

Use Markdown task lists: `- [ ]` not done, `- [x]` done. Update this file as you finish items.

**References:** [REQUIREMENTS.md](./REQUIREMENTS.md) (especially §3 objectives, §17 milestones, §19 open questions).

---

## Done so far

- [x] Requirements and scope documented (`REQUIREMENTS.md`)
- [x] Reference PDFs collected under `resources/pdfs/` (papers + doc snapshots)
- [x] `.gitignore` includes `.DS_Store`
- [x] MVP scaffold added: Python package, CLI, Streamlit UI, sample corpus, evaluation questions
- [x] Deterministic baseline pipeline works: ingest → chunk → heuristic extract → graph/vector indexes → query
- [x] Optional Ollama and LightRAG integration points added

---

## Ongoing tracker (maps to milestones)

### Decisions (§19 open questions)

- [x] Main prototype stack chosen (LightRAG harness + lightweight local baselines)
- [x] Graph storage choice for v1 (local JSON + NetworkX; LightRAG working dir optional)
- [x] Corpus language(s): English for v1 bundled demo
- [x] First local LLM to test (Ollama `llama3.1:8b`; heuristic fallback)
- [x] Target article count for demo (8 bundled now; 10–30 recommended for final)
- [x] UI emphasis: NL answers plus evidence and graph fragment
- [x] Event extraction depth (light event nodes from titles/event-like phrases)
- [ ] Report emphasis: comparison vs architecture vs evaluation

### Milestone coverage

- [ ] **M1** Literature and tool review complete
- [x] **M2** Tutorial POC run end-to-end on sample data
- [x] **M3** Article corpus prepared + test question set
- [x] **M4** Prototype: ingest → extract → graph → query (+ simple UI)
- [ ] **M5** Local LLM experiment documented (vs cloud if applicable)
- [x] **M6** Evaluation run (baseline + qualitative/quantitative notes)
- [ ] **M7** Final report draft + demo scenario + findings summary

### Core objectives (§3) — check when evidenced in repo or report

- [ ] GraphRAG vs classical RAG explained (report or docs)
- [ ] At least two approaches/tools compared; one main path selected
- [x] POC processes a small article corpus
- [x] Entities / events / relations extracted (as designed)
- [x] Knowledge stored in a graph-like form
- [x] Simple search or query interface works
- [x] Relation-style questions supported (within chosen limits)
- [ ] Local LLM feasibility tested where applicable
- [x] Evaluation shows whether the approach helps for your case
- [ ] Final report covers assumptions, architecture, tests, limits, continuation

---

## Next five weeks (week-by-week)

Adjust dates in headings to match your calendar when the sprint starts.

### Week 1 — Orientation and choice

- [ ] Skim official GraphRAG docs + one survey paper; note local vs global search roles
- [ ] Install/run **one** tutorial stack (e.g. Microsoft GraphRAG or LightRAG) on a toy corpus
- [ ] Short notes: setup issues, config knobs, what “index” vs “query” produced
- [ ] Decide **primary** stack for the semester prototype (document in README or ADR)
- [ ] Resolve at least two §19 items (corpus language, target article count)

### Week 2 — Tutorial depth and corpus

- [ ] Finish **M2**: index + query demo documented (screenshots or log excerpts OK)
- [ ] Select dataset(s): e.g. MIND subset, manual articles, or other licensed source
- [ ] Normalize input format (folders, metadata, IDs)
- [ ] Draft **entity / event / relation** types you will actually extract (keep schema small)
- [ ] Write **10–20** investigator-style test questions for later evaluation
- [ ] Start **M3** checklist in issue list or this file

### Week 3 — Pipeline on real corpus

- [ ] Ingest pipeline for your corpus (chunking, dedup strategy)
- [ ] Extraction configured (prompts or NER/RE stack); first full index on small batch
- [ ] Inspect graph quality (sample nodes/edges, noise, deduplication)
- [ ] Graph build/export matches storage choice (tool default or Neo4j, etc.)
- [ ] One **working** query path: from question to answer with source pointers

### Week 4 — UI, retrieval polish, local model

- [ ] Minimal UI or CLI: load corpus, ask question, show answer + sources
- [ ] Optional: graph fragment or path visualization (even static export)
- [ ] **M5**: run one local model (Ollama or similar) on extraction or QA; record latency/quality
- [ ] Compare to API/cloud on a **fixed** subset of questions (if applicable)
- [ ] Fix worst failure modes found in Week 3 (schema, prompts, or chunk size)

### Week 5 — Evaluation, report, demo

- [ ] Run full test question set; log answers and retrieval context
- [ ] **M6**: baseline (e.g. vector-only) vs GraphRAG on same questions — short table + narrative
- [ ] Manual audit on a subset (faithfulness to articles / graph)
- [ ] **M7**: final report sections drafted (intro, related work, architecture, eval, limits)
- [ ] Demo script rehearsed (5–10 minutes: corpus → question → answer → graph peek)
- [ ] Repo cleaned: how to reproduce index + query (`README` or `docs/`)

---

## Blocked / waiting

*(Add rows when something depends on supervisor, data access, or hardware.)*

| Item | Blocked on | Owner |
|------|------------|-------|
| | | |

---

## Notes / retro (optional)

*Capture one lesson per week so the final report writes itself.*

- Week 1:
- Week 2:
- Week 3:
- Week 4:
- Week 5:
