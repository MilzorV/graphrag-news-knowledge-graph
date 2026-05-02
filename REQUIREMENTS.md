# REQUIREMENTS.md

# GraphRAG Prototype for Discovering Connections Between Objects and Events in Press Articles

**Project title:** Opracowanie prototypu GraphRAG wspomagającego wyszukiwanie powiązań pomiędzy obiektami i zdarzeniami występującymi w artykułach prasowych  
**English title:** Development of the GraphRAG prototype supporting the search for connections between objects and events occurring in press articles  
**Supervisor:** Kamil Pietak  
**Project type:** project workshop / prototype / possible foundation for a master’s thesis  
**Version:** 0.1  
**Status:** initial requirements and scope definition

---

## 1. Project Summary

The goal of this project is to design and implement a prototype knowledge base for identifying semantic connections between objects, entities, and events described in press articles and other open-source texts.

The prototype should use the GraphRAG concept: Retrieval-Augmented Generation supported by a graph-based representation of knowledge. Unlike classical RAG, which usually retrieves semantically similar text chunks from a vector database, GraphRAG builds or uses a knowledge graph where information is organized as nodes and edges. Nodes represent entities, events, documents, places, dates, organizations, people, topics, or objects. Edges represent relationships between them.

The final system should allow a user to load a collection of press articles, automatically extract structured knowledge from them, build a searchable graph, and ask questions such as:

- “In which events did this person participate?”
- “Who was involved in this event?”
- “Where and when did this event happen?”
- “What connects person X with organization Y?”
- “Which articles mention the same event or related actors?”
- “Show the path of relations between two entities.”

At the end of the semester, the expected deliverables are a working prototype, a report explaining GraphRAG principles and applications, a short evaluation showing whether the approach works for the selected case, and a description of performance and limitations.

---

## 2. Motivation

Press articles often describe people, organizations, locations, objects, dates, and events in an unstructured way. Standard keyword search or vector-based semantic search can retrieve related fragments, but it does not explicitly model relationships such as who participated in what, where an event occurred, or how two entities are connected through multiple articles.

GraphRAG is useful for this problem because it can represent extracted information as a knowledge graph. This makes it possible to search not only for similar text, but also for structured connections between entities and events.

The project is exploratory: the main goal is not to build a production system or evaluate ChatGPT itself, but to understand how GraphRAG works, test one or more available technologies, and adapt the approach to a concrete use case based on press articles.

---

## 3. Main Objectives

The project should achieve the following objectives:

1. Explain how GraphRAG works and how it differs from classical vector-based RAG.
2. Review selected GraphRAG technologies and choose one main approach for the prototype.
3. Build a proof of concept that can process a small corpus of articles.
4. Extract entities, events, and relationships from input texts.
5. Store extracted knowledge in a graph-like representation.
6. Provide a simple search/query interface.
7. Support questions about relations between people, organizations, places, dates, events, and articles.
8. Use or test local LLMs where feasible, especially models that can run on a laptop.
9. Evaluate whether the prototype actually helps discover meaningful relationships.
10. Prepare a final report describing assumptions, architecture, implementation, tests, performance, limitations, and possible continuation as a master’s thesis.

---

## 4. Scope

### 4.1 In Scope

The following elements are part of the project scope:

- Research and explanation of GraphRAG principles.
- Comparison of at least a few GraphRAG-related tools or approaches.
- Selection of one main technology or implementation path for the prototype.
- Implementation of a prototype pipeline:
  - input text loading,
  - preprocessing,
  - chunking,
  - entity extraction,
  - relation/event extraction,
  - graph construction,
  - graph-based retrieval,
  - answer generation or search result presentation.
- Simple user interface for querying the indexed corpus.
- Support for press/news articles and other open-source texts.
- Basic evaluation of extraction quality, answer usefulness, latency, and limitations.
- Description of local LLM feasibility.
- Documentation and tutorial-style notes explaining how the chosen technology was tested and adapted.

### 4.2 Out of Scope

The following elements are not required for the initial prototype:

- Full production deployment.
- Large-scale indexing of millions of articles.
- Perfect information extraction accuracy.
- Full fact-checking system.
- Training a new LLM from scratch.
- Building a complete custom graph database engine.
- Full multilingual support unless time allows.
- Replacing professional intelligence-analysis or newsroom tools.
- Formal benchmark-grade evaluation on very large datasets.

