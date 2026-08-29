# Synthetic Adaptive Ordinal Borrowing v0.3

**Status:** completed exploratory candidate validation; not a canonical method or theorem

## Experimental question

Can candidate Adaptive Ordinal Borrowing v0.3 use actual neighboring
calibration observations to replace rare-class `+infinity` thresholds, while
its frozen DKW/KS certificate responds to ordinal structure and preserves the
target class-conditional inclusion probability?

## Generator

There are (K=5) classes, (alpha=0.10), and population probabilities


[
\pi=(0.30,0.25,0.22,0.20,0.03).

]

Class 4 is the rare class.  The direct true-label score generator is


[
S\mid Y=k\sim N(\mu_k,0.20^2).

]

No candidate-class scores were defined.  Thus this study evaluates thresholds
and true-label inclusion coverage only; prediction-set size and full-set rate
are intentionally not reported.  They would require a separately specified
candidate-score generator.

| Scenario | (mu_0,ldots,mu_4) |
| --- | --- |
| Strong smoothness | (0.500, 0.505, 0.510, 0.515, 0.520) |
| Moderate smoothness | (0.500, 0.535, 0.570, 0.605, 0.640) |
| Local discontinuity | (0.500, 0.505, 0.510, 0.800, 0.805) |
| No ordinal structure | (0.500, 1.100, 0.460, 1.200, 0.400) |

The exact normal-location KS distance was used for structural validation:


[
d_{jk}^{\rm true}=2\Phi\left(\frac{|\mu_j-\mu_k|}{2(0.20)}\right)-1.

]

## Sampling design

For every scenario, calibration size (n_{\rm cal}\in\{200,400,800,1600\}),
and Monte Carlo repetition, independently sampled:

- (D_{\rm str}): 50,000 i.i.d. population observations;
- (D_{\rm cal}): (n_{\rm cal}) i.i.d. population observations;
- (D_{\rm test}): 100,000 i.i.d. population observations.

There were 100 repetitions and seed 20260828.  In particular, final
calibration was i.i.d. from the population: no final calibration class counts
were fixed or stratified.  Expected class-4 supports were 6, 12, 24, and 48.

The unusually large structural sample is intentional.  With a 3% rare class,
the stipulated DKW radius is too large at structural sizes such as 500 or
2,000 to certify a sub-(\alpha) positive-radius neighborhood.

## Methods

The implementation follows the candidate v0.3 contract exactly:

1. Independent Mondrian uses the class-only rank
   (lceil(n_k+1)(1-alpha)\rceil), with `+infinity` when that rank exceeds
   (n_k).
2. Fixed ordinal pooling uses radius one and nominal (1-alpha).  It is a
   naive reference and has no individual class-conditional validity claim.
3. Adaptive approximate uses the structural-selected v0.3 radius, then
   nominal (1-alpha) pooled calibration.
4. Certified v0.3 uses the same frozen radius and rank
   (lceil(N_k^\star+1)(1-alpha+epsilon_k^\star)\rceil), with the required
   `+infinity` conventions.

The only candidate radii were (0,1,2).  DKW radii use
(delta_{\rm str}=0.05); direct, ordinal-path, and minimum certificates are
saved per repetition and pair.

## Results

The primary severe-sparsity condition is strong smoothness with
(n_{\rm cal}=200).  Mean class-4 support was 5.91.  The certified method
selected mean radius 1.50, with mean certified discrepancy 0.0818 and mean
pooled support 67.15.

| Method | Class-4 coverage | Class-4 finite threshold rate | Marginal coverage | Mean worst-class coverage |
| --- | ---: | ---: | ---: | ---: |
| Independent Mondrian | 0.989 | 0.10 | 0.913 | 0.866 |
| Fixed pooling (h=1) | 0.909 | 1.00 | 0.905 | 0.880 |
| Adaptive approximate | 0.904 | 0.98 | 0.910 | 0.865 |
| Certified v0.3 | 0.989 | 0.51 | 0.913 | 0.867 |

The classwise coverages in this condition (classes 0 through 4) were:

