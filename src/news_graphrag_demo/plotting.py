from __future__ import annotations

import networkx as nx
import plotly.graph_objects as go


NODE_COLORS = {
    "Article": "#2F4858",
    "PERSON": "#D1495B",
    "ORGANIZATION": "#00798C",
    "LOCATION": "#30638E",
    "EVENT": "#EDAE49",
    "DATE_TIME": "#7A6F9B",
    "OBJECT": "#4D9078",
    "TOPIC": "#6C757D",
}


def make_graph_figure(nodes: list[dict], edges: list[dict]) -> go.Figure:
    graph = nx.Graph()
    for node in nodes:
        graph.add_node(node["id"], **node)
    for edge in edges:
        graph.add_edge(edge["source"], edge["target"], **edge)

    if not graph.nodes:
        fig = go.Figure()
        fig.update_layout(height=420, margin=dict(l=0, r=0, t=20, b=0))
        return fig

    positions = nx.spring_layout(graph, seed=11, k=0.9)
    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    for source, target in graph.edges():
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="#8A8F98"),
        hoverinfo="none",
        mode="lines",
    )

    node_x: list[float] = []
    node_y: list[float] = []
    labels: list[str] = []
    colors: list[str] = []
    hover: list[str] = []
    for node_id, attrs in graph.nodes(data=True):
        x, y = positions[node_id]
        node_x.append(x)
        node_y.append(y)
        labels.append(attrs.get("label", node_id))
        node_type = attrs.get("type", "TOPIC")
        colors.append(NODE_COLORS.get(node_type, "#6C757D"))
        hover.append(f"{attrs.get('label', node_id)}<br>{node_type}")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=labels,
        textposition="top center",
        hovertext=hover,
        hoverinfo="text",
        marker=dict(size=15, color=colors, line=dict(width=1, color="#FFFFFF")),
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        height=460,
        showlegend=False,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="#FFFFFF",
    )
    return fig
