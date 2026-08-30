# Direct Two-Sample KS Structural Certificate: Theory Audit

**Status:** exploratory structural-certificate candidate; not a change to the
Adaptive Ordinal Borrowing v0.3 mechanism or a canonical method.

## Problem

For independent structural samples of sizes \(n=m_j\) and \(m=m_k\) from
continuous score CDFs \(F_j\) and \(F_k\), respectively, we require a
computable upper confidence bound on

\[
d(F_j,F_k)=\sup_t|F_j(t)-F_k(t)|
\]

from \(\widehat d_{jk}=d(\widehat F_j,\widehat F_k)\), without imposing
\(F_j=F_k\). A null two-sample KS critical value does not solve this problem.

## Existing v0.3 certificate

The current certificate is

\[
d(F_j,F_k)\le \widehat d_{jk}+e_j+e_k,
\qquad
e_a=\sqrt{\frac{\log(2K/\delta_{\rm str})}{2m_a}},
\]

with clipping at one and its documented zero-support fallback. It follows from
the reverse triangle inequality for the KS metric plus simultaneous one-sample
DKW bounds. It is valid, but pays independently for both empirical CDF errors,
which explains its large rare-class penalty.

## Candidate direct non-null inequality

The candidate source is Underwood and Paillusson, *One and two sample
Dvoretzky--Kiefer--Wolfowitz--Massart type inequalities for differing
underlying distributions*, arXiv:2409.18087v1 (2024), Proposition 2b,
equation (11). This is an arXiv preprint, not a peer-reviewed theorem source;
the implementation and any later formal claim must retain that qualification.

Let \(F_n\) and \(G_m\) be empirical CDFs of independent univariate i.i.d.
samples with **continuous** underlying CDFs \(F\) and \(G\). The source
explicitly permits \(F\ne G\), and permits unequal positive \(n,m\). For

\[
z\ge \sqrt{\frac{\log 2}{2}}(n^{-1/2}+m^{-1/2}),
\]

it states the two-sided, distribution-free inequality

\[
\Pr\!\left\{\left|d(F_n,G_m)-d(F,G)\right|>z\right\}
\le B_{n,m}(z):=\min\{1,A_{n,m}(z)+A_{m,n}(z)\},
\]

where

\[
\begin{aligned}
A_{n,m}(z)={}&
\left(1+\frac{n}{m+n}\right)2^{-m/n}
\exp\!\left[-2mz\!\left(z-\sqrt{\frac{\log4}{n}}\right)\right]\\
&+\sqrt{8\pi}\,z\frac{mn}{(m+n)^{3/2}}
\exp\!\left[-\frac{2mnz^2}{m+n}\right]
\operatorname{erf}\!\left(
\sqrt{\frac{2m^2z^2}{m+n}}-
\sqrt{\frac{(m+n)\log2}{n}}
\right).
\end{aligned}
\]

The proof invokes a one-sided DKWM ingredient and notes an additional
threshold \(z\ge1.0841n^{-2/3}\) (and symmetrically for \(m\)). The candidate
implementation enforces the maximum of all three stated lower-domain
thresholds. It does not use an asymptotic KS approximation or a null
distribution result.

The bound has no unknown population-distance parameter. Its source derives it
from the empirical-process deviation, so its constants depend only on
\((n,m,z)\), not on \(d(F,G)\). Its stated continuity assumption is material:
this audit validates the normal-score synthetic comparison, but it does not
silently extend the certificate to tied/discrete score distributions.

Primary source: [Underwood & Paillusson, arXiv:2409.18087](https://arxiv.org/abs/2409.18087).
For contrast, the classical finite two-sample DKW work concerns the null
setting and is not used as this non-null UCB: [Wei & Dudley (2012)](https://doi.org/10.1016/j.spl.2011.11.012).

## Inversion and UCB

For pairwise failure probability \(\delta_{jk}\), define

\[
r_{jk}^{\rm 2S}=\inf\{z\in[z_{\min},1]:B_{m_j,m_k}(z)\le\delta_{jk}\},
\]

where

\[
z_{\min}=\max\!\left\{
\sqrt{\frac{\log2}{2}}(m_j^{-1/2}+m_k^{-1/2}),
1.0841m_j^{-2/3},1.0841m_k^{-2/3}\right\}.
\]

The code evaluates this deterministic inversion by bisection. If either
structural count is zero, if \(z_{\min}\ge1\), or if no \(z\le1\) achieves
the requested failure probability, it returns radius one and therefore the
safe uninformative UCB. For supported pairs,

\[
U_{jk}^{\rm 2S,direct}=\min\{1,\widehat d_{jk}+r_{jk}^{\rm 2S}\}.
\]

The displayed two-sided inequality immediately implies the needed one-sided
event \(d(F_j,F_k)\le\widehat d_{jk}+r_{jk}^{\rm 2S}\) with probability at
least \(1-\delta_{jk}\). The ordinal path tightening remains valid because it
only applies the triangle inequality to simultaneous direct upper bounds.

## Multiple-pair correction

For \(K=5\), use Bonferroni across the ten unordered pairs:

\[
\delta_{jk}=\frac{\delta_{\rm str}}{\binom52}=0.005
\quad\text{when}\quad\delta_{\rm str}=0.05.
\]

The union bound gives simultaneous direct-pair coverage at least
\(1-\sum_{j<k}\delta_{jk}=0.95\). The path/minimum certificate preserves
coverage on that same event.

## Audit verdict

**THEORY VALID FOR EXPERIMENT**

This verdict is restricted to the source's stated setting: independent
structural samples from continuous univariate score distributions and the
enforced domain constraints. It is sufficient for the existing normal-score
synthetic generator. It is not yet sufficient to replace the v0.3 theorem
contract for arbitrary tied or discrete scores, and the arXiv status requires
formal review before any method claim.
