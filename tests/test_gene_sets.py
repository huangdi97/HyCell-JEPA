from __future__ import annotations

from pathlib import Path

import pytest

from hycell.config import load_config
from hycell.gene_sets import gene_sets_from_config, score_gene_sets, write_score_rows
from hycell.toy_data import generate_toy_cells


def test_score_gene_sets_adds_expected_readouts() -> None:
    toy_config = load_config("configs/toy_data.yaml")
    score_config = load_config("configs/gene_sets.yaml")
    rows = generate_toy_cells(toy_config)

    scored = score_gene_sets(rows, gene_sets_from_config(score_config))

    assert len(scored) == len(rows)
    assert {"senescence", "proliferation", "ecm_remodeling"}.issubset(scored[0])
    assert scored[0]["senescence"] == pytest.approx(
        (rows[0]["CDKN1A"] + rows[0]["CDKN2A"]) / 2
    )


def test_missing_gene_policy_errors() -> None:
    rows = [{"cell_id": "x", "action": "control", "CDKN1A": "1.0"}]

    with pytest.raises(ValueError, match="missing genes"):
        score_gene_sets(rows, {"senescence": ["CDKN1A", "CDKN2A"]})


def test_write_score_rows() -> None:
    output = Path("outputs/test_tmp/scores_test.csv")

    write_score_rows(
        [{"cell_id": "x", "action": "control", "senescence": 1.25}],
        output,
    )

    assert output.read_text(encoding="utf-8").splitlines()[0] == "cell_id,action,senescence"
