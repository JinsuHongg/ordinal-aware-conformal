# Current Research State

**Last updated:** 2026-08-28
**Status:** Candidate v0.3 ready for synthetic validation; canonical proposed method remains unfixed

## Current primary direction

> **Assumption-Based Adaptive Ordinal Borrowing**

The current question is whether known ordinal relationships can borrow actual calibration evidence from neighboring classes while maintaining controlled finite-sample individual class-conditional coverage. The method targets sparse class support directly; it is not another score-transformation construction.

The candidate uses independent `D_train`, `D_str`, and `D_cal`. The predictor and score are frozen before structural and final calibration. The current theorem contract requires `D_cal` to be an ordinary i.i.d. population sample. **Fixed-count class-stratified final calibration is not covered by that theorem.**

## Completed negative results

1. **Class-constant additive threshold: NO-GO.** For \(\widetilde q_k\) plus classwise additive residual Mondrian correction, translation equivariance gives
   \[
   \widetilde q_k+Q^{\mathrm{conf}}_{1-\alpha}(S-\widetilde q_k)=Q^{\mathrm{conf}}_{1-\alpha}(S).
   \]
   It is independent Mondrian on a smaller split.
2. **Affine input-dependent ordinal threshold: ordinal-specific NO-GO.** It produced useful generic conditional adaptation, but the four-scenario robustness study found at most about 0.006 labels between ordinal and non-ordinal conditional models. The benefit was from conditioning on \(x\), not ordinal sharing.

The completed records remain authoritative historical evidence:

- `synthetic_linear_structured_qk_note.md`
- `synthetic_input_dependent_structured_qxk_note.md`
- `synthetic_input_dependent_robustness_note.md`

## v0.3 candidate rule

`D_str` supplies simultaneous DKW certificates for true-label score CDF distances. These produce ordinal-only adaptive neighborhoods that are frozen before final calibration scores are observed. For each target class, v0.3 pools final scores within its certified ordinal neighborhood, spends the certified mixture-to-class error from \(\alpha\), and uses a conservative pooled order statistic. Unsupported structural classes suppress borrowing rather than being excluded by assumption.

The detailed executable theory contract is in `docs/methods/proposed_theory.md`; the concise audit is in `assumption_based_ordinal_borrowing_v0_3.md`.

## Guarantee status

The target candidate theorem is a **high-probability structural-certificate guarantee**: with probability at least \(1-\delta_{\mathrm{str}}\) over `D_str`, classwise coverage is at least \(1-\alpha\), conditional on the structural sample. It is not the same statement as exact distribution-free Mondrian validity. It must not be claimed as established until synthetic and formal review are complete.

## Immediate next experiment

Run theorem-aligned synthetic validation only. Compare Independent Mondrian, Ordinal Cluster Calibration, adaptive borrowing approximate, and certified v0.3. Draw final calibration i.i.d. from the population; vary population class probabilities and summarize by realized rare support bins around 5, 10, 20, 50, and 100. Do not begin real-data experiments or freeze `proposed_method.md`.
