# Guarded Local Structural Certificate v0.1

**Status:** exploratory theory skeleton and feasibility study; not a proposed method.

## 1. Motivation

The coverage transfer needs only the directional discrepancy. For
\(D_{j\to k}(I)=\sup_{t\in I}\{F_j(t)-F_k(t)\}\), nonnegative mixture weights give

\[
F_{k,h}^{\rm mix}(t)-F_k(t)
=\sum_j\rho_{kj}\{F_j(t)-F_k(t)\}
\le\max_jD_{j\to k}(I),\quad t\in I.
\]

Thus a directional certificate on a protected interval is sufficient.

## 2. Guarded construction

Freeze an interval \(I_{k,h}\) and error \(\epsilon_{k,h}^{\rm loc}\) from structural data. For realized pooled support \(N\), form

\[
r=\lceil(N+1)(1-\alpha+\epsilon_{k,h}^{\rm loc})\rceil
\]

and let \(T\) be the corresponding pooled order statistic. Define

\[
q=\begin{cases}T,&T\in I_{k,h},\\+\infty,&T\notin I_{k,h}.
\end{cases}
\]

An inadmissible error or rank also returns \(+\infty\).

## 3. Coverage proof audit

**GUARD THEORY GO.** Condition on a valid structural event, frozen neighborhood, interval, and error, then condition on the random pooled count. The pooled calibration scores and fresh mixture score are i.i.d., so ordinary rank validity gives

\[
\mathbb E[F_{k,h}^{\rm mix}(T)]\ge1-\alpha+\epsilon_{k,h}^{\rm loc}.
\]

Do not condition on \(A=\{T\in I\}\). Instead, pointwise,

\[
F_k(q)\ge F_{k,h}^{\rm mix}(T)-\epsilon_{k,h}^{\rm loc}.
\]

On \(A\), use the local transfer inequality. On \(A^c\), \(q=+\infty\) and \(F_k(q)=1\), which is at least the right side. Taking expectations gives target-class coverage at least \(1-\alpha\), then averaging over random pooled support completes the existing v0.3 proof pattern. The monotone guard does not require conditional exchangeability on \(A\).

### Theorem skeleton

With probability at least \(1-\delta_{\rm str}\) over structural data, suppose every selected ordinal neighborhood has a frozen interval and directional transfer bound on that interval. For i.i.d. population final calibration, the guarded rank rule above has class-conditional coverage at least \(1-\alpha\), conditional on the structural sample. This retains the current v0.3 i.i.d.-final-calibration and random-pooled-count requirements.

## 4. Interval-selection validity

Architecture A was used. The pre-specified family consists of probability floors \(.70,.80,.85,.90\). Operational intervals are

\[
I_p=[\widehat Q^{\rm str}_{\rm mix}(p),\infty).
\]

Their endpoints are structural pooled empirical quantiles, not synthetic-tuned score values. Reeve's selected band is uniform over all score values, so it is also valid for every structural-data-measurable endpoint and all four candidate intervals; no extra interval union penalty is needed. Architecture B is unnecessary for this uniform-band construction, but would be required for a non-uniform local result without simultaneous interval control.

## 5. Local concentration theorem

The valid certificate uses Reeve (2024), Corollary 3. With \(\beta=2\),

\[
\eta_m(\delta)=\log(2\lceil\log_\beta m\rceil/\delta)/m,
\]

and, for \(q\in[0,1]\),

\[
U_\beta(q,\eta)=
\frac{3\beta(2q-1)(3\beta-1)\eta+
\sqrt{\eta\{18q(1-q)+\eta(3\beta-1)^2\}}}
{9+2\eta(3\beta-1)^2}.
\]

