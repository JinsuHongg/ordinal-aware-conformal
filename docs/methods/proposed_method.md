# Proposed Method Contract

**Status:** Pre-specification / method not yet finalized
**Canonical method version:** TBD

This document will become the normative implementation contract for the proposed ordinal-aware class-conditional conformal method.

At present, only the interface, target guarantee, and design constraints are frozen.

No specific cross-class information-sharing rule has yet been accepted.

## 1. Intended scope

The method should be model-agnostic at the conformal-calibration level.

A generic fitted predictor should provide a candidate-wise nonconformity score

\[
S(x,k),
\qquad
k\in\{0,\ldots,K-1\}.
\]

The conformal method should convert these scores and a calibration sample into an ordinal prediction set

\[
C(x)\subseteq\{0,\ldots,K-1\}.
\]

## 2. Intended target guarantee

The primary target is finite-sample class-conditional coverage:

\[
\Pr\{Y\in C(X)\mid Y=k\}\ge1-lpha
\qquad
	ext{for every class }k.
\]

A final canonical method must state exactly:

- the conditioning assumptions;
- the exchangeability assumptions;
- what parts of the fitted procedure are frozen before calibration;
- the exact finite-sample calibration rule;
- how ties and insufficient support are handled.

## 3. Predictor interface

The conformal method should not require a specific training loss.

Candidate predictive model families may include:

- standard regression;
- quantile regression;
- probabilistic classification;
- ordinal regression.

The final validity theorem should ideally depend on the score and calibration construction rather than on how the predictor was trained.

## 4. Candidate-wise score interface

The implementation should expose a function conceptually equivalent to

\[
S:\mathcal X	imes\mathcal Yightarrow\mathbb R.
\]

The score for candidate class \(k\) must be computable without knowing the test true label.

The first prototype may use a standard regression model

\[
X\mapsto\widehat z(X)
\]

and a fixed ordinal embedding \(e(k)\), with a score such as

\[
S(x,k)=|\widehat z(x)-e(k)|.
\]

This score is exploratory and is not yet canonical.

Alternative scores may be investigated.

## 5. Calibration interface

The calibration rule should accept:

- calibration candidate scores;
- true ordinal labels;
- target miscoverage \(lpha\);
- fixed class ordering;
- any method-specific hyperparameters that were selected without calibration/test leakage.

The method should produce the information required to evaluate every candidate class at test time.

## 6. Ordinal information use

The final method must use the known ordering of classes in a nontrivial way.

The research objective is to improve on fully independent class-wise Mondrian calibration by exploiting relationships between nearby classes.

However, the following operations are not valid by assumption and must not be implemented as canonical behavior without proof:

- arbitrary pooling of neighboring class scores;
- smoothing class-specific conformal quantiles;
- averaging neighboring thresholds;
- replacing a low-support class threshold by another class threshold;
- selecting a neighborhood using realized calibration performance.

Any cross-class information-sharing rule must have a corresponding validity argument in `proposed_theory.md`.

## 7. Candidate prediction-set construction

The final rule is TBD.

The canonical specification must eventually define:

1. how a candidate class \(k\) is accepted or rejected;
2. whether acceptance uses a class-specific threshold or another calibrated object;
3. whether the raw set is required to be contiguous;
4. whether an ordinal hull or another post-processing rule is used;
5. how empty prediction sets are handled;
6. whether post-processing can only add labels.

No OCQR fallback or hull rule should be inherited automatically.

## 8. Exact finite-sample behavior

The final method contract must explicitly specify:

- conformal rank formula;
- tie handling;
- finite versus infinite thresholds;
- zero-support classes;
- nonfinite model outputs;
- deterministic versus randomized behavior;
- whether finite-sample validity is exact, conservative, or approximate.

No interpolated empirical quantile should be used in a method claiming an exact split-conformal guarantee unless the theory explicitly justifies it.

## 9. Comparison controls

For the main calibration comparison, Proposed should share the same:

- standard-regression checkpoint;
- score definition;

with Pooled CP and Mondrian CP.

This is required to isolate the effect of the calibration rule.

## 10. Data independence

Before accessing calibration outcomes for method calibration, freeze all choices that can affect the score or prediction set, including:

- trained model and checkpoint;
- target representation;
- ordinal embedding;
- score definition;
- class ordering;
- method hyperparameters;
- neighborhood structure if any;
- post-processing policy;
- evaluation definitions used for method selection.

Calibration performance must not be used to choose among proposed variants for the final test evaluation unless an additional valid selection split or nested procedure is explicitly designed.

Test data must not be used for method design.

## 11. Required metadata

The final implementation should record at least:

- method version;
- \(lpha\);
- score type;
- model/checkpoint identifier;
- per-class calibration counts;
- any class neighborhood or structural object;
- calibrated thresholds or equivalent objects;
- split-assignment identifier/hash;
- seed;
- configuration hash;
- code commit.

## 12. Required tests

Before a candidate method becomes canonical, tests should cover:

- score computation for every candidate class;
- true-label calibration grouping where applicable;
- exact conformal rank behavior;
- ties;
- zero-support classes;
- deterministic edge cases;
- nonfinite score handling;
- prediction-set construction;
- post-processing monotonicity if used;
- repeated synthetic finite-sample coverage.

## 13. Promotion criterion

An exploratory method should be promoted into a canonical version only after:

1. its exact mathematical rule is written here;
2. the corresponding validity statement is written in `proposed_theory.md`;
3. deterministic unit tests match the contract;
4. synthetic experiments support the expected coverage behavior;
5. no unresolved code/specification mismatch remains.
