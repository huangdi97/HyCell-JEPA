"""Training and evaluation helpers for the toy JEPA transition core."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from hycell.config import load_config
from hycell.datasets import TransitionDataset, build_transition_dataset, load_score_rows, train_eval_split
from hycell.encoders import AdapterEncoder, ActionEncoder, BioStateEncoder, ContextEncoder, encoder_metadata
from hycell.gene_sets import gene_sets_from_config, score_gene_sets, write_score_rows
from hycell.jepa import JEPAEncoderStack, JEPATransitionCore, fit_transition_core, mean_squared_error
from hycell.toy_data import generate_toy_cells, toy_cell_columns, write_toy_cells


def load_transition_dataset_from_config(config: dict[str, Any]) -> TransitionDataset:
    """Load the configured toy score table and build adjacent transitions."""

    ensure_toy_scores(config)
    rows = load_score_rows(config["scores_path"])
    return build_transition_dataset(
        rows,
        feature_names=[str(item) for item in config.get("belief_features", [])] or None,
        timepoints=[str(item) for item in config.get("timepoints", [])] or None,
    )


def ensure_toy_scores(config: dict[str, Any]) -> None:
    """Prepare small toy score files when a local training config asks for it."""

    if not config.get("auto_prepare_toy_scores", False):
        return
    scores_path = Path(config["scores_path"])
    toy_cells_path = Path(config.get("toy_cells_path", "outputs/toy_data/toy_cells.csv"))
    if scores_path.exists() and toy_cells_path.exists():
        return

    toy_config = load_config(config.get("toy_data_config", "configs/toy_data.yaml"))
    gene_set_config = load_config(config.get("gene_sets_config", "configs/gene_sets.yaml"))
    toy_rows = generate_toy_cells(toy_config)
    write_toy_cells(toy_rows, toy_cells_path, toy_cell_columns(toy_config))
    scored_rows = score_gene_sets(toy_rows, gene_sets_from_config(gene_set_config))
    write_score_rows(scored_rows, scores_path)


def train_toy_encoder(config: dict[str, Any]) -> dict[str, Any]:
    """Fit compact encoders and write local verification artifacts."""

    seed = int(config.get("seed", 0))
    dataset = load_transition_dataset_from_config(config)
    all_states = np.vstack([dataset.current_states, dataset.next_states])

    bio = BioStateEncoder.fit(
        all_states,
        feature_names=dataset.feature_names,
        embedding_dim=int(config.get("bio_state_embedding_dim", 4)),
        seed=seed + 1,
    )
    action = ActionEncoder.fit(
        dataset.actions,
        embedding_dim=int(config.get("action_embedding_dim", 3)),
        seed=seed + 2,
        extra_categories=[str(item) for item in config.get("action_labels", [])],
    )
    context = ContextEncoder.fit(
        dataset.context_labels,
        embedding_dim=int(config.get("context_embedding_dim", 3)),
        seed=seed + 3,
    )
    adapter = AdapterEncoder.fit(
        dataset.adapter_labels,
        embedding_dim=int(config.get("adapter_embedding_dim", 2)),
        seed=seed + 4,
    )
    encoders = JEPAEncoderStack(bio_state=bio, action=action, context=context, adapter=adapter)
    encoded = encoders.encode(
        dataset.current_states,
        dataset.actions,
        dataset.context_labels,
        dataset.adapter_labels,
    )
    embeddings = encoded.concatenate()

    encoder_checkpoint = Path(config.get("encoder_checkpoint", "outputs/checkpoints/best_encoder.pt"))
    embeddings_path = Path(config.get("embeddings_path", "outputs/embeddings/embeddings.npy"))
    metrics_path = Path(config.get("metrics_path", "outputs/reports/metrics.json"))
    _save_encoder_checkpoint(encoder_checkpoint, encoders)
    embeddings_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(embeddings_path, embeddings)

    metrics = {
        "stage": "encoder",
        "data_status": "toy_engineering_validation_only",
        "n_transitions": dataset.n_examples,
        "embedding_shape": list(embeddings.shape),
        "checkpoint_path": str(encoder_checkpoint),
        "embeddings_path": str(embeddings_path),
    }
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "dataset": dataset,
        "encoders": encoders,
        "embeddings": embeddings,
        "metrics": metrics,
        "encoder_checkpoint": encoder_checkpoint,
        "embeddings_path": embeddings_path,
        "metrics_path": metrics_path,
    }


def train_toy_jepa(config: dict[str, Any]) -> dict[str, Any]:
    """Train the compact toy JEPA transition model and persist artifacts."""

    seed = int(config.get("seed", 0))
    dataset = load_transition_dataset_from_config(config)
    train_idx, eval_idx = train_eval_split(
        dataset,
        train_fraction=float(config.get("train_fraction", 0.75)),
        seed=seed,
    )

    bio = BioStateEncoder.fit(
        dataset.current_states[train_idx],
        feature_names=dataset.feature_names,
        embedding_dim=int(config.get("bio_state_embedding_dim", 4)),
        seed=seed + 1,
    )
    action = ActionEncoder.fit(
        dataset.actions,
        embedding_dim=int(config.get("action_embedding_dim", 3)),
        seed=seed + 2,
        extra_categories=[str(item) for item in config.get("action_labels", [])],
    )
    context = ContextEncoder.fit(
        dataset.context_labels,
        embedding_dim=int(config.get("context_embedding_dim", 3)),
        seed=seed + 3,
    )
    adapter = AdapterEncoder.fit(
        dataset.adapter_labels,
        embedding_dim=int(config.get("adapter_embedding_dim", 2)),
        seed=seed + 4,
    )
    encoders = JEPAEncoderStack(bio_state=bio, action=action, context=context, adapter=adapter)

    encoded_train = encoders.encode(
        dataset.current_states[train_idx],
        dataset.actions[train_idx],
        dataset.context_labels[train_idx],
        dataset.adapter_labels[train_idx],
    )
    core = fit_transition_core(
        encoded_train,
        dataset.next_states[train_idx],
        ridge_lambda=float(config.get("ridge_lambda", 0.001)),
    )

    train_predictions = core.predict(
        encoders,
        dataset.current_states[train_idx],
        dataset.actions[train_idx],
        dataset.context_labels[train_idx],
        dataset.adapter_labels[train_idx],
    )
    eval_predictions = core.predict(
        encoders,
        dataset.current_states[eval_idx],
        dataset.actions[eval_idx],
        dataset.context_labels[eval_idx],
        dataset.adapter_labels[eval_idx],
    )
    metrics = {
        "data_status": "toy_engineering_validation_only",
        "n_transitions": dataset.n_examples,
        "n_train": int(len(train_idx)),
        "n_eval": int(len(eval_idx)),
        "train_mse": mean_squared_error(train_predictions, dataset.next_states[train_idx]),
        "eval_mse": mean_squared_error(eval_predictions, dataset.next_states[eval_idx]),
    }

    output_dir = Path(config.get("output_dir", "outputs/jepa_toy"))
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / str(config.get("model_filename", "toy_jepa_model.npz"))
    metadata_path = output_dir / str(config.get("metadata_filename", "toy_jepa_metadata.json"))
    metrics_path = output_dir / str(config.get("metrics_filename", "toy_jepa_metrics.json"))

    save_model_npz(model_path, encoders, core)
    if "jepa_checkpoint" in config:
        save_model_npz(config["jepa_checkpoint"], encoders, core)
    metadata = {
        "project": "HyCell-JEPA",
        "model_kind": "compact_numpy_jepa_transition",
        "formula": "b_t + a_t + c_t + h_t -> b_{t+1}",
        "limitations": [
            "Toy engineering validation only.",
            "Predicts compact gene-set readout features, not transcriptomes.",
            "Not clinical guidance or biological discovery evidence.",
        ],
        "encoders": encoder_metadata(bio, action, context, adapter),
        "model_path": str(model_path),
        "metrics_path": str(metrics_path),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if "metrics_path" in config:
        report_metrics_path = Path(config["metrics_path"])
        report_metrics_path.parent.mkdir(parents=True, exist_ok=True)
        report_metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "dataset": dataset,
        "encoders": encoders,
        "core": core,
        "metrics": metrics,
        "model_path": model_path,
        "metadata_path": metadata_path,
        "metrics_path": metrics_path,
    }


def evaluate_toy_jepa(config: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a persisted toy JEPA model on configured score transitions."""

    output_dir = Path(config.get("output_dir", "outputs/jepa_toy"))
    model_path = output_dir / str(config.get("model_filename", "toy_jepa_model.npz"))
    dataset = load_transition_dataset_from_config(config)
    encoders, core = load_model_npz(model_path)
    predictions = core.predict(
        encoders,
        dataset.current_states,
        dataset.actions,
        dataset.context_labels,
        dataset.adapter_labels,
    )
    per_feature_mse = ((predictions - dataset.next_states) ** 2).mean(axis=0)
    metrics = {
        "data_status": "toy_engineering_validation_only",
        "n_transitions": dataset.n_examples,
        "mse": mean_squared_error(predictions, dataset.next_states),
        "per_feature_mse": {
            feature: float(value)
            for feature, value in zip(dataset.feature_names, per_feature_mse)
        },
    }
    metrics_path = output_dir / str(config.get("metrics_filename", "toy_jepa_metrics.json"))
    eval_metrics_path = metrics_path.with_name("toy_jepa_eval_metrics.json")
    eval_metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    metrics["metrics_path"] = str(eval_metrics_path)
    return metrics


