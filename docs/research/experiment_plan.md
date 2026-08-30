# Experiment Plan

**Status:** v0.3 synthetic validation is immediate; broader benchmark plan is later
**Default target miscoverage:** \(\alpha=0.10\)

## Immediate experiment: adaptive ordinal borrowing v0.3

Compare, with the same predictor, score, i.i.d. final calibration realization, and test realization within a repetition:

1. Independent Mondrian CP;
2. Ordinal Cluster Calibration (reference only; no individual validity claim);
3. Adaptive Ordinal Borrowing — approximate;
4. Adaptive Ordinal Borrowing — certified v0.3.

Use independent `D_train`, `D_str`, and `D_cal`. Do not tune radii, structural models, or safety parameters on final calibration score values or test results.

### Sampling contract

The theorem-aligned final calibration sample must be an ordinary i.i.d. population draw. Do not use a fixed-count class-stratified `D_cal` and claim the v0.3 theorem: conditioning on a stratified count design changes the pooled neighborhood mixture. Vary population class probabilities instead, then report results conditionally on realized rare-class support bins near 5, 10, 20, 50, and 100.

### Scenarios

- Strong ordinal smoothness: expect positive certified borrowing and rare-class finite-threshold recovery.
- Moderate smoothness: expect smaller radii and reduced gain.
- Heterogeneous local smoothness: expect class-specific radii and no crossing of sharp distributional boundaries.
- No useful ordinal smoothness: expect \(h_k^\star=0\) or infeasible borrowing.
- Certificate/assumption stress: insufficient `D_str` support or explicit structural-assumption violation; report the failure mode rather than tuning.

### Required reporting

Report marginal, per-class, worst-class, and rare-class coverage; set size and ordinal span; selected radii; \(\epsilon_k^\star\); pooled support; finite/\(+\infty\) rates; direct and path certificates; true synthetic KS distances; structural-UCB coverage; and certificate-failure rate. Preserve configuration, seeds, score definition, split roles, code commit, and raw per-run provenance.

## Decision gate

Mark v0.3 **GO** only if certified coverage is retained under valid smoothness, rare classes achieve materially better finite-threshold rates than Mondrian, radii respond sensibly to smoothness, weak/no smoothness falls back safely, and the safety penalty leaves useful efficiency. If validity holds but the penalty is too conservative, mark PARTIAL GO and study sharper bounds. If useful rare recovery disappears, mark NO-GO.

## Later benchmark plan

After this gate, the planned datasets remain Synthetic, RetinaMNIST, UTKFace, Solar flare, and Amazon Reviews. The broader comparison set remains Pooled CP, Mondrian CP, LAC, APS, Min-CPS, RPS-CP, OCQR, and the eventual proposed method. Real-data work, checkpoint reuse, and classifier baselines remain out of scope until this synthetic gate is resolved.
