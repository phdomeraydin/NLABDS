from src import (
    ExperimentConfig,
    LieSignatureExperimentApp,
)


if __name__ == "__main__":

    config = ExperimentConfig(

        # ----------------------------------------------------
        # Output directory
        # ----------------------------------------------------
        output_dir="results",

        # ----------------------------------------------------
        # Baseline dimension experiment
        # ----------------------------------------------------
        dimensions=(
            16,
            32,
            64,
            128,
        ),

        # Baseline finite field
        field_bits=61,

        # Baseline structured class-2 Lie algebra parameters
        center_fraction=0.25,
        density=0.35,

        # ----------------------------------------------------
        # Experimental design
        #
        # For each parameter configuration:
        #
        # 10 independent Lie algebras
        # x
        # 10 cryptographic trials per algebra
        #
        # = 100 trials per configuration
        # ----------------------------------------------------
        algebra_instances_per_configuration=10,
        trials_per_algebra=10,

        # ----------------------------------------------------
        # Reproducibility
        # ----------------------------------------------------
        master_seed=20260824,

        # ----------------------------------------------------
        # ABLATION / PARAMETER-SENSITIVITY STUDIES
        # ----------------------------------------------------
        run_ablations=True,

        # All sensitivity studies use n = 64
        # unless dimension itself is being studied.
        ablation_dimension=64,

        # ----------------------------------------------------
        # 1. Field-size sensitivity
        #
        # n = 64
        # center_fraction = 0.25
        # density = 0.35
        #
        # Only field size changes.
        # ----------------------------------------------------
        ablation_field_bits=(
            61,
            127,
            255,
        ),

        # ----------------------------------------------------
        # 2. Central-fraction sensitivity
        #
        # n = 64
        # field_bits = 61
        # density = 0.35
        #
        # Only dim(Z)/n changes.
        # ----------------------------------------------------
        ablation_center_fractions=(
            0.125,
            0.25,
            0.375,
            0.50,
        ),

        # ----------------------------------------------------
        # 3. Bracket-density sensitivity
        #
        # n = 64
        # field_bits = 61
        # center_fraction = 0.25
        #
        # Only bracket density changes.
        # ----------------------------------------------------
        ablation_densities=(
            0.15,
            0.35,
            0.55,
            0.75,
        ),
    )

    # --------------------------------------------------------
    # Create and run the complete experiment application
    # --------------------------------------------------------
    app = LieSignatureExperimentApp(
        config
    )

    results, tables, ablation_results = app.run()

    # --------------------------------------------------------
    # Final terminal summary
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("EXPERIMENTS COMPLETED")
    print("=" * 70)

    print(
        "\nBaseline dimension study:"
    )

    for result in results:

        print(
            f"n={result['n']:>3} | "
            f"trials={result['repetitions']:>3} | "
            f"attack success="
            f"{result['attack_success_rate']:.1f}% | "
            f"forgery="
            f"{result['forgery_rate']:.1f}% | "
            f"rank="
            f"{result['mean_rank']:.2f} | "
            f"nullity="
            f"{result['mean_nullity']:.2f} | "
            f"attack mean="
            f"{result['attack']['mean']:.6f} ms"
        )

    # --------------------------------------------------------
    # Ablation summary
    # --------------------------------------------------------
    if ablation_results is not None:

        print(
            "\n" + "=" * 70
        )

        print(
            "FIELD-SIZE SENSITIVITY"
        )

        print(
            "=" * 70
        )

        for result in (
            ablation_results[
                "field_bits"
            ]
        ):

            print(
                f"field_bits="
                f"{result['field_bits']:>3} | "
                f"attack mean="
                f"{result['attack']['mean']:.6f} ms | "
                f"SD="
                f"{result['attack']['sd']:.6f} | "
                f"rank="
                f"{result['mean_rank']:.2f} | "
                f"nullity="
                f"{result['mean_nullity']:.2f} | "
                f"success="
                f"{result['attack_success_rate']:.1f}% | "
                f"forgery="
                f"{result['forgery_rate']:.1f}%"
            )

        print(
            "\n" + "=" * 70
        )

        print(
            "CENTER-FRACTION SENSITIVITY"
        )

        print(
            "=" * 70
        )

        for result in (
            ablation_results[
                "center_fraction"
            ]
        ):

            print(
                f"center_fraction="
                f"{result['center_fraction']:.3f} | "
                f"attack mean="
                f"{result['attack']['mean']:.6f} ms | "
                f"rank="
                f"{result['mean_rank']:.2f} | "
                f"nullity="
                f"{result['mean_nullity']:.2f} | "
                f"normalized rank="
                f"{result['normalized_rank']:.4f} | "
                f"normalized nullity="
                f"{result['normalized_nullity']:.4f} | "
                f"success="
                f"{result['attack_success_rate']:.1f}% | "
                f"forgery="
                f"{result['forgery_rate']:.1f}%"
            )

        print(
            "\n" + "=" * 70
        )

        print(
            "BRACKET-DENSITY SENSITIVITY"
        )

        print(
            "=" * 70
        )

        for result in (
            ablation_results[
                "density"
            ]
        ):

            print(
                f"density="
                f"{result['density']:.2f} | "
                f"realized="
                f"{result['realized_density']:.4f} | "
                f"attack mean="
                f"{result['attack']['mean']:.6f} ms | "
                f"rank="
                f"{result['mean_rank']:.2f} | "
                f"nullity="
                f"{result['mean_nullity']:.2f} | "
                f"success="
                f"{result['attack_success_rate']:.1f}% | "
                f"forgery="
                f"{result['forgery_rate']:.1f}%"
            )

    print(
        "\n" + "=" * 70
    )

    print(
        "All CSV tables and PNG figures "
        "have been saved in the results folder."
    )

    print(
        "=" * 70
    )