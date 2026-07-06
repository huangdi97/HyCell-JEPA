from __future__ import annotations

import numpy as np

from hycell.data_loaders import SingleCellDataset
from hycell.schema import AnnDataSchemaValidator


def test_schema_validator_accepts_minimal_valid_dataset() -> None:
    dataset = SingleCellDataset(
        expression=np.asarray([[1.0, 2.0], [3.0, 4.0]]),
        obs=[
            {"cell_id": "c1", "perturbation": "vehicle", "timepoint": "t0", "cell_system": "hdf"},
            {"cell_id": "c2", "perturbation": "repair", "timepoint": "t1", "cell_system": "hdf"},
        ],
        var_names=["GENE_A", "GENE_B"],
        source_path="memory",
        file_format="test",
    )
    validator = AnnDataSchemaValidator(_schema_config())

    result = validator.validate(dataset)

    assert result.valid is True
    assert result.errors == []


def test_schema_validator_reports_actionable_errors() -> None:
    dataset = SingleCellDataset(
        expression=np.asarray([[1.0, 2.0], [3.0, 4.0]]),
        obs=[
            {"cell_id": "c1", "perturbation": "", "timepoint": "t0", "cell_system": "hdf"},
            {"cell_id": "c1", "perturbation": "ambiguous", "timepoint": "t1", "cell_system": "unexpected"},
        ],
        var_names=["GENE_A", "GENE_A"],
        source_path="memory",
        file_format="test",
    )
    validator = AnnDataSchemaValidator(_schema_config())

    result = validator.validate(dataset)
    messages = [issue.message for issue in result.issues]

    assert result.valid is False
    assert any("duplicate cell_id" in message for message in messages)
    assert any("duplicate var_names" in message for message in messages)
    assert any("empty perturbation labels" in message for message in messages)
    assert any("ambiguous perturbation labels" in message for message in messages)
    assert result.warnings[0].field == "cell_system"


def _schema_config() -> dict:
    return {
        "required_obs_fields": ["cell_id", "perturbation", "timepoint", "cell_system"],
        "min_cells": 1,
        "min_genes": 1,
        "allowed_cell_systems": ["hdf"],
        "require_unique_cell_ids": True,
        "require_unique_var_names": True,
        "disallow_empty_perturbation": True,
    }
