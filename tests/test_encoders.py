from __future__ import annotations

import numpy as np

from hycell.encoders import ActionEncoder, BioStateEncoder, ContextEncoder


def test_bio_state_encoder_shape_and_determinism() -> None:
    states = np.asarray([[1.0, 2.0, 3.0], [1.5, 2.5, 2.8], [0.8, 2.2, 3.2]])

    first = BioStateEncoder.fit(states, feature_names=["a", "b", "c"], embedding_dim=2, seed=11)
    second = BioStateEncoder.fit(states, feature_names=["a", "b", "c"], embedding_dim=2, seed=11)

    assert first.transform(states).shape == (3, 2)
    np.testing.assert_allclose(first.transform(states), second.transform(states))


def test_categorical_encoders_handle_known_and_unknown_labels() -> None:
    labels = np.asarray(["control", "aging_stress", "control"])

    action = ActionEncoder.fit(labels, embedding_dim=3, seed=3)
    context = ContextEncoder.fit(np.asarray(["t0->t1|toy_hdf"]), embedding_dim=2, seed=4)

    assert action.transform(np.asarray(["control", "missing"])).shape == (2, 3)
    assert context.transform(np.asarray(["t0->t1|toy_hdf"])).shape == (1, 2)
    assert "__unknown__" in action.categories
