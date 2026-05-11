# Research Notes For The Prototype

These notes summarize why the MVP is shaped as a comparison testbench rather than only a single GraphRAG package wrapper.

## GraphRAG Concepts

- Microsoft GraphRAG motivates graph indexing for questions that are hard for flat vector RAG, especially corpus-level and relationship-heavy questions.
- Its main distinction is building an entity/relationship graph first, then using local search for entity-specific questions and global/community search for broader dataset questions.
- For this project's news use case, local entity/event search is the MVP priority because the example questions ask who, where, when, and what connects two actors.

## LightRAG

- LightRAG is a good first external stack because it focuses on simple, fast graph-enhanced retrieval with low-level and high-level retrieval paths.
- The MVP keeps LightRAG optional so the project remains runnable before local models are pulled and before heavier dependencies are installed.
- The built-in custom graph/vector/keyword modes provide a controlled baseline for explaining what graph retrieval contributes.

## Information Extraction

- GLiNER is relevant because it supports flexible entity labels without training a new task-specific NER model.
- REBEL is relevant for relation extraction, but adding it in v1 would increase model/runtime complexity.
- The MVP therefore starts with deterministic heuristic extraction plus optional Ollama JSON extraction. This gives a working graph now and leaves GLiNER/REBEL as clear next experiments.

## Event-Centric Modeling

- EventKG and WikiEvents support the idea that news graphs should treat events as first-class nodes, not only people and organizations.
- The MVP creates event nodes from article titles and event-like phrases, then links people, organizations, locations, and dates to those events with evidence snippets.

## Evaluation

- RAGAS is useful background for systematic RAG evaluation, but this semester MVP starts with a fixed manual question set and a CSV comparison table.
- The evaluation output is designed to support later manual scoring: expected answer, mode, generated answer, top source, evidence count, and latency.
