from __future__ import annotations

import numpy as np

from hycell.encoders import AdapterEncoder, ActionEncoder, BioStateEncoder, ContextEncoder
from hycell.jepa import JEPAEncoderStack, fit_transition_core, mean_squared_error


def test_jepa_transition_core_predicts_target_shape() -> None:
    states = np.asarray([[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]])
    targets = states + 0.1
    actions = np.asarray(["control", "aging_stress", "control"])
    contexts = np.asarray(["t0->t1|toy_hdf", "t0->t1|toy_hdf", "t1->t2|toy_hdf"])
    adapters = np.asarray(["toy_hdf", "toy_hdf", "toy_hdf"])

    encoders = JEPAEncoderStack(
        bio_state=BioStateEncoder.fit(states, feature_names=["x", "y"], embedding_dim=2, seed=1),
        action=ActionEncoder.fit(actions, embedding_dim=2, seed=2),
        context=ContextEncoder.fit(contexts, embedding_dim=2, seed=3),
        adapter=AdapterEncoder.fit(adapters, embedding_dim=1, seed=4),
    )
    encoded = encoders.encode(states, actions, contexts, adapters)
    core = fit_transition_core(encoded, targets, ridge_lambda=0.001)

    predictions = core.predict(encoders, states, actions, contexts, adapters)

    assert predictions.shape == targets.shape
    assert mean_squared_error(predictions, targets) < 0.01
