# Approximate Ordinal Class-Conditional Coverage v0.1

**Status:** exploratory theory skeleton and minimal synthetic validation
(2026-08-28).  This is not a canonical proposed method.

## 1. Motivation

Exact individual class-conditional recovery after cross-class borrowing has
proved impractical in the intended rare-class regime.  This candidate instead
makes the cost of pooling explicit: it uses ordinary pooled split conformal at
nominal \(1-\alpha\), and supplies an assumption-based lower bound of
\(1-\alpha-B_{k,h}\) for each target class.

## 2. Directional smoothness, mixture, and borrowing cost

For true-label score CDFs \(F_k(t)=\Pr\{S(X,k)\le t\mid Y=k\}\), assume

\[
D^+_{j\to k}:=\sup_t\{F_j(t)-F_k(t)\}\le L|j-k|.
\]

This is the required orientation: only an upward source CDF can make a pooled
threshold overstate target-class coverage.  For the ordinal ball
\(\mathcal G_k(h)\), let \(\rho_{kj}=\Pr(Y=j\mid Y\in\mathcal G_k(h))\).
Then, pointwise,

\[
\begin{aligned}
F_{k,h}^{\rm mix}(t)-F_k(t)
 &=\sum_{j\in\mathcal G_k(h)}\rho_{kj}\{F_j(t)-F_k(t)\}\\
 &\le\sum_j\rho_{kj}D^+_{j\to k}
 \le B_{k,h},
\end{aligned}
\]

where

\[
B_{k,h}=L\sum_{j\in\mathcal G_k(h)}\rho_{kj}|j-k|\le Lh.
\]

Thus \(F_k(t)\ge F_{k,h}^{\rm mix}(t)-B_{k,h}\).  The implementation uses
the weighted cost, not the looser \(Lh\) cost.

## 3. Pooled conformal rule and theorem skeleton

Freeze \(h\) independently of final calibration score values.  With an i.i.d.
population calibration draw, pool observations whose labels are in
\(\mathcal G_k(h)\).  For its random pooled count \(N_{k,h}\), use rank

\[
r_{k,h}=\lceil(N_{k,h}+1)(1-\alpha)\rceil,
\]

returning \(+\infty\) when the rank exceeds \(N_{k,h}\).

**Theorem (candidate).**  Under the directional smoothness assumption with a
fixed constant \(L\), i.i.d. population final calibration, and a neighborhood
fixed before final score values, the resulting threshold satisfies

\[
\Pr\{S(X_{n+1},k)\le q_{k,h}\mid Y_{n+1}=k\}
\ge1-\alpha-B_{k,h}.
\]

**Proof skeleton.** Condition first on the random pooled count \(N_{k,h}=n\).
The selected scores are i.i.d. from the *population* mixture
\(F_{k,h}^{\rm mix}\), not from realized class-count weights.  Exchangeability
with a new mixture score gives \(\mathbb E[F_{k,h}^{\rm mix}(q_{k,h})]\ge
1-\alpha\).  The pointwise transfer inequality above, evaluated at the random
threshold and then averaged, gives \(\mathbb E[F_k(q_{k,h})]\ge
1-\alpha-B_{k,h}\).  Average over \(N_{k,h}\).  This is exactly the
target-class inclusion probability.  Conditioning on the full vector of
within-ball class counts is neither needed nor appropriate for mixture-i.i.d.
exchangeability.

The theorem-level weights are population weights.  Estimated or realized
weights are a future operational/tuning issue; silently substituting them
would change the theorem.  This study uses known synthetic population
probabilities and the true minimal global directional \(L\).  It makes no
distribution-free claim when \(L\) is unknown.

## 4. Slack budget and radius rule

For a user slack \(\eta\), select the largest nested ordinal radius satisfying
\(B_{k,h}\le\eta\).  Therefore every selected class has the interpretable
floor \(1-\alpha-\eta\).  For example, \(\alpha=.10,\eta=.02\) gives .88.
No score values from final calibration select the radius.

## 5. Relation to existing work and novelty

