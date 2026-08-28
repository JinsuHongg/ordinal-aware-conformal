# Assumption-Based Adaptive Ordinal Borrowing v0.3

**Status:** Candidate ready for synthetic validation; not canonical

## Purpose

v0.3 is the first current candidate that borrows actual final calibration evidence from ordinal neighbors. It follows two established negative results: class-constant additive residual thresholds cancel exactly, and affine input-dependent ordinal sharing did not improve on non-ordinal conditional adaptation.

## Construction audit

Use independent `D_train`, `D_str`, and i.i.d. population `D_cal`. Freeze the predictor and score before `D_str` and `D_cal`. From `D_str`, use simultaneous DKW error radii \(e_k\), direct KS UCBs \(U_{jk}^{\mathrm{direct}}\), ordinal-path UCBs \(U_{jk}^{\mathrm{path}}\), and \(\Delta_{jk}^U=\min\{U_{jk}^{\mathrm{direct}},U_{jk}^{\mathrm{path}}\}\). Unsupported structural classes have \(e_k=1\), so borrowing is suppressed.

Neighborhoods are ordinal balls only. The radius minimizes the frozen planning heuristic \(\epsilon_{k,h}^U+1/(N_{k,h}^{\mathrm{plan}}+1)\), with smallest-radius tie breaking and rejection when \(\epsilon_{k,h}^U\ge\alpha\). Direct KS comparisons tighten certificates only; they do not choose non-ordinal neighbors.

Final pooled calibration spends \(\epsilon_k^\star\) from \(\alpha\), uses rank \(\lceil(N_k^\star+1)(1-\alpha+\epsilon_k^\star)\rceil\), and returns \(+\infty\) when the certificate or rank makes a finite threshold impossible. An equivalent finite-threshold condition is \(\alpha-\epsilon_k^\star\ge1/(N_k^\star+1)\).

## Mathematical audit

The candidate theorem is high probability over the structural sample, not exact distribution-free Mondrian validity. Its proof conditions first on the random pooled count, applies the mixture rank argument, averages over that count, then transfers mixture coverage to the target class through the certified CDF bound. It must not condition on the entire vector of per-class pooled counts and assert mixture-i.i.d. exchangeability.

The theorem does not cover fixed-count class-stratified final calibration. Such a design changes the selected pooled mixture. The theorem-aligned experiment must use ordinary i.i.d. `D_cal` sampling.

## Synthetic gate

Validate strong, moderate, heterogeneous, no-smoothness, and certificate-stress scenarios. Record coverage, size/span, radii, certificates, direct/path comparisons, true KS distances, pooled support, finite rates, and certificate failures. GO requires safe adaptive borrowing and material rare-class finite-threshold recovery after the safety penalty; otherwise record PARTIAL GO or NO-GO without adding complexity.
