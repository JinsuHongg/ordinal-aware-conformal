# Local-Path Approximate Ordinal Borrowing v0.2

**Status:** oracle-structural theory refinement and synthetic validation
(2026-08-28).  This is an exploratory candidate, not a proposed method.

## 1. Motivation

v0.1's single directional Lipschitz constant \(L\) made a discontinuity
anywhere in the ordinal chain constrain every class.  v0.2 replaces it with
known directional adjacent-edge costs, so a path is charged only for the local
edges it traverses.

## 2. Directed edges, triangle inequality, and paths

Let \(D^+_{a\to b}=\sup_t\{F_a(t)-F_b(t)\}\).  Adjacent assumptions are

\[
D^+_{r\to r+1}\le\lambda_r^+,qquad
D^+_{r+1\to r}\le\lambda_r^-.
\]

They are intentionally asymmetric.  Since, for every \(t\),

\[
F_a(t)-F_c(t)=[F_a(t)-F_b(t)]+[F_b(t)-F_c(t)]
\le D^+_{a\to b}+D^+_{b\to c},
\]

taking a supremum proves
\(D^+_{a\to c}\le D^+_{a\to b}+D^+_{b\to c}\).  Hence define

\[
c(j\to k)=
\begin{cases}
\sum_{r=j}^{k-1}\lambda_r^+,&j<k,\\
0,&j=k,\\
\sum_{r=k}^{j-1}\lambda_r^-,&j>k.
\end{cases}
\]

The directional indexing follows the travel direction: upward labels use
\(\lambda^+\), downward labels use \(\lambda^-\).  Repeated triangle
inequalities give \(D^+_{j\to k}\le c(j\to k)\).

## 3. Mixture cost and approximate coverage theorem

For population mixture weights
\(\rho_{kj}=\Pr(Y=j\mid Y\in\mathcal G_k(h))\), set

\[
B^{\rm path}_{k,h}=\sum_{j\in\mathcal G_k(h)}\rho_{kj}c(j\to k).
\]

Then

\[
F^{\rm mix}_{k,h}(t)-F_k(t)
\le\sum_j\rho_{kj}D^+_{j\to k}
\le B^{\rm path}_{k,h},
\]

so \(F_k(t)\ge F^{\rm mix}_{k,h}(t)-B^{\rm path}_{k,h}\).

**Candidate theorem.** Under the stated directed-edge assumptions, a
neighborhood frozen before final score values, and ordinary i.i.d. population
final calibration, nominal pooled split conformal gives

\[
\Pr\{Y_{n+1}\in C(X_{n+1})\mid Y_{n+1}=k\}
\ge1-\alpha-B^{\rm path}_{k,h}.
\]

Condition first on the random pooled count.  The selected calibration scores
are i.i.d. from the population mixture, so the ordinary rank argument gives
\(\mathbb E[F^{\rm mix}_{k,h}(q)]\ge1-\alpha\).  Apply the pointwise
transfer at the random threshold and average over the pooled count.  This is
the same valid conditioning pattern as v0.1; it does not use realized
within-neighborhood mixture weights.

For slack \(\eta\), choose the population-neighborhood with maximum mass
subject to \(B^{\rm path}_{k,h}\le\eta\), with smaller-radius tie breaking.
The cost need not be monotone in radius: enlarging a ball changes all its
conditional mixture weights, so a newly added low-cost/high-mass class can
lower the weighted average.  Thus this explicit support objective is safer
than asserting that the largest admissible radius is always optimal.

If all directed edges are bounded by \(L\), then
\(c(j\to k)\le L|j-k|\), so v0.1's global-L cost upper-bounds the path cost.
v0.2 is therefore a local refinement of the same mixture-transfer theorem.

## 4. Synthetic setup

The exact four normal-score scenarios, \(K=5\), \(\alpha=.10\), population
probabilities \((.30,.25,.22,.20,.03)\), i.i.d. calibration sizes
\(200,400,800,1600\), 100 repetitions, and slacks
\((0,.005,.01,.02,.05)\) were used.  Edge costs are **oracle** population
quantities \(\lambda_r^+=D^+_{r\to r+1}\) and
\(\lambda_r^-=D^+_{r+1\to r}\).  They are neither estimated nor certified.

Comparisons are independent Mondrian, v0.1 global-L approximate borrowing,
and v0.2 local-path borrowing.  Oracle mixture discrepancy, a Ding-style
target-to-cluster worst-case symmetric KS penalty, and symmetrized edge paths
are diagnostics only.  The direct-score generator does not define complete
candidate-label scores, so results are true-label inclusion coverage and
threshold/support metrics, not prediction-set size.

