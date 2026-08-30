# Novelty Stress Test: Local-Path Ordinal Borrowing

**Status:** oracle-information novelty falsification study (2026-08-28).
This does not define a new method or alter historical results.

## 1. Research question and fair setup

The question is whether local ordinal paths add scientific value beyond (i)
Ding-style contiguous clusters and (ii) unrestricted directional
score-distribution borrowing.  Every borrowing method receives true synthetic
population information; no result is attributable to an estimator or a
certificate.  All final calibration samples are i.i.d. population draws.

The compared rules are:

1. **Mondrian:** \(G_k=\{k\}\), zero borrowing cost.
2. **Ding-style contiguous:** choose an ordinal ball with cluster-wide
   symmetric penalty \(\max_{a,b\in G}D_{\rm KS}(F_a,F_b)\).  This is the
   faithful population analog of the all-within-cluster
   almost-exchangeability condition in Ding et al.'s imperfect-clustering
   result.
3. **Local path:** contiguous ordinal ball with
   \(B^{\rm path}_{k,G}=\sum_{j\in G}\rho_{kj}c(j\to k)\).
4. **Generic directional:** enumerate every subset \(G\ni k\), using
   \(B^{\rm direct}_{k,G}=\sum_{j\in G}\rho_{kj}D^+_{j\to k}\).

Each chooses maximum population mass subject to its applicable cost at most
\(\eta\), with deterministic ties.

## 2. Generic directional theorem

For any frozen arbitrary group \(G\ni k\),

\[
F_G^{\rm mix}(t)-F_k(t)
=\sum_{j\in G}\rho_{kj}\{F_j(t)-F_k(t)\}
\le\sum_{j\in G}\rho_{kj}D^+_{j\to k}=B^{\rm direct}_{k,G}.
\]

Conditioning on random pooled support, ordinary nominal split conformal gives
mixture coverage \(1-\alpha\).  The pointwise inequality then gives

\[
\Pr\{Y_{n+1}\in C(X_{n+1})\mid Y_{n+1}=k\}
\ge1-\alpha-B^{\rm direct}_{k,G}.
\]

This is the same guarantee type as local-path borrowing.  It is an oracle
benchmark, not an operational proposal.

## 3. Synthetic design

The existing four direct-normal-score scenarios were retained and one
adversarial scenario was added:

\[
(\mu_0,\ldots,\mu_4)=(.520,.90,.35,.40,.520),
\]

called `nonordinal_favorable_donor`.  It makes distant class 0 match rare
target class 4 while adjacent class 3 is mismatched.  All scenarios use
\(K=5\), \(\alpha=.10\), \(\pi=(.30,.25,.22,.20,.03)\), i.i.d. calibration
sizes \(200,400,800,1600\), 100 repetitions, and
\(\eta\in\{0,.005,.01,.02,.05\}\).

## 4. Support under slack

For rare target 4, strong smoothness gives the expected ordinal behavior.  At
\(\eta=.01\), every borrowing rule selects \(\{3,4\}\), mass .23.  At
\(\eta=.02\), Ding selects \(\{2,3,4\}\), mass .45, while both path and
generic directional select \(\{1,2,3,4\}\), mass .70.  Thus mixture-weighted
directional cost changes a decision relative to Ding's cluster-wide symmetric
maximum, but generic direct cost is effectively the same as the path cost in
this ordinal generator.

## 5. Local discontinuity

At class 4, \(n_{\rm cal}=200\), and \(\eta=.01\), Ding, path, and generic
all select \(\{3,4\}\), mass .23 / expected pooled support 46.  Their finite
rate is 100%; Mondrian is 17%.  Ding's penalty is .009973, and path/generic
cost is .008672.  The path is tighter but does not change the selected group.
It correctly avoids the 2--3 discontinuity, but so does the contiguous
Ding-style reference.  Therefore locality alone is not a distinctive
practical result in this scenario.

