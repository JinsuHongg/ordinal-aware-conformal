# Robustness Validation: Input-Dependent Ordinal Structured Calibration

**Status:** Exploratory robustness result; not a canonical method or theorem

## Design

This study preserves the frozen transformed-score rule. Both conditional models are fit only on an independent structured-training sample; the entire class-labelled calibration sample is used for the unchanged exact residual Mondrian correction at \(\alpha=0.10\).

The four scenarios are: (A) the previous affine well-specified generator, (B) nonlinear \(x\)- and label-dependent difficulty, (C) irregular but partially smooth class effects, and (D) irregular class effects unrelated to ordinal position. Each uses five labels, rare calibration supports \(100,50,20,10,5\), 50 repetitions, and the same realization across all four methods within repetition.

The ordinal conditional model has four shared parameters, \([1,x,k,xk]\). The non-ordinal ablation has ten parameters, two separate affine-in-\(x\) parameters per class. This capacity difference favors the non-ordinal ablation.

## Results

Full class-specific residual Mondrian retained approximately target average per-class coverage for both conditional methods across scenarios. The sparse \(n=10\) rare-class estimates have substantial Monte Carlo and calibration-order-statistic variability; at \(n=5\), the exact rank requires \(+\infty\) for both residual methods, as expected.

Input-dependent calibration reduced mean set size relative to independent Mondrian in every finite-support scenario tested:

| Scenario | Typical relative size change for conditional methods |
| --- | ---: |
| A: well-specified | about \(-6\%\) to \(-7\%\) |
| B: nonlinear misspecification | about \(-3\%\) to \(-4\%\) |
| C: weaker smoothness | about \(-3\%\) to \(-5\%\) |
| D: no useful ordinal structure | about \(-3\%\) to \(-4\%\) |

Thus the original gain is not confined to the exactly affine generator: a smaller conditional-efficiency gain survives the nonlinear and irregular scenarios.

However, the ordinal-versus-non-ordinal ablation is effectively tied. Across scenarios and supports, the ordinal model's mean-set-size difference from the non-ordinal model is between approximately \(-0.006\) and \(+0.002\) labels, materially smaller than the per-repetition set-size standard deviations recorded in the output tables. This holds even though the non-ordinal model has greater capacity.

Ordinal Cluster Calibration remains visibly unsafe as an individual-class reference in the irregular scenarios; for example, scenario D has large classwise coverage disparities despite small sets. It must not be interpreted as a class-conditional-valid method.

## Answers

**Q1 — Validity robustness.** The residual methods show the expected approximately 0.90 classwise coverage pattern under every scenario. This is empirical consistency with the frozen transformed-score Mondrian argument, not a formal theorem.

**Q2 — Misspecification.** Roughly half of the original set-size gain survives nonlinear misspecification (about 3–4% rather than 6–7%).

**Q3 — Ordinal smoothness.** Efficiency remains positive under weaker smoothness, but it is reduced to about 3–5%.

**Q4 — Negative control.** With no useful ordinal structure, there is no catastrophic degradation; the conditional methods retain a modest input-dependent gain over independent Mondrian.

**Q5 — Ordinal contribution.** No meaningful extra benefit from ordinal parameter sharing was observed beyond the non-ordinal input-dependent ablation.

**Q6 — Rare classes.** Both residual methods retain full calibration support. At five rare examples, \(+\infty\) is imposed by the exact finite-rank convention; this is a finite-sample conformal limitation, not a structured-model failure.

## Research decision

**NO-GO — ordinal structure does not provide sufficient additional value in the current affine structured model.**

The study supports input-dependent residual calibration as a useful mechanism, but the current evidence attributes the gain to conditioning on \(x\), not to ordinal sharing. Do not proceed to real-data experiments with this affine ordinal construction as the proposed ordinal method. Preserve the result, and revise the structured model or research claim before extending the benchmark.

## Artifacts

The reproducible runner is `scripts/synthetic/run_input_dependent_robustness.py`. Raw per-run data and per-class diagnostics are preserved under `outputs/synthetic_input_dependent_robustness/<scenario>/`; scenario-level comparisons and plots are under `outputs/synthetic_input_dependent_robustness/`.
