# Direct Class-Conditional Threshold Certification

Status: exploratory theory and minimal synthetic feasibility study (2026-08-28).
This is not a proposed method and does not change the v0.3 borrowing rule.

## 1. Motivation

The empirical-CDF structural-certificate family is not practical for a 3% rare
class at the desired structural sample sizes.  This study instead lets ordinal
borrowing propose a fixed threshold and asks an independent target-class sample
the directly relevant question: does that threshold cover at least 90% of the
target-class score distribution?

## 2. Guarantee target and candidate construction

For class 4, a proposal sample of size 200 pools classes \(\{3,4\}\).  For
each fixed, separately reported \(\tau\in\{.90,.93,.95,.97\}\), its candidate
is the order statistic with rank

\[
r_\tau=\lceil(N+1)\tau\rceil,
\]

and is \(+\infty\) when \(r_\tau>N\).  The proposal quantile is not itself a
validity claim.  An independent i.i.d. certification sample supplies the
class-4 scores.  No \(\tau\) is selected from the certification outcomes.

## 3. Exact binomial certification theorem

Set \(p_0=1-\alpha=.90\).  Given a proposal-fixed finite threshold \(q\), let
\(X=\sum_{i:Y_i=4}\mathbb{1}\{S_i\le q\}\) among \(m\) certification scores.
Conditional on the proposal data,

\[
X\sim\operatorname{Binomial}(m,p),\qquad p=F_4(q).
\]

The one-sided Clopper--Pearson lower bound is

\[
L(x,m;\delta)=
\begin{cases}
0,&x=0,\\
\operatorname{Beta}^{-1}(\delta;x,m-x+1),&x>0.
\end{cases}
\]

Accept when \(L(X,m;\delta_4)\ge p_0\), and otherwise return \(+\infty\).
The bound has \(\Pr_p\{p\ge L(X,m;\delta_4)\}\ge1-\delta_4\).  Thus, on
that event, an accepted threshold has \(F_4(q)\ge p_0\); a rejected threshold
has \(F_4(+\infty)=1\).  Conditioning on the independent proposal and then
averaging proves the same statement jointly over proposal and certification
data.  For all five classes, \(\delta_k=.05/5=.01\) and Bonferroni gives

\[
\Pr_{D_{\rm prop},D_{\rm cert}}\{\forall k:F_k(q_k)\ge .90\}\ge .95.
\]

This is **PAC/training-conditional class-conditional coverage**:
\(\Pr_{\rm data}[\Pr_{\rm test}(Y\in C(X)\mid Y=k,\mathrm{data})\ge.90]\ge.95\).
It is not ordinary Mondrian split-conformal validity, which averages the
coverage probability over calibration and test randomness.

Equivalently, acceptance rejects \(H_0:p\le p_0\) by the exact binomial tail.
The smallest accepted count is

\[
x_{\min}(m)=\min\{x:\Pr_{p_0}(\operatorname{Binomial}(m,p_0)\ge x)\le\delta_4\}.
\]

## 4. Literature and novelty audit

