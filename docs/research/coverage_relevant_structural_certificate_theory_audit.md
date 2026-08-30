# Coverage-Relevant One-Sided / Local Structural Certificate: Theory Audit

**Status:** theory audit only. This does not change Adaptive Ordinal Borrowing
v0.3, its final conformal rule, or any historical result.

## 1. Current bottleneck

The v0.3 global DKW/KS certificate is valid but required approximately
\(n_{\rm str}=50{,}000\) to make radius-one borrowing common for the 3% class.
The direct non-null two-sample KS refinement was also valid in the continuous
normal synthetic setting, but changed class-(3,4) admissibility only from
0.96 to 0.99 at 50,000. Thus the remaining issue is global, worst-score
control rather than the null-KS approximation.

## 2. Minimal discrepancy required for coverage transfer

For a source class \(j\) and target class \(k\), define

\[
D_{j\to k}:=\sup_t\{F_j(t)-F_k(t)\}.
\]

For \(F_{k,h}^{\rm mix}=\sum_{j\in\mathcal G_k(h)}\rho_{kj}F_j\), where
\(\rho_{kj}\ge0\) and \(\sum_j\rho_{kj}=1\), every \(t\) satisfies

\[
\begin{aligned}
F_{k,h}^{\rm mix}(t)-F_k(t)
 &=\sum_{j\in\mathcal G_k(h)}\rho_{kj}\{F_j(t)-F_k(t)\}\\
 &\le\sum_j\rho_{kj}D_{j\to k}
 \le\max_{j\in\mathcal G_k(h)}D_{j\to k}=:\epsilon_{k,h}^+.
\end{aligned}
\]

Hence

\[
F_k(t)\ge F_{k,h}^{\rm mix}(t)-\epsilon_{k,h}^+.
\]

This is exactly the inequality used in the mixture-to-class transfer. The
absolute value in KS is not algebraically necessary. It becomes a question of
how to certify the directional quantity before final calibration.

## 3. Global one-sided certificate

Writing \(\widehat F_a\) for structural empirical CDFs gives the exact
decomposition

\[
F_j(t)-F_k(t)=
\{F_j(t)-\widehat F_j(t)\}+
\{\widehat F_j(t)-\widehat F_k(t)\}+
\{\widehat F_k(t)-F_k(t)\}.
\]

Therefore

\[
D_{j\to k}\le\widehat D_{j\to k}+A_j^-+A_k^+,
\]

where \(\widehat D_{j\to k}=\sup_t(\widehat F_j-\widehat F_k)\),
\(A_j^-=\sup_t(F_j-\widehat F_j)\), and
\(A_k^+=\sup_t(\widehat F_k-F_k)\).

Massart's one-sided DKWM result gives, for a continuous CDF and
\(u\ge\sqrt{\log(2)/(2m)}\),

\[
\Pr\{\sup_t(\widehat F_m(t)-F(t))>u\}\le e^{-2mu^2}.
\]

