# Current Research State

**Last updated:** 2026-08-26  
**Branch:** `research/ordinal-calibration`  
**Status:** Active method exploration; calibration rule not yet fixed

## Current research question

Can known ordinal relationships be used to share calibration information across neighboring classes while preserving finite-sample individual class-conditional coverage?

The target remains

\[
\Pr\{Y \in C(X) \mid Y=k\} \ge 1-\alpha,
\qquad \forall k.
\]

## Current insight from Ding et al. (2023)

Ding et al. address sparse class-wise calibration by clustering classes with similar conformity-score behavior and using a shared cluster-level calibration threshold.

This is directly relevant because ordinal labels already provide a known notion of proximity:

\[
0 < 1 < 2 < \cdots < K-1.
\]

Unlike nominal multiclass problems, neighboring ordinal classes are known a priori and provide a natural structural prior for calibration.

## Ordinal clustering as a reference direction

A simple first construction is an **Ordinal Clustered CP** reference method.

For class \(k\), define an ordinal group or neighborhood, for example

\[
G_k(r)=\{j: |j-k| \le r\}.
\]

Calibration samples from the classes in \(G_k(r)\) can then be pooled to estimate a shared threshold.

This may reduce the low-support problem because the effective calibration size changes from roughly \(n_k\) to a neighborhood count such as \(n_{k-1}+n_k+n_{k+1}\).

However, **Ordinal Clustered CP is currently treated as a reference method / ablation, not as the final proposed method.**

## Main unresolved issue

Pooling classes into a group naturally supports a group- or cluster-level calibration statement, but this does not automatically imply the desired guarantee for every individual class.

Therefore the main theoretical problem is:

> How can calibration information be borrowed across ordinal neighbors while retaining rigorous individual class-conditional validity?

## Current methodological direction

The target framework should:

1. use known ordinal geometry rather than treating classes as unrelated nominal groups;
2. allow useful information sharing across nearby classes;
3. preserve finite-sample individual class-conditional coverage;
4. improve calibration efficiency relative to independent Mondrian calibration, especially for low-support classes.

The desired comparison is

\[
\text{Pooled CP}
\leftrightarrow
\text{Independent Mondrian CP}
\leftrightarrow
\text{Ordinal Clustered CP}
\leftrightarrow
\text{Proposed structured calibration}.
\]

## Overlapping ordinal neighborhoods

Disjoint clustering may impose artificial boundaries on an ordered label space.

A more natural structure may use overlapping neighborhoods such as

\[
G_0=\{0,1\},\;
G_1=\{0,1,2\},\;
G_2=\{1,2,3\},\;
G_3=\{2,3,4\},\;
G_4=\{3,4\}.
\]

This remains exploratory. No validity result has yet been established for a final prediction rule under these overlapping groups.

## Current relationship to OCQR

OCQR remains the predecessor and comparison method.

The scientific focus of the new project is the calibration layer:

\[
\text{generic predictor}
\rightarrow
S(x,k)
\rightarrow
\text{structured ordinal-aware calibration}
\rightarrow
\text{ordinal prediction set}.
\]

Pooled CP, Mondrian CP, and Proposed should continue to share the same regression predictor and the same base score in the main calibration comparison.

## Current theory priority

Before fixing a proposed calibration rule, study how structured or overlapping group information can be incorporated without invalidating per-class conformal guarantees.

Immediate questions:

1. What guarantee does simple Ordinal Clustered CP actually provide?
2. Under what conditions can cluster-level information help recover individual class validity?
3. Can overlapping ordinal groups be combined with class-specific calibration in a finite-sample valid way?
4. Can neighboring information regularize or select a valid class-specific threshold without weakening coverage?
5. What sample splitting or simultaneous-calibration construction would be required for adaptive neighborhood selection?

## Immediate next tasks

1. Read conditional/group conformal work with emphasis on overlapping groups and finite-sample guarantees.
2. Formalize a simple Ordinal Clustered CP reference method.
3. Write down exactly what guarantee Ordinal Clustered CP provides and what it does not provide.
4. Build a minimal synthetic setting where independent Mondrian becomes inefficient for rare classes.
5. Compare independent Mondrian and ordinal clustering under controlled neighbor similarity.
6. Explore candidate constructions that recover individual class validity while borrowing ordinal information.
7. Do not promote any cross-class borrowing rule into `proposed_method.md` until its validity argument is clear.

## Current decision boundary

The calibration method remains **unfixed**.

Use the branch `research/ordinal-calibration` for this exploration until the calibration rule and its theory are stable enough to promote into the canonical method contract and merge into `main`.