It gives a uniform one-sided lower CDF band
\(F(t)\ge\widehat F_m(t)-[U_\beta\{\widehat F_m(t),\eta_m\}\vee1/m]\). Applying it to \(-S\) supplies the other direction; a \(1/m\) jump correction is included. Allocate \(.05/(2K)=.005\) to each of the \(2K\) directional class events, yielding simultaneous structural probability at least .95. The directional local UCB maximizes empirical difference plus those two radii over the interval. [Reeve (2024)](https://arxiv.org/abs/2403.16651). Maillard's sharper exact fixed-probability-region result remains non-operational here because population interval endpoints are unknown. [Maillard (2021)](https://arxiv.org/abs/2012.10320).

## 6. Oracle-local diagnostic

For the frozen normal generator, global \(D_{3\to4}=.009973\). Exact mixture-tail intervals give:

| Floor | Interval lower endpoint | True local discrepancy |
| ---: | ---: | ---: |
| .70 | .62054 | .008734 |
| .80 | .68398 | .007053 |
| .85 | .72295 | .005885 |
| .90 | .77197 | .004439 |

The .90 region reduces the population discrepancy by 55%, so the oracle signal is material.

## 7. Valid local certificate results

One hundred structural repetitions were run at each specified size, with the frozen strong-smoothness generator. For the primary (3,4) pair and floor .90:

| \(n_{\rm str}\) | Mean \(m_4\) | Local UCB | DKW UCB | Direct-2S UCB | \(P(U^{\rm loc}<.1)\) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 500 | 14.59 | .543 | .836 | .788 | .00 |
| 1,000 | 29.58 | .432 | .578 | .540 | .00 |
| 2,000 | 61.13 | .308 | .414 | .387 | .00 |
| 5,000 | 148.94 | .178 | .264 | .247 | .00 |
| 10,000 | 300.98 | .108 | .184 | .172 | .25 |
| 20,000 | 601.06 | .066 | .134 | .125 | 1.00 |
| 50,000 | 1,499.00 | .036 | .084 | .078 | 1.00 |

At 20,000, local admissibility across floors .70, .80, .85, and .90 is .93, .96, .98, and 1.00.

## 8. Guard activation results

With independent i.i.d. final calibration of size 200, this is a feasibility diagnostic rather than a new coverage experiment.

| \(n_{\rm str}\) | Floor | Rank finite | Guard in region | Joint guarded feasibility | Oracle guarded feasibility |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10,000 | .90 | .00 | .00 | .00 | .74 |
| 20,000 | .70 | .63 | .63 | .63 | 1.00 |
| 20,000 | .80 | .74 | .74 | .74 | .99 |
| 20,000 | .85 | .79 | .79 | .79 | .95 |
| 20,000 | .90 | .90 | .88 | .88 | .74 |
| 50,000 | .70 | 1.00 | 1.00 | 1.00 | 1.00 |
| 50,000 | .90 | 1.00 | .95 | .95 | .74 |

The joint quantity is an empirical finite-threshold feasibility upper bound, not a new method's coverage estimate.

## 9. Structural sample requirement

The valid local certificate shifts common primary-pair admissibility from 50,000 to 20,000 structural observations. At 10,000, 17--25% of runs are locally admissible, but none has a finite safety-adjusted rank with naturally sparse final pooled support. Usable guarded feasibility is therefore around 20,000, not 5,000--10,000.

## 10. Comparison with DKW and direct two-sample KS

At 20,000, the .90 local UCB is .066 versus .134 for DKW and .125 for direct two-sample KS. Its guarded feasibility is .88, while prior global-certificate sensitivity runs had no admissible borrowing through 20,000. This is meaningful but incomplete.

## 11. Limitations

- Continuous normal true-label scores only.
- Reeve's uniform local band pays a \(\log\log m\)-type cost.
- Floors are feasibility candidates, not yet part of a frozen planning rule.
- No full class-conditional coverage experiment was run.

## 12. Research decision

**LOCAL FEASIBILITY PARTIAL GO**

The guard has a correct finite-sample proof skeleton and materially improves this feasibility study. However, useful guarded thresholds still require about 20,000 structural observations for the 3% class. Further constant-level empirical-CDF refinement is unlikely to reach 5,000--10,000; continue only if a sharper operational local band or a different framework can change that scaling.