---

## 5. Target Use Case

The main use case is exploratory search over press articles.

A user has a collection of news articles describing real-world events. The user wants to understand relations between people, organizations, places, objects, and events mentioned across those articles.

Example workflow:

1. User uploads or provides a folder of articles.
2. System reads the documents and splits them into smaller text units.
3. System extracts entities such as people, organizations, places, dates, and events.
4. System extracts relationships between those entities.
5. System builds a graph-based knowledge representation.
6. User asks a natural language question or searches for an entity.
7. System retrieves relevant graph nodes, relationships, source articles, and text fragments.
8. System returns an answer with supporting evidence and, ideally, a visual graph/path.

---

## 6. Core System Workflow

The prototype should follow this high-level pipeline:

```text
Input articles
    ↓
Document loading and preprocessing
    ↓
Chunking / text unit creation
    ↓
Entity, event, and relation extraction
    ↓
Entity normalization and deduplication
    ↓
Knowledge graph construction
    ↓
Graph + vector indexing
    ↓
Query processing
    ↓
Graph/vector retrieval
    ↓
Answer generation + evidence display
    ↓
Evaluation and reporting
```

---

## 7. Functional Requirements

### FR-01: Document Input

The system should allow loading a small corpus of press articles from local files.

Minimum supported formats:

- `.txt`
- `.md`
- `.json` or `.csv` with article title/body fields

Optional formats:

- `.html`
- `.pdf`
- URL-based article import

Each document should keep metadata such as:

- document ID,
- title,
- source,
- publication date if available,
- author if available,
- original file path or URL.

### FR-02: Text Preprocessing

The system should clean and normalize input text.

Minimum preprocessing:

- remove obvious boilerplate,
- normalize whitespace,
- preserve paragraph boundaries where useful,
- optionally detect language,
- split documents into chunks/text units.

Chunking should preserve source references so that extracted facts can be traced back to the original text.

### FR-03: Entity Extraction

The system should extract entities from articles.

Minimum entity types:

- `PERSON`
- `ORGANIZATION`
- `LOCATION`
- `EVENT`
- `DATE/TIME`
- `OBJECT` or `TOPIC`
- `DOCUMENT`

Candidate approaches:

- LLM-based extraction through prompts,
- GLiNER for open-type named entity recognition,
- spaCy or Stanza for baseline NER,
- REBEL or similar models for relation triples,
- custom prompt templates for event-centric extraction.

Each extracted entity should store:

- canonical name,
- entity type,
- aliases or mentions,
- source document IDs,
- source text spans or snippets,
- confidence score if available.

### FR-04: Event Extraction

The system should identify events mentioned in articles.

Each event should ideally include:

- event name or generated label,
- event type/category if possible,
- participants,
- location,
- date/time,
- related organizations,
- related objects/topics,
- source article and evidence snippet.

The prototype does not need perfect event extraction, but it should demonstrate at least a basic event representation.

### FR-05: Relation Extraction

The system should extract relationships between entities and events.

Example relation types:

- `PARTICIPATED_IN`
- `INVOLVED_IN`
- `LOCATED_IN`
- `OCCURRED_AT`
- `OCCURRED_ON`
- `MEMBER_OF`
- `WORKS_FOR`
- `MET_WITH`
- `MENTIONED_IN`
- `CAUSES` / `CAUSED_BY`
- `RELATED_TO`
- `SUPPORTED_BY_EVIDENCE`

Each relation should store:

- source node,
- target node,
- relation type,
- textual description,
- source document,
- evidence snippet,
- confidence score if available.

### FR-06: Entity Normalization and Deduplication

The system should attempt to merge duplicate mentions of the same real-world entity.

Examples:

- “Donald Trump”, “Trump”, and “President Trump” should ideally map to one entity.
- “USA”, “United States”, and “United States of America” should ideally map to one entity.

Minimum solution:

- exact normalized string matching,
- case-insensitive matching,
- optional alias rules.

Optional advanced solution:

- embedding similarity,
- LLM-assisted entity resolution,
- Wikidata/EventKG linking.

### FR-07: Graph Construction

The system should build a graph representation from extracted entities, events, documents, and relationships.

Required node categories:

- Article/document nodes,
- Entity nodes,
- Event nodes,
- Optional topic/community nodes.

Required edge categories:

