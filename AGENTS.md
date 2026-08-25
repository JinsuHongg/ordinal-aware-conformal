# Agent Instructions

This repository supports research on ordinal-aware class-conditional conformal prediction.

Before modifying research code, experiment logic, calibration rules, dataset interfaces, or evaluation code, read the relevant specification documents in this order:

1. `docs/methods/proposed_method.md`
2. `docs/methods/proposed_theory.md`
3. `docs/methods/baseline_rules.md`
4. the relevant file under `docs/datasets/` when available
5. `docs/research/experiment_plan.md`
6. `docs/research/research_direction.md`
7. `docs/research/decision_log.md`

## Source-of-truth priority

When documents disagree, use the following priority:

1. normative method contract
2. theory specification
3. dataset contract
4. frozen experiment plan
5. research direction
6. decision log
7. existing implementation

Do not infer a research decision from existing code when the documentation specifies otherwise.

Do not silently change a conformal rule, score definition, split policy, target representation, or evaluation metric to make an experiment run. Report the mismatch and update the relevant specification only when the research decision has actually changed.

## Research status

The proposed ordinal-aware calibration rule is not yet finalized.

Accordingly:

- do not invent an ordinal information-sharing rule;
- do not claim a coverage theorem that has not been proved;
- do not treat exploratory ideas as canonical method behavior;
- keep experimental prototypes clearly labeled as exploratory until promoted into `docs/methods/proposed_method.md`;
- preserve exact baseline definitions from `docs/methods/baseline_rules.md`.

## Reproducibility

For every canonical experiment, preserve:

- dataset split assignments;
- random seed;
- configuration;
- model checkpoint identifier;
- code commit;
- preprocessing settings;
- target and label definitions;
- calibration method version;
- evaluation output provenance.

Existing classifier and quantile-regression checkpoints may be reused only when their training/validation split assignments, preprocessing, target definitions, and checkpoint-selection rules match the current experiment contract.

## Implementation principle

Keep predictive models, nonconformity scores, conformal calibration rules, and prediction-set construction modular.

The intended high-level abstraction is:

`predictor -> candidate score S(x,k) -> calibration rule -> ordinal prediction set`

Pooled CP, Mondrian CP, and the proposed method should share the same regression predictor and the same base score whenever the experiment is intended to isolate the effect of calibration.

## Documentation updates

When a research decision is frozen, update the appropriate document rather than relying on chat history.

Use `docs/research/decision_log.md` for dated decisions and changes.

Use `docs/research/research_direction.md` for motivation, questions, and open research directions.

Use `docs/research/experiment_plan.md` for the current benchmark and evaluation plan.

Use `docs/methods/*.md` for exact method definitions and theoretical statements.