Ding et al.'s [Class-Conditional Conformal Prediction with Many
Classes](https://papers.neurips.cc/paper_files/paper/2023/file/cb931eddd563f8d473c355518ce8601c-Paper-Conference.pdf)
already establishes the central approximate-coverage pattern: clustered
pooling has classwise coverage \(1-\alpha-\epsilon\) under an
almost-exchangeable, symmetric score-discrepancy condition.  It learns general
clusters on a separate split.

The present construction is a constrained specialization, not a new general
approximate-coverage theorem: fixed ordinal balls, directional rather than
symmetric discrepancy, a distance-Lipschitz assumption, and a
mixture-weighted class-specific cost/slack budget.  These distinctions may be
useful as an ordinal modelling formulation, but novelty remains uncertain and
cannot be claimed from this experiment.  Hierarchical/group fallback and
multivalid/group conditional CP address related sparse-group goals but do not
by themselves establish this directional ordinal transfer.  Ordinal CP work
focused on interval efficiency or marginal coverage is also a different
target.

## 6. Synthetic design

The existing direct normal-score generator was reused, with \(K=5\),
\(\alpha=.10\), \(\pi=(.30,.25,.22,.20,.03)\), i.i.d. final calibration sizes
\(200,400,800,1600\), and 100 repetitions.  Expected class-4 supports are
about 6, 12, 24, and 48.  The scenarios are strong smoothness, moderate
smoothness, local discontinuity, and no ordinal structure.  For each scenario,
the true minimal global directional \(L\) was calculated from its known
equal-variance normal distributions.  Slack values were \(0,.01,.02,.05\).

The methods are independent Mondrian, fixed radius-one ordinal pooling
(diagnostic), and weighted-cost approximate ordinal borrowing.  The generator
defines true-label scores only, so it reports exact classwise inclusion
coverage and threshold/support behavior, not prediction-set size.

## 7. Results

For rare class 4 in strong smoothness, the global directional constant is
\(L=.0099733\).  Weighted costs and selected radii are:

| \(\eta\) | selected \(h_4\) | \(B_{4,h}\) | guaranteed floor |
|---:|---:|---:|---:|
| .00 | 0 | .0000 | .9000 |
| .01 | 1 | .00867 | .89133 |
| .02 | 3 | .01980 | .88020 |
| .05 | 4 | .02583 | .87417 |

At \(n_{\rm cal}=200\), the corresponding pooled supports were 5.77, 46.39,
140.78, and 200.00; finite rates were 12%, 100%, 100%, and 100%; and mean
actual class-4 coverage was .994, .904, .896, and .892.  These are observed
coverage averages over calibration randomness; the guarantee floors are lower
bounds, not predictions of observed coverage.

For the 47 runs with \(n_4\le5\) in this same setting, Mondrian had 0% finite
thresholds.  Approximate borrowing had 100% finite thresholds at every
positive slack: \(\eta=.01,.02,.05\) gave mean pooled support 45.3, 141.3,
and 200.0, floors .891, .880, and .874, and observed coverage .898, .894,
and .891.

The assumed global \(L\) correctly blocks borrowing in moderate smoothness,
local discontinuity, and no-structure scenarios for all tested \(\eta\le.05\)
for class 4.  This is a coherent safety response, but exposes a limitation:
a sharp transition anywhere in the label chain can inflate a global \(L\) and
prevent otherwise local safe borrowing.  It is not a data-driven fallback.

The weighted cost materially improved admissibility relative to \(Lh\).  In
strong smoothness at \(\eta=.01\), it selected \(h_4=1\) with cost .00867,
whereas \(Lh=.00997\) would only permit radius one marginally; at
\(\eta=.02\), weighted selection permits \(h_4=3\) while worst-case selection
permits \(h_4=2\).  The oracle directional mixture costs closely matched the
weighted bound in the strong normal-location scenario (e.g., .00867243 versus
.00867243 at \(h_4=1\)); that tightness is generator-specific.

## 8. Limitations and research decision

The theorem is conditional on a specified structural assumption, not
distribution-free; this first study supplies the true synthetic \(L\).  The
global \(L\) is potentially too brittle for heterogeneous ordinal structure,
and Ding et al. substantially overlaps the approximate-coverage idea.  No
Ding-style clustered implementation was added because mapping its general
split-and-cluster algorithm to this score-only generator would add ambiguity
without a clean comparable hyperparameter contract.

**APPROXIMATE BORROWING PARTIAL GO**

The candidate theorem is valid and a 1% slack restores rare-class finite
thresholds in the strong-smoothness regime without structural-certificate
sample inflation.  However, useful borrowing disappears under the fixed global
directional-L assumption outside that favorable regime, and novelty relative
to Ding et al. remains limited.  The next work should formalize the assumption
scope and comparative positioning before treating this as a method direction.