- Mention edges from documents to entities/events,
- Semantic relation edges between entities/events,
- Evidence/provenance edges or attributes.

Possible graph storage options:

- Neo4j,
- NetworkX for a lightweight POC,
- SQLite with edge/node tables,
- LightRAG internal graph representation,
- Microsoft GraphRAG output tables,
- other property graph or RDF storage.

### FR-08: Search and Query Interface

The system should expose a simple interface for querying the corpus.

Minimum interface options:

- CLI, Streamlit, simple FastAPI endpoint, or minimal web UI.

The interface should support:

- natural language questions,
- entity search,
- viewing related entities/events,
- retrieving source articles and snippets,
- displaying relation paths where possible.

Example queries:

- “What events involve [person]?”
- “Where did [event] happen?”
- “Who participated in [event]?”
- “What connects [person A] and [organization B]?”
- “Which articles mention [entity]?”
- “Show all events connected to [location].”

### FR-09: Graph-Based Retrieval

The system should retrieve information using graph structure, not only vector similarity.

Minimum retrieval modes:

- entity-based local search,
- relationship/path search,
- source document lookup,
- hybrid graph + text retrieval.

Optional retrieval modes:

- global search over graph communities,
- community summaries,
- path-based retrieval,
- query decomposition,
- query expansion using neighboring graph nodes.

### FR-10: Answer Generation

The system may use an LLM to produce natural language answers based on retrieved graph data and source snippets.

Generated answers should include:

- direct answer,
- relevant entities/events,
- relationship explanation,
- evidence snippets or source references,
- uncertainty when evidence is weak.

The system should avoid unsupported claims where possible. Answers should be grounded in indexed source documents.

### FR-11: Local LLM Support

The project should investigate whether local LLMs can be used for extraction, retrieval support, or answer generation.

Candidate local model runners:

- Ollama,
- LM Studio,
- llama.cpp,
- vLLM if hardware permits.

Candidate local models:

- Llama 3.x / Llama 3.1 8B-class models,
- Mistral 7B-class models,
- Qwen 2.5 / Qwen 3 small or medium models,
- Phi-class small models,
- Gemma-class small models.

Candidate embedding models:

- sentence-transformers,
- BGE small/base,
- E5 small/base,
- nomic-embed-text,
- multilingual models if Polish articles are used.

The report should describe which models fit on a laptop and whether they are usable for the prototype.

### FR-12: Baseline Comparison

The project should compare GraphRAG against at least one simpler baseline.

Possible baselines:

- keyword search,
- vector-only RAG,
- manual graph search,
- direct LLM over a small context.

The goal is to show whether graph structure helps answer relationship-oriented questions.

### FR-13: Evaluation

The prototype should include a small evaluation.

Minimum evaluation dimensions:

- answer correctness for manually prepared questions,
- whether evidence snippets support the answer,
- quality of extracted entities,
- quality of extracted relations,
- usefulness of graph paths,
- latency of indexing and querying,
- memory/storage requirements,
- comparison with vector-only retrieval or keyword search.

Suggested manual test set:

- 10–30 articles,
- 10–20 questions,
- expected entities/events/relations for a subset of articles,
- manual notes about correct and incorrect outputs.

Optional metrics:

- precision of extracted entities,
- precision of extracted relations,
- retrieval hit rate,
- answer faithfulness,
- response latency,
- indexing time per document,
- graph size: number of nodes, edges, communities.

---

## 8. Non-Functional Requirements

### NFR-01: Simplicity

The prototype should remain simple enough to implement and explain within one semester.

### NFR-02: Reproducibility

The repository should include clear setup and run instructions.

Required documentation:

- installation instructions,
- environment variables,
- data folder structure,
- indexing command,
- query command,
- example input and output.

### NFR-03: Laptop Feasibility

At least one version of the prototype should run on a normal laptop for a small corpus.

A cloud/API-based option may be used for comparison, but local feasibility should be discussed.

### NFR-04: Transparency

The system should preserve provenance:

- where each entity came from,
- where each relation came from,
- which document/snippet supports an answer.

### NFR-05: Extensibility

The design should allow later replacement of components:

- different LLM,
- different embedding model,
- different graph database,
- different extraction method,
- larger dataset.

### NFR-06: Performance Awareness

The prototype does not need to be highly optimized, but the report should describe:

- indexing time,
- query time,
- graph size,
- model/resource usage,
- bottlenecks.

