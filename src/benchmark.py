import math
import random
import statistics
import time
from statistics import NormalDist

from .algebra import (
    Class2LieAlgebra,
    vectors_equal,
)
from .attacks import (
    LinearizationAttack,
)
from .crypto import (
    DigitalSignatureScheme,
    serialize_vector,
)


# ============================================================
# Statistical helper functions
# ============================================================

def _student_t_critical_975(df):
    """
    Approximate the two-sided 95% Student-t critical value
    t_(0.975, df) using a Cornish-Fisher expansion.

    For the default design:
        10 independent Lie algebra instances
    we use:
        df = 9
    and obtain approximately:
        t_(0.975, 9) = 2.262
    """

    if df <= 0:
        return 0.0

    z = NormalDist().inv_cdf(0.975)

    v = float(df)

    term1 = (
        z**3 + z
    ) / (
        4.0 * v
    )

    term2 = (
        5.0 * z**5
        + 16.0 * z**3
        + 3.0 * z
    ) / (
        96.0 * v**2
    )

    term3 = (
        3.0 * z**7
        + 19.0 * z**5
        + 17.0 * z**3
        - 15.0 * z
    ) / (
        384.0 * v**3
    )

    return (
        z
        + term1
        + term2
        + term3
    )


def summarize(
    values,
    independent_unit_means=None,
):
    """
    Descriptive statistics are calculated over all
    cryptographic trials.

    The 95% confidence interval is calculated from the
    means of the independent Lie algebra instances.

    Example:

        10 independent Lie algebras
        x
        10 cryptographic trials per algebra

    gives:

        100 trial observations

    but the confidence interval uses:

        N_independent = 10

    algebra-level means.

    This avoids treating repeated trials on the same
    algebra instance as 100 independent algebra samples.
    """

    values = list(values)

    if not values:
        raise ValueError(
            "Cannot summarize an empty sequence."
        )

    count = len(values)

    pooled_mean = statistics.mean(
        values
    )

    median = statistics.median(
        values
    )

    pooled_sd = (
        statistics.stdev(values)
        if count > 1
        else 0.0
    )

    minimum = min(values)
    maximum = max(values)

    # --------------------------------------------------------
    # Cluster-aware / algebra-aware confidence interval
    # --------------------------------------------------------

    if independent_unit_means is None:
        independent_unit_means = values

    independent_unit_means = list(
        independent_unit_means
    )

    independent_count = len(
        independent_unit_means
    )

    independent_mean = statistics.mean(
        independent_unit_means
    )

    between_unit_sd = (
        statistics.stdev(
            independent_unit_means
        )
        if independent_count > 1
        else 0.0
    )

    if independent_count > 1:

        t_critical = (
            _student_t_critical_975(
                independent_count - 1
            )
        )

        standard_error = (
            between_unit_sd
            / math.sqrt(
                independent_count
            )
        )

        half_width = (
            t_critical
            * standard_error
        )

    else:

        t_critical = 0.0
        standard_error = 0.0
        half_width = 0.0

    # Equal number of trials are performed for every
    # algebra instance, so pooled_mean and independent_mean
    # should coincide up to floating-point precision.
    ci_center = independent_mean

    return {
        # Trial-level descriptive statistics
        "count": count,
        "mean": pooled_mean,
        "sd": pooled_sd,
        "median": median,
        "min": minimum,
        "max": maximum,

        # Independent algebra-level statistics
        "independent_units": (
            independent_count
        ),

        "independent_mean": (
            independent_mean
        ),

        "between_algebra_sd": (
            between_unit_sd
        ),

        "ci_standard_error": (
            standard_error
        ),

        "t_critical": (
            t_critical
        ),

        # 95% cluster-aware CI
        "ci95_low": (
            ci_center
            - half_width
        ),

        "ci95_high": (
            ci_center
            + half_width
        ),

        "ci95_half_width": (
            half_width
        ),

        "ci95_basis": (
            "independent Lie algebra means"
        ),
    }


# ============================================================
# Timing helper
# ============================================================

def timed_call(
    func,
    *args,
    **kwargs,
):
    start = (
        time.perf_counter_ns()
    )

    result = func(
        *args,
        **kwargs,
    )

    elapsed_ms = (
        time.perf_counter_ns()
        - start
    ) / 1_000_000

    return (
        result,
        elapsed_ms,
    )


# ============================================================
# Storage helpers
# ============================================================

def private_key_size_bytes(
    algebra
):
    return len(
        serialize_vector(
            [0] * algebra.n,
            algebra.p,
        )
    )


