from __future__ import annotations

import numpy as np

from hycell.config import load_config
from hycell.datasets import build_transition_dataset, load_score_rows
from hycell.gene_sets import gene_sets_from_config, score_gene_sets, write_score_rows
from hycell.hdf_adapter import HDFAdapter
from hycell.planner import TargetStatePlanner
from hycell.toy_data import generate_toy_cells
from hycell.training import load_model_npz, train_toy_jepa
from hycell.verifier import BiologicalVerifier


def test_planner_proposes_toy_action_sequence() -> None:
    config = dict(load_config("configs/jepa_toy.yaml"))
    config["output_dir"] = "outputs/test_tmp/planner_model"
    config["scores_path"] = _write_scores("outputs/test_tmp/planner_scores.csv")
    train_toy_jepa(config)
    dataset = build_transition_dataset(load_score_rows(config["scores_path"]), feature_names=config["belief_features"], timepoints=config["timepoints"])
    encoders, core = load_model_npz("outputs/test_tmp/planner_model/toy_jepa_model.npz")
    adapter = HDFAdapter()
    verifier = BiologicalVerifier(dataset.feature_names)
    planner = TargetStatePlanner(
        encoders=encoders,
        core=core,
        adapter=adapter,
        verifier=verifier,
        feature_names=dataset.feature_names,
    )

    start = adapter.state_for(dataset, action="control", source_timepoint="t0")
    target = start + np.asarray([-0.1, 0.2, 0.2, -0.1, 0.1, 0.0])
    plan = planner.plan(start, target, horizon=2)

    assert len(plan.actions) == 2
    assert plan.distance >= 0.0
    assert plan.verification["status"] in {"warn", "fail"}


def _write_scores(path: str) -> str:
    toy_config = load_config("configs/toy_data.yaml")
    score_config = load_config("configs/gene_sets.yaml")
    rows = generate_toy_cells(toy_config)
    scored = score_gene_sets(rows, gene_sets_from_config(score_config))
    write_score_rows(scored, path)
    return path
