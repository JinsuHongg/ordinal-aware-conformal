# Experiment Plan

**Status:** Working plan with frozen benchmark choices
**Target miscoverage:** \(lpha=0.10\) unless explicitly changed by a later decision

## 1. Goals

The experimental design should evaluate:

1. whether the proposed calibration method preserves class-conditional coverage;
2. whether it improves efficiency relative to independent Mondrian calibration;
3. whether gains are strongest under sparse or imbalanced calibration support;
4. whether the calibration contribution is independent of a particular predictive model;
5. whether the method remains useful across different modalities and target types.

## 2. Planned datasets

The current benchmark suite is fixed to five datasets.

### 2.1 Synthetic ordinal data

Primary role:

- controlled mechanism study;
- vary class imbalance and calibration support;
- control the relationship between neighboring classes;
- test conditions under which ordinal borrowing helps or fails;
- validate finite-sample coverage behavior.

The synthetic generator is not yet specified.

### 2.2 RetinaMNIST

Role:

- small standard ordinal image benchmark;
- five diabetic-retinopathy severity levels;
- class-only ordinal target setting.

Expected target representation for regression-based experiments:

\[
Z=e(Y_{\mathrm{ord}})
\]

with a fixed documented embedding.

Dataset-specific details should be placed in a separate dataset contract before canonical experiments.

### 2.3 UTKFace

Role:

- image-based continuous-target-to-ordinal setting;
- chronological age provides a natural regression target;
- ordinal classes are constructed from fixed age bins.

Existing OCQR split assignments and compatible model checkpoints may be reused if all experiment conditions match.

### 2.4 Solar-flare forecasting

Role:

- strongly imbalanced scientific application;
- rare extreme ordinal classes;
- continuous numeric flare-intensity target with ordinal flare labels;
- temporal generalization stress test.

The chronological evaluation does not itself establish calibration/test exchangeability.

Coverage results must therefore be interpreted under the assumptions of the conformal theorem and separately from temporal-extrapolation behavior.

### 2.5 Amazon Reviews

Role:

- text modality;
- large public ordinal benchmark;
- 1--5 star ratings;
- evidence that the framework is not image-specific.

The initial plan is to use an English subset and a small pretrained text encoder with a task-specific head.

Exact model, sequence length, preprocessing, and splits remain to be frozen.

## 3. Planned conformal comparisons

The current comparison set contains seven baselines plus the proposed method.

1. Pooled CP
2. Mondrian CP
3. LAC
4. APS
5. Min-CPS
6. RPS-CP
7. OCQR
8. Proposed

OCQR is currently unpublished and should be treated as a predecessor or secondary comparison rather than as peer-reviewed prior art.

## 4. Base model families

The current plan uses three predictive model families.

### 4.1 Standard regression model

Used by:

- Pooled CP
- Mondrian CP
- Proposed

The key comparison should use the same trained checkpoint and the same base score for all three methods.

This is the main calibration ablation:

\[
	ext{Pooled}
\leftrightarrow
	ext{Mondrian}
\leftrightarrow
	ext{Proposed}.
\]

The intended interpretation is:

- Pooled CP: maximum information sharing, generally marginal rather than class-conditional calibration;
- Mondrian CP: no cross-class information sharing, class-wise calibration;
- Proposed: ordinal-aware information use with the target class-wise validity property.

### 4.2 Softmax probabilistic classifier

Shared by:

- LAC
- APS
- Min-CPS
- RPS-CP

These methods should use the same classifier checkpoint within a dataset and seed whenever their published definitions permit it.

### 4.3 Quantile-regression model

Used by:

- OCQR

OCQR should use the canonical quantile model and calibration rule defined in the OCQR project.

## 5. Existing checkpoint reuse

Existing classifier and quantile-regression checkpoints from the OCQR experiments may be reused for:

- RetinaMNIST;
- UTKFace;
- Solar flare.

Reuse is allowed only when the following match the new experiment:

