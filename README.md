# Ordinal-Aware Class-Conditional Conformal Prediction

This repository investigates how known ordinal structure can improve class-conditional conformal prediction without losing finite-sample validity. The proposed calibration rule is not finalized; this repository does not claim an ordinal information-sharing guarantee before one is specified and proved.

The intended architecture is:

```text
predictor -> candidate score S(x, k) -> calibration rule -> ordinal prediction set
```

The main comparison holds the predictor and candidate score fixed while varying only the calibration layer:

- Pooled CP;
- Mondrian CP;
- Proposed ordinal-aware calibration.

OCQR is retained as a separate quantile-regression baseline. Its method contract is not the proposed method contract.

## Status and specifications

Read the project specifications before changing research behavior:

1. [proposed method contract](docs/methods/proposed_method.md)
2. [proposed theory](docs/methods/proposed_theory.md)
3. [baseline rules](docs/methods/baseline_rules.md)
4. [experiment plan](docs/research/experiment_plan.md)

In particular, do not introduce cross-class calibration pooling, smoothing, or
threshold borrowing as canonical behavior until the method and theory documents
define and justify it.

## Repository layout

```text
src/ordinal_aware_conformal/
  checkpoint_reuse.py       # split/provenance/checkpoint compatibility checks
  data/                     # dataset helpers and fixed Solar retained-population rule
  evaluation/               # prediction-artifact schema and set metrics
  models/                   # reusable image-model backbones
  utils/                    # shared losses and helpers
data/split_assignments/
  conference_v0_3/          # copied, immutable RetinaMNIST and UTKFace assignments
scripts/
  data/                     # split-assignment regeneration for audit only
  solar/                    # Solar data preflight and statistics utilities
  validate_checkpoint_reuse.py
docs/                       # method, dataset, and experiment specifications
tests/                      # focused reproducibility tests
```

## Setup

Create the Conda environment:

```bash
conda env create -f environment.yml
conda activate ordinal-aware-conformal
export PYTHONPATH="$PWD/src"
```

`environment.yml` uses PyTorch 2.6 to remain compatible with the existing
OCQR checkpoints. For a CUDA-specific PyTorch build, install the appropriate
official PyTorch wheel after environment creation, using the CUDA version of
the target machine.

Run the focused checks:

```bash
PYTHONPATH=src python -m unittest tests/test_checkpoint_reuse.py
```

## Fixed split assignments and checkpoint reuse

The repository includes the frozen OCQR assignments for RetinaMNIST and
UTKFace. Their copied assignment hashes are:

| Dataset | SHA-256 |
| --- | --- |
| RetinaMNIST | `9212f1c384918de800b496f93e902530534eb70adfaba3ded2a13aa0c1e2236b` |
| UTKFace | `3ba4118683ff2031df19ae63651ba3a7718e883dc268d1b8bc06a74e79064c83` |

Checkpoint binaries remain in the OCQR repository. Before a reuse run, verify
the copied assignment, source provenance, source configuration hash, and the
checkpoint binary itself:

```bash
PYTHONPATH=src python scripts/validate_checkpoint_reuse.py \
  --manifest-directory data/split_assignments/conference_v0_3/retinamnist \
  --source-provenance /path/to/ordinal-cqr/outputs/conference_v0_3/retinamnist/ocqr/seed_0/provenance.json \
  --dataset retinamnist \
  --training-criterion "pinball loss" \
  --checkpoint-selection-criterion "validation pinball loss" \
  --source-configuration-hash f622a3277f9ded0ab90e3e0eb47cb762a55e146c99c7bf878701b269b9b012ca
```

The validator resolves `checkpoint.pt` beside the source provenance file and
reports its SHA-256. Dataset adapters must additionally verify that the local
preprocessing, target definition, ordinal bins, and class labels match the
checkpoint’s frozen experiment contract.

Reuse is appropriate for compatible QR checkpoints (OCQR) and classifier
checkpoints (classification baselines). The Pooled CP, Mondrian CP, and
Proposed comparison requires a newly trained shared standard-regression model.

Solar uses chronological source split files rather than a copied assignment in
this repository. Its exact source hashes and retained-population audit must be
validated before any Solar checkpoint is reused.

## Reproducibility requirements

Canonical runs must record the fixed assignment hash, seed, configuration,
checkpoint identifier and hash, source commit, preprocessing, target/label
definition, calibration method version, and evaluation provenance. See
[AGENTS.md](AGENTS.md) for the full repository protocol.
