# Research Direction

**Status:** Working research note; v0.3 is a candidate, not a canonical method

## Central problem

Independent Mondrian calibration has the desired individual class-conditional reference guarantee, but a rare class has little evidence. Directly pooling neighbor scores changes the calibration population and does not automatically preserve individual class coverage.

The paper remains calibration-first:

\[
\text{predictor}\to S(x,k)\to\text{ordinal calibration}\to C(x).
\]

All central comparisons must share the predictor and base score. Ordinal-aware nonconformity-score design remains deferred.

## Historical boundary

The class-constant additive residual construction is an established NO-GO by translation equivariance. The frozen affine input-dependent construction is an ordinal-specific NO-GO: generic conditional adaptation helped, but ordinal sharing did not outperform a higher-capacity non-ordinal ablation. Neither is the proposed method.

## Primary candidate: Assumption-Based Adaptive Ordinal Borrowing

v0.3 borrows **calibration scores**, not merely score parameterization. An independent structural sample certifies that nearby true-label score CDFs are close enough to pool conservatively. Candidate neighborhoods are always ordinal balls \(\mathcal G_k(h)=\{j:|j-k|\le h\}\); direct KS estimates only tighten their safety certificates and never define non-ordinal borrowing neighborhoods.

The method has three roles:

1. `D_train` freezes the predictor and score.
2. `D_str` computes simultaneous DKW structural certificates and fixes each borrowing radius before final score values are seen.
3. `D_cal` supplies i.i.d. final pooled scores and the conservative quantile.

The planning objective trades certified distributional mismatch against planned pooled support. It is a design heuristic, not a claimed optimality result.

## Theory boundary

The intended result is high probability over `D_str`, followed by a mixture-to-class transfer after a pooled conformal rank argument conditional on the **random pooled count**. It requires ordinary i.i.d. population final calibration. A fixed-count stratified final calibration design changes the mixture composition and is outside the present theorem.

This candidate may be useful only when the structural certificate permits a positive radius and the resulting safety penalty leaves a finite useful threshold. In no-smoothness settings, the desired fallback is \(h_k^\star=0\) or an uninformative threshold—not unsafe pooling.

## Validation gate

Before real data, the synthetic study must demonstrate certified coverage under valid smoothness, higher rare-class finite-threshold rates than independent Mondrian, sensible radius response to smoothness, no-borrowing fallback under weak/no smoothness, and practical efficiency after the certificate penalty. If only validity survives, assess sharper bounds; if utility vanishes, stop this direction.
