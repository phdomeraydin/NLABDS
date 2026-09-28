from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class ReportGenerator:

    def __init__(
        self,
        output_dir: Path,
    ):

        self.output_dir = Path(
            output_dir
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ========================================================
    # CSV helper
    # ========================================================

    def _save_csv(
        self,
        rows,
        filename,
    ):

        df = pd.DataFrame(
            rows
        )

        df.to_csv(
            self.output_dir
            / filename,
            index=False,
        )

        return df

    # ========================================================
    # Timing-table helper
    # ========================================================

    @staticmethod
    def _timing_row(
        n,
        stats,
        extra=None,
    ):

        row = {

            "n": n,

            "Cryptographic trials": (
                stats[
                    "count"
                ]
            ),

            "Independent Lie algebras for CI": (
                stats[
                    "independent_units"
                ]
            ),

            "Mean (ms)": (
                stats[
                    "mean"
                ]
            ),

            "Trial-level SD (ms)": (
                stats[
                    "sd"
                ]
            ),

            "Median (ms)": (
                stats[
                    "median"
                ]
            ),

            "Min (ms)": (
                stats[
                    "min"
                ]
            ),

            "Max (ms)": (
                stats[
                    "max"
                ]
            ),

            "Between-algebra SD of means (ms)": (
                stats[
                    "between_algebra_sd"
                ]
            ),

            "95% CI low (ms)": (
                stats[
                    "ci95_low"
                ]
            ),

            "95% CI high (ms)": (
                stats[
                    "ci95_high"
                ]
            ),

            "95% CI half-width (ms)": (
                stats[
                    "ci95_half_width"
                ]
            ),
        }

        if extra:
            row.update(
                extra
            )

        return row

    # ========================================================
    # Main tables
    # ========================================================

    def create_all_tables(
        self,
        results,
    ):

        tables = {}

        # ----------------------------------------------------
        # Experimental configurations
        # ----------------------------------------------------

        tables[2] = (
            self._save_csv(
                [
                    {
                        "Configuration": (
                            f"P{i}"
                        ),

                        "Dimension n": (
                            r[
                                "n"
                            ]
                        ),

                        "Field bit length": (
                            r[
                                "field_bits"
                            ]
                        ),

                        "Nilpotency class c": (
                            2
                        ),

                        "Center fraction": (
                            r[
                                "center_fraction"
                            ]
                        ),

                        "Target bracket density": (
                            r[
                                "density"
                            ]
                        ),

                        "Mean realized density": (
                            r[
                                "realized_density"
                            ]
                        ),

                        "Independent Lie algebras": (
                            r[
                                "algebra_instances"
                            ]
                        ),

                        "Trials per algebra": (
                            r[
                                "trials_per_algebra"
                            ]
                        ),

                        "Total cryptographic trials": (
                            r[
                                "repetitions"
                            ]
                        ),
                    }

                    for i, r
                    in enumerate(
                        results,
                        start=1,
                    )
                ],

                (
                    "Table2_Experimental_"
                    "Configurations.csv"
                ),
            )
        )

        # ----------------------------------------------------
        # KeyGen
        # ----------------------------------------------------

        tables[3] = (
            self._save_csv(
                [
                    self._timing_row(
                        r[
                            "n"
                        ],

                        r[
                            "keygen"
                        ],
                    )

                    for r
                    in results
                ],

                "Table3_KeyGen.csv",
            )
        )

        # ----------------------------------------------------
        # Signing
        # ----------------------------------------------------

        tables[4] = (
            self._save_csv(
                [
                    self._timing_row(
                        r[
                            "n"
                        ],

                        r[
                            "sign"
                        ],
                    )

                    for r
                    in results
                ],

                "Table4_Sign.csv",
            )
        )

        # ----------------------------------------------------
        # Verification
        # ----------------------------------------------------

        tables[5] = (
            self._save_csv(
                [
                    self._timing_row(
                        r[
                            "n"
                        ],

                        r[
                            "verify"
                        ],

                        {
                            "Correctness (%)": (
                                r[
                                    "correctness_rate"
                                ]
                            )
                        },
                    )

                    for r
                    in results
                ],

                "Table5_Verify.csv",
            )
        )

        # ----------------------------------------------------
        # Storage
        # ----------------------------------------------------

        tables[6] = (
            self._save_csv(
                [
                    {
                        "n": (
                            r[
                                "n"
                            ]
                        ),

                        "Private key (bytes)": (
                            r[
                                "private_bytes"
                            ]
                        ),

                        "Public-key payload g,y (bytes)": (
                            r[
                                "public_payload_bytes"
                            ]
                        ),

                        "Signature (bytes)": (
                            r[
                                "signature_bytes"
                            ]
                        ),

                        "Dense algebra parameters (bytes)": (
                            r[
                                "dense_algebra_parameter_bytes"
                            ]
                        ),

                        "Mean sparse algebra parameter size (bytes)": (
                            r[
                                "sparse_algebra_parameter_bytes"
                            ]
                        ),

                        "Total public material, dense (bytes)": (
                            r[
                                "total_public_material_dense_bytes"
                            ]
                        ),
                    }

                    for r
                    in results
                ],

                "Table6_Sizes.csv",
            )
        )

        # ----------------------------------------------------
        # Linearization attack
        # ----------------------------------------------------

        tables[7] = (
            self._save_csv(
                [
                    {
                        "n": (
                            r[
                                "n"
                            ]
                        ),

                        "Cryptographic trials": (
                            r[
                                "attack"
                            ][
                                "count"
                            ]
                        ),

                        "Independent Lie algebras for CI": (
                            r[
                                "attack"
                            ][
                                "independent_units"
                            ]
                        ),

                        "Matrix mean (ms)": (
                            r[
                                "matrix_attack"
                            ][
                                "mean"
                            ]
                        ),

                        "Matrix trial-level SD (ms)": (
                            r[
                                "matrix_attack"
                            ][
                                "sd"
                            ]
                        ),

                        "Matrix 95% CI low (ms)": (
                            r[
                                "matrix_attack"
                            ][
                                "ci95_low"
                            ]
                        ),

                        "Matrix 95% CI high (ms)": (
                            r[
                                "matrix_attack"
                            ][
                                "ci95_high"
                            ]
                        ),

                        "Solve mean (ms)": (
                            r[
                                "solve_attack"
                            ][
                                "mean"
                            ]
                        ),

                        "Solve trial-level SD (ms)": (
                            r[
                                "solve_attack"
                            ][
                                "sd"
                            ]
                        ),

                        "Solve 95% CI low (ms)": (
                            r[
                                "solve_attack"
                            ][
                                "ci95_low"
                            ]
                        ),

                        "Solve 95% CI high (ms)": (
                            r[
                                "solve_attack"
                            ][
                                "ci95_high"
                            ]
                        ),

                        "Total attack mean (ms)": (
                            r[
                                "attack"
                            ][
                                "mean"
                            ]
                        ),

                        "Total attack trial-level SD (ms)": (
                            r[
                                "attack"
                            ][
                                "sd"
                            ]
                        ),

                        "Total attack median (ms)": (
                            r[
                                "attack"
                            ][
                                "median"
                            ]
                        ),

                        "Total attack min (ms)": (
                            r[
                                "attack"
                            ][
                                "min"
                            ]
                        ),

                        "Total attack max (ms)": (
                            r[
                                "attack"
                            ][
                                "max"
                            ]
                        ),

                        "Between-algebra SD of attack means (ms)": (
                            r[
                                "attack"
                            ][
                                "between_algebra_sd"
                            ]
                        ),

                        "95% CI low (ms)": (
                            r[
                                "attack"
                            ][
                                "ci95_low"
                            ]
                        ),

                        "95% CI high (ms)": (
                            r[
                                "attack"
                            ][
                                "ci95_high"
                            ]
                        ),

                        "Attack success (%)": (
                            r[
                                "attack_success_rate"
                            ]
                        ),

                        "Singularity verified (%)": (
                            r[
                                "singularity_verified_rate"
                            ]
                        ),

                        "g in kernel (%)": (
                            r[
                                "g_in_kernel_rate"
                            ]
                        ),
                    }

                    for r
                    in results
                ],

                (
                    "Table7_"
                    "Linearization_Attack.csv"
                ),
            )
        )

        # ----------------------------------------------------
        # Rank and centralizer
        # ----------------------------------------------------

        tables[8] = (
            self._save_csv(
                [
                    {
                        "n": (
                            r[
                                "n"
                            ]
                        ),

                        "Mean rank": (
                            r[
                                "mean_rank"
                            ]
                        ),

                        "Mean normalized rank rho_g": (
                            r[
                                "normalized_rank"
                            ]
                        ),

                        "Mean dim C_L(g)": (
                            r[
                                "mean_nullity"
                            ]
                        ),

                        "Mean normalized centralizer delta_g": (
                            r[
                                "normalized_nullity"
                            ]
                        ),
                    }

                    for r
                    in results
                ],

                (
                    "Table8_"
                    "Rank_Centralizer.csv"
                ),
            )
        )

        # ----------------------------------------------------
        # Equivalent-secret forgery
        # ----------------------------------------------------

        tables[9] = (
            self._save_csv(
                [
                    {
                        "n": (
                            r[
                                "n"
                            ]
                        ),

                        "Independent Lie algebras": (
                            r[
                                "algebra_instances"
                            ]
                        ),

                        "Cryptographic trials": (
                            r[
                                "repetitions"
                            ]
                        ),

                        "Compatible secrets recovered": (
                            r[
                                "compatible_secrets"
                            ]
                        ),

                        "Recovered original secret": (
                            r[
                                "original_secret_recovered"
                            ]
                        ),

                        "Equivalent but different secrets": (
                            r[
                                "equivalent_but_different"
                            ]
                        ),

                        "Accepted forged signatures": (
                            r[
                                "accepted_forgeries"
                            ]
                        ),

                        "Forgery rate (%)": (
                            r[
                                "forgery_rate"
                            ]
                        ),

                        "Kernel basis valid (%)": (
                            r[
                                "kernel_basis_valid_rate"
                            ]
                        ),
                    }

                    for r
                    in results
                ],

                (
                    "Table9_"
                    "Equivalent_Secret_"
                    "Forgery.csv"
                ),
            )
        )

        # ----------------------------------------------------
        # Legitimate vs attack cost
        # ----------------------------------------------------

        tables[10] = (
            self._save_csv(
                [
                    {
                        "n": (
                            r[
                                "n"
                            ]
                        ),

                        "T_Legit mean (ms)": (
                            r[
                                "legit_mean"
                            ]
                        ),

                        "T_Lin mean (ms)": (
                            r[
                                "attack"
                            ][
                                "mean"
                            ]
                        ),

                        "R_T": (
                            r[
                                "RT"
                            ]
                        ),
                    }

                    for r
                    in results
                ],

                (
                    "Table10_"
                    "Legitimate_vs_"
                    "Attack.csv"
                ),
            )
        )

        return tables

    # ========================================================
    # Independent algebra summaries
    # ========================================================

    def create_per_algebra_table(
        self,
        results,
    ):

        rows = []

        for r in results:

            for item in (
                r[
                    "algebra_summaries"
                ]
            ):

                rows.append(
                    {
                        "n": (
                            r[
                                "n"
                            ]
                        ),

                        "field_bits": (
                            r[
                                "field_bits"
                            ]
                        ),

                        "center_fraction": (
                            r[
                                "center_fraction"
                            ]
                        ),

                        "target_density": (
                            r[
                                "density"
                            ]
                        ),

                        **item,
                    }
                )

        return self._save_csv(
            rows,

            (
                "Per_Algebra_"
                "Summary.csv"
            ),
        )

    # ========================================================
    # Figure 2:
    # KeyGen / Sign / Verify
    #
    # Error bars = 95% CI calculated from
    # 10 independent Lie algebra means.
    # ========================================================

    def create_performance_chart(
        self,
        results,
    ):

        n_values = [
            r[
                "n"
            ]
            for r
            in results
        ]

        series_data = {
            "Key Generation": (
                "keygen"
            ),
            "Signing": (
                "sign"
            ),
            "Verification": (
                "verify"
            ),
        }

        x = np.arange(
            len(
                n_values
            )
        )

        width = 0.25

        offsets = {
            "Key Generation": (
                -width
            ),
            "Signing": (
                0.0
            ),
            "Verification": (
                width
            ),
        }

        fig, ax = (
            plt.subplots(
                figsize=(
                    10,
                    6,
                )
            )
        )

        for (
            label,
            result_key,
        ) in series_data.items():

            means = np.array(
                [
                    r[
                        result_key
                    ][
                        "mean"
                    ]
                    for r
                    in results
                ],
                dtype=float,
            )

            ci_low = np.array(
                [
                    r[
                        result_key
                    ][
                        "ci95_low"
                    ]
                    for r
                    in results
                ],
                dtype=float,
            )

            ci_high = np.array(
                [
                    r[
                        result_key
                    ][
                        "ci95_high"
                    ]
                    for r
                    in results
                ],
                dtype=float,
            )

            lower_error = (
                means
                - ci_low
            )

            upper_error = (
                ci_high
                - means
            )

            # Numerical safety only.
            lower_error = np.maximum(
                lower_error,
                0.0,
            )

            upper_error = np.maximum(
                upper_error,
                0.0,
            )

            yerr = np.vstack(
                [
                    lower_error,
                    upper_error,
                ]
            )

            bars = ax.bar(
                x
                + offsets[
                    label
                ],

                means,

                width,

                label=label,

                yerr=yerr,

                capsize=4,
            )

            for (
                bar,
                value,
            ) in zip(
                bars,
                means,
            ):

                ax.annotate(
                    f"{value:.3f}",

                    xy=(
                        bar.get_x()
                        + bar.get_width()
                        / 2,

                        value,
                    ),

                    xytext=(
                        0,
                        5,
                    ),

                    textcoords=(
                        "offset points"
                    ),

                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

        ax.set_yscale(
            "log"
        )

        ax.set_xlabel(
            (
                "Lie Algebra "
                "Dimension (n)"
            ),
            fontsize=12,
        )

        ax.set_ylabel(
            (
                "Execution Time "
                "(ms, logarithmic scale)"
            ),
            fontsize=12,
        )

        ax.set_xticks(
            x
        )

        ax.set_xticklabels(
            n_values
        )

        ax.legend()

        ax.grid(
            axis="y",
            which="both",
            linestyle="--",
            alpha=0.35,
        )

        plt.tight_layout()

        fig.savefig(
            self.output_dir
            / (
                "KeyGen_Signing_"
                "Verification.png"
            ),

            dpi=300,

            bbox_inches="tight",
        )

        plt.close(
            fig
        )

    # ========================================================
    # Figure 3:
    # Linearization attack
    #
    # Error bars = 95% CI calculated from
    # 10 independent Lie algebra means.
    # ========================================================

    def create_attack_chart(
        self,
        results,
    ):

        n_values = np.array(
            [
                r[
                    "n"
                ]
                for r
                in results
            ]
        )

        means = np.array(
            [
                r[
                    "attack"
                ][
                    "mean"
                ]
                for r
                in results
            ],
            dtype=float,
        )

        ci_low = np.array(
            [
                r[
                    "attack"
                ][
                    "ci95_low"
                ]
                for r
                in results
            ],
            dtype=float,
        )

        ci_high = np.array(
            [
                r[
                    "attack"
                ][
                    "ci95_high"
                ]
                for r
                in results
            ],
            dtype=float,
        )

        lower_error = (
            means
            - ci_low
        )

        upper_error = (
            ci_high
            - means
        )

        lower_error = np.maximum(
            lower_error,
            0.0,
        )

        upper_error = np.maximum(
            upper_error,
            0.0,
        )

        yerr = np.vstack(
            [
                lower_error,
                upper_error,
            ]
        )

        fig, ax = (
            plt.subplots(
                figsize=(
                    8,
                    6,
                )
            )
        )

        ax.errorbar(
            n_values,
            means,

            yerr=yerr,

            marker="o",

            markersize=7,

            linewidth=2,

            capsize=5,
        )

        ax.set_yscale(
            "log"
        )

        ax.set_xlabel(
            (
                "Lie Algebra "
                "Dimension (n)"
            ),
            fontsize=12,
        )

        ax.set_ylabel(
            (
                "Linearization Attack Time "
                "(ms, logarithmic scale)"
            ),
            fontsize=12,
        )

        ax.set_xticks(
            n_values
        )

        ax.grid(
            True,
            which="both",
            linestyle="--",
            alpha=0.35,
        )

        plt.tight_layout()

        fig.savefig(
            self.output_dir
            / (
                "Linearization_"
                "Attack_Time.png"
            ),

            dpi=300,

            bbox_inches="tight",
        )

        plt.close(
            fig
        )

    # ========================================================
    # Ablation tables
    # ========================================================

    def create_ablation_tables(
        self,
        studies,
    ):

        tables = {}

        for (
            study_name,
            results,
        ) in (
            studies.items()
        ):

            rows = []

            for r in results:

                rows.append(
                    {
                        "Study": (
                            study_name
                        ),

                        "n": (
                            r[
                                "n"
                            ]
                        ),

                        "Field bits": (
                            r[
                                "field_bits"
                            ]
                        ),

                        "Center fraction": (
                            r[
                                "center_fraction"
                            ]
                        ),

                        "Target density": (
                            r[
                                "density"
                            ]
                        ),

                        "Realized density": (
                            r[
                                "realized_density"
                            ]
                        ),

                        "Independent Lie algebras": (
                            r[
                                "algebra_instances"
                            ]
                        ),

                        "Cryptographic trials": (
                            r[
                                "repetitions"
                            ]
                        ),

                        "Attack mean (ms)": (
                            r[
                                "attack"
                            ][
                                "mean"
                            ]
                        ),

                        "Trial-level attack SD (ms)": (
                            r[
                                "attack"
                            ][
                                "sd"
                            ]
                        ),

                        "Between-algebra SD of attack means (ms)": (
                            r[
                                "attack"
                            ][
                                "between_algebra_sd"
                            ]
                        ),

                        "Attack 95% CI low (ms)": (
                            r[
                                "attack"
                            ][
                                "ci95_low"
                            ]
                        ),

                        "Attack 95% CI high (ms)": (
                            r[
                                "attack"
                            ][
                                "ci95_high"
                            ]
                        ),

                        "Mean rank": (
                            r[
                                "mean_rank"
                            ]
                        ),

                        "Mean nullity": (
                            r[
                                "mean_nullity"
                            ]
                        ),

                        "Normalized rank": (
                            r[
                                "normalized_rank"
                            ]
                        ),

                        "Normalized nullity": (
                            r[
                                "normalized_nullity"
                            ]
                        ),

                        "Attack success (%)": (
                            r[
                                "attack_success_rate"
                            ]
                        ),

                        "Forgery rate (%)": (
                            r[
                                "forgery_rate"
                            ]
                        ),
                    }
                )

            tables[
                study_name
            ] = (
                self._save_csv(
                    rows,

                    (
                        f"Ablation_"
                        f"{study_name}.csv"
                    ),
                )
            )

        return tables

    # ========================================================
    # Generate all figures
    # ========================================================

    def create_all_figures(
        self,
        results,
    ):

        self.create_performance_chart(
            results
        )

        self.create_attack_chart(
            results
        )