"""Lightweight evidence graph for toy action/readout summaries."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

SCORE_NON_READOUT_COLUMNS = {
    "cell_id",
    "action",
    "action_label",
    "timepoint",
    "cell_system",
    "is_toy",
}


def build_evidence_graph(score_rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Build a deterministic evidence graph from per-cell gene set scores."""

    rows = list(score_rows)
    if not rows:
        raise ValueError("cannot build an evidence graph from empty scores")

    readouts = [
        column
        for column in rows[0].keys()
        if column not in SCORE_NON_READOUT_COLUMNS
    ]
    actions = _ordered_unique(str(row["action"]) for row in rows)
    action_labels = {
        str(row["action"]): str(row.get("action_label", row["action"]))
        for row in rows
    }

    nodes: list[dict[str, Any]] = [
        {
            "id": "assumption:toy_configured_effects",
            "kind": "assumption",
            "label": "Toy configured perturbation effects",
            "description": "Action/readout links come from deterministic toy configuration, not empirical discovery.",
        },
        {
            "id": "limitation:engineering_validation_only",
            "kind": "limitation",
            "label": "Engineering validation only",
            "description": "Toy-data graph edges are software validation artifacts, not biological claims.",
        },
        {
            "id": "limitation:not_clinical",
            "kind": "limitation",
            "label": "Not clinical guidance",
            "description": "The graph must not be used for diagnosis, treatment, or dosing decisions.",
        },
    ]

    for action in actions:
        nodes.append(
            {
                "id": f"action:{action}",
                "kind": "action",
                "label": action_labels[action],
            }
        )
    for readout in readouts:
        nodes.append(
            {
                "id": f"readout:{readout}",
                "kind": "readout",
                "label": readout.replace("_", " "),
            }
        )

    edges: list[dict[str, Any]] = []
    summaries = _summarize_scores(rows, readouts)
    for summary in summaries:
        action = summary["action"]
        readout = summary["readout"]
        edges.append(
            {
                "source": f"action:{action}",
                "target": f"readout:{readout}",
                "kind": "toy_summary_mean_score",
                "mean_score": summary["mean_score"],
                "n_cells": summary["n_cells"],
            }
        )
        edges.append(
            {
                "source": "assumption:toy_configured_effects",
                "target": f"action:{action}",
                "kind": "qualifies",
            }
        )
        edges.append(
            {
                "source": "limitation:engineering_validation_only",
                "target": f"readout:{readout}",
                "kind": "limits_interpretation",
            }
        )

    return {
        "graph_version": "0.1",
        "project": "HyCell-JEPA",
        "data_status": "toy_engineering_validation_only",
        "nodes": nodes,
        "edges": _dedupe_edges(edges),
        "summaries": summaries,
    }


def write_evidence_graph(graph: dict[str, Any], path: str | Path) -> Path:
    """Write evidence graph JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(graph, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def default_output_path(scores_path: str | Path) -> Path:
    """Return default graph path next to a score CSV."""

    return Path(scores_path).with_name("evidence_graph.json")


def _summarize_scores(
    rows: list[dict[str, Any]], readouts: list[str]
) -> list[dict[str, Any]]:
    values: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        action = str(row["action"])
        for readout in readouts:
            values[(action, readout)].append(float(row[readout]))

    summaries: list[dict[str, Any]] = []
    for action, readout in sorted(values):
        readout_values = values[(action, readout)]
        summaries.append(
            {
                "action": action,
                "readout": readout,
                "mean_score": round(sum(readout_values) / len(readout_values), 4),
                "n_cells": len(readout_values),
            }
        )
    return summaries


def _ordered_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _dedupe_edges(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for edge in edges:
        key = json.dumps(edge, sort_keys=True)
        if key not in seen:
            seen.add(key)
            deduped.append(edge)
    return deduped