| Method | 0 | 1 | 2 | 3 | 4 |
| --- | ---: | ---: | ---: | ---: |
| Independent Mondrian | .909 | .912 | .911 | .911 | .989 |
| Fixed pooling (h=1) | .908 | .904 | .904 | .904 | .909 |
| Adaptive approximate | .909 | .912 | .911 | .911 | .904 |
| Certified v0.3 | .909 | .912 | .911 | .911 | .989 |

The apparent conservatism for rare-class Mondrian and certified v0.3 reflects
the nontrivial `+infinity` rate, which gives inclusion probability one.  The
mean worst-class statistic is the mean of a per-repetition minimum and is not
the same quantity as any classwise coverage guarantee.

The central support-bin comparison in the same strong-smoothness,
(n_{\rm cal}=200) condition is:

| Realized (n_4) | Repetitions | Mondrian finite rate | Certified v0.3 finite rate | Certified class-4 coverage | Certified mean (N_4^\star) |
| --- | ---: | ---: | ---: | ---: | ---: |
| (n_4\le5) | 43 | 0.000 | 0.419 | 0.991 | 63.7 |
| (6\le n_4\le10) | 54 | 0.130 | 0.574 | 0.988 | 69.4 |
| (11\le n_4\le20) | 3 | 1.000 | 0.667 | 0.985 | 77.3 |

Thus the event “Mondrian `+infinity` while certified v0.3 is finite” occurs
substantially often in the intended sparse, smooth regime.  The safety penalty
does remove some otherwise finite pooled thresholds: this is visible in the
0.98 approximate versus 0.51 certified finite rate.

Radius behavior for class 4 was as follows (mean selected radius / mean
certified discrepancy):

| Scenario | (n_{cal}=200) | 400 | 800 | 1600 |
| --- | --- | --- | --- | --- |
| Strong smoothness | 1.50 / .082 | .02 / .001 | 0 / 0 | 0 / 0 |
| Moderate smoothness | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Local discontinuity | .94 / .079 | 0 / 0 | 0 / 0 | 0 / 0 |
| No ordinal structure | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

This behavior is a property of the stated planning objective: once own-class
support is sufficient, (1/(N_{k,h}^{\rm plan}+1)) no longer offsets the
positive certificate cost, so it selects (h=0).  In the local-discontinuity
scenario, class 4 borrows locally from class 3 in the sparse regime; the sharp
2--3 boundary is not crossed.  In moderate and irregular scenarios the
certificate rejects positive-radius borrowing.

The fixed-pooling reference illustrates why the certificate matters.  At
(n_{\rm cal}=200), it has class-4 coverage 0.884 under moderate smoothness
and worst-class coverage 0.700 under no ordinal structure, whereas certified
v0.3 falls back to independent Mondrian in both cases.

## Structural validation

Across 1,600 structural samples and all 10 class pairs per sample, every true
KS distance was at most its final direct/path-minimum certificate: per-pair
coverage was 1.000 for every reported pair, simultaneous coverage was 1.000,
and there were zero structural certificate failures.  This is consistent with
the expected at-least-(1-delta_{\rm str}=0.95) high-probability certificate
and also demonstrates that the specified DKW construction is conservative in
this setting.  The detailed values are in
`pairwise_certificate_summary.csv` and `structural_certificate_summary.csv`.

## Interpretation

**Empirical observation.** In the strong-smoothness, naturally sparse regime,
certified v0.3 raises the rare-class finite-threshold rate from 0.10 to 0.51
while preserving highly conservative class-4 inclusion coverage.  It falls
back to (h=0) under moderate and irregular neighboring distributions.

**Theoretical expectation.** The observed conservatism is expected from the
DKW/KS upper bound and the rule that spends (epsilon_k^\star) from
(alpha).  This experiment supports the candidate theorem contract; it does
not establish the theorem.

**Possible implementation artifact.** The very large structural sample was
needed to make a positive radius certifiable for a 3% class.  A smaller
structural sample would be expected to suppress borrowing.  Also, direct
true-label score draws cannot assess actual prediction-set efficiency.

All raw outcomes and provenance are retained under
`outputs/synthetic_adaptive_ordinal_borrowing_v0_3/`.

## Decision

**GO**
