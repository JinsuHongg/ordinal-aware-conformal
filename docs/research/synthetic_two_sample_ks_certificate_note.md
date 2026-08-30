# Synthetic Direct Two-Sample KS Certificate Comparison

**Status:** completed certificate-only diagnostic; the v0.3 borrowing and conformal-calibration mechanisms were not changed.

## Question and frozen design

Can a direct non-null two-sample KS certificate materially reduce the structural sample size needed to certify borrowing for the 3% rare class? This exactly reuses the v0.3 strong-smoothness generator:

\[
K=5,\quad \alpha=0.10,\quad\delta_{\rm str}=0.05,
\quad\pi=(.30,.25,.22,.20,.03),
\]

\[
S\mid Y=k\sim N(\mu_k,.20^2),\qquad
(\mu_0,\ldots,\mu_4)=(.500,.505,.510,.515,.520).
\]

There is no final calibration or test sample. For 100 independent structural repetitions at every \(n_{\rm str}\in\{500,1000,2000,5000,10000,20000,50000\}\), the current DKW UCB was compared with the direct two-sample UCB using pairwise Bonferroni \(\delta_{jk}=.05/10=.005\), then the unchanged ordinal-path tightening. The normal-location formula \(d^{\rm true}_{jk}=2\Phi(|\mu_j-\mu_k|/(2(.20)))-1\) gives exact population KS distances. For adjacent pair \((3,4)\), direct and path UCBs coincide.

## Results: primary rare-neighbor pair

\(d^{\rm true}_{34}=0.0099733\). Positive reduction means the direct certificate is tighter.

| \(n_{\rm str}\) | Mean \(m_3\) | Mean \(m_4\) | Mean \(\widehat d_{34}\) | Mean DKW UCB | Mean two-sample UCB | Mean reduction | \(P(U^{\rm DKW}_{34}<.10)\) | \(P(U^{\rm 2S}_{34}<.10)\) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 500 | 100.62 | 14.59 | .24498 | .83556 | .78777 | .04779 | .00 | .00 |
| 1,000 | 200.05 | 29.58 | .16004 | .57773 | .53985 | .03787 | .00 | .00 |
| 2,000 | 398.78 | 61.13 | .12268 | .41387 | .38687 | .02700 | .00 | .00 |
| 5,000 | 998.84 | 148.94 | .07849 | .26365 | .24663 | .01702 | .00 | .00 |
| 10,000 | 2,000.90 | 300.98 | .05354 | .18388 | .17183 | .01204 | .00 | .00 |
| 20,000 | 4,001.28 | 601.06 | .04139 | .13355 | .12503 | .00851 | .00 | .00 |
| 50,000 | 10,012.00 | 1,499.00 | .02531 | .08363 | .07825 | .00538 | .96 | .99 |

The direct certificate is uniformly tighter, but its absolute gain contracts with sample size. It does not make radius-one borrowing common at 5,000--10,000 structural observations: both certificates first become commonly admissible only at 50,000. The 50,000-point difference is three additional successful repetitions out of 100 (0.99 versus 0.96), not a practical change in the structural-support requirement.

## Certificate validity diagnostics

At every structural size, both methods covered every known pairwise KS distance in all 100 repetitions. Observed pairwise and simultaneous coverage are therefore both 1.000 for DKW and two-sample certificates. This is consistent with, but does not precisely establish, the nominal simultaneous lower bound of .95.

## Artifacts

- `outputs/synthetic_two_sample_ks_certificate/certificate_per_repetition.csv`
- `outputs/synthetic_two_sample_ks_certificate/certificate_summary.csv`
- `outputs/synthetic_two_sample_ks_certificate/pairwise_summary.csv`
- `outputs/synthetic_two_sample_ks_certificate/config.json`
- `outputs/synthetic_two_sample_ks_certificate/plots/`

The raw table records direct/path two-sample UCBs, DKW UCBs, known KS values, and pairwise/all-pair coverage flags.

## Decision

**CERTIFICATE PARTIAL GO**

The audited non-null bound is valid for this continuous-score synthetic setting and modestly tighter. It does not materially lower the structural sample size at which rare-class borrowing is feasible. Per the pre-registered gate, no full conformal comparison was run. Global KS control remains the bottleneck; the next certificate direction should be quantile-local or one-sided rather than another global-KS refinement.