The reverse direction has the same bound by applying the result to \(-X\)
(with the usual left-limit convention; the continuous normal synthetic scores
have no ties). Massart's original one-sided statement has this useful-range
restriction. Reeve's Theorem 1 removes a failure-probability restriction and
gives the sharper local statement below. Sources: [Massart (1990)](https://doi.org/10.1214/aop/1176990746) and [Reeve (2024), Theorem 1](https://arxiv.org/abs/2403.16651).

Allocate \(\delta_{a,+}=\delta_{a,-}=\delta_{\rm str}/(2K)\). On the
intersection of all \(2K\) directional events, which has probability at
least \(1-\delta_{\rm str}\),

\[
A_a^+,A_a^-\le
\sqrt{\frac{\log(2K/\delta_{\rm str})}{2m_a}}=e_a.
\]

Thus the simultaneous global one-sided certificate is

\[
U_{j\to k}^{\rm global+}=
\min\{1,\widehat D_{j\to k}+e_j+e_k\}.
\]

Every class is both a potential target and a potential source under
simultaneous classwise coverage (including the two boundary directions).
Consequently both \(A_a^+\) and \(A_a^-\) are needed for every class. There
is no valid multiplicity reduction from replacing all-pair absolute KS by
global directional control.

## 4. Does global one-sided control improve the simultaneous certificate?

**No, not in its concentration radii.** The \(2K\) one-sided union bound gives
exactly the existing \(\log(2K/\delta_{\rm str})\) term. It can only reduce
the empirical term from \(\widehat d_{jk}\) to \(\widehat D_{j\to k}\).

In the frozen strong-smoothness generator, \(\mu_3<\mu_4\) implies
\(F_3(t)\ge F_4(t)\) for all \(t\). For the critical source-to-target pair
\(3\to4\), the population directional discrepancy equals absolute KS, and
the empirical directional discrepancy is correspondingly not expected to
remove the bottleneck. A global one-sided certificate is therefore not an
implementation candidate.

## 5. Local DKW literature

Reeve (arXiv:2403.16651, Theorem 1) defines \(\varepsilon(n,\delta)=
\log(1/\delta)/n\) and \(\omega(p,\varepsilon)\) as the unique
\(\eta\in[0,1-p]\) solving

\[
\operatorname{kl}(p+\eta\|p)=\varepsilon.
\]

For any fixed interval \(I\subset\mathbb R\), it states

\[
\Pr\!\left\{
\sup_{t\in I}(\widehat F_n(t)-F(t))>
\sup_{t\in I}\omega(F(t),\varepsilon(n,\delta))
\right\}\le\delta.
\]

The result is finite-sample and one-sided. Its Corollary 3 is uniform over
all \(t\), variance-adaptive, and data-evaluable, but pays an additional
\(\log\log n\)-type factor through
\(\varepsilon_\beta(n,\delta)=\log(2\lceil\log_\beta n\rceil/\delta)/n\).
It supplies a simultaneous lower confidence band; applying it to \(-S\)
supplies the other directional deviation.

Maillard's exact local results give finite-\(n\) formulae for
\(\Pr\{\sup_{u\in[a,b]}(U_n(u)-u)>\varepsilon\}\) and the opposite
direction, for a uniform CDF and a fixed probability interval \([a,b]\).
They are numerically invertible. This is directly relevant only when the
probability interval is fixed independently of the sample. [Maillard (2021),
Theorems 3--4](https://arxiv.org/abs/2012.10320).

Bartl and Mendelson prove a related uniform variance-adaptive bound: for
absolute constants \(c_0,c_1\), \(\Delta\gtrsim\log\log(m)/m\), and every
\(t\) with \(F(t)\in[\Delta,1-\Delta]\),

\[
|\widehat F_m(t)-F(t)|\le
\sqrt{\Delta\min\{F(t),1-F(t)\}}
\]

with probability at least \(1-2e^{-c_1\Delta m}\). Its constants are not
ready for an exact implementation. [Bartl & Mendelson (2023)](https://arxiv.org/abs/2308.04757).

## 6. Random-threshold problem

The final pooled conformal threshold is an order statistic of final
calibration scores. Split-conformal rank validity gives an expectation/rank
statement for \(F_{\rm mix}(q)\); it does not imply deterministically that
\(q\) lies in a specified population-CDF range. Therefore a local band near
0.9 cannot simply be evaluated at the realized \(q\).

Moreover, if a score-dependent local error is used to choose the final rank,
then the rank is no longer frozen before final calibration scores. Standard
pooled conformal rank validity cannot be invoked without a new argument.

## 7. Candidate architectures

| Candidate | Quantity controlled | Uniform in score? | Handles random \(q\) now? | Extra split? | Finite-sample status | Main issue |
| --- | --- | --- | --- | --- | --- | --- |
| v0.3 global KS | \(\sup_t|F_j-F_k|\) | Yes | Yes | No | Valid candidate contract | Very high worst-score penalty |
| Direct two-sample KS | \(\sup_t|F_j-F_k|\) | Yes | Yes | No | Valid in continuous synthetic setting | Still global/high |
| Global one-sided | \(\sup_t(F_j-F_k)\) | Yes | Yes | No | Valid | Same simultaneous radii |
| L1 fixed score interval | directional discrepancy on \(I\) | On \(I\) | Only with \(q\in I\) guard | No | Potentially valid | Must predefine/guard \(I\) |
| L2 fixed probability region | directional discrepancy in a CDF range | In that range | No direct guarantee | No | Local theorem exists | \(q\)'s population location is random |
| L3 certification split | discrepancy at a pilot \(q\) | No | Not with one final split | Yes, likely two roles | Incomplete | Circular rank/error selection |
| finite calibration thresholds | discrepancy at order-statistic candidates | Finite set | Not with adaptive rank | Yes | Incomplete | Candidate/rank selection uses final scores |

### L1: guarded frozen interval

A valid route is conceptually available but not yet a fully specified method:
use Reeve's uniform variance-adaptive band on the structural sample, choose a
structural-data-measurable upper-score interval \(I_{k,h}\), and form a
**constant** \(\epsilon_{k,h}(I)\) by maximizing the directional structural
UCB over \(t\in I\) and sources \(j\). This is frozen before final
calibration. Use the ordinary conservative pooled rank with that fixed error.
If its order-statistic threshold is outside \(I\), return \(+\infty\).
On the structural event, every finite returned threshold is in \(I\), so the
existing mixture-to-class proof applies unchanged. The fallback is essential.

This avoids an extra split because Reeve's band is uniform in \(t\), allowing
the interval to be structural-data-measurable. It remains incomplete because
the interval-selection rule, its finite-rate cost, and an exact numerical
implementation of both CDF directions are not frozen.

### L2 and L3

A fixed probability interval is theoretically attractive but cannot assert
that the random final order statistic lies there. An independent certification
sample can evaluate discrepancy at a pilot threshold, but using the resulting
error to alter the same threshold's rank is circular. Enumerating final
calibration order statistics does not repair this: choosing the rank after
seeing those scores breaks the ordinary rank argument. A clean version would
need at least a pilot/calibration role to select a fixed rank and a separate
final conformal sample, or a new adaptive-rank theorem.

## 8. Back-of-the-envelope structural requirement

For the primary pair, use \(m_3\approx.20n_{\rm str}\),
\(m_4\approx.03n_{\rm str}\), \(D_{3\to4}^{\rm true}=.00997\), and
per-direction failure probability .005. The following is an **optimistic
pointwise KL-inversion calculation** at tail probability .9; it is not a
certificate for random \(q\).

| \(n_{\rm str}\) | Global one-sided lower-envelope | Ideal fixed-tail local | Uniform local proxy (Reeve, \(\beta=2\)) |
| ---: | ---: | ---: | ---: |
| 500 | .593 | .443 | .539 |
| 1,000 | .422 | .302 | .371 |
| 2,000 | .302 | .208 | .257 |
| 5,000 | .194 | .130 | .162 |
| 10,000 | .140 | .093 | .115 |
| 20,000 | .102 | .068 | .083 |
| 50,000 | .068 | .046 | .056 |

The global column has no directional benefit for (3,4). An ideal fixed-tail
band could plausibly cross .10 around 10,000, but the currently uniform,
data-evaluable local proxy crosses only near 20,000. These estimates ignore
the empirical directional discrepancy and interval/fallback losses, so they
are optimistic. They do not support claiming likely activation at 5,000.

## 9. Recommended next construction

The single recommended next candidate is the **guarded frozen upper-score
interval (L1)**: use two-direction Reeve uniform local bands on structural
data, a pre-registered structural interval rule, a constant interval-maximal
error frozen before final calibration, and a \(+\infty\) fallback when the
final order statistic lies outside the interval. It preserves the ordinal
neighborhood and ordinary final conformal rank rule.

Before implementation, its interval rule and finite-rate trade-off must be
specified without using final-calibration or test outcomes. That is a genuine
new construction, not a replacement of \(\epsilon\) by a local value at a
random threshold.

## 10. Research decision

**LOCAL CERTIFICATE NEEDS NEW SPLIT/CONSTRUCTION**

Global one-sided control is an analytical negative result. Local theory is
promising, but no currently frozen construction both exploits it and preserves
the final rank argument without an interval guard, a fallback, or additional
data roles. No certificate code or synthetic experiment should be added until
that construction is formally specified.
