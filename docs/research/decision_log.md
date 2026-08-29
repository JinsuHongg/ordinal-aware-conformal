# Decision Log

This file records research decisions that have been explicitly made.

It is not a substitute for the normative method or experiment specifications.

## 2026-08-24

### Research direction

The new project will focus on ordinal-aware class-conditional conformal calibration rather than defining the framework around quantile regression.

Desired abstraction:

\[
\text{generic predictor}
\rightarrow
S(x,k)
\rightarrow
\text{ordinal-aware class-conditional calibration}
\rightarrow
\text{ordinal prediction set}.
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

The frozen RetinaMNIST and UTKFace conference split assignments from the OCQR repository will be copied into this repository and verified by SHA-256 before reusing compatible classifier or quantile-regression checkpoints. Checkpoint binaries remain external artifacts and must be referenced with their source provenance. New standard-regression checkpoints are required for the shared Pooled CP, Mondrian CP, and Proposed comparison.

### Selective OCQR infrastructure reuse

The new repository will reuse only infrastructure compatible with its modular predictor-to-calibration design: immutable split assignments, checkpoint provenance validation, dataset adapters, image backbones, shared losses, evaluation artifacts, and Solar data-audit utilities.

Legacy OCQR experiment orchestration, cluster launch scripts, and mixed baseline wrappers are not canonical infrastructure for this project. OCQR will instead be ported as an isolated baseline that preserves its documented rule.

References to OCQR dataset-contract version `0.2.0` and method version `0.3.0` identify source artifacts only; they are not versions of the new proposed method, whose canonical version remains TBD.

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

## 2026-08-27

### Calibration-first scope

The conference-paper scope is calibration-first.

Ordinal-aware nonconformity-score design is deferred / optional so that the main comparison can isolate the calibration rule.

### Ordinal Cluster Calibration

Ordinal Cluster Calibration is treated as a baseline / reference inspired by clustered class-conditional conformal prediction.

It is not the proposed method because shared cluster-level calibration does not automatically provide individual per-class validity.

### First structured-threshold candidate

The first structured candidate used a class-only threshold

\[
\widetilde q_k=q(k;\widehat\theta),
\]

with the simplest form

\[
\widetilde q_k=\widehat\beta_0+\widehat\beta_1k.
\]

The theory-friendly proof-of-concept used an independent structured split and a final class-specific Mondrian residual correction.

### Hard-split additive \(q_k\): NO-GO

The synthetic study established the identity

\[
\widetilde q_k+
Q^{\mathrm{conf}}_{1-\alpha}
\{S_i-\widetilde q_k:Y_i=k\}
=
Q^{\mathrm{conf}}_{1-\alpha}
\{S_i:Y_i=k\}.
\]

Therefore the class-constant structured term cancels exactly.

The resulting construction is ordinary independent Mondrian calibration on the smaller final split.

Decision:

> **Do not continue class-constant additive structured \(q_k\) + final additive Mondrian residual correction as an efficiency method.**

The validity route remains straightforward, but the construction cannot produce a different final threshold and loses calibration support due to hard splitting.

The negative result is preserved in:

`docs/research/synthetic_linear_structured_qk_note.md`

### New primary research question

The new priority is:

> Can an ordinally structured, input-dependent threshold \(\widetilde q(x,k)\), learned before conformal calibration, improve efficiency while a full class-specific Mondrian residual calibration preserves finite-sample class-conditional validity?

### Input-dependent threshold

The next candidate should vary within class:

\[
\widetilde q(x,k).
\]

A simple conceptual form is

\[
\widetilde q(x,k)=a(x)+b(x)k,
\]

but the exact parameterization is not fixed.

### Preferred data-use strategy

Prefer learning \(\widetilde q(x,k)\) using training/validation information and freezing it before conformal calibration.

Then use the **entire calibration set** for class-specific residual calibration:

\[
R_i=S(X_i,Y_i)-\widetilde q(X_i,Y_i).
\]

This avoids the rare-class support loss caused by splitting calibration data.

### Candidate validity route

If the structured threshold and base score are frozen before calibration, treat

\[
R(x,k)=S(x,k)-\widetilde q(x,k)
\]

as the fixed transformed nonconformity score.

Investigate whether standard Mondrian split-conformal exchangeability directly gives the desired finite-sample class-conditional validity.

This theorem route must still be formally checked before being claimed.

### Cross-fitting and augmented conformalization

Cross-fitting is no longer the immediate next step.

Use it only if the structured model must learn from calibration-stage data or if the pre-calibration approach is insufficient.

Augmented/full-conformal-style calibration remains a deferred high-complexity option.

### Next go / no-go experiment

Before moving to the real benchmark suite, run a new controlled synthetic study comparing:

1. Independent Mondrian;
2. Ordinal Cluster Calibration;
3. input-dependent structured threshold + full class-specific Mondrian residual calibration.

Continue the direction only if the third method retains class-wise validity and shows a meaningful efficiency/stability gain over independent Mondrian.

### Input-dependent affine robustness: ordinal-specific NO-GO

The frozen input-dependent threshold study found useful generic conditional adaptation: approximately 6--7% smaller sets in the favorable generator and 3--5% under several misspecified or irregular generators. However, the ordinal versus non-ordinal conditional difference was at most approximately 0.006 labels. Decision: do not treat affine ordinal parameter sharing as the proposed method; its observed gain was attributable to conditioning on input difficulty.

### Adaptive ordinal borrowing v0.3

The new candidate is Assumption-Based Adaptive Ordinal Borrowing. It uses an independent structural sample to build simultaneous DKW certificates, freezes ordinal borrowing neighborhoods before final score values are observed, and pools i.i.d. final calibration scores with a certified miscoverage penalty. Direct KS comparisons only tighten ordinal-path certificates.

The candidate theorem is a high-probability structural-certificate guarantee, not exact distribution-free Mondrian validity. It requires ordinary i.i.d. population final calibration; fixed-count class-stratified final calibration is outside the current proof. The next action is theorem-aligned synthetic validation, not implementation promotion, real-data experiments, or a canonical `proposed_method.md`.

## 2026-08-28

### Structural-certificate sensitivity: certificate too conservative

The adaptive borrowing mechanism remains a GO. The current global DKW/KS
structural certificate is the bottleneck and should be refined without changing
the core borrowing construction.  In the frozen strong-smoothness synthetic
scenario with a 3% rare class, positive-radius borrowing was never admissible
through (n_{m str}=20{,}000), and became active only around 50,000
structural observations.  The next research step is to develop a sharper
structural certificate while preserving v0.3's ordinal borrowing mechanism.
