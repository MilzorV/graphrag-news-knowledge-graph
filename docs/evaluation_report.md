# Evaluation Report (M6)

Evaluation on **corpus_v1** (18 interconnected energy/climate articles) and **questions_v1** (18 investigator-style questions).

Index: `outputs/corpus_v1_index/` (heuristic extraction).  
Artifact: `outputs/corpus_v1_index/evaluation.csv`

## Summary by retrieval mode

| Mode | Questions | Avg expected overlap | Avg evidence count | Avg latency (ms) |
|------|-----------|---------------------|-------------------|------------------|
| vector | 18 | **0.520** | 5.0 | 0 |
| keyword | 18 | 0.485 | 5.0 | 0 |
| graph | 18 | 0.400 | 5.0 | 14 |
| hybrid | 18 | 0.400 | 5.0 | 16 |

**Metric:** `expected_overlap` = fraction of non-stopword tokens from the reference answer that appear in the generated answer (see `evaluation.py`). This is a coarse proxy, not semantic equivalence.

## Interpretation

1. **Vector and keyword modes score highest on overlap** because template answers often echo top TF-IDF/lexical hits, which align with article titles and lead sentences.
2. **Graph and hybrid modes trade overlap for structure** — they surface neighborhood evidence (entities, relations) that template generation does not always verbalize, lowering the token overlap score while still retrieving relevant sources.
3. **Latency:** graph/hybrid add ~14–16 ms per question on this corpus (in-memory NetworkX walk); still negligible vs LLM generation.

## Manual audit (5 questions)

### q1 — What connects Maria Nowak with GreenGrid Europe?

| Mode | Top source | Faithful? | Notes |
|------|------------|-----------|-------|
| vector | GreenGrid milestones article | Partial | Mentions both actors indirectly |
| graph | GreenGrid software rollout | Partial | Correct org, weak narrative link to Maria |
| hybrid | Same as graph | Partial | Evidence exists across articles; answer template generic |

**Verdict:** Retrieval finds relevant articles; answer generation is the bottleneck.

### q3 — Where did the Vistula Flood Response happen?

| Mode | Top source | Faithful? | Notes |
|------|------------|-----------|-------|
| keyword/vector | Krakow flood article | **Yes** | Clear location in title and body |
| graph | Flood resilience plan | Partial | Krakow correct, different article angle |

**Verdict:** Factual “where” questions favor lexical/vector modes.

### q8 — How is NordicGrid connected to Vilnius?

| Mode | Top source | Faithful? | Notes |
|------|------------|-----------|-------|
| vector/graph/hybrid | Vilnius talks / resilience plan | **Yes** | Operations center and talks both relevant |

**Verdict:** Graph mode matches vector when entity names are distinctive.

### q13 — Who is Ewa Lewandowska?

| Mode | Top source | Faithful? | Notes |
|------|------------|-----------|-------|
| graph/hybrid | Warsaw energy summit | **No** | Wrong context; port director not in top graph hit |
| vector | Gdansk procurement review | **Yes** | Correct role and review |

**Verdict:** Failure mode — graph entity linking confused similar government-energy context.

### q18 — European Climate Directorate review scope

| Mode | Top source | Faithful? | Notes |
|------|------------|-----------|-------|
| graph/hybrid | Phase one deadline article | **Yes** | Directorate tracking mentioned; multi-topic coverage |

**Verdict:** Graph helps when question spans multiple linked events.

## Failure modes

1. **Noisy `RELATED_TO` edges** (411 of 736 edges) from heuristic co-occurrence inflate graph neighborhoods.
2. **Shallow entity resolution** — “Warsaw” as location vs Warsaw-hosted events conflate evidence.
3. **Template answers** — `generation.py` patterns do not synthesize multi-hop paths; hurts graph/hybrid overlap scores.
4. **No explicit path queries** — “show path between A and B” not implemented.

## Does GraphRAG help for this case?

**Yes, selectively.** For cross-article relationship questions (q8, q18), graph retrieval surfaces connected articles that a single vector hit might miss. For simple location/fact lookup (q3), vector/keyword suffice. **Hybrid** should combine both but current weighting still inherits template-answer limits.

**Recommendation for demo:** Show q8 or q18 with `graph` vs `vector` side by side; use q3 to show when classical retrieval wins.

## Reproduction

```bash
uv run news-graphrag ingest --input data/corpus_v1/corpus.json \
  --output outputs/corpus_v1_index --extractor heuristic
uv run news-graphrag eval --index outputs/corpus_v1_index \
  --questions data/questions_v1.json
```
