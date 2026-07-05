from __future__ import annotations

from pathlib import Path

import numpy as np

from hycell.config import load_config
from hycell.toy_data import generate_toy_cells, toy_cell_columns, write_toy_cells, write_toy_npz


def test_generate_toy_cells_is_deterministic() -> None:
    config = load_config("configs/toy_data.yaml")

    first = generate_toy_cells(config)
    second = generate_toy_cells(config)

    assert first == second
    assert len(first) == 4 * 3 * 6
    assert first[0]["cell_id"] == "toy_control_t0_000"
    assert first[0]["is_toy"] == "true"


def test_action_effects_change_expected_toy_readouts() -> None:
    config = load_config("configs/toy_data.yaml")
    rows = generate_toy_cells(config)

    aging_t2 = next(row for row in rows if row["action"] == "aging_stress" and row["timepoint"] == "t2")
    control_t2 = next(row for row in rows if row["action"] == "control" and row["timepoint"] == "t2")

    assert aging_t2["CDKN1A"] > control_t2["CDKN1A"]
    assert aging_t2["MKI67"] < control_t2["MKI67"]


def test_write_toy_cells_round_trip() -> None:
    config = load_config("configs/toy_data.yaml")
    rows = generate_toy_cells(config)
    output = Path("outputs/test_tmp/toy_cells_test.csv")

    write_toy_cells(rows, output, toy_cell_columns(config))

    text = output.read_text(encoding="utf-8")
    assert text.startswith("cell_id,action,action_label,timepoint")
    assert "toy_partial_reprogramming_t2_005" in text


def test_write_toy_npz() -> None:
    output = Path("outputs/test_tmp/toy_matrix_test.npz")

    write_toy_npz(output, n_cells=12, n_genes=8, seed=7)

    data = np.load(output)
    assert data["expression"].shape == (12, 8)
    assert data["gene_names"][0] == "TOY_GENE_0000"
    assert data["cell_ids"][-1] == "toy_cell_000011"
    assert bool(data["is_toy"]) is True
