from __future__ import annotations

import importlib.util
import json
import platform
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .evaluation import run_evaluation, save_evaluation
from .graph_store import graph_summary
from .lightrag_adapter import build_lightrag_index, is_lightrag_installed, query_lightrag
from .loaders import load_articles
from .ollama_client import DEFAULT_CHAT_MODEL, DEFAULT_EMBED_MODEL, get_status
from .paths import DEFAULT_LIGHTRAG_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_QUESTIONS_PATH, DEFAULT_SAMPLE_DIR
from .pipeline import build_index
from .retrieval import RetrievalEngine
from .storage import load_graph_index


app = typer.Typer(help="Prototype GraphRAG testbench for news articles.")
console = Console()


@app.command()
def doctor() -> None:
    """Check local runtime, optional models, and optional LightRAG availability."""
    table = Table(title=f"News GraphRAG Demo {__version__}")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Details")

    table.add_row("Python", "ok", platform.python_version())
    for package in ["streamlit", "networkx", "sklearn", "pandas", "plotly", "typer"]:
        table.add_row(f"Python package: {package}", "ok" if importlib.util.find_spec(package) else "missing", "")

    status = get_status()
    if status.available:
        table.add_row("Ollama server", "ok", f"{len(status.models)} model(s) installed")
        table.add_row(DEFAULT_CHAT_MODEL, "ok" if DEFAULT_CHAT_MODEL in status.models else "missing", "ollama pull llama3.1:8b")
        table.add_row(DEFAULT_EMBED_MODEL, "ok" if DEFAULT_EMBED_MODEL in status.models else "missing", "ollama pull nomic-embed-text")
    else:
        table.add_row("Ollama server", "missing", status.error or "Start Ollama, then rerun doctor.")

    table.add_row("LightRAG package", "ok" if is_lightrag_installed() else "optional", "uv sync --extra lightrag --extra dev")
    console.print(table)


@app.command()
def ingest(
    input_path: Annotated[Path, typer.Option("--input", "-i", help="Article file or folder.")] = DEFAULT_SAMPLE_DIR,
    output_dir: Annotated[Path, typer.Option("--output", "-o", help="Index output directory.")] = DEFAULT_OUTPUT_DIR,
    extractor: Annotated[str, typer.Option("--extractor", help="auto, heuristic, or ollama.")] = "auto",
    ollama_model: Annotated[str, typer.Option("--model", help="Ollama chat model for extraction.")] = DEFAULT_CHAT_MODEL,
    max_chunk_chars: Annotated[int, typer.Option("--max-chunk-chars")] = 1200,
) -> None:
    """Build graph, keyword, and vector indexes."""
    info = build_index(
        input_path=input_path,
        output_dir=output_dir,
        extractor_mode=extractor,
        ollama_model=ollama_model,
        max_chunk_chars=max_chunk_chars,
    )
    console.print_json(json.dumps(info))


@app.command()
def query(
    question: Annotated[str, typer.Argument(help="Question to ask over the indexed corpus.")],
    output_dir: Annotated[Path, typer.Option("--index", "-x", help="Index directory.")] = DEFAULT_OUTPUT_DIR,
    mode: Annotated[str, typer.Option("--mode", "-m", help="keyword, vector, graph, or hybrid.")] = "hybrid",
    top_k: Annotated[int, typer.Option("--top-k", "-k")] = 5,
    use_ollama: Annotated[bool, typer.Option("--ollama/--no-ollama", help="Use Ollama for final answer generation if model exists.")] = False,
) -> None:
    """Run one question against a retrieval mode."""
    engine = RetrievalEngine.from_output_dir(output_dir)
    result = engine.query(question, mode=mode, top_k=top_k, use_ollama=use_ollama)
    console.print(f"[bold]{result.answer}[/bold]\n")
    table = Table(title="Evidence")
    table.add_column("Score")
    table.add_column("Source")
    table.add_column("Title")
    table.add_column("Snippet")
    for item in result.evidence:
        table.add_row(f"{item.score:.2f}", item.source, item.title, item.snippet[:220])
    console.print(table)


@app.command()
def eval(
    output_dir: Annotated[Path, typer.Option("--index", "-x", help="Index directory.")] = DEFAULT_OUTPUT_DIR,
    questions_path: Annotated[Path, typer.Option("--questions", "-q", help="Evaluation questions JSON.")] = DEFAULT_QUESTIONS_PATH,
    modes: Annotated[str, typer.Option("--modes", help="Comma-separated modes.")] = "keyword,vector,graph,hybrid",
    use_ollama: Annotated[bool, typer.Option("--ollama/--no-ollama", help="Use Ollama for generated answers.")] = False,
) -> None:
    """Run the sample evaluation questions across retrieval modes."""
    engine = RetrievalEngine.from_output_dir(output_dir)
    mode_list = [mode.strip() for mode in modes.split(",") if mode.strip()]
    df = run_evaluation(engine, questions_path=questions_path, modes=mode_list, use_ollama=use_ollama)
    path = save_evaluation(df, output_dir)
    console.print(f"Wrote evaluation: {path}")
    console.print(df[["id", "mode", "top_source", "evidence_count", "latency_ms"]].to_string(index=False))


@app.command("summary")
def summary(
    output_dir: Annotated[Path, typer.Option("--index", "-x", help="Index directory.")] = DEFAULT_OUTPUT_DIR,
) -> None:
    """Print graph/index counts."""
    index = load_graph_index(output_dir)
    console.print_json(json.dumps(graph_summary(index)))


@app.command("lightrag-index")
def lightrag_index(
    input_path: Annotated[Path, typer.Option("--input", "-i", help="Article file or folder.")] = DEFAULT_SAMPLE_DIR,
    working_dir: Annotated[Path, typer.Option("--workdir", "-w", help="LightRAG working dir.")] = DEFAULT_LIGHTRAG_DIR,
    llm_model: Annotated[str, typer.Option("--model")] = DEFAULT_CHAT_MODEL,
    embed_model: Annotated[str, typer.Option("--embed-model")] = DEFAULT_EMBED_MODEL,
) -> None:
    """Build the optional embedded LightRAG index."""
    articles = load_articles(input_path)
    result = build_lightrag_index(articles, working_dir=working_dir, llm_model=llm_model, embed_model=embed_model)
    console.print(f"LightRAG index ready: {result}")


@app.command("lightrag-query")
def lightrag_query(
    question: Annotated[str, typer.Argument()],
    working_dir: Annotated[Path, typer.Option("--workdir", "-w")] = DEFAULT_LIGHTRAG_DIR,
    mode: Annotated[str, typer.Option("--mode", "-m")] = "hybrid",
    llm_model: Annotated[str, typer.Option("--model")] = DEFAULT_CHAT_MODEL,
    embed_model: Annotated[str, typer.Option("--embed-model")] = DEFAULT_EMBED_MODEL,
) -> None:
    """Query the optional embedded LightRAG index."""
    console.print(query_lightrag(question, working_dir=working_dir, mode=mode, llm_model=llm_model, embed_model=embed_model))


if __name__ == "__main__":
    app()
