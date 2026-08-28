# Proposed Method Theory

**Status:** v0.3 candidate theorem/proof contract; not an established theorem
**Candidate version:** Assumption-Based Adaptive Ordinal Borrowing v0.3

## Scope and data roles

Let \(Y\in\{0,\ldots,K-1\}\), with frozen candidate score \(S(x,k)\), and let \(F_k(t)=\Pr\{S(X,k)\le t\mid Y=k\}\). Use independent \(D_{\mathrm{train}}\), \(D_{\mathrm{str}}\), and \(D_{\mathrm{cal}}\). The predictor and score are frozen before the latter two samples. This contract requires \(D_{\mathrm{cal}}\) to be an ordinary i.i.d. population sample. A fixed-count class-stratified final calibration design is **not covered** because it changes the pooled neighborhood mixture.

The target is a high-probability structural-certificate statement, not exact distribution-free Mondrian validity: with probability at least \(1-\delta_{\mathrm{str}}\) over \(D_{\mathrm{str}}\), simultaneously for every class \(k\),

\[
\Pr\{Y_{n+1}\in C(X_{n+1})\mid Y_{n+1}=k,D_{\mathrm{str}}\}\ge1-\alpha,
\]

where the inner probability is over i.i.d. final calibration and test data.

## Structural DKW certificate

For structural class count \(m_k>0\), set

\[
e_k=\min\left\{1,\sqrt{\frac{\log(2K/\delta_{\mathrm{str}})}{2m_k}}\right\};
\]

for \(m_k=0\), set \(e_k=1\). Zero support is not excluded: it supplies an uninformative certificate and suppresses borrowing.

For supported pairs,

\[
\widehat d_{jk}=\sup_t|\widehat F_j^{\mathrm{str}}(t)-\widehat F_k^{\mathrm{str}}(t)|,
\quad U_{jk}^{\mathrm{direct}}=\min\{1,\widehat d_{jk}+e_j+e_k\}.
\]

If either class is unsupported, use \(U_{jk}^{\mathrm{direct}}=1\). For adjacent classes let \(d_r^U=U_{r,r+1}^{\mathrm{direct}}\), and define

\[
U_{jk}^{\mathrm{path}}=\begin{cases}0,&j=k,\\
\min\{1,\sum_{r=\min(j,k)}^{\max(j,k)-1}d_r^U\},&j\ne k.\end{cases}
\]

The tightened certificate is \(\Delta_{jk}^{U}=\min\{U_{jk}^{\mathrm{direct}},U_{jk}^{\mathrm{path}}\}\). Direct KS comparisons only tighten certificates; borrowing neighborhoods remain ordinal.

## Frozen adaptive neighborhood

For \(\mathcal G_k(h)=\{j:|j-k|\le h\}\), define \(\epsilon_{k,h}^{U}=\max_{j\in\mathcal G_k(h)}\Delta_{kj}^{U}\). On the simultaneous structural event,

\begin{equation}
\left\|F_{k,h}^{\mathrm{mix}}-F_k\right\|_{\infty}\le\epsilon_{k,h}^{U}.
\label{eq:mixture_ks_bound}
\end{equation}

Using structural proportions, plan

\[
N_{k,h}^{\mathrm{plan}}=n_{\mathrm{cal}}\sum_{j\in\mathcal G_k(h)}\widehat\pi_j^{\mathrm{str}},
\qquad \Psi_{k,h}=\epsilon_{k,h}^{U}+\frac1{N_{k,h}^{\mathrm{plan}}+1}.
\]

Choose \(h_k^\star=\arg\min_{h\in\mathcal H_k}\Psi_{k,h}\), with deterministic smallest-radius tie breaking, and reject at minimum radii with \(\epsilon_{k,h}^{U}\ge\alpha\). This objective is a design heuristic, not a theoretically optimal rule. Selection must be frozen before final calibration score values are observed.

## Certified pooled calibration

Let \(\mathcal G_k^\star=\mathcal G_k(h_k^\star)\), \(\epsilon_k^\star=\epsilon_{k,h_k^\star}^{U}\), and pool final scores with labels in \(\mathcal G_k^\star\). Let realized pooled support be \(N_k^\star\). If \(\epsilon_k^\star\ge\alpha\), set \(q_k=+\infty\). Otherwise set

\[
r_k^\star=\left\lceil(N_k^\star+1)(1-\alpha+\epsilon_k^\star)\right\rceil.
\]

If \(r_k^\star>N_k^\star\), set \(q_k=+\infty\); otherwise use the corresponding pooled order statistic. Then \(C(x)=\{k:S(x,k)\le q_k\}\). For integer \(N_k^\star\), an equivalent finite-threshold condition is

\[
\alpha-\epsilon_k^\star\ge\frac1{N_k^\star+1}.
\]

## Candidate theorem and proof audit

Use a real manuscript theorem environment: `\begin{theorem}[Certified class-conditional coverage under adaptive ordinal borrowing]\label{thm:adaptive_ordinal_coverage}`.

The proof must first condition on \(D_{\mathrm{str}}\), the frozen neighborhood, and the random pooled count \(N_k^\star=n\). Under i.i.d. population sampling, the selected \(n\) pooled scores are i.i.d. from \(F_{k,h_k^\star}^{\mathrm{mix}}\), and a new mixture score has that law. The rank argument gives mixture coverage at least \(1-\alpha+\epsilon_k^\star\); then average over \(N_k^\star\). Do **not** condition on the entire vector of per-class pooled counts and claim mixture-i.i.d. exchangeability.

Transfer with

\begin{equation}
F_k(t)\ge F_{k,h_k^\star}^{\mathrm{mix}}(t)-\epsilon_k^\star.
\label{eq:class_mix_lower}
\end{equation}

Thus \(\mathbb E[F_{k,h_k^\star}^{\mathrm{mix}}(q_k)]\ge1-\alpha+\epsilon_k^\star\) implies \(\mathbb E[F_k(q_k)]\ge1-\alpha\).

## Historical exclusions and validation

Class-constant additive residual thresholds are an established NO-GO by translation equivariance. The affine input-dependent ordinal model is an ordinal-specific NO-GO: its gain was generic conditional adaptation. v0.3 is a new candidate, not a promotion of either result. Synthetic validation must measure certificates, true KS distances, selected radii, pooled support, finite-threshold rates, and coverage before any canonical method is frozen.