For the 46 local-discontinuity runs with \(n_4\le5\), all three borrowing
rules are 100% finite at \(\eta\ge.01\); Mondrian is 0%.  This important
rare-class gain is not ordinal-path-specific.

## 6. No structure and adversarial non-ordinal donor

In `no_ordinal_structure`, generic directional and local-path both choose
\(\{3,4\}\) for target 4 at zero slack because \(D^+_{3\to4}=0\): class 3
is one-sided conservative for target 4.  This is a stochastic-dominance fact,
not evidence of useful ordinal geometry.

In `nonordinal_favorable_donor`, Ding and path remain target-only through
\(\eta=.05\), mass .03, and have 0% finite rate on the \(n_4\le5\) subset.
Generic directional selects non-contiguous \(\{0,1,4\}\) at zero cost, mass
.58 / expected pooled support 116, and is finite in every repetition.  It
uses classes 0 and 1 because their score distributions are stochastically
conservative or identical relative to target 4.  This is an intentional
demonstration that the ordinal restriction can impose a large statistical
support cost when similarity disagrees with label geometry.

## 7. Contiguity, tightness, and directionality

For target 4, generic groups are contiguous ordinal balls in strong,
moderate, local-discontinuity, and no-structure settings across the grid; in
the adversarial donor setting they are non-contiguous and exclude nearer class
3 while including distant classes 0 and 1 at every slack.  With only five
classes, Spearman distance--directional-discrepancy diagnostics are descriptive
only: target 4 has correlation 1.0 in the monotone normal scenarios and
negative correlation (-.738) in the adversarial scenario.

For \(\{3,4\}\), path/direct/oracle costs coincide at .008672 in strong and
local-discontinuity settings; Ding's symmetric cluster penalty is .009973
(about 15% larger).  For strong \(\{1,2,3,4\}\), direct/path are about .0198,
oracle is .01980, and Ding is .02991 (about 1.51 times oracle).  Mixture
weighting changes decisions; directionality changes decisions for lower-index
targets whose downward donor paths are zero-cost.  For rare target 4,
directionality does not change the selected group because all donors lie to
its left and paths are upward.

## 8. Relation to Ding et al. and decision

Ding et al.'s [Class-Conditional Conformal Prediction with Many
Classes](https://papers.neurips.cc/paper_files/paper/2023/file/cb931eddd563f8d473c355518ce8601c-Paper-Conference.pdf)
already supplies approximate class-conditional coverage under a cluster-wide
score-discrepancy condition.  The present path formulation is a tighter,
target-specific contiguous-cluster specialization, but it does not show an
ordinal-specific support advantage over an oracle generic directional rule.

Answers to the novelty questions:

* **Q1:** Path exceeds Ding support at strong smoothness \(\eta=.02\), but not
  in the decisive local-discontinuity rare-class example.
* **Q2:** Yes; mixture weighting changes the strong-smoothness radius.
* **Q3:** Yes for lower-index targets, not for rare target 4 here.
* **Q4:** No measurable advantage over direct directional discrepancy in the
  genuinely ordinal scenarios tested.
* **Q5:** Generic borrowing matches path in ordinal scenarios and strongly
  dominates it when a non-ordinal favorable donor exists.
* **Q6:** Non-contiguous selection appears only in the deliberately
  non-ordinal donor scenario here.
* **Q7:** Known ordinal geometry is a regularization/interpretability
  restriction in this oracle study, not a measurable statistical advantage.
* **Q8:** At present, the candidate is best described as Ding-style
  approximate pooling specialized to contiguous ordinal neighborhoods with a
  directional, mixture-weighted penalty.

**ORDINAL NOVELTY NO-GO**

Per the stop rule, do not continue modifying path penalties or start edge
estimation.  The next research decision should reconsider whether ordinal
structure belongs in score/prediction-set construction or whether clustered
conformal is simply a baseline rather than a method branch to extend.
