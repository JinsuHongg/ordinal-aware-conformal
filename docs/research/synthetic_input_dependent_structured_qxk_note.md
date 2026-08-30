# Minimal Synthetic Test: Input-Dependent Structured \(\widetilde q(x,k)\)

**Status:** Exploratory candidate; not a canonical method or theorem

## Purpose

This follows the class-constant hard-split NO-GO result. It tests whether a frozen preliminary threshold that varies within class can improve efficiency while preserving the standard class-conditional residual-Mondrian validity route.

The synthetic model uses five ordinal labels, a scalar feature \(x\in[0,1]\), and the shared score

\[
S(x,k)=|z-0.60k|,\qquad z=0.60Y+\epsilon,\qquad
\epsilon\sim N(0,\sigma(x,Y)^2),
\]

where

\[
\sigma(x,k)=0.09+0.38x+0.035k+0.018xk.
\]

Thus \(x\) predicts within-class difficulty and the effect changes smoothly with ordinal class index. The method learns the affine ordinal structure \([1,x,k,xk]\) from an independent structured-training sample only, estimates the conditional mean absolute score, and scales it to the corresponding Gaussian \(0.90\) quantile. It is frozen before calibration.

For the full calibration set, the rule is

\[
R_i=S(X_i,Y_i)-\widetilde q(X_i,Y_i),
\qquad
c_k=Q^{\mathrm{conf}}_{1-\alpha}\{R_i:Y_i=k\}.
\]

A test candidate \(k\) is accepted when

\[
S(x,k)\le \widetilde q(x,k)+c_k.
\]

The exact rank is \(\lceil(m_k+1)(1-\alpha)\rceil\), with \(+\infty\) when this exceeds \(m_k\). No calibration observation trains \(\widetilde q\), and no test result selects a setting.

## Candidate validity argument

Conditional on the independently trained, frozen score and threshold model, \(R(x,k)\) is a fixed transformation. Under within-class exchangeability, class-\(k\) calibration residuals and the class-\(k\) test residual are exchangeable. The ordinary exact Mondrian rank argument therefore gives the candidate class-conditional statement. This remains a corollary candidate requiring formal review, not a new theorem claim.

## Reproduction

```bash
PYTHONPATH=src python scripts/synthetic/run_input_dependent_structured_qxk.py
```

Outputs under `outputs/synthetic_input_dependent_structured_qxk/` contain the frozen-model provenance, raw per-run records, classwise and aggregate summaries, and plots of coverage/efficiency against rare-class calibration support.

This first configuration is intentionally favorable: the affine ordinal threshold model matches the generator's conditional score scale. A positive result is evidence that the construction can escape the class-constant cancellation, not evidence that it is robust to misspecification or ready to become canonical.
