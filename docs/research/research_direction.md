# Research Direction

**Status:** Working research note
**Project:** Ordinal-Aware Class-Conditional Conformal Prediction

## 1. Motivation

The current OCQR line combines an ordinal-aware predictive representation with true-label Mondrian calibration.

The predictive model exploits ordinal structure, but standard Mondrian calibration treats the ordered classes as independent groups and does not use their known relationships.

For class \(k\), ordinary class-wise calibration estimates its correction only from calibration observations with \(Y=k\). Neighboring classes such as \(k-1\) and \(k+1\) are ignored even when their score distributions may be more informative than those of distant classes.

This issue is especially important under class imbalance or sparse calibration support.

Independent class-wise calibration can lead to:

- high variance in class-specific corrections;
- conservative prediction sets;
- poor calibration-sample efficiency;
- unstable rare-class behavior;
- uninformative infinite corrections under exact finite-sample rules when class support is insufficient.

The central limitation is therefore:

> Independent class-wise calibration does not exploit known ordinal relationships and can be statistically inefficient for low-support classes.

## 2. Primary research question

> Can ordinal structure be incorporated into conformal calibration to improve sample efficiency while preserving finite-sample class-conditional coverage?

A more specific question is:

> Can information from neighboring ordinal classes be used to improve the statistical efficiency of class-wise calibration without sacrificing the target guarantee for every class?

The target property is

\[
\Pr\{Y \in C(X)\mid Y=k\}\ge 1-lpha,
\qquad orall k.
\]

## 3. Desired framework

The project should move beyond a quantile-regression-specific formulation.

The intended abstraction is

\[
	ext{generic predictor}
ightarrow
S(x,k)
ightarrow
	ext{ordinal-aware class-conditional calibration}
ightarrow
	ext{ordinal prediction set}.
\]

The predictive model may be:

- standard regression;
- quantile regression;
- probabilistic classification;
- ordinal regression;
- another model that provides a valid candidate-wise score.

The new contribution should center on the conformal calibration layer rather than on one predictive loss or architecture.

## 4. Relationship to OCQR

OCQR remains an important predecessor and comparison method.

OCQR can be summarized as:

\[
	ext{quantile regression}
+
	ext{true-label independent Mondrian calibration}
+
	ext{candidate-specific inversion}
+
	ext{ordinal post-processing}.
\]

The new project should not be treated as a minor OCQR variant.

The scientific distinction should be that the new framework investigates how ordinal relationships can be used during calibration itself.

OCQR may serve as:

- a comparison method;
- a motivating predecessor;
- a quantile-based special case;
- a source of reusable experimental infrastructure and checkpoints.

## 5. Current preferred prototype

The first prototype should use a standard regression predictor

\[
X \mapsto \widehat z(X)
\]

with a candidate-wise ordinal score such as

\[
S(x,k)=|\widehat z(x)-e(k)|,
\]

where \(e(k)\) is a fixed ordinal embedding.

This score is a starting point, not yet a frozen method definition.

The purpose of this prototype is to isolate the calibration question:

\[
	ext{same predictor}
+
	ext{same score}
+
	ext{different calibration rule}.
\]

## 6. Main technical challenge

Neighboring ordinal classes are related, but this does not automatically justify pooling their calibration scores.

Naive operations such as

- pooling neighboring classes;
- averaging class-specific quantiles;
- smoothing class-specific thresholds;
- replacing a rare-class threshold with a nearby class threshold;

can invalidate exact class-conditional coverage.

The central theoretical problem is therefore:

> How can ordinal information be borrowed across classes while retaining exact or rigorously controlled per-class validity?

## 7. Candidate research directions

These directions are exploratory and are not canonical method rules.

### A. Ordinal-aware nonconformity score

Use ordinal distance or cumulative structure directly in the score.

Potential benefit:
better use of label geometry.

Limitation:
a new score alone does not solve sparse class-wise calibration.

### B. Ordinal-aware calibration

Allow neighboring classes to contribute information to the calibration of class \(k\).

This is currently the main research direction.

The validity argument must determine exactly when and how such borrowing is permitted.

### C. Structured or hierarchical Mondrian calibration

Investigate ordinal neighborhoods, nested groups, hierarchical partitions, or distance-dependent taxonomies.

Examples to study include neighborhoods such as

\[
\{k-1,k,k+1\}.
\]

Any such construction must be analyzed for class-conditional validity.

### D. Joint score-and-calibration design

The score and calibration rule may need to be designed together if neither component alone provides both efficiency and validity.

## 8. Theoretical target

### Minimum target

Finite-sample class-conditional validity:

\[
\Pr\{Y\in C(X)\mid Y=k\}\ge1-lpha
\quad
	ext{for all }k.
\]

### Stronger target

Show an efficiency advantage over independent Mondrian calibration under interpretable assumptions.

Possible quantities include:

- expected prediction-set size;
- ordinal interval width or span;
- class-wise set size;
- calibration sample complexity;
- conservativeness of class-specific correction;
- rare-class efficiency.

The strongest result would show that ordinal information can be borrowed across neighboring classes while retaining exact or provably controlled class-wise coverage.

## 9. Key reviewer questions

The final method should answer:

1. Why is this not ordinary Mondrian CP with a different score?
2. What part of the method fundamentally uses ordinal structure?
3. Why does information sharing not invalidate class-conditional coverage?
4. What efficiency is gained relative to independent Mondrian calibration?
5. Does the method generalize beyond the original OCQR quantile model?

## 10. Experimental hypothesis

The main hypothesis is:

> Ordinal-aware calibration should be most useful when calibration support is uneven, especially for rare or extreme classes, while maintaining the target class-wise coverage.

Synthetic experiments should vary:

- ordinal smoothness;
- class imbalance;
- class-specific calibration support;
- adjacent-class separation;
- model misspecification;
- the degree to which neighboring class score distributions are actually related.

A strong method should also reveal when ordinal borrowing should not help.

## 11. Current open problems

- How should neighboring information enter calibration?
- Can exact class-conditional validity be preserved?
- What assumptions are required for any efficiency result?
- What score interface is most general without weakening the contribution?
- Should the final framework require contiguous prediction sets, or should contiguity be treated as a separate output constraint?
- How should the method behave when ordinal smoothness assumptions are violated?

These questions should remain open until a valid construction is established.
