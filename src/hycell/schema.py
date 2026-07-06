"""AnnData-like schema validation for small candidate datasets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hycell.data_loaders import SingleCellDataset


@dataclass(frozen=True)
class SchemaIssue:
    severity: str
    field: str
    message: str


@dataclass(frozen=True)
class SchemaValidationResult:
    issues: list[SchemaIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    @property
    def errors(self) -> list[SchemaIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[SchemaIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": [issue.__dict__ for issue in self.errors],
            "warnings": [issue.__dict__ for issue in self.warnings],
        }


class AnnDataSchemaValidator:
    """Validate the minimal AnnData-like contract used by real-data scaffolding."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.required_obs_fields = list(config.get("required_obs_fields", []))
        self.min_cells = int(config.get("min_cells", 1))
        self.min_genes = int(config.get("min_genes", 1))
        self.allowed_cell_systems = {str(value) for value in config.get("allowed_cell_systems", [])}
        self.require_unique_cell_ids = bool(config.get("require_unique_cell_ids", True))
        self.require_unique_var_names = bool(config.get("require_unique_var_names", True))
        self.disallow_empty_perturbation = bool(config.get("disallow_empty_perturbation", True))

    def validate(self, dataset: SingleCellDataset) -> SchemaValidationResult:
        issues: list[SchemaIssue] = []
        n_cells, n_genes = dataset.expression.shape if dataset.expression.ndim == 2 else (-1, -1)

        if dataset.expression.ndim != 2:
            issues.append(_error("expression", "expression matrix must be 2-dimensional"))
        if n_cells != len(dataset.obs):
            issues.append(_error("obs", f"obs row count {len(dataset.obs)} does not match expression rows {n_cells}"))
        if n_genes != len(dataset.var_names):
            issues.append(_error("var_names", f"var_names count {len(dataset.var_names)} does not match expression columns {n_genes}"))
        if n_cells < self.min_cells:
            issues.append(_error("expression", f"dataset has {n_cells} cells, minimum is {self.min_cells}"))
        if n_genes < self.min_genes:
            issues.append(_error("var_names", f"dataset has {n_genes} genes, minimum is {self.min_genes}"))

        for field_name in self.required_obs_fields:
            missing_rows = [idx for idx, row in enumerate(dataset.obs) if field_name not in row or _is_blank(row[field_name])]
            if missing_rows:
                sample = ", ".join(str(idx) for idx in missing_rows[:5])
                issues.append(_error(field_name, f"missing required obs field {field_name!r} in rows: {sample}"))

        if self.require_unique_cell_ids and _has_field(dataset.obs, "cell_id"):
            issues.extend(_duplicate_issues("cell_id", [str(row.get("cell_id", "")) for row in dataset.obs]))

        if self.require_unique_var_names:
            issues.extend(_duplicate_issues("var_names", [str(name) for name in dataset.var_names]))

        if self.disallow_empty_perturbation and _has_field(dataset.obs, "perturbation"):
            empty = [idx for idx, row in enumerate(dataset.obs) if _is_blank(row.get("perturbation"))]
            if empty:
                sample = ", ".join(str(idx) for idx in empty[:5])
                issues.append(_error("perturbation", f"empty perturbation labels in rows: {sample}"))

        if _has_field(dataset.obs, "perturbation"):
            ambiguous = [
                idx
                for idx, row in enumerate(dataset.obs)
                if str(row.get("perturbation", "")).strip().lower() in {"unknown", "ambiguous", "mixed", "multiple"}
            ]
            if ambiguous:
                sample = ", ".join(str(idx) for idx in ambiguous[:5])
                issues.append(_error("perturbation", f"ambiguous perturbation labels in rows: {sample}"))

        if self.allowed_cell_systems and _has_field(dataset.obs, "cell_system"):
            unexpected = sorted(
                {
                    str(row.get("cell_system", ""))
                    for row in dataset.obs
                    if str(row.get("cell_system", "")) not in self.allowed_cell_systems
                }
            )
            if unexpected:
                issues.append(
                    _warning(
                        "cell_system",
                        f"unexpected cell_system values {unexpected}; allowed values are {sorted(self.allowed_cell_systems)}",
                    )
                )

        return SchemaValidationResult(issues=issues)


def _has_field(obs: list[dict[str, Any]], field_name: str) -> bool:
    return any(field_name in row for row in obs)


def _duplicate_issues(field_name: str, values: list[str]) -> list[SchemaIssue]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        return [_error(field_name, f"duplicate {field_name} values: {sorted(duplicates)[:5]}")]
    return []


def _is_blank(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def _error(field: str, message: str) -> SchemaIssue:
    return SchemaIssue(severity="error", field=field, message=message)


def _warning(field: str, message: str) -> SchemaIssue:
    return SchemaIssue(severity="warning", field=field, message=message)