def public_key_payload_size_bytes(
    algebra
):
    return (
        2
        * private_key_size_bytes(
            algebra
        )
    )


def signature_size_bytes(
    algebra
):
    return (
        2
        * private_key_size_bytes(
            algebra
        )
    )


# ============================================================
# Deterministic seed derivation
# ============================================================

def _derive_seed(
    master_seed,
    *parts,
):
    """
    Deterministic seed derivation that does not depend
    on Python's randomized hash().
    """

    seed = (
        master_seed
        & (
            (1 << 63)
            - 1
        )
    )

    for part in parts:

        if isinstance(
            part,
            float,
        ):
            value = int(
                round(
                    part
                    * 1_000_000
                )
            )
        else:
            value = int(
                part
            )

        seed = (
            seed
            * 6364136223846793005
            + value
            + 1442695040888963407
        ) & (
            (1 << 63)
            - 1
        )

    return seed


# ============================================================
# Benchmark runner
# ============================================================

class BenchmarkRunner:

    def __init__(
        self,
        config,
    ):
        self.config = config

    def benchmark_configuration(
        self,
        *,
        n,
        field_bits,
        center_fraction,
        density,
        seed,
        label=None,
    ):

        p = (
            self.config
            .prime_for_bits(
                field_bits
            )
        )

        # ====================================================
        # Trial-level measurements
        # ====================================================

        keygen_times = []
        sign_times = []
        verify_times = []

        matrix_times = []
        solve_times = []
        attack_times = []

        ranks = []
        nullities = []

        realized_densities = []

        dense_structure_sizes = []
        sparse_structure_sizes = []

        # ====================================================
        # Independent algebra-level means
        #
        # These are used for the 95% CI.
        # ====================================================

        algebra_keygen_means = []
        algebra_sign_means = []
        algebra_verify_means = []

        algebra_matrix_means = []
        algebra_solve_means = []
        algebra_attack_means = []

        # ====================================================
        # Success counters
        # ====================================================

        correct_count = 0

        attack_success_count = 0
        compatible_count = 0
        forged_count = 0

        recovered_original_count = 0

        singularity_verified_count = 0
        g_in_kernel_count = 0
        kernel_basis_valid_count = 0

        latest_k_pub = None
        latest_k_priv = None
        latest_attack = None
        latest_algebra = None

        algebra_summaries = []

        # ====================================================
        # Generate independent Lie algebra instances
        # ====================================================

        for algebra_index in range(
            self.config
            .algebra_instances_per_configuration
        ):

            algebra_seed = (
                _derive_seed(
                    seed,
                    n,
                    field_bits,
                    center_fraction,
                    density,
                    algebra_index,
                )
            )

            rng = random.Random(
                algebra_seed
            )

            algebra = (
                Class2LieAlgebra
                .random_algebra(
                    n=n,
                    p=p,
                    rng=rng,
                    center_fraction=(
                        center_fraction
                    ),
                    density=density,
                )
            )

            scheme = (
                DigitalSignatureScheme(
                    algebra,
                    rng,
                )
            )

            attack_engine = (
                LinearizationAttack(
                    algebra
                )
            )

            # ------------------------------------------------
            # Trial measurements belonging to this
            # independent algebra instance
            # ------------------------------------------------

            current_keygen_times = []
            current_sign_times = []
            current_verify_times = []

            current_matrix_times = []
            current_solve_times = []
            current_attack_times = []

            current_ranks = []
            current_nullities = []

            realized_densities.append(
                algebra.bracket_density()
            )

            dense_structure_sizes.append(
                algebra
                .dense_structure_size_bytes()
            )

            sparse_structure_sizes.append(
                algebra
                .sparse_structure_size_bytes()
            )

            # ================================================
            # Cryptographic trials for this fixed algebra
            # ================================================

            for trial_index in range(
                self.config
                .trials_per_algebra
            ):

                message = (
                    f"benchmark-message-"
                    f"{label}-"
                    f"{n}-"
                    f"{field_bits}-"
                    f"{algebra_index}-"
                    f"{trial_index}"
                ).encode()

                # --------------------------------------------
                # Key generation
                # --------------------------------------------

                (
                    (
                        k_pub,
                        k_priv,
                    ),
                    keygen_ms,
                ) = timed_call(
                    scheme.keygen
                )

                # --------------------------------------------
                # Legitimate signature
                # --------------------------------------------

                (
                    sigma,
                    sign_ms,
                ) = timed_call(
                    scheme.sign,
                    k_pub,
                    k_priv,
                    message,
                )

                # --------------------------------------------
                # Verification
                # --------------------------------------------

                (
                    accepted,
                    verify_ms,
                ) = timed_call(
                    scheme.verify,
                    k_pub,
                    message,
                    sigma,
                )

                if accepted:
                    correct_count += 1

                # --------------------------------------------
                # Linearization attack
                # --------------------------------------------

                attack = (
                    attack_engine.run(
                        k_pub
                    )
                )

                # --------------------------------------------
                # Global trial-level timing
                # --------------------------------------------

                keygen_times.append(
                    keygen_ms
                )

                sign_times.append(
                    sign_ms
                )

                verify_times.append(
                    verify_ms
                )

                matrix_times.append(
                    attack[
                        "matrix_ms"
                    ]
                )

                solve_times.append(
                    attack[
                        "solve_ms"
                    ]
                )

                attack_times.append(
                    attack[
                        "total_ms"
                    ]
                )

                ranks.append(
                    attack[
                        "rank"
                    ]
                )

                nullities.append(
                    attack[
                        "nullity"
                    ]
                )

                # --------------------------------------------
                # Current algebra timing
                # --------------------------------------------

                current_keygen_times.append(
                    keygen_ms
                )

                current_sign_times.append(
                    sign_ms
                )

                current_verify_times.append(
                    verify_ms
                )

                current_matrix_times.append(
                    attack[
                        "matrix_ms"
                    ]
                )

                current_solve_times.append(
                    attack[
                        "solve_ms"
                    ]
                )

                current_attack_times.append(
                    attack[
                        "total_ms"
                    ]
                )

                current_ranks.append(
                    attack[
                        "rank"
                    ]
                )

                current_nullities.append(
                    attack[
                        "nullity"
                    ]
                )

                # --------------------------------------------
                # Structural diagnostics
                # --------------------------------------------

                if attack[
                    "singularity_verified"
                ]:
                    singularity_verified_count += 1

                if attack[
                    "g_in_kernel"
                ]:
                    g_in_kernel_count += 1

                if attack[
                    "kernel_basis_valid"
                ]:
                    kernel_basis_valid_count += 1

                # --------------------------------------------
                # Equivalent-secret forgery
                # --------------------------------------------

                if attack[
                    "success"
                ]:

                    attack_success_count += 1
                    compatible_count += 1

                    if vectors_equal(
                        k_priv,
                        attack[
                            "x_prime"
                        ],
                    ):
                        recovered_original_count += 1

                    forged_message = (
                        f"fresh-forged-"
                        f"message-"
                        f"{label}-"
                        f"{n}-"
                        f"{field_bits}-"
                        f"{algebra_index}-"
                        f"{trial_index}"
                    ).encode()

                    forged_sigma = (
                        scheme.sign(
                            k_pub,
                            attack[
                                "x_prime"
                            ],
                            forged_message,
                        )
                    )

                    if scheme.verify(
                        k_pub,
                        forged_message,
                        forged_sigma,
                    ):
                        forged_count += 1

                latest_k_pub = (
                    k_pub
                )

                latest_k_priv = (
                    k_priv
                )

                latest_attack = (
                    attack
                )

                latest_algebra = (
                    algebra
                )

            # =================================================
            # Independent algebra-level means
            # =================================================

            keygen_mean = statistics.mean(
                current_keygen_times
            )

            sign_mean = statistics.mean(
                current_sign_times
            )

            verify_mean = statistics.mean(
                current_verify_times
            )

            matrix_mean = statistics.mean(
                current_matrix_times
            )

            solve_mean = statistics.mean(
                current_solve_times
            )

            attack_mean = statistics.mean(
                current_attack_times
            )

            algebra_keygen_means.append(
                keygen_mean
            )

            algebra_sign_means.append(
                sign_mean
            )

            algebra_verify_means.append(
                verify_mean
            )

            algebra_matrix_means.append(
                matrix_mean
            )

            algebra_solve_means.append(
                solve_mean
            )

            algebra_attack_means.append(
                attack_mean
            )

            algebra_summaries.append(
                {
                    "algebra_index": (
                        algebra_index
                    ),

                    "seed": (
                        algebra_seed
                    ),

                    "realized_density": (
                        algebra
                        .bracket_density()
                    ),

                    "keygen_mean_ms": (
                        keygen_mean
                    ),

                    "sign_mean_ms": (
                        sign_mean
                    ),

                    "verify_mean_ms": (
                        verify_mean
                    ),

                    "matrix_mean_ms": (
                        matrix_mean
                    ),

                    "solve_mean_ms": (
                        solve_mean
                    ),

                    "attack_mean_ms": (
                        attack_mean
                    ),

                    "mean_rank": (
                        statistics.mean(
                            current_ranks
                        )
                    ),

                    "mean_nullity": (
                        statistics.mean(
                            current_nullities
                        )
                    ),

                    "dense_structure_bytes": (
                        algebra
                        .dense_structure_size_bytes()
                    ),

                    "sparse_structure_bytes": (
                        algebra
                        .sparse_structure_size_bytes()
                    ),
                }
            )

        # ====================================================
        # Total number of cryptographic trials
        # ====================================================

        total_trials = (
            self.config
            .algebra_instances_per_configuration
            * self.config
            .trials_per_algebra
        )

        # ====================================================
        # Descriptive statistics + cluster-aware CI
        # ====================================================

        keygen_stats = summarize(
            keygen_times,
            algebra_keygen_means,
        )

        sign_stats = summarize(
            sign_times,
            algebra_sign_means,
        )

        verify_stats = summarize(
            verify_times,
            algebra_verify_means,
        )

        matrix_stats = summarize(
            matrix_times,
            algebra_matrix_means,
        )

        solve_stats = summarize(
            solve_times,
            algebra_solve_means,
        )

        attack_stats = summarize(
            attack_times,
            algebra_attack_means,
        )

        # ====================================================
        # Rank / nullity
        # ====================================================

        mean_rank = (
            statistics.mean(
                ranks
            )
        )

        mean_nullity = (
            statistics.mean(
                nullities
            )
        )

        # ====================================================
        # Legitimate computational cost
        # ====================================================

        legit_mean = (
            keygen_stats[
                "mean"
            ]
            + sign_stats[
                "mean"
            ]
            + verify_stats[
                "mean"
            ]
        )

        representative_algebra = (
            latest_algebra
        )

        # ====================================================
        # Algebra parameter storage
        # ====================================================

        dense_parameter_mean = (
            statistics.mean(
                dense_structure_sizes
            )
        )

        sparse_parameter_mean = (
            statistics.mean(
                sparse_structure_sizes
            )
        )

        public_payload_bytes = (
            public_key_payload_size_bytes(
                representative_algebra
            )
        )

        # ====================================================
        # Result structure
        # ====================================================

        return {

            "label": (
                label
                or "configuration"
            ),

            "algebra": (
                representative_algebra
            ),

            "n": n,
            "p": p,

            "field_bits": (
                field_bits
            ),

            "center_fraction": (
                center_fraction
            ),

            "density": (
                density
            ),

            "realized_density": (
                statistics.mean(
                    realized_densities
                )
            ),

            "algebra_instances": (
                self.config
                .algebra_instances_per_configuration
            ),

            "trials_per_algebra": (
                self.config
                .trials_per_algebra
            ),

            "repetitions": (
                total_trials
            ),

            # Timing
            "keygen": (
                keygen_stats
            ),

            "sign": (
                sign_stats
            ),

            "verify": (
                verify_stats
            ),

            "matrix_attack": (
                matrix_stats
            ),

            "solve_attack": (
                solve_stats
            ),

            "attack": (
                attack_stats
            ),

            # Correctness
            "correctness_rate": (
                correct_count
                / total_trials
                * 100
            ),

            # Attack success
            "attack_success_rate": (
                attack_success_count
                / total_trials
                * 100
            ),

            # Forgery
            "forgery_rate": (
                forged_count
                / compatible_count
                * 100
                if compatible_count
                else 0.0
            ),

            "compatible_secrets": (
                compatible_count
            ),

            "accepted_forgeries": (
                forged_count
            ),

            "original_secret_recovered": (
                recovered_original_count
            ),

            "equivalent_but_different": (
                compatible_count
                - recovered_original_count
            ),

            # Structural checks
            "singularity_verified_rate": (
                singularity_verified_count
                / total_trials
                * 100
            ),

            "g_in_kernel_rate": (
                g_in_kernel_count
                / total_trials
                * 100
            ),

            "kernel_basis_valid_rate": (
                kernel_basis_valid_count
                / total_trials
                * 100
            ),

            # Rank and centralizer
            "mean_rank": (
                mean_rank
            ),

            "mean_nullity": (
                mean_nullity
            ),

            "normalized_rank": (
                mean_rank
                / n
            ),

            "normalized_nullity": (
                mean_nullity
                / n
            ),

            # Storage
            "private_bytes": (
                private_key_size_bytes(
                    representative_algebra
                )
            ),

            "public_payload_bytes": (
                public_payload_bytes
            ),

            "public_bytes": (
                public_payload_bytes
            ),

            "signature_bytes": (
                signature_size_bytes(
                    representative_algebra
                )
            ),

            "dense_algebra_parameter_bytes": (
                dense_parameter_mean
            ),

            "sparse_algebra_parameter_bytes": (
                sparse_parameter_mean
            ),

            "total_public_material_dense_bytes": (
                public_payload_bytes
                + dense_parameter_mean
            ),

            # Legitimate-vs-attack
            "legit_mean": (
                legit_mean
            ),

            "RT": (
                attack_stats[
                    "mean"
                ]
                / legit_mean
                if legit_mean > 0
                else float(
                    "nan"
                )
            ),

            # Independent algebra summaries
            "algebra_summaries": (
                algebra_summaries
            ),

            # Last generated values
            "latest_k_pub": (
                latest_k_pub
            ),

            "latest_k_priv": (
                latest_k_priv
            ),

            "latest_attack": (
                latest_attack
            ),
        }

    # ========================================================
    # Baseline dimension study
    # ========================================================

    def run_dimension_study(
        self
    ):

        results = []

        for index, n in enumerate(
            self.config.dimensions
        ):

            print(
                "Running dimension study: "
                f"n={n}, "
                f"field_bits="
                f"{self.config.field_bits}, "
                f"algebras="
                f"{self.config.algebra_instances_per_configuration}, "
                f"trials/algebra="
                f"{self.config.trials_per_algebra}"
            )

            result = (
                self
                .benchmark_configuration(
                    n=n,

                    field_bits=(
                        self.config
                        .field_bits
                    ),

                    center_fraction=(
                        self.config
                        .center_fraction
                    ),

                    density=(
                        self.config
                        .density
                    ),

                    seed=(
                        _derive_seed(
                            self.config
                            .master_seed,
                            1000,
                            index,
                        )
                    ),

                    label=(
                        "dimension"
                    ),
                )
            )

            results.append(
                result
            )

        return results

    # ========================================================
    # Ablation studies
    # ========================================================

    def run_ablations(
        self
    ):

        baseline_n = (
            self.config
            .ablation_dimension
        )

        baseline_bits = (
            self.config
            .field_bits
        )

        baseline_cf = (
            self.config
            .center_fraction
        )

        baseline_density = (
            self.config
            .density
        )

        studies = {
            "field_bits": [],
            "center_fraction": [],
            "density": [],
        }

        # ----------------------------------------------------
        # Field-size sensitivity
        # ----------------------------------------------------

        for index, bits in enumerate(
            self.config
            .ablation_field_bits
        ):

            studies[
                "field_bits"
            ].append(

                self
                .benchmark_configuration(
                    n=baseline_n,

                    field_bits=bits,

                    center_fraction=(
                        baseline_cf
                    ),

                    density=(
                        baseline_density
                    ),

                    seed=(
                        _derive_seed(
                            self.config
                            .master_seed,
                            2000,
                            index,
                        )
                    ),

                    label=(
                        "field_bits"
                    ),
                )
            )

        # ----------------------------------------------------
        # Center-fraction sensitivity
        # ----------------------------------------------------

        for index, cf in enumerate(
            self.config
            .ablation_center_fractions
        ):

            studies[
                "center_fraction"
            ].append(

                self
                .benchmark_configuration(
                    n=baseline_n,

                    field_bits=(
                        baseline_bits
                    ),

                    center_fraction=cf,

                    density=(
                        baseline_density
                    ),

                    seed=(
                        _derive_seed(
                            self.config
                            .master_seed,
                            3000,
                            index,
                        )
                    ),

                    label=(
                        "center_fraction"
                    ),
                )
            )

        # ----------------------------------------------------
        # Bracket-density sensitivity
        # ----------------------------------------------------

        for index, density in enumerate(
            self.config
            .ablation_densities
        ):

            studies[
                "density"
            ].append(

                self
                .benchmark_configuration(
                    n=baseline_n,

                    field_bits=(
                        baseline_bits
                    ),

                    center_fraction=(
                        baseline_cf
                    ),

                    density=density,

                    seed=(
                        _derive_seed(
                            self.config
                            .master_seed,
                            4000,
                            index,
                        )
                    ),

                    label=(
                        "density"
                    ),
                )
            )

        return studies

    # ========================================================
    # Compatibility helper
    # ========================================================

    def run_all(
        self
    ):
        return (
            self.run_dimension_study()
        )