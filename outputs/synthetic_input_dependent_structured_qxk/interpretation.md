# Input-dependent structured threshold: synthetic result

This is an **exploratory** study, not a canonical method or theorem claim.

The preliminary threshold is trained and frozen using an independent sample, then the full calibration set supplies class-specific residual-Mondrian corrections. Conditional on this frozen function, the residual is a fixed transformed score; the intended validity route is the standard within-class Mondrian rank argument.

| Rare calibration support | Method | Rare-class coverage | Mean set size |
| ---: | --- | ---: | ---: |
| 100 | independent_mondrian | 0.902 | 1.983 |
| 100 | input_dependent_structured_mondrian | 0.900 | 1.843 |
| 50 | independent_mondrian | 0.900 | 1.954 |
| 50 | input_dependent_structured_mondrian | 0.901 | 1.833 |
| 20 | independent_mondrian | 0.901 | 1.976 |
| 20 | input_dependent_structured_mondrian | 0.904 | 1.844 |
| 10 | independent_mondrian | 0.893 | 2.017 |
| 10 | input_dependent_structured_mondrian | 0.886 | 1.867 |
| 5 | independent_mondrian | 1.000 | 2.816 |
| 5 | input_dependent_structured_mondrian | 1.000 | 2.710 |

Interpret these results together with `summary_by_class.csv`: the input-dependent method is useful only if it retains approximately 0.90 classwise coverage while reducing set size/span or residual correction magnitude without discarding calibration support. The experiment does not tune any model setting on test outcomes.

## First controlled interpretation

In this favorable, correctly structured heteroscedastic regime, finite-support settings provide a **GO signal for further validation** when the table shows target-level rare-class coverage with a smaller mean set size. This is not sufficient to freeze a method: the preliminary model matches the generator's affine ordinal difficulty pattern, so the next test should assess misspecification and weaker ordinal smoothness without changing the final residual-Mondrian rule. At rare support five, the exact finite-rank convention makes both methods uninformative; this construction preserves full calibration support but cannot overcome that fundamental limit.