## 5. Results

### Strong smoothness

v0.2 matches v0.1 exactly.  At class 4 and \(n_{\rm cal}=200\), both select
\(h=1\) at \(\eta=.01\), pool 46.39 observations, have cost .008672 and
floor .89133, are finite in every run, and have mean coverage .9039.  At
\(\eta=.02\), both select \(h=3\) and pool 140.78 observations.  This is the
required consistency check.

### Moderate smoothness

The local class-4 edge itself is too costly for the requested slack grid.
Neither v0.1 nor v0.2 borrows through \(\eta=.05\); this is an informative
negative result, not a tuning failure.

### Local discontinuity: central result

The oracle directed edges are

| edge | \(\lambda_r^+\) | \(\lambda_r^-\) |
|---|---:|---:|
| 0--1 | .00997 | 0 |
| 1--2 | .00997 | 0 |
| 2--3 | .53155 | 0 |
| 3--4 | .00997 | 0 |

Thus \(c(3\to4)=.00997\), \(c(2\to4)=.54152\), and
\(c(1\to4)=.55149\).  The sharp boundary is paid only by paths that cross
it.

At class 4 and \(n_{\rm cal}=200\), v0.1 selects \(h=0\) through
\(\eta=.05\): its global-L cost for radius one is .462.  v0.2 selects
\(h=1\) at \(\eta=.01\), pools 45.54 observations instead of 6.14, is finite
in 100% rather than 17% of repetitions, has path cost .008672/floor .89133,
and mean coverage .9042.  It does not cross the 2--3 discontinuity.

Among the 46 local-discontinuity repetitions with \(n_4\le5\), Mondrian and
v0.1 were finite in 0%; v0.2 at \(\eta\ge.01\) was finite in 100%, with mean
pooled support 44.83 and observed coverage .9025.

### No ordinal structure

v0.2 selects only class 3 for target class 4, even at \(\eta=0\).  This is
not an unsafe arbitrary borrowing event: in this generator class 3 has a
strictly larger normal-score mean than class 4, hence
\(D^+_{3\to4}=0\); pooling it is one-sided conservative for class 4.  It does
not expand beyond radius one because the next edge is expensive.  This
illustrates both the benefit and interpretation cost of a directional rather
than symmetric assumption.

## 6. Tightness and directionality

For local discontinuity, target 4/radius one, the oracle mixture cost is
.00867243 and the path cost is .00867243, while v0.1's global cost is .46222
and Ding-style worst-case symmetric KS is .0099733.  At radius two, the path
and oracle costs are about .26918 and .26702, respectively, whereas the
global cost is .75598.  Thus local paths remove the unrelated-boundary
inflation but do not evade an actually crossed boundary.

Symmetrizing edges changes selected radii substantially for lower-index target
classes in the monotone normal scenarios: costs that are zero in the safe
downward direction become positive.  For rare target class 4, source paths run
upward, so directed and symmetrized selection coincide.  Directionality is
therefore material for the full classwise rule but is not the source of the
class-4 discontinuity improvement; locality is.

## 7. Relation to Ding et al. and decision

Ding et al.'s [clustered conformal prediction](https://papers.neurips.cc/paper_files/paper/2023/file/cb931eddd563f8d473c355518ce8601c-Paper-Conference.pdf)
already establishes approximate class-conditional coverage under
almost-exchangeable clusters and a symmetric score discrepancy.  v0.2 is not
new approximate coverage.  Its possible distinct contribution is the known
ordinal path graph, directed edge composition, target-specific mixture
weighting, and a user slack budget.  For class 4/radius one in local
discontinuity the path penalty (.00867) is smaller than the Ding-style
cluster-wide symmetric penalty (.00997), but the difference is modest.  The
larger practical benefit comes from avoiding a global-L artifact, not from
beating the best cluster-wise bound by orders of magnitude.

**LOCAL-PATH PARTIAL GO**

The theorem is valid and the oracle local-path method solves the precise
unrelated-discontinuity failure of v0.1 with only a 1% slack.  It provides no
benefit in moderate smoothness at \(\eta\le.05\), and overlap with contiguous
clustered conformal remains substantial.  Do not estimate edges yet; first
formalize whether the ordinal/directional formulation offers enough distinct
scientific value beyond Ding-style contiguous clusters.
