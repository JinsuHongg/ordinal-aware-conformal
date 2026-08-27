# Minimal synthetic linear structured $q_k$ result

This is an **exploratory** hard-split proof-of-concept, not a canonical method result.

## Result

The final residual-Mondrian threshold is algebraically identical to applying independent Mondrian calibration to the final split alone, class by class:

$$\widetilde q_{k} + Q^{conf}_{1-\alpha}(S-\widetilde q_{k})=Q^{conf}_{1-\alpha}(S).$$

The saved summaries should therefore show class-conditional coverage at or above the conservative target when the final threshold is finite, but no efficiency advantage attributable to the linear preliminary fit.  Relative to independent Mondrian using the whole calibration stage, hard splitting reduces final class support and makes $+\infty$ thresholds occur sooner.  With $\alpha=0.10$, the exact rank is finite only for at least 9 final class observations; the prescribed half split consequently makes the rare-class final threshold uninformative for total supports 10 and 5.

| Total rare calibration support | Method | Rare-class coverage | Mean set size | Rare $+\infty$ rate |
| ---: | --- | ---: | ---: | ---: |
| 100 | independent_mondrian | 0.897 | 0.974 | 0.00 |
| 100 | linear_structured_final_mondrian | 0.902 | 0.979 | 0.00 |
| 50 | independent_mondrian | 0.909 | 0.971 | 0.00 |
| 50 | linear_structured_final_mondrian | 0.928 | 0.985 | 0.00 |
| 20 | independent_mondrian | 0.906 | 0.979 | 0.00 |
| 20 | linear_structured_final_mondrian | 0.899 | 0.988 | 0.00 |
| 10 | independent_mondrian | 0.902 | 0.977 | 0.00 |
| 10 | linear_structured_final_mondrian | 1.000 | 1.936 | 1.00 |
| 5 | independent_mondrian | 1.000 | 1.924 | 1.00 |
| 5 | linear_structured_final_mondrian | 1.000 | 1.933 | 1.00 |

## Recommendation

**NO-GO / revisit the hard-split construction as an efficiency method.** The final correction preserves validity, but translation equivariance eliminates any preliminary-threshold gain for an additive classwise residual correction. The next research direction, if pursued, should be a separately justified sample-efficient construction (for example cross-fitting), not extra complexity layered onto this hard split.

## Files

- `config.json`: generator, split, seed, code commit, and configuration hash.
- `per_run_results.csv`: raw method/class/repetition results and threshold diagnostics.
- `summary_by_class.csv`: requested classwise coverage, size/span, variances, corrections, and infinite rates.
- `summary_aggregate.csv`: marginal, worst-class, rare-class, and efficiency summaries.
- `*.svg`: performance versus rare-class calibration count.