The certification mechanism is established, not novel.  Vovk's
[conditional-validity analysis](https://proceedings.mlr.press/v25/vovk12.html)
derives training-conditional/PAC inductive-conformal guarantees through exact
binomial conditions.  Park et al.'s [PAC confidence sets](https://trustml.github.io/docs/iclr20b.pdf)
use Clopper--Pearson binomial intervals.  The direct target-score order
statistic is also the standard one-sided nonparametric tolerance limit: such
limits are confidence bounds for population percentiles, as documented by
[NIST](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/tolelimi.htm).

For a finite family of candidate \(\tau\)'s selected using certification data,
the construction is an instance of [Learn then Test](https://arxiv.org/abs/2110.01052):
each threshold is a hyperparameter and its class-specific miscoverage is a
risk.  Valid selection then needs an LTT/multiple-testing procedure (or a
separate selection split); it was intentionally not implemented here.
[Risk-controlling prediction sets](https://arxiv.org/abs/2101.02703) provide a
broader finite-sample risk-control context, but their usual guarantee controls
expected risk rather than automatically supplying this classwise PAC event.

The only possible contribution here would be the *ordinal proposal policy plus
an equal-budget advantage* over a standard target-class PAC/tolerance
threshold.  The certification layer itself has no novelty claim.

## 5. Direct PAC baselines

For target scores \(S_{(1)}\le\cdots\le S_{(m)}\), the direct PAC baseline
uses \(S_{(x_{\min}(m))}\), or \(+\infty\) if no such rank exists.  It is the
least finite order statistic certified by the same exact rule, without ordinal
borrowing.  Two valid comparisons were run:

* **Split matched:** only target scores in \(D_{\rm cert}\).
* **Total-budget matched:** all target scores in \(D_{\rm prop}\cup D_{\rm cert}\).

The latter is decisive: it uses the same total population-label budget as the
proposal-plus-certification arm and does not discard proposal target scores.

## 6. Exact sample-complexity diagnostic

The full exact table is saved in
`outputs/synthetic_direct_threshold_certification/exact_binomial_acceptance_table.csv`.
Selected rows (entry is \(x_{\min};\Pr[\mathrm{accept}]\)) are:

| \(m\) | \(p=.90\) | \(p=.93\) | \(p=.95\) | \(p=.97\) |
|---:|---:|---:|---:|---:|
| 30 | infeasible | infeasible | infeasible | infeasible |
| 60 | 60; .0018 | 60; .0129 | 60; .0461 | 60; .1608 |
| 150 | 144; .0056 | 144; .0934 | 144; .3729 | 144; .8340 |
| 300 | 282; .0097 | 282; .2935 | 282; .8250 | 282; .9979 |
| 600 | 557; .0099 | 557; .6032 | 557; .9919 | 557; \(>.999999\) |

At the boundary \(p=.90\), acceptance probability is at most the 1% test
level (and exactly no finite decision is possible at \(m=30\)).  Practical
certification requires a real coverage margin: at \(m\approx150\), \(p=.95\)
accepts only 37%; at \(m\approx300\), it accepts 82%.

## 7. Synthetic design and results

The known Strong Ordinal Smoothness normal-score generator was reused:
\(K=5\), \(\pi=(.30,.25,.22,.20,.03)\), class-4 mean .520, common score
standard deviation .20, \(\alpha=.10\), and 100 independent repetitions.
The proposal sample has 200 population observations; certification sizes are
1,000, 2,000, 5,000, 10,000, and 20,000 (mean rare supports 30, 61, 150, 298,
and 601).

The pooled candidates did create margins, but only by choosing conservative
proposal quantiles.  Across certification settings, mean true candidate
coverage was respectively about .902--.909 (\(\tau=.90\)), .935--.940
(\(.93\)), .952--.959 (\(.95\)), and .974--.979 (\(.97\)).  The uncertified
candidate's target-valid rate was only .52--.67 at \(\tau=.90\), .83--.90 at
\(.93\), .93--.95 at \(.95\), and .97--1.00 at \(.97\); certification is
therefore doing essential validity work.

For the strongest candidate (\(\tau=.97\)), ordinal-plus-certification finite
rates were 1%, 54%, 86%, 90%, and 93% as \(n_{\rm cert}\) increased.  The
total-budget direct PAC threshold had rates 10%, 100%, 100%, 100%, and 100%.
At 5,000 certification observations the direct threshold's mean finite score
threshold was .856, versus .984 for accepted ordinal candidates; lower score
threshold is the relevant less-conservative direction here.  Thus the direct
PAC baseline had both a higher finite rate and less conservative finite
thresholds in this controlled generator.  The split-matched direct baseline
also reached 100% finite rate from 2,000 onward.

Independent Mondrian (using the total target support) was finite in every
replication, but its ordinary, not PAC, target coverage fluctuated around the
90% target (mean .90--.91; valid-run fraction .54--.66).  The PAC methods
returned \(+\infty\) on rejection, hence their realised output coverage is
near one; that is the cost of their high-probability guarantee, not an
efficiency gain.

No accepted ordinal candidate had true target coverage below .90 in these 500
Monte Carlo settings; this is a diagnostic, not a proof beyond the exact
Clopper--Pearson theorem.

## 8. Limitations and decision

This first study evaluates one fixed neighborhood, one smooth known generator,
and threshold magnitude rather than full prediction-set size.  It does not
select across \(\tau\), does not prove a new ordinal method, and cannot support
real-data claims.

**DIRECT CERTIFICATION NO-GO**

Exact class-specific certification is valid but standard PAC/tolerance/LTT
machinery.  In the required total-budget-matched comparison, direct
target-class PAC thresholding dominates the ordinal proposal arm on finite rate
and finite-threshold conservatism.  Per the stop rule, this split-and-certify
direction should not be extended with more calibration splits.
