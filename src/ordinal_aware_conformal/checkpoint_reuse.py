"""Validate immutable split assignments before reusing a source checkpoint."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckpointReuseRecord:
    """Portable provenance required to reuse a checkpoint from another repository."""

    source_repository: str
    checkpoint_relative_path: str
    checkpoint_sha256: str
    manifest_sha256: str
    dataset_version: str
    preprocessing_identifier: str
    target_definition: str
    checkpoint_selection_criterion: str


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hash of a file without changing it."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest_metadata(manifest_directory: Path) -> dict[str, object]:
    """Load and verify a copied fixed split assignment against its metadata."""
    metadata_path = manifest_directory / "manifest_metadata.json"
    manifest_path = manifest_directory / "manifest.jsonl"
    metadata = json.loads(metadata_path.read_text())
    expected_hash = metadata.get("manifest_sha256")
    if not isinstance(expected_hash, str):
        raise ValueError(f"{metadata_path} has no manifest_sha256.")
    actual_hash = sha256_file(manifest_path)
    if actual_hash != expected_hash:
        raise ValueError(
            f"Split assignment hash mismatch for {manifest_path}: "
            f"expected {expected_hash}, found {actual_hash}."
        )
    return metadata


def validate_checkpoint_reuse(
    *,
    manifest_directory: Path,
    source_provenance_path: Path,
    expected_dataset: str,
    expected_training_criterion: str,
    expected_checkpoint_selection_criterion: str,
    expected_source_configuration_hash: str | None = None,
) -> CheckpointReuseRecord:
    """Validate split identity and declared provenance before checkpoint loading.

    The checkpoint binary itself stays outside this repository.  Its source
    provenance must agree with the immutable local assignment and the caller's
    frozen split, training, and checkpoint-selection contract. Dataset adapters
    must separately validate the target and preprocessing fields they consume;
    the source provenance records only their configuration hash.
    """
    metadata = load_manifest_metadata(manifest_directory)
    provenance = json.loads(source_provenance_path.read_text())
    manifest_hash = metadata["manifest_sha256"]
    if provenance.get("manifest_hash") != manifest_hash:
        raise ValueError("Source checkpoint provenance does not match the local split assignment.")
    if provenance.get("dataset") != expected_dataset:
        raise ValueError("Source checkpoint dataset does not match the requested dataset.")
    if provenance.get("training_criterion") != expected_training_criterion:
        raise ValueError("Source checkpoint training criterion does not match.")
    if provenance.get("checkpoint_selection_criterion") != expected_checkpoint_selection_criterion:
        raise ValueError("Source checkpoint selection criterion does not match.")
    source_configuration_hash = provenance.get("configuration_hash")
    if expected_source_configuration_hash is not None and source_configuration_hash != expected_source_configuration_hash:
        raise ValueError("Source checkpoint configuration hash does not match.")
    dataset_version = metadata.get("dataset_version")
    if not isinstance(dataset_version, str):
        raise ValueError("Split metadata has no dataset_version.")
    checkpoint_identifier = provenance.get("checkpoint_identifier")
    if not isinstance(checkpoint_identifier, str):
        raise ValueError("Source checkpoint provenance has no checkpoint_identifier.")
    checkpoint_path = source_provenance_path.parent / checkpoint_identifier
    if not checkpoint_path.is_file():
        raise ValueError(f"Source checkpoint is not a readable file: {checkpoint_path}.")
    return CheckpointReuseRecord(
        source_repository="ordinal-cqr",
        checkpoint_relative_path=checkpoint_identifier,
        checkpoint_sha256=sha256_file(checkpoint_path),
        manifest_sha256=manifest_hash,
        dataset_version=dataset_version,
        preprocessing_identifier=str(source_configuration_hash or "unrecorded"),
        target_definition=expected_training_criterion,
        checkpoint_selection_criterion=expected_checkpoint_selection_criterion,
    )
