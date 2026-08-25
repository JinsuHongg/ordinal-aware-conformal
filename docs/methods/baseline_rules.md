# Baseline Conformal Prediction Rules

**Status:** Working baseline specification

This document defines the intended comparison roles and shared-model requirements.

Exact published baseline formulas and implementation details must be verified against the original papers or official implementations before canonical experiments.

Do not silently substitute a convenient implementation for a published method.

## 1. Comparison set

The current comparison set is:

1. Pooled CP
2. Mondrian CP
3. LAC
4. APS
5. Min-CPS
6. RPS-CP
7. OCQR
8. Proposed

The first seven are comparison methods; Proposed is the new method.

## 2. Shared base-model policy

### Standard regression family

Shared by:

- Pooled CP
- Mondrian CP
- Proposed

These methods should use the same trained regression checkpoint and the same candidate score in the main calibration comparison.

This comparison is intended to isolate the calibration rule.

### Softmax classifier family

Shared by:

- LAC
- APS
- Min-CPS
- RPS-CP

Use the same classifier checkpoint within each dataset and seed whenever consistent with the published method definitions.

### Quantile-regression family

Used by:

- OCQR

OCQR follows its own quantile-regression training and canonical calibration contract.

## 3. Pooled CP

### Role

Provide a marginal-calibration reference that shares information across all classes.

### Base model

Standard regression model in the main comparison.

### Base score

Must be the same score used by Mondrian CP and Proposed.

For the first regression prototype, a candidate score may be

\[
S(x,k)=|\widehat z(x)-e(k)|.
\]

This score is not yet frozen.

### Calibration

Pool calibration scores across classes to form a common conformal threshold.

### Interpretation

Pooled calibration uses more calibration samples but does not generally provide the target per-class guarantee.

### Exact rule

The exact finite-sample pooled split-conformal quantile convention should be specified in code/tests before canonical reporting.

## 4. Mondrian CP

### Role

Primary control baseline for the proposed calibration method.

### Base model

Same standard regression checkpoint as Pooled CP and Proposed.

### Base score

Exactly the same candidate-wise score as Pooled CP and Proposed.

### Calibration

Calibrate each true class independently using only calibration samples with that label.

### Target property

Under the appropriate within-class exchangeability assumptions and exact split-conformal rank rule, this serves as the class-conditional validity reference point.

### Importance

This is the most important baseline for attributing any efficiency improvement to ordinal-aware calibration rather than to a different predictor or score.

## 5. LAC

### Role

Standard classification conformal baseline.

### Base model

Softmax probabilistic classifier.

### Standard score form

The commonly used LAC nonconformity score is

\[
S(x,y)=1-\widehat p_y(x).
\]

The exact finite-sample calibration convention must be verified and implemented consistently.

## 6. APS

### Role

Adaptive classification conformal baseline based on sorted class probabilities and cumulative probability mass.

### Base model

Same Softmax classifier as LAC where applicable.

### Implementation requirement

The exact APS score, randomization convention if any, finite-sample quantile rule, and prediction-set construction must be verified from the canonical source before implementation.

Do not define APS from memory in the final experiment contract.

## 7. Min-CPS

### Role

Ordinal conformal baseline focused on efficient contiguous or minimum-length ordinal prediction sets.

### Base model

Current plan: use the shared Softmax classifier if consistent with the published method.

### Implementation requirement

Before canonical experiments, verify:

- required model outputs;
- score definition;
- interval/set construction;
- calibration rule;
- coverage target;
- tie handling;
- whether any model-specific assumptions are required.

The exact rule is intentionally not reproduced here until verified against the source.

## 8. RPS-CP

### Role

Ordinal-aware score baseline.

It is especially useful for testing whether an ordinal-aware score alone can explain gains that might otherwise be attributed to ordinal-aware calibration.

### Base model

Current plan: shared Softmax classifier.

### Implementation requirement

Verify the exact Ranked Probability Score based conformal construction against the canonical source before implementation.

The experiment should distinguish:

\[
	ext{ordinal-aware score + ordinary calibration}
\]

from

\[
	ext{shared generic score + ordinal-aware calibration}.
\]

## 9. OCQR

### Role

Quantile-regression-based predecessor and secondary comparison.

OCQR is currently unpublished and should not be presented as established peer-reviewed prior art.

### Base model

Quantile-regression model.

### Canonical behavior

Use the OCQR v0.3 contract and theory from the existing project rather than re-defining OCQR loosely in this repository.

The canonical OCQR method includes:

- fixed numeric target representation;
- lower and upper quantile regression;
- crossing correction;
- CQR nonconformity score;
- true-label class-wise Mondrian calibration;
- exact augmented conformal order statistic;
- candidate-specific class correction;
- numeric-bin intersection;
- conservative empty-set fallback;
- ordinal hull.

### Checkpoint reuse

Existing OCQR quantile checkpoints may be reused for RetinaMNIST, UTKFace, and Solar flare if the current split assignments and preprocessing match.

The new repository should rerun the evaluation rather than import old final metrics.

## 10. Proposed

The proposed method is defined only by `proposed_method.md`.

Do not infer its rule from experimental code.

Until the method is finalized, label all implementations as exploratory variants.

## 11. Fair comparison requirements

For every baseline:

- use the same train/validation/calibration/test assignment where method requirements allow;
- avoid test-based model or hyperparameter selection;
- record the trained checkpoint;
- use the same target \(lpha\);
- report per-class calibration support;
- use a common evaluation implementation where possible;
- record whether the method targets marginal, class-conditional, or another form of coverage;
- record whether its prediction set is necessarily contiguous.

## 12. Baseline verification checklist

Before promoting a baseline to canonical status, record:

- original paper/reference;
- official implementation if available;
- exact score;
- exact conformal quantile/rank convention;
- calibration population;
- tie handling;
- randomization;
- set-construction rule;
- post-processing;
- stated theoretical guarantee;
- any differences between our implementation and the source.

This document should be updated with verified formulas as each baseline implementation is completed.
