from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from news_graphrag_demo.evaluation import run_evaluation, save_evaluation
from news_graphrag_demo.graph_store import graph_summary
from news_graphrag_demo.lightrag_adapter import is_lightrag_installed, query_lightrag
from news_graphrag_demo.ollama_client import DEFAULT_CHAT_MODEL, DEFAULT_EMBED_MODEL
from news_graphrag_demo.paths import DEFAULT_LIGHTRAG_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_QUESTIONS_PATH, DEFAULT_SAMPLE_DIR
from news_graphrag_demo.pipeline import build_index
from news_graphrag_demo.plotting import make_graph_figure
from news_graphrag_demo.retrieval import RetrievalEngine
from news_graphrag_demo.storage import INDEX_FILE, load_graph_index


st.set_page_config(page_title="News GraphRAG Testbench", layout="wide")


def main() -> None:
    st.title("News GraphRAG Testbench")
    st.caption("Compare keyword, vector, graph, hybrid, and optional LightRAG retrieval over a small news corpus.")

    with st.sidebar:
        st.header("Index")
        input_path = Path(st.text_input("Article folder/file", str(DEFAULT_SAMPLE_DIR)))
        output_dir = Path(st.text_input("Index output", str(DEFAULT_OUTPUT_DIR)))
        extractor = st.selectbox("Extractor", ["auto", "heuristic", "ollama"], index=0)
        ollama_model = st.text_input("Ollama chat model", DEFAULT_CHAT_MODEL)
        if st.button("Build / refresh index", use_container_width=True):
            with st.spinner("Building graph and vector indexes..."):
                info = build_index(
                    input_path=input_path,
                    output_dir=output_dir,
                    extractor_mode=extractor,
                    ollama_model=ollama_model,
                )
            st.success(f"Indexed {info['summary']['articles']} articles and {info['summary']['edges']} edges.")

    if not (output_dir / INDEX_FILE).exists():
        st.info("Build the sample index from the sidebar to start querying.")
        return

    index = load_graph_index(output_dir)
    engine = RetrievalEngine.from_output_dir(output_dir)
    summary = graph_summary(index)

    metric_cols = st.columns(4)
    metric_cols[0].metric("Articles", summary["articles"])
    metric_cols[1].metric("Chunks", summary["chunks"])
    metric_cols[2].metric("Nodes", summary["nodes"])
    metric_cols[3].metric("Edges", summary["edges"])

    query_tab, graph_tab, docs_tab, eval_tab = st.tabs(["Query", "Graph", "Documents", "Evaluation"])

    with query_tab:
        col_a, col_b = st.columns([0.72, 0.28])
        with col_a:
            question = st.text_input("Question", "What connects Maria Nowak with GreenGrid Europe?")
        with col_b:
            mode = st.selectbox("Retrieval mode", ["hybrid", "graph", "vector", "keyword", "lightrag"], index=0)
        use_ollama = st.checkbox("Use Ollama for final wording", value=False)
        top_k = st.slider("Evidence count", 1, 10, 5)
        if st.button("Ask", type="primary"):
            if mode == "lightrag":
                st.subheader("LightRAG Answer")
                if not is_lightrag_installed():
                    st.warning("LightRAG is optional. Install it with `uv sync --extra lightrag --extra dev`, then build it with `uv run news-graphrag lightrag-index`.")
                else:
                    with st.spinner("Querying LightRAG..."):
                        answer = query_lightrag(
                            question,
                            working_dir=DEFAULT_LIGHTRAG_DIR,
                            llm_model=ollama_model,
                            embed_model=DEFAULT_EMBED_MODEL,
                        )
                    st.write(answer)
                return
            result = engine.query(question, mode=mode, top_k=top_k, use_ollama=use_ollama, ollama_model=ollama_model)
            st.subheader("Answer")
            st.write(result.answer)

            st.subheader("Evidence")
            st.dataframe(pd.DataFrame([item.to_dict() for item in result.evidence]), use_container_width=True)

            st.subheader("Retrieved graph fragment")
            st.plotly_chart(make_graph_figure(result.graph_nodes, result.graph_edges), use_container_width=True)

    with graph_tab:
        st.subheader("Graph Counts")
        count_a, count_b = st.columns(2)
        count_a.dataframe(pd.DataFrame(summary["node_counts"].items(), columns=["node_type", "count"]), use_container_width=True)
        count_b.dataframe(pd.DataFrame(summary["edge_counts"].items(), columns=["edge_type", "count"]), use_container_width=True)

    with docs_tab:
        rows = [
            {
                "id": article.id,
                "title": article.title,
                "source": article.source,
                "published_at": article.published_at,
                "characters": len(article.text),
            }
            for article in index.articles
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

    with eval_tab:
        st.write("Run the fixed sample questions across retrieval modes. The CSV is written back into the index directory.")
        if st.button("Run evaluation"):
            with st.spinner("Running evaluation..."):
                df = run_evaluation(engine, questions_path=DEFAULT_QUESTIONS_PATH, use_ollama=False)
                path = save_evaluation(df, output_dir)
            st.success(f"Wrote {path}")
            st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main()