### NFR-07: Data Ethics and Licensing

The project should use open datasets or articles with appropriate usage rights.

The report should mention:

- source of articles,
- licensing constraints,
- limitations of scraping,
- privacy considerations if using non-public texts.

---

## 9. Candidate Technologies

### 9.1 Microsoft GraphRAG

Useful for understanding the canonical GraphRAG workflow:

- text chunking,
- entity and relationship extraction,
- graph construction,
- community detection,
- community summaries,
- local/global search.

Good for the report because it has clear documentation and a research paper.

Repository: https://github.com/microsoft/graphrag

### 9.2 LightRAG

Promising candidate for the prototype because it is designed as a simpler and faster graph-enhanced RAG system.

Important aspects:

- graph-enhanced text indexing,
- entity and relationship extraction,
- dual-level retrieval,
- incremental updates,
- practical open-source implementation.

Repository: https://github.com/HKUDS/LightRAG

### 9.3 EdgeQuake

Technology to inspect as part of the “how does this work?” research/tutorial phase.

Repository: https://github.com/raphaelmansuy/edgequake  
Docs/comparison: https://edgequake.com/docs/comparisons/

### 9.4 Neo4j

Useful graph database option for storing and querying entities/events/relations.

Possible use:

- store graph nodes and edges,
- query with Cypher,
- visualize graph paths,
- integrate with LLM/GraphRAG pipelines.

GraphRAG overview: https://neo4j.com/blog/genai/what-is-graphrag/

### 9.5 Lightweight POC Stack

A minimal implementation could use:

- Python,
- FastAPI or Streamlit,
- NetworkX for graph representation,
- SQLite or JSON for persistence,
- Chroma/Qdrant/FAISS for vector search,
- Ollama for local LLM inference,
- sentence-transformers for embeddings.

This option may be easier to fully understand and explain in the report.

---

## 10. Suggested Technical Architecture

### 10.1 Minimal Prototype Architecture

```text
frontend/
  Streamlit or simple React UI

backend/
  FastAPI or Python service

pipeline/
  loaders.py
  preprocessing.py
  extraction.py
  graph_builder.py
  retrieval.py
  generation.py
  evaluation.py

storage/
  graph.json or Neo4j
  vector index
  source documents

models/
  local LLM via Ollama or API-based fallback
  local embedding model
```

### 10.2 Recommended First Implementation Path

For fastest progress:

1. Start with a small local corpus of 10–30 articles.
2. Use LightRAG or Microsoft GraphRAG tutorial as the first POC.
3. Run indexing on the sample corpus.
4. Inspect the extracted graph/entities/relations.
5. Build a simple query interface.
6. Prepare 10–20 manual test questions.
7. Compare with vector-only retrieval.
8. Write the report around what worked, what failed, and why.

---

## 11. Data Sources

Potential open data sources:

### 11.1 GDELT

Useful for global news/event data and downloadable datasets.

- GDELT Project: https://www.gdeltproject.org/
- GDELT DOC API: https://api.gdeltproject.org/api/v2/doc/doc
- GDELT data/download page: https://www.gdeltproject.org/data.html

### 11.2 MIND Dataset

Microsoft News Dataset containing English news articles.

- Dataset: https://msnews.github.io/

### 11.3 Wikipedia Current Events

Useful for event-oriented short news-like summaries.

- https://en.wikipedia.org/wiki/Portal:Current_events

### 11.4 EventKG

Useful as background/reference for event-centric knowledge graphs.

- http://eventkg.l3s.uni-hannover.de/

### 11.5 Small Manual Corpus

For the prototype, a manually collected corpus may be better than a huge dataset.

Recommended size for first evaluation:

- 10–30 articles for initial POC,
- 50–100 articles for final demo if performance allows.

---

## 12. Evaluation Plan

### 12.1 Qualitative Evaluation

Prepare a small set of questions and manually verify the answers.

Example questions:

1. Which people are connected to event X?
2. Which organizations are mentioned together with person Y?
3. Where did event Z happen?
4. What articles mention both entity A and entity B?
5. What path connects person A to organization B?
6. Which events happened in location L?
7. Which entities are central in the graph?
8. Does the answer cite the correct article/snippet?

### 12.2 Quantitative / Semi-Quantitative Evaluation

Measure:

- number of processed articles,
- number of chunks,
- number of extracted entities,
- number of extracted events,
- number of relations,
- indexing time,
- average query time,
- average answer length,
- manual correctness score,
- percentage of answers with valid evidence.

### 12.3 Baseline Evaluation

Compare GraphRAG with:

- keyword search,
- vector-only RAG,
- possibly direct LLM answering with the same snippets.

For relationship queries, GraphRAG should be expected to perform better when the answer depends on multi-hop relations or structured connections.

### 12.4 Example Evaluation Table

| Query | Expected answer | GraphRAG answer | Vector RAG answer | Evidence correct? | Notes |
|---|---|---|---|---|---|
| Who participated in event X? | A, B, C | A, B | A | Partially | Missing C |
| What connects person A and org B? | A works for B | A linked to B through event Y | irrelevant snippet | Yes | Graph path useful |

---

## 13. Acceptance Criteria

The project can be considered successful if:

1. The report explains GraphRAG clearly and compares it with classical RAG.
2. At least one GraphRAG technology is tested through a tutorial/POC.
3. The prototype can load a small article corpus.
4. The prototype extracts entities and relationships into a graph-like structure.
5. The user can ask relationship-oriented questions through a simple interface.
6. The system returns source snippets or article references as evidence.
7. At least 10 test questions are evaluated manually.
8. The report discusses performance, limitations, and whether GraphRAG worked for the selected case.
9. The project includes notes about local LLM feasibility.
10. The repository contains clear instructions for reproducing the demo.

---

## 14. Final Report Scope

The final report should include:

1. Introduction and motivation.
2. Explanation of RAG and GraphRAG.
3. Why graph representation is useful for press articles.
4. Review of selected technologies:
   - Microsoft GraphRAG,
   - LightRAG,
   - EdgeQuake,
   - Neo4j or other graph tools,
   - optional extraction models such as GLiNER or REBEL.
5. Chosen architecture.
6. Data sources and preprocessing.
7. Entity/event/relation extraction approach.
8. Graph schema.
9. Search/query interface.
10. Local LLM experiments.
11. Evaluation methodology.
12. Results.
13. Performance observations.
14. Limitations.
15. Future work and possible master’s thesis direction.

---

## 15. Possible Graph Schema

### 15.1 Node Types

```text
Article
Person
Organization
Location
Event
DateTime
Topic
Object
```

### 15.2 Edge Types

```text
MENTIONS
PARTICIPATED_IN
INVOLVED_IN
LOCATED_IN
OCCURRED_AT
OCCURRED_ON
AFFILIATED_WITH
RELATED_TO
SUPPORTED_BY
SAME_AS
```

### 15.3 Example Graph Fragment

```text
(Article: "Article 001") -[:MENTIONS]-> (Person: "John Smith")
(Article: "Article 001") -[:MENTIONS]-> (Event: "Press conference")
(Person: "John Smith") -[:PARTICIPATED_IN]-> (Event: "Press conference")
(Event: "Press conference") -[:OCCURRED_AT]-> (Location: "Warsaw")
(Event: "Press conference") -[:OCCURRED_ON]-> (DateTime: "2025-04-12")
```

---

## 16. Suggested Repository Structure

```text
graphrag-news-prototype/
  README.md
  REQUIREMENTS.md
  pyproject.toml or requirements.txt
  .env.example

  data/
    raw/
    processed/
    sample_articles/

  notebooks/
    01_technology_review.ipynb
    02_extraction_experiments.ipynb
    03_evaluation.ipynb

  src/
    loaders/
    preprocessing/
    extraction/
    graph/
    retrieval/
    generation/
    evaluation/
    ui/

  configs/
    models.yaml
    graph_schema.yaml
    prompts/

  outputs/
    graphs/
    indexes/
    evaluation/

  docs/
    report_notes.md
    tutorial_notes.md
    architecture.md
```

---

## 17. Milestones

### Milestone 1: Literature and Tool Review

- Read basic GraphRAG materials.
- Understand RAG vs GraphRAG.
- Inspect Microsoft GraphRAG, LightRAG, EdgeQuake, Neo4j examples.
- Decide which technology to use for the first POC.

### Milestone 2: Tutorial POC

- Run one existing GraphRAG tutorial.
- Index a small sample dataset.
- Query the data.
- Document setup problems and observations.

### Milestone 3: Article Corpus Preparation

- Select or collect a small set of articles.
- Convert them to a consistent format.
- Define expected entity/event types.
- Prepare test questions.

