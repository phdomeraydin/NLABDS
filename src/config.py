from dataclasses import (
    dataclass,
    field,
)
from pathlib import Path


@dataclass
class ExperimentConfig:
    """
    Experimental configuration.

    Every parameter configuration
    is evaluated using multiple
    independently generated
    Lie-algebra instances.

    Several cryptographic trials
    are then performed for each
    fixed algebra instance.
    """

    output_dir: Path | str = (
        Path("results")
    )

    # ========================================================
    # Main dimension experiment
    # ========================================================

    dimensions: tuple[
        int,
        ...
    ] = (
        16,
        32,
        64,
        128,
    )

    field_bits: int = 61

    center_fraction: float = (
        0.25
    )

    density: float = 0.35

    # ========================================================
    # Independent experimental instances
    # ========================================================

    algebra_instances_per_configuration: int = (
        10
    )

    trials_per_algebra: int = (
        10
    )

    # ========================================================
    # Reproducibility
    # ========================================================

    master_seed: int = (
        20260824
    )

    # ========================================================
    # Optional ablation studies
    # ========================================================

    run_ablations: bool = False

    ablation_dimension: int = 64

    ablation_field_bits: tuple[
        int,
        ...
    ] = (
        61,
        127,
        255,
    )

    ablation_center_fractions: tuple[
        float,
        ...
    ] = (
        0.125,
        0.25,
        0.375,
        0.50,
    )

    ablation_densities: tuple[
        float,
        ...
    ] = (
        0.15,
        0.35,
        0.55,
        0.75,
    )

    # ========================================================
    # Prime moduli
    # ========================================================

    primes: dict[
        int,
        int
    ] = field(
        default_factory=lambda: {
            61: (
                (1 << 61)
                - 1
            ),
            127: (
                (1 << 127)
                - 1
            ),
            255: (
                (1 << 255)
                - 19
            ),
        }
    )

    def __post_init__(self):
        if not self.dimensions:
            raise ValueError(
                "dimensions must "
                "not be empty."
            )

        if (
            self.algebra_instances_per_configuration
            <= 0
        ):
            raise ValueError(
                "algebra_instances_per_"
                "configuration must "
                "be positive."
            )

        if (
            self.trials_per_algebra
            <= 0
        ):
            raise ValueError(
                "trials_per_algebra "
                "must be positive."
            )

        if not (
            0
            < self.center_fraction
            < 1
        ):
            raise ValueError(
                "center_fraction "
                "must lie strictly "
                "between 0 and 1."
            )

        if not (
            0
            <= self.density
            <= 1
        ):
            raise ValueError(
                "density must lie "
                "in [0, 1]."
            )

        self.prime_for_bits(
            self.field_bits
        )

    @property
    def prime(self):
        return self.prime_for_bits(
            self.field_bits
        )

    @property
    def repetitions(self):
        return (
            self.algebra_instances_per_configuration
            * self.trials_per_algebra
        )

    def prime_for_bits(
        self,
        field_bits,
    ):
        if (
            field_bits
            not in self.primes
        ):
            raise ValueError(
                "No prime modulus "
                "is defined for "
                f"field_bits="
                f"{field_bits}."
            )

        return self.primes[
            field_bits
        ]

    def prepare_output_dir(
        self
    ):
        self.output_dir = Path(
            self.output_dir
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        return self.output_dir