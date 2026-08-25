# Proposed Method Theory

**Status:** Research scaffold / theorem not yet established
**Method version:** TBD

This document records the theoretical target and proof obligations for the proposed ordinal-aware calibration method.

It must not be read as claiming a theorem that has not yet been proved.

## 1. Setup

Let

\[
(X,Y)
\]

be an observation with ordinal label

\[
Y\in\mathcal Y=\{0,\ldots,K-1\}.
\]

Let a fitted predictive procedure define a candidate-wise score

\[
S(x,k).
\]

All predictive-model training, validation-based checkpoint selection, score design, structural hyperparameters, and method-selection choices must be frozen before canonical conformal calibration.

Let \(\mathcal F\) denote the information used to construct this frozen procedure.

The exact contents of \(\mathcal F\) must be specified once the proposed method is finalized.

## 2. Target theorem

The primary target is a finite-sample class-conditional statement of the form

\[
\Pr\{Y_{n+1}\in C(X_{n+1})
\mid
\mathcal F,Y_{n+1}=k\}
\ge1-lpha
\]

for every ordinal class \(k\).

A marginal label-conditional statement would then follow by averaging over the fitted procedure when justified.

## 3. Baseline validity reference point

Independent true-label Mondrian split conformal obtains class-wise validity by calibrating class \(k\) with exchangeable scores from the same class.

Conceptually, for class \(k\), the relevant calibration sequence and test score are exchangeable conditional on the frozen procedure and the test label.

This independent construction provides the reference validity argument that the proposed method must match or appropriately generalize.

## 4. Central theoretical obstacle

The proposed research seeks to use information from neighboring ordinal classes.

However, scores drawn from different labels are generally not exchangeable with the class-\(k\) test score conditional on \(Y_{n+1}=k\).

Therefore, simply adding neighboring-class scores to the class-\(k\) calibration sample does not inherit the standard Mondrian rank argument.

This is the core proof obstacle.

## 5. Invalidity risks to analyze

The theory should explicitly analyze why the following generic operations are not automatically valid:

- pooled neighboring-class calibration;
- smoothed class-specific thresholds;
- weighted empirical quantiles using other classes;
- data-dependent selection of ordinal neighborhoods;
- threshold shrinkage toward nearby classes.

A valid method may eventually use one of these ideas only if an additional construction or assumption restores the desired guarantee.

## 6. Candidate routes to validity

The following are research directions, not established results.

### 6.1 Conservative augmentation

Neighboring information may be used to choose a threshold only if the resulting threshold can be shown to dominate a valid class-specific conformal threshold in a direction that preserves coverage.

The efficiency implications would need separate analysis.

### 6.2 Hierarchical or nested calibration

A structured family of ordinal groups may allow multiple valid conformal statements to be combined.

The final candidate rule would need to prove that the class-specific event remains covered after any group selection or intersection/union operation.

### 6.3 Sample splitting for adaptive structure

One subset of data might choose a neighborhood or structural parameter while an independent calibration subset performs the final conformal calibration.

This may preserve validity at the cost of calibration efficiency.

### 6.4 Simultaneous or multiple-calibration construction

It may be possible to construct several valid candidate thresholds and combine them using a rule that preserves class-wise coverage.

Any multiplicity or selection effect must be accounted for.

### 6.5 Assumption-based borrowing

Efficiency results may require an explicit assumption linking neighboring class score distributions, such as stochastic ordering, smoothness, or bounded distributional change.

An assumption alone does not replace the finite-sample validity proof.

## 7. Required assumptions

The final theorem must state precisely which assumptions are needed.

Candidates include:

- independence of training/validation from calibration/test;
- within-class exchangeability;
- fixed ordinal class ordering;
- fixed score function conditional on \(\mathcal F\);
- any additional structural relationship between neighboring score distributions;
- independence required by any data-adaptive neighborhood selection.

Do not silently assume calibration/test exchangeability for chronological solar-flare experiments.

## 8. Efficiency target

A stronger theoretical result should compare the proposed method with independent Mondrian calibration.

Possible quantities include:

\[
\mathbb E[|C(X)|],
\]

expected ordinal span,

class-specific expected set size,

or required calibration support to achieve a finite informative threshold.

Potential efficiency assumptions should be stated separately from the assumptions required only for coverage validity.

## 9. Synthetic validation

Once a candidate theorem is proposed, the synthetic data generator should mirror its assumptions.

The simulation should test:

- exact or conservative per-class coverage;
- finite-sample behavior at small class counts;
- rare-class thresholds;
- regimes with strong neighbor similarity;
- regimes where neighboring distributions differ sharply;
- failure modes when structural assumptions are violated.

Empirical coverage is not a substitute for proof, but it should detect implementation errors and expose assumption sensitivity.

## 10. Proof checklist

Before claiming finite-sample class-conditional coverage, verify:

1. What objects are random after conditioning on \(\mathcal F\)?
2. Which calibration scores are exchangeable with the class-\(k\) test score?
3. Does the ordinal borrowing rule introduce data-dependent selection?
4. If so, is that selection independent of the final conformal ranks?
5. What is the exact finite-sample rank rule?
6. How are ties handled?
7. What happens for zero or very small class support?
8. Does any post-processing only add labels?
9. Is the theorem conditional on additional structural assumptions?
10. Does the implementation match every proof step?

## 11. Current theory status

No ordinal-aware cross-class calibration rule has yet been shown here to preserve the target class-conditional guarantee.

The current theoretical contribution is therefore an identified problem and proof target, not an established method theorem.