def save_model_npz(path: str | Path, encoders: JEPAEncoderStack, core: JEPATransitionCore) -> Path:
    """Persist model arrays and string vocabularies."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        np.savez_compressed(
            handle,
            bio_feature_names=np.asarray(encoders.bio_state.feature_names),
            bio_mean=encoders.bio_state.mean,
            bio_scale=encoders.bio_state.scale,
            bio_projection=encoders.bio_state.projection,
            action_categories=np.asarray(encoders.action.categories),
            action_projection=encoders.action.projection,
            context_categories=np.asarray(encoders.context.categories),
            context_projection=encoders.context.projection,
            adapter_categories=np.asarray(encoders.adapter.categories),
            adapter_projection=encoders.adapter.projection,
            transition_weights=core.weights,
            transition_bias=core.bias,
        )
    return output_path


def load_model_npz(path: str | Path) -> tuple[JEPAEncoderStack, JEPATransitionCore]:
    """Load a persisted toy JEPA model."""

    data = np.load(path, allow_pickle=False)
    bio = BioStateEncoder(
        feature_names=[str(item) for item in data["bio_feature_names"].tolist()],
        mean=data["bio_mean"],
        scale=data["bio_scale"],
        projection=data["bio_projection"],
    )
    action = ActionEncoder(
        categories=[str(item) for item in data["action_categories"].tolist()],
        projection=data["action_projection"],
    )
    context = ContextEncoder(
        categories=[str(item) for item in data["context_categories"].tolist()],
        projection=data["context_projection"],
    )
    adapter = AdapterEncoder(
        categories=[str(item) for item in data["adapter_categories"].tolist()],
        projection=data["adapter_projection"],
    )
    core = JEPATransitionCore(
        weights=data["transition_weights"],
        bias=data["transition_bias"],
    )
    return JEPAEncoderStack(bio_state=bio, action=action, context=context, adapter=adapter), core


def _save_encoder_checkpoint(path: str | Path, encoders: JEPAEncoderStack) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        np.savez_compressed(
            handle,
            bio_feature_names=np.asarray(encoders.bio_state.feature_names),
            bio_mean=encoders.bio_state.mean,
            bio_scale=encoders.bio_state.scale,
            bio_projection=encoders.bio_state.projection,
            action_categories=np.asarray(encoders.action.categories),
            action_projection=encoders.action.projection,
            context_categories=np.asarray(encoders.context.categories),
            context_projection=encoders.context.projection,
            adapter_categories=np.asarray(encoders.adapter.categories),
            adapter_projection=encoders.adapter.projection,
        )
    return output_path