- training split assignment;
- validation split assignment;
- preprocessing;
- target definition;
- class definition and bins;
- architecture and model interface;
- checkpoint-selection rule.

The new evaluation should load the checkpoint and rerun prediction, calibration, and evaluation under the unified experiment pipeline rather than copying old result tables.

The COPOC-specific classifier checkpoint is not currently needed because COPOC is not in the selected comparison set.

For the current ICLR direction, a new standard regression model is expected for RetinaMNIST, UTKFace, and Solar flare.

Amazon Reviews will require new model training.

## 6. Split policy

Use fixed sample-to-split assignments.

Human-facing documentation should prefer the terms:

- `split assignment`;
- `fixed split file`;

rather than `split manifest`.

A split ratio alone is not sufficient for checkpoint reuse.

For example, two 60/10/20/10 splits may contain different samples.

Canonical experiments should therefore preserve the actual sample identifiers assigned to:

- train;
- validation;
- calibration;
- test.

The split creation seed should be recorded, but canonical reruns should read the frozen split assignment rather than regenerate it from the seed.

## 7. Random seeds

The current default is to reuse the established five-seed convention:

\[
\{0,1,2,3,4\}.
\]

A later method-development decision may reduce seeds for exploratory experiments, but final canonical comparisons should use a common seed set across methods.

Model initialization seeds and data split assignments should be treated as separate reproducibility objects.

## 8. Model selection

All predictive model choices must be finalized before conformal calibration.

Checkpoint selection must use training/validation information only.

The previous OCQR convention is:

- classifier: minimum validation cross-entropy;
- quantile model: minimum total validation pinball loss.

The standard regression model requires a frozen validation criterion before canonical experiments, likely validation regression loss such as MSE or MAE.

The exact criterion is TBD.

Calibration performance must not be used to select a predictive checkpoint.

## 9. Primary metrics

At minimum report:

- marginal coverage;
- class-conditional coverage;
- worst-class coverage;
- extreme-class coverage where meaningful;
- mean prediction-set size;
- per-class prediction-set size;
- ordinal span or interval width;
- full-set rate;
- empty-set rate before conservative post-processing if the method can produce one.

For the proposed method, also report calibration-efficiency diagnostics that directly measure the effect of ordinal information sharing.

## 10. Calibration-support experiments

A central experiment should vary calibration support while keeping the trained predictor fixed.

Possible controlled settings:

- calibration fraction;
- per-class calibration count;
- rare-class downsampling;
- long-tailed calibration distributions.

The main comparison should be between:

- Pooled CP;
- independent Mondrian CP;
- Proposed.

This experiment is expected to be more important than simply adding many benchmark methods.

## 11. Synthetic study requirements

The synthetic benchmark should eventually allow controlled variation of:

- number of ordinal classes;
- class probabilities;
- per-class calibration support;
- neighboring-class distribution similarity;
- adjacent-class separation;
- model noise;
- violations of ordinal smoothness.

The final synthetic design should be tied directly to the assumptions of the proposed theory.

Do not freeze a synthetic generator before the method assumptions are understood.

## 12. Reporting

Every canonical run should preserve:

- dataset;
- split-assignment identifier or hash;
- seed;
- model family;
- checkpoint identifier;
- calibration method;
- method version;
- configuration hash;
- code commit;
- per-class calibration counts;
- per-class coverage and efficiency metrics.

Baseline and proposed results should be produced by the same evaluator where possible.

## 13. Current implementation order

Recommended order:

1. build shared score and calibration interfaces;
2. implement standard regression predictor;
3. implement Pooled CP;
4. implement independent Mondrian CP;
5. build synthetic benchmark;
6. verify coverage behavior for the controls;
7. prototype proposed ordinal-aware calibration;
8. add the classifier-based baselines;
9. integrate existing OCQR checkpoints;
10. add Amazon Reviews and final multi-dataset experiments.

The proposed method should not be optimized against test data.
