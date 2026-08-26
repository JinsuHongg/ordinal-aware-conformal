# Research Direction

**Status:** Working research note  
**Project:** Ordinal-Aware Class-Conditional Conformal Prediction

## 1. Motivation

The current OCQR line combines an ordinal-aware predictive representation with true-label Mondrian calibration.

The predictive model exploits ordinal structure, but standard Mondrian calibration treats the ordered classes as independent groups and does not use their known relationships.

For class \(k\), ordinary class-wise calibration estimates its correction only from calibration observations with \(Y=k\). Neighboring classes such as \(k-1\) and \(k+1\) are ignored even when their score distributions may contain relevant information.

This issue is especially important under class imbalance or sparse calibration support.

The central limitation is:

> Independent class-wise calibration does not exploit known ordinal relationships and can be statistically inefficient for low-support classes.

## 2. Refined research question

> **Can known ordinal relationships be used to share calibration information across neighboring classes while preserving finite-sample individual class-conditional coverage?**

The target remains

\[
\Pr\{Y \in C(X)\mid Y=k\}\ge 1-\alpha,
\qquad \forall k.
\]

The distinction between group-level and individual class-level validity is central.

## 3. Insight from clustered class-conditional conformal prediction

Ding et al. (2023) motivate sharing calibration information by clustering classes with similar conformity-score behavior and using a shared cluster-level threshold.

This suggests a natural connection to ordinal classification.

In a nominal multiclass problem, class similarity may need to be estimated from data. In an ordinal problem, the label space already provides known geometry:

\[
0 < 1 < 2 < \cdots < K-1.
\]

This makes nearby-class grouping particularly natural and may avoid the need to learn class relationships from scratch.

However, directly clustering ordinal classes and sharing one threshold generally changes the conditioning event from an individual class to a group of classes. A valid group-level statement does not automatically imply valid coverage for each member class.

Therefore, simple ordinal clustering is useful but does not by itself solve the target problem.

## 4. Ordinal Clustered CP as a reference method

A simple ordinal adaptation of clustered calibration should be studied as a reference or ablation.

For example, define

\[
G_k(r)=\{j:|j-k|\le r\}
\]

or a set of fixed disjoint ordinal clusters.

Calibration scores within a group can be pooled to estimate a shared threshold.

This construction may substantially increase effective calibration support for rare classes.

However:

> **Ordinal Clustered CP is not currently the proposed method.**

Its role is to establish how much efficiency can be obtained from straightforward ordinal pooling and to expose the loss of individual class-wise validity that the final method must address.

## 5. Desired framework

The project should move beyond a quantile-regression-specific formulation.

The intended abstraction is

\[
\text{generic predictor}
\rightarrow
S(x,k)
\rightarrow
\text{structured ordinal-aware calibration}
\rightarrow
\text{ordinal prediction set}.
\]

The predictive model may be standard regression, quantile regression, probabilistic classification, ordinal regression, or another model that provides a valid candidate-wise score.

The new contribution should center on the conformal calibration layer rather than on one predictive loss or architecture.

## 6. Relationship to OCQR

OCQR remains an important predecessor and comparison method.

The new project should not be treated as a minor OCQR variant.

The scientific distinction is that the new framework investigates how ordinal relationships can be used during calibration itself.

## 7. Current preferred prototype

The first prototype should use a standard regression predictor

\[
X \mapsto \widehat z(X)
\]

with a candidate-wise ordinal score such as

\[
S(x,k)=|\widehat z(x)-e(k)|.
\]

This score is a starting point, not yet a frozen method definition.

The purpose is to isolate the calibration question using the same predictor and same score with different calibration rules.

## 8. Main technical challenge

Neighboring ordinal classes are related, but this does not automatically justify pooling their calibration scores.

Naive pooling, smoothing, averaging of class-specific quantiles, or threshold replacement can invalidate exact individual class-conditional coverage.

The central theoretical problem is:

> **How can ordinal information be borrowed across classes while retaining exact or rigorously controlled per-class validity?**

The final contribution should be stronger than ordinary class clustering by recovering the individual class guarantee.

## 9. Structured and overlapping ordinal neighborhoods

Disjoint clusters may impose artificial boundaries on an ordered label space.

A potentially more natural construction uses overlapping ordinal neighborhoods, for example

\[
G_0=\{0,1\},\quad
G_1=\{0,1,2\},\quad
G_2=\{1,2,3\},\quad
G_3=\{2,3,4\},\quad
G_4=\{3,4\}.
\]

This remains exploratory.

Any final use of overlapping groups must include a validity argument explaining how group information can be used without weakening the target class-wise guarantee.

## 10. Candidate research directions

### A. Ordinal-aware nonconformity score

Use ordinal distance or cumulative structure directly in the score.

### B. Ordinal-aware calibration

Allow neighboring classes to contribute information to the calibration of class \(k\).

### C. Structured or overlapping group calibration

Investigate fixed ordinal neighborhoods, nested groups, overlapping groups, hierarchical partitions, or distance-dependent taxonomies.

### D. Conservative or validity-preserving borrowing

Use neighboring information only through a construction that preserves or dominates a valid class-specific conformal rule.

### E. Joint score-and-calibration design

Design the score and calibration rule together if needed to achieve both efficiency and validity.

## 11. Theoretical target

### Minimum target

\[
\Pr\{Y\in C(X)\mid Y=k\}\ge1-\alpha
\quad
\text{for all }k.
\]

### Stronger target

Show an efficiency advantage over independent Mondrian calibration under interpretable assumptions, using quantities such as expected set size, ordinal span, calibration sample complexity, or rare-class efficiency.

## 12. Key reviewer questions

1. Why is this not ordinary Mondrian CP with a different score?
2. Why is this not simply clustered class-conditional conformal prediction with ordinal clusters?
3. What part of the method fundamentally uses ordinal structure?
4. Why does information sharing not invalidate individual class-conditional coverage?
5. What efficiency is gained relative to independent Mondrian calibration?
6. Does the method generalize beyond the original OCQR quantile model?

## 13. Experimental hypothesis

Ordinal-aware calibration should be most useful when calibration support is uneven, especially for rare or extreme classes, while maintaining the target individual class-wise coverage.

A particularly important comparison is independent Mondrian versus simple Ordinal Clustered CP versus the proposed method.

## 14. Current open problems

- What guarantee does simple Ordinal Clustered CP actually provide?
- How should neighboring information enter calibration?
- Can exact individual class-conditional validity be preserved?
- Can overlapping ordinal groups be used in a finite-sample valid construction?
- What assumptions are required for any efficiency result?
- What score interface is most general without weakening the contribution?
- Should the final framework require contiguous prediction sets, or should contiguity be separate from calibration?
- How should the method behave when ordinal smoothness assumptions are violated?

These questions should remain open until a valid construction is established.
