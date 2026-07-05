from __future__ import annotations

import json
from pathlib import Path

from hycell.config import load_config
from hycell.evidence_graph import build_evidence_graph, write_evidence_graph
from hycell.gene_sets import gene_sets_from_config, score_gene_sets
from hycell.toy_data import generate_toy_cells


def test_evidence_graph_links_actions_readouts_and_limitations() -> None:
    toy_config = load_config("configs/toy_data.yaml")
    score_config = load_config("configs/gene_sets.yaml")
    rows = generate_toy_cells(toy_config)
    scored = score_gene_sets(rows, gene_sets_from_config(score_config))

    graph = build_evidence_graph(scored)

    node_ids = {node["id"] for node in graph["nodes"]}
    assert "action:aging_stress" in node_ids
    assert "readout:senescence" in node_ids
    assert "limitation:engineering_validation_only" in node_ids
    assert any(
        edge["source"] == "action:aging_stress"
        and edge["target"] == "readout:senescence"
        and edge["kind"] == "toy_summary_mean_score"
        for edge in graph["edges"]
    )
    assert graph["data_status"] == "toy_engineering_validation_only"


def test_write_evidence_graph() -> None:
    graph = {
        "graph_version": "0.1",
        "nodes": [{"id": "limitation:test", "kind": "limitation"}],
        "edges": [],
        "summaries": [],
    }
    output = Path("outputs/test_tmp/graph_test.json")

    write_evidence_graph(graph, output)

    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["nodes"][0]["id"] == "limitation:test"
