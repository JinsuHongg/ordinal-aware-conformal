# Minimal Synthetic Validation of Linear Structured \(q_k\)

**Status:** Exploratory proof-of-concept; not a canonical method or theorem
**Method label:** `exploratory-hard-split-v1`

## Purpose and fixed setup

This study answers the narrow go/no-go question for a linear preliminary threshold with a disjoint, classwise final Mondrian correction. It compares only independent Mondrian CP, fixed ordinal-neighborhood calibration (radius one, reference only), and linear structured \(q_k\) plus final Mondrian correction. All methods use the same direct score generator and each repetition shares its calibration and test realization across methods.

There are five labels \(\{0,\ldots,4\}\), \(\alpha=0.10\), and class 0 is the controlled rare class with total calibration support \(100,50,20,10,5\). Other classes have 100 calibration scores. The direct regression-like generator is

\[
z=Y+\epsilon_Y,\qquad \epsilon_Y\sim N(0,\sigma_Y^2),\qquad
S(x,k)=|z-k|,
\]

with \(\sigma_Y=0.18+0.045Y\). Thus neighboring classes have related, smoothly changing true-label score distributions, while no trained predictor or ordinal-aware score is introduced.

The structured/final split is stratified within class using floor-half structured support and the remainder as final support. The exact conformal rank is \(\lceil(n+1)(1-\alpha)\rceil\); if it exceeds \(n\), the threshold is \(+\infty\). No interpolation is used.

## Intended validity argument (candidate corollary)

This is an adaptation of the usual Mondrian split-conformal rank argument, pending formal review; it is not a new theorem claim.

1. \(D_{\mathrm{struct}}\) is independent of \(D_{\mathrm{final}}\) and the test observation.
2. Conditional on \(D_{\mathrm{struct}}\), the fitted \(\widetilde q_k\) is fixed.
3. Conditional on \(Y=k\), final calibration and test residual scores \(R=S-\widetilde q_k\) are exchangeable.
4. The exact classwise Mondrian rank argument applied to those residuals gives the conservative \((1-\alpha)\) residual quantile \(c_k\).
5. Hence
   \[
   \Pr\{S_{n+1}\le \widetilde q_k+c_k\mid Y_{n+1}=k\}\ge 1-\alpha.
   \]

## Critical efficiency identity

For every class with a finite correction, subtracting the fixed preliminary threshold translates every final class score by the same amount. The conformal order statistic is translation equivariant:

\[
\widetilde q_k+Q^{\mathrm{conf}}_{1-\alpha}\{S_i-\widetilde q_k:Y_i=k\}
=Q^{\mathrm{conf}}_{1-\alpha}\{S_i:Y_i=k\}.
\]

The same identity holds for the \(+\infty\) case. Therefore this exact additive hard-split construction cannot retain an efficiency benefit from the fitted linear preliminary threshold: it is precisely independent Mondrian calibration on the smaller final split. This is a mathematical property of the specified rule, not an empirical interpretation chosen after inspecting test performance.

## Expected go/no-go interpretation

The construction has the intended candidate validity argument, but it is **NO-GO as an efficiency construction**. It cannot have a different final threshold from independent Mondrian on the final subset; compared with independent Mondrian on the full calibration stage, it discards support. At \(\alpha=0.10\), finite exact thresholds require at least nine final class scores. A half split makes total rare-class supports 10 and 5 uninformative (\(+\infty\)) in every run.

Run the reproducible study with:

```bash
PYTHONPATH=src python scripts/synthetic/run_linear_structured_qk.py
```

Results are written under `outputs/synthetic_linear_structured_qk/` and include raw per-run data, classwise and aggregate tables, plots, configuration/provenance, and a generated interpretation file.
