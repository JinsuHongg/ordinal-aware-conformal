# Robustness validation: frozen input-dependent ordinal calibration

This is an exploratory robustness study, not a canonical method or theorem claim. The preliminary ordinal and non-ordinal models are fit only on independent structured-training data; every residual method uses the unchanged full class-specific exact Mondrian correction.

Read `scenario_method_summary.csv` for scenario-level coverage, set size, relative efficiency versus independent Mondrian, and ordinal-versus-non-ordinal size differences. `summary_by_class.csv` within each scenario contains per-class diagnostics, including correction dispersion and infinite rates.

| Scenario | Rare support | Method | Rare coverage | Mean set size | Size vs Mondrian | Ordinal - non-ordinal |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| A_well_specified | 100 | independent_mondrian | 0.904 | 1.981 | 0.0% | 0.137 |
| A_well_specified | 100 | ordinal_cluster | 0.921 | 1.964 | -0.8% | 0.120 |
| A_well_specified | 100 | input_dependent_nonordinal | 0.904 | 1.844 | -6.9% | 0.000 |
| A_well_specified | 100 | input_dependent_ordinal | 0.906 | 1.844 | -6.9% | -0.000 |
| A_well_specified | 50 | independent_mondrian | 0.905 | 1.953 | 0.0% | 0.118 |
| A_well_specified | 50 | ordinal_cluster | 0.926 | 1.953 | -0.0% | 0.118 |
| A_well_specified | 50 | input_dependent_nonordinal | 0.902 | 1.835 | -6.0% | 0.000 |
| A_well_specified | 50 | input_dependent_ordinal | 0.903 | 1.837 | -5.9% | 0.002 |
| A_well_specified | 20 | independent_mondrian | 0.893 | 1.973 | 0.0% | 0.126 |
| A_well_specified | 20 | ordinal_cluster | 0.932 | 1.974 | 0.1% | 0.127 |
| A_well_specified | 20 | input_dependent_nonordinal | 0.905 | 1.847 | -6.4% | 0.000 |
| A_well_specified | 20 | input_dependent_ordinal | 0.905 | 1.843 | -6.6% | -0.003 |
| A_well_specified | 10 | independent_mondrian | 0.892 | 2.018 | 0.0% | 0.142 |
| A_well_specified | 10 | ordinal_cluster | 0.926 | 1.989 | -1.4% | 0.113 |
| A_well_specified | 10 | input_dependent_nonordinal | 0.889 | 1.876 | -7.0% | 0.000 |
| A_well_specified | 10 | input_dependent_ordinal | 0.887 | 1.872 | -7.2% | -0.004 |
| A_well_specified | 5 | independent_mondrian | 1.000 | 2.819 | 0.0% | 0.104 |
| A_well_specified | 5 | ordinal_cluster | 0.934 | 2.000 | -29.1% | -0.715 |
| A_well_specified | 5 | input_dependent_nonordinal | 1.000 | 2.715 | -3.7% | 0.000 |
| A_well_specified | 5 | input_dependent_ordinal | 1.000 | 2.712 | -3.8% | -0.003 |
| B_nonlinear_misspecified | 100 | independent_mondrian | 0.907 | 1.652 | 0.0% | 0.059 |
| B_nonlinear_misspecified | 100 | ordinal_cluster | 0.940 | 1.631 | -1.3% | 0.038 |
| B_nonlinear_misspecified | 100 | input_dependent_nonordinal | 0.898 | 1.593 | -3.5% | 0.000 |
| B_nonlinear_misspecified | 100 | input_dependent_ordinal | 0.899 | 1.593 | -3.6% | -0.000 |
| B_nonlinear_misspecified | 50 | independent_mondrian | 0.891 | 1.649 | 0.0% | 0.050 |
| B_nonlinear_misspecified | 50 | ordinal_cluster | 0.947 | 1.661 | 0.8% | 0.063 |
| B_nonlinear_misspecified | 50 | input_dependent_nonordinal | 0.887 | 1.598 | -3.1% | 0.000 |
| B_nonlinear_misspecified | 50 | input_dependent_ordinal | 0.890 | 1.599 | -3.0% | 0.000 |
| B_nonlinear_misspecified | 20 | independent_mondrian | 0.916 | 1.674 | 0.0% | 0.068 |
| B_nonlinear_misspecified | 20 | ordinal_cluster | 0.962 | 1.682 | 0.5% | 0.076 |
| B_nonlinear_misspecified | 20 | input_dependent_nonordinal | 0.909 | 1.606 | -4.0% | 0.000 |
| B_nonlinear_misspecified | 20 | input_dependent_ordinal | 0.909 | 1.605 | -4.1% | -0.001 |
| B_nonlinear_misspecified | 10 | independent_mondrian | 0.910 | 1.667 | 0.0% | 0.051 |
| B_nonlinear_misspecified | 10 | ordinal_cluster | 0.954 | 1.659 | -0.5% | 0.043 |
| B_nonlinear_misspecified | 10 | input_dependent_nonordinal | 0.921 | 1.616 | -3.1% | 0.000 |
| B_nonlinear_misspecified | 10 | input_dependent_ordinal | 0.917 | 1.613 | -3.3% | -0.003 |
| B_nonlinear_misspecified | 5 | independent_mondrian | 1.000 | 2.540 | 0.0% | 0.037 |
| B_nonlinear_misspecified | 5 | ordinal_cluster | 0.961 | 1.678 | -33.9% | -0.825 |
| B_nonlinear_misspecified | 5 | input_dependent_nonordinal | 1.000 | 2.503 | -1.4% | 0.000 |
| B_nonlinear_misspecified | 5 | input_dependent_ordinal | 1.000 | 2.502 | -1.5% | -0.002 |
| C_weaker_ordinal_smoothness | 100 | independent_mondrian | 0.890 | 1.958 | 0.0% | 0.060 |
| C_weaker_ordinal_smoothness | 100 | ordinal_cluster | 0.918 | 1.933 | -1.3% | 0.035 |
| C_weaker_ordinal_smoothness | 100 | input_dependent_nonordinal | 0.894 | 1.898 | -3.1% | 0.000 |
| C_weaker_ordinal_smoothness | 100 | input_dependent_ordinal | 0.894 | 1.898 | -3.1% | 0.000 |
| C_weaker_ordinal_smoothness | 50 | independent_mondrian | 0.903 | 1.980 | 0.0% | 0.078 |
| C_weaker_ordinal_smoothness | 50 | ordinal_cluster | 0.924 | 1.955 | -1.3% | 0.053 |
| C_weaker_ordinal_smoothness | 50 | input_dependent_nonordinal | 0.907 | 1.902 | -4.0% | 0.000 |
| C_weaker_ordinal_smoothness | 50 | input_dependent_ordinal | 0.906 | 1.902 | -4.0% | -0.000 |
| C_weaker_ordinal_smoothness | 20 | independent_mondrian | 0.906 | 1.971 | 0.0% | 0.087 |
| C_weaker_ordinal_smoothness | 20 | ordinal_cluster | 0.931 | 1.947 | -1.2% | 0.062 |
| C_weaker_ordinal_smoothness | 20 | input_dependent_nonordinal | 0.897 | 1.884 | -4.4% | 0.000 |
| C_weaker_ordinal_smoothness | 20 | input_dependent_ordinal | 0.897 | 1.883 | -4.5% | -0.001 |
| C_weaker_ordinal_smoothness | 10 | independent_mondrian | 0.920 | 2.010 | 0.0% | 0.101 |
| C_weaker_ordinal_smoothness | 10 | ordinal_cluster | 0.935 | 1.969 | -2.0% | 0.061 |
| C_weaker_ordinal_smoothness | 10 | input_dependent_nonordinal | 0.909 | 1.908 | -5.0% | 0.000 |
| C_weaker_ordinal_smoothness | 10 | input_dependent_ordinal | 0.915 | 1.904 | -5.2% | -0.004 |
| C_weaker_ordinal_smoothness | 5 | independent_mondrian | 1.000 | 2.816 | 0.0% | 0.056 |
| C_weaker_ordinal_smoothness | 5 | ordinal_cluster | 0.936 | 1.965 | -30.2% | -0.794 |
| C_weaker_ordinal_smoothness | 5 | input_dependent_nonordinal | 1.000 | 2.760 | -2.0% | 0.000 |
| C_weaker_ordinal_smoothness | 5 | input_dependent_ordinal | 1.000 | 2.756 | -2.1% | -0.004 |
| D_no_useful_ordinal_structure | 100 | independent_mondrian | 0.901 | 2.005 | 0.0% | 0.076 |
| D_no_useful_ordinal_structure | 100 | ordinal_cluster | 0.838 | 1.889 | -5.8% | -0.040 |
| D_no_useful_ordinal_structure | 100 | input_dependent_nonordinal | 0.898 | 1.929 | -3.8% | 0.000 |
| D_no_useful_ordinal_structure | 100 | input_dependent_ordinal | 0.900 | 1.923 | -4.1% | -0.006 |
| D_no_useful_ordinal_structure | 50 | independent_mondrian | 0.899 | 2.016 | 0.0% | 0.073 |
| D_no_useful_ordinal_structure | 50 | ordinal_cluster | 0.807 | 1.884 | -6.6% | -0.059 |
| D_no_useful_ordinal_structure | 50 | input_dependent_nonordinal | 0.903 | 1.943 | -3.6% | 0.000 |
| D_no_useful_ordinal_structure | 50 | input_dependent_ordinal | 0.905 | 1.941 | -3.7% | -0.002 |
| D_no_useful_ordinal_structure | 20 | independent_mondrian | 0.895 | 2.000 | 0.0% | 0.079 |
| D_no_useful_ordinal_structure | 20 | ordinal_cluster | 0.763 | 1.818 | -9.1% | -0.103 |
| D_no_useful_ordinal_structure | 20 | input_dependent_nonordinal | 0.909 | 1.920 | -4.0% | 0.000 |
| D_no_useful_ordinal_structure | 20 | input_dependent_ordinal | 0.909 | 1.920 | -4.0% | -0.001 |
| D_no_useful_ordinal_structure | 10 | independent_mondrian | 0.893 | 2.025 | 0.0% | 0.068 |
| D_no_useful_ordinal_structure | 10 | ordinal_cluster | 0.738 | 1.828 | -9.7% | -0.129 |
| D_no_useful_ordinal_structure | 10 | input_dependent_nonordinal | 0.901 | 1.957 | -3.4% | 0.000 |
| D_no_useful_ordinal_structure | 10 | input_dependent_ordinal | 0.902 | 1.953 | -3.6% | -0.004 |
| D_no_useful_ordinal_structure | 5 | independent_mondrian | 1.000 | 2.745 | 0.0% | 0.073 |
| D_no_useful_ordinal_structure | 5 | ordinal_cluster | 0.733 | 1.803 | -34.3% | -0.869 |
| D_no_useful_ordinal_structure | 5 | input_dependent_nonordinal | 1.000 | 2.672 | -2.6% | 0.000 |
| D_no_useful_ordinal_structure | 5 | input_dependent_ordinal | 1.000 | 2.670 | -2.7% | -0.003 |

Interpret ordinal gains cautiously: the non-ordinal ablation has 10 parameters (two per class), while the ordinal affine model has four shared parameters. This capacity imbalance favors the non-ordinal ablation. A result where the ordinal method is no better than the ablation means the current gain is attributable primarily to input-dependent calibration rather than ordinal sharing.

The exact finite-rank rule makes both residual methods uninformative at rare support five; this is a finite-sample conformal limitation, not evidence for or against ordinal structure.
