from __future__ import annotations

import numpy as np

from hycell.hdf_adapter import HDFAdapter


def test_hdf_adapter_maps_actions_and_context() -> None:
    adapter = HDFAdapter()

    spec = adapter.action_spec("regeneration")
    state, actions, contexts, adapters = adapter.model_inputs(
        np.ones(6),
        action="regeneration",
        source_timepoint="t0",
        target_timepoint="t1",
    )

    assert spec.scenario == "Toy HDF regeneration scenario"
    assert state.shape == (1, 6)
    assert actions.tolist() == ["regeneration"]
    assert contexts.tolist() == ["t0->t1|toy_hdf"]
    assert adapters.tolist() == ["toy_hdf"]
