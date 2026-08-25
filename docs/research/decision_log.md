# Decision Log

This file records research decisions that have been explicitly made.

It is not a substitute for the normative method or experiment specifications.

## 2026-08-24

### Research direction

The new project will focus on ordinal-aware class-conditional conformal calibration rather than defining the framework around quantile regression.

Desired abstraction:

\[
	ext{generic predictor}
ightarrow
S(x,k)
ightarrow
	ext{ordinal-aware class-conditional calibration}
ightarrow
	ext{ordinal prediction set}.
\]

The main open problem is how to use neighboring ordinal information without losing rigorous class-conditional validity.

### Relationship to OCQR

OCQR will remain a comparison method and predecessor.

The new project should be scientifically distinct from OCQR rather than an OCQR v2 implementation.

### Repository

New project repository:

`JinsuHongg/ordinal-aware-conformal`

Existing OCQR repository:

`JinsuHongg/ordinal-cqr`

The new repository should keep its new method, experiments, and research specifications separate while selectively reusing compatible infrastructure or checkpoints.

### Datasets

The planned benchmark suite is:

1. Synthetic
2. RetinaMNIST
3. UTKFace
4. Solar flare
5. Amazon Reviews

### Conformal comparisons

The planned comparison set is:

1. Pooled CP
2. Mondrian CP
3. LAC
4. APS
5. Min-CPS
6. RPS-CP
7. OCQR
8. Proposed

This is seven baselines plus the proposed method.

### Model families

Current plan:

- Standard regression model:
  - Pooled CP
  - Mondrian CP
  - Proposed

- Softmax classifier:
  - LAC
  - APS
  - Min-CPS
  - RPS-CP

- Quantile-regression model:
  - OCQR

Therefore the current experiment design uses three model families.

### Checkpoint reuse

Existing classifier and quantile-regression checkpoints may be reused for:

- RetinaMNIST;
- UTKFace;
- Solar flare;

provided the training/validation split assignments, preprocessing, targets, class definitions, and checkpoint-selection rules are unchanged.

The evaluation and conformal calibration should be rerun in the new unified pipeline.

The previous COPOC-specific classifier checkpoint is not required under the current baseline set.

### Fixed split assignments and checkpoint reuse

The frozen RetinaMNIST and UTKFace conference split assignments from the OCQR
repository will be copied into this repository and verified by SHA-256 before
reusing compatible classifier or quantile-regression checkpoints. Checkpoint
binaries remain external artifacts and must be referenced with their source
provenance. New standard-regression checkpoints are required for the shared
Pooled CP, Mondrian CP, and Proposed comparison.

### Selective OCQR infrastructure reuse

The new repository will reuse only infrastructure compatible with its modular
predictor-to-calibration design: immutable split assignments, checkpoint
provenance validation, dataset adapters, image backbones, shared losses,
evaluation artifacts, and Solar data-audit utilities.

Legacy OCQR experiment orchestration, cluster launch scripts, and mixed
baseline wrappers are not canonical infrastructure for this project. OCQR will
instead be ported as an isolated baseline that preserves its documented rule.

References to OCQR dataset-contract version `0.2.0` and method version `0.3.0`
identify source artifacts only; they are not versions of the new proposed
method, whose canonical version remains TBD.

### Split terminology

For human-facing project documentation, prefer:

- `split assignment`;
- `fixed split file`;

instead of `split manifest`.

A random seed is not equivalent to a split assignment.

The seed controls randomized procedures used to generate a split, whereas the split assignment records the actual sample-to-partition membership.

### Main calibration comparison

Pooled CP, Mondrian CP, and Proposed should use:

- the same standard-regression checkpoint;
- the same candidate-wise base score;

so that the main difference is the calibration rule.

### Documentation workflow

Notion is used as the broader research notebook.

The Git repository should be the executable source of truth for frozen method rules, experiment design, dataset contracts, and reproducibility requirements.

Research decisions made in discussion should be transferred into repository documentation rather than relying only on chat history.
