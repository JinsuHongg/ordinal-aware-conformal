#!/usr/bin/env python3
"""Validate a source checkpoint's provenance against a copied split assignment."""

from __future__ import annotations

import argparse
from pathlib import Path

from ordinal_aware_conformal.checkpoint_reuse import validate_checkpoint_reuse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-directory", type=Path, required=True)
    parser.add_argument("--source-provenance", type=Path, required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--training-criterion", required=True)
    parser.add_argument("--checkpoint-selection-criterion", required=True)
    parser.add_argument("--source-configuration-hash")
    args = parser.parse_args()
    record = validate_checkpoint_reuse(
        manifest_directory=args.manifest_directory,
        source_provenance_path=args.source_provenance,
        expected_dataset=args.dataset,
        expected_training_criterion=args.training_criterion,
        expected_checkpoint_selection_criterion=args.checkpoint_selection_criterion,
        expected_source_configuration_hash=args.source_configuration_hash,
    )
    print(record)


if __name__ == "__main__":
    main()