### Milestone 4: Prototype Implementation

- Implement loading and preprocessing.
- Implement or configure extraction.
- Build graph representation.
- Add query/retrieval logic.
- Add simple UI.

### Milestone 5: Local LLM Experiments

- Test at least one local model for extraction or answering.
- Compare with API/cloud model if available.
- Document quality and performance.

### Milestone 6: Evaluation

- Run test questions.
- Compare with baseline.
- Measure indexing/query time.
- Analyze errors.

### Milestone 7: Final Report and Demo

- Prepare final report.
- Prepare demo scenario.
- Summarize findings and future work.

---

## 18. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---:|---|
| Graph extraction is noisy | High | Keep evidence snippets, manually inspect subset, simplify relation schema |
| Local models are too weak or slow | Medium/High | Use smaller corpus, use local embeddings, allow API fallback for comparison |
| Existing GraphRAG tools are complex | Medium | Start with tutorial first, then reduce scope to minimal custom POC |
| Article scraping/licensing issues | Medium | Use open datasets or manually provided sample texts |
| Evaluation is subjective | Medium | Prepare fixed test questions and expected answers |
| Too much focus on technology comparison | Medium | Choose one main implementation path early |
| Graph becomes too dense/noisy | Medium | Deduplicate entities, filter low-confidence relations, use relation whitelist |
| Time constraints | High | Prioritize small working prototype over large dataset |

---

## 19. Open Questions

The team should decide:

1. Which implementation will be the main prototype: LightRAG, Microsoft GraphRAG, EdgeQuake, or custom lightweight pipeline?
2. Should the graph be stored in Neo4j or in a simpler local format for the first version?
3. Which language should the first corpus use: English, Polish, or both?
4. Which local LLM should be tested first?
5. How many articles are realistic for the final demo?
6. Should the UI focus on natural language answers, graph visualization, or both?
7. How detailed should event extraction be?
8. Should the final report emphasize technology comparison, prototype architecture, or evaluation?

---

## 20. Future Work / Master’s Thesis Direction

This project can become the beginning of a master’s thesis if extended in one or more directions:

- systematic comparison of GraphRAG technologies,
- evaluation of local LLMs for graph construction,
- event-centric GraphRAG for news analysis,
- multilingual GraphRAG for Polish and English press articles,
- improved entity resolution and event coreference,
- graph-based explanation and visualization of news narratives,
- hybrid vector + graph retrieval benchmark,
- temporal reasoning over events,
- integration with external knowledge graphs such as Wikidata or EventKG.

---

## 21. Useful Starting Resources

### GraphRAG and RAG

- Neo4j: What is GraphRAG?  
  https://neo4j.com/blog/genai/what-is-graphrag/

- Microsoft GraphRAG repository  
  https://github.com/microsoft/graphrag

- Microsoft GraphRAG paper: From Local to Global: A GraphRAG Approach to Query-Focused Summarization  
  https://arxiv.org/abs/2404.16130

- GraphRAG Survey  
  https://arxiv.org/abs/2408.08921

- Retrieval-Augmented Generation with Graphs survey  
  https://arxiv.org/abs/2501.00309

### Tools to Test

- LightRAG  
  https://github.com/HKUDS/LightRAG

- EdgeQuake  
  https://github.com/raphaelmansuy/edgequake

- EdgeQuake comparisons  
  https://edgequake.com/docs/comparisons/

### Information Extraction

- GLiNER: open-type named entity recognition  
  https://github.com/urchade/GLiNER

- REBEL: relation extraction by end-to-end language generation  
  https://github.com/Babelscape/rebel

### Evaluation

- RAGAS  
  https://github.com/explodinggradients/ragas

### News/Event Data

- GDELT  
  https://www.gdeltproject.org/

- Microsoft News Dataset / MIND  
  https://msnews.github.io/

- EventKG  
  http://eventkg.l3s.uni-hannover.de/

---

## 22. Definition of Done

A minimal “done” version of the project means:

- A small corpus of articles is processed end-to-end.
- Extracted entities and relations are stored as a graph.
- The system supports at least a few meaningful relationship queries.
- The answer includes evidence from source articles.
- A simple UI or CLI demonstrates the workflow.
- Evaluation results are documented.
- The final report explains GraphRAG, the selected technology, the prototype, and its limitations.

