# Structural Sample-Size Sensitivity for Adaptive Ordinal Borrowing v0.3

**Status:** completed diagnostic experiment; v0.3 remains a candidate, not a canonical method or theorem

## Experimental question

This experiment holds the strong-smoothness generator and final calibration
regime from the preceding v0.3 proof-of-concept fixed and varies only the
structural sample size.  It asks when the specified global DKW/KS certificate
permits useful class-4 borrowing for a 3% population class.

## Frozen setup

The generator is unchanged: (K=5), (alpha=0.10),
(delta_{m str}=0.05),
(pi=(.30,.25,.22,.20,.03)), and


[
Smid Y=ksim N(mu_k,.20^2),qquad
(\mu_0,ldots,\mu_4)=(.500,.505,.510,.515,.520).

]

Class 4 is rare.  The final calibration size is fixed at 200 and test size is
100,000.  For every one of 100 repetitions, the final calibration and test
samples are independent i.i.d. population samples.  They are paired across
structural sizes within each repetition, while each structural sample is an
independent i.i.d. draw.  No final-calibration counts were fixed or
stratified.

The structural-size grid is
(n_{m str}in\{500,1000,2000,5000,10000,20000,50000\}).  The only methods
are independent Mondrian, adaptive approximate borrowing, and certified v0.3.
The DKW rule, direct/path certificates, candidate radii ({0,1,2}),
planning objective, and certified rank are unchanged.

## Main result

| (n_{m str}) | Mean (m_4) | Mean (e_4) | Mean (epsilon_4^star) | Mean (h_4^star) | (P(h_4^star=0)) | (P(h_4^star=1)) | (P(h_4^star=2)) | Mondrian finite | Approx. finite | Certified finite | Mondrian cov. | Approx. cov. | Certified cov. | Mean (N_4^star) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 500 | 14.6 | .439 | .000 | 0.00 | 1.00 | .00 | .00 | .18 | .18 | .18 | .987 | .987 | .987 | 6.0 |
| 1,000 | 29.6 | .302 | .000 | 0.00 | 1.00 | .00 | .00 | .18 | .18 | .18 | .987 | .987 | .987 | 6.0 |
| 2,000 | 61.1 | .210 | .000 | 0.00 | 1.00 | .00 | .00 | .18 | .18 | .18 | .987 | .987 | .987 | 6.0 |
| 5,000 | 148.9 | .134 | .000 | 0.00 | 1.00 | .00 | .00 | .18 | .18 | .18 | .987 | .987 | .987 | 6.0 |
| 10,000 | 301.0 | .094 | .000 | 0.00 | 1.00 | .00 | .00 | .18 | .18 | .18 | .987 | .987 | .987 | 6.0 |
| 20,000 | 601.1 | .066 | .000 | 0.00 | 1.00 | .00 | .00 | .18 | .18 | .18 | .987 | .987 | .987 | 6.0 |
| 50,000 | 1,499.0 | .042 | .082 | 1.51 | .04 | .41 | .55 | .18 | .97 | .47 | .987 | .905 | .992 | 69.7 |

Here (epsilon_4^star=0) through 20,000 because the frozen selector falls
back to (h=0), for which the stipulated discrepancy is exactly zero.  This
is safe fallback, not evidence that the positive-radius certificate is tight.
At every size through 20,000, the radius-one admissibility rate
(P{epsilon_{4,1}^U<.10}) was zero.  At 50,000 it was 0.96; radius two was
admissible in 0.55 of repetitions.

The 50,000-point selected (epsilon_4^star) distribution had median .085,
10th percentile .074, and 90th percentile .095.  Its mean
(alpha-epsilon_4^star) was .018, explaining why the certified finite rate
(.47) is far below the approximate finite rate (.97) even after pooling.

## Rare final-calibration support

The important (n_4le5) group contains 43 repetitions.  For every structural
size from 500 through 20,000, both Mondrian and certified v0.3 had finite rate
0.000 because v0.3 selected (h=0).  At 50,000, Mondrian remained at 0.000,
whereas certified v0.3 was finite in 0.488 of these runs, with coverage .993,
mean (h_4^star=1.56), and mean (epsilon_4^star=.085).

For (6le n_4le10) at 50,000 (53 repetitions), finite rates were .264 for
Mondrian and .453 for certified v0.3; certified coverage was .992.  The four
runs with (n_4>10) are too few for a stable bin-level comparison.

## Structural certificate coverage

For each structural size, all 100 structural draws simultaneously covered all
10 known pairwise KS distances.  Thus pairwise coverage, simultaneous
coverage, and the observed failure count were respectively 1.000, 1.000, and
0 at every grid point.  This is compatible with the intended at-least-.95
simultaneous structural coverage; it is not a requirement that future runs
have no failures.

## Answers to the diagnostic questions

1. (P(h_4^star>0)) becomes materially positive only around
   (n_{m str}=50{,}000): it is .96 there and 0 through 20,000.
2. Certified finite-rate improvement begins at the same point.  It is zero
   through 20,000 and .29 at 50,000 (.47 minus .18).
3. The DKW certificate becomes useful only near mean (m_4approx1{,}500) in
   this 3% class.  Mean (m_4approx601) at 20,000 remains insufficient.
4. Certified class-4 coverage remains conservative across every structural
   size (.987 through .992).  Before borrowing is admissible it exactly
   reduces to independent Mondrian.
5. The primary bottleneck is insufficient structural rare-class support,
   amplified by the global DKW radius and then by conformal rank granularity.
   True score-distribution mismatch is not the bottleneck in this frozen
   strong-smoothness scenario.
6. For a 3% class, a structural split of roughly 50,000 observations merely
   to activate this certificate is not practically plausible for many intended
   datasets.  The current global DKW/KS certificate is therefore not practical
   as the structural component of this method at realistic rare-class sizes.

The outputs include raw class-4 repetition records, candidate-radius
admissibility, rare-support summaries, pairwise certificate records, and four
SVG sensitivity plots under
`outputs/synthetic_structural_sample_sensitivity_v0_3/`.

## Decision

**CERTIFICATE TOO CONSERVATIVE**
