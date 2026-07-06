from __future__ import annotations

import numpy as np

from hycell.data_loaders import SingleCellDataset
from hycell.perturbation_adapter import HDFAgingMetadataAdapter, PerturbationAdapter, aliases_from_config


def test_perturbation_adapter_preserves_original_and_maps_aliases() -> None:
    adapter = PerturbationAdapter({"control": ["vehicle"], "regeneration": ["repair"]})

    mapped = adapter.map_label("repair")
    unknown = adapter.map_label("novel ligand")

    assert mapped.original_label == "repair"
    assert mapped.canonical_action == "regeneration"
    assert mapped.mapping_status == "mapped"
    assert unknown.original_label == "novel ligand"
    assert unknown.canonical_action == "unknown"
    assert unknown.mapping_status == "unknown"


def test_hdf_aging_metadata_adapter_maps_context_labels() -> None:
    config = {"canonical_actions": {"control": ["vehicle"], "aging_stress": ["senescence"]}}
    adapter = HDFAgingMetadataAdapter(PerturbationAdapter(aliases_from_config(config)))
    dataset = SingleCellDataset(
        expression=np.asarray([[1.0], [2.0]]),
        obs=[
            {"cell_id": "c1", "perturbation": "vehicle", "timepoint": "t0", "cell_system": "hdf"},
            {"cell_id": "c2", "perturbation": "senescence", "timepoint": "t1", "cell_system": "hdf"},
        ],
        var_names=["GENE_A"],
        source_path="memory",
        file_format="test",
    )

    rows = adapter.map_dataset(dataset)

    assert rows[0]["original_perturbation"] == "vehicle"
    assert rows[0]["canonical_action"] == "control"
    assert rows[0]["context_label"] == "hdf|t0|control"
    assert rows[1]["canonical_action"] == "aging_stress"
