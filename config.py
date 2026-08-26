from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentConfig:
    """
    Configuration class for the Lie algebra digital signature experiments.
    """

    # ============================================================
    # Output directory
    # ============================================================

    output_dir: Path | str = Path("results")

    # ============================================================
    # Experimental parameters
    # ============================================================

    # Lie algebra dimensions
    dimensions: tuple[int, ...] = (
        16,
        32,
        64,
        128
    )

    # Finite-field bit length
    field_bits: int = 61

    # Number of repetitions for each dimension
    repetitions: int = 30

    # Number of forgery tests
    forgery_tests: int = 30

    # ============================================================
    # Reproducibility
    # ============================================================

    # Master random seed
    master_seed: int = 20260824

    # ============================================================
    # Class-2 Lie algebra generation parameters
    # ============================================================

    # Approximate fraction of the algebra used as the center
    center_fraction: float = 0.25

    # Density of randomly generated structure constants
    density: float = 0.35

    # ============================================================
    # Prime moduli
    # ============================================================

    primes: dict[int, int] = field(
        default_factory=lambda: {
            61: (1 << 61) - 1,
            127: (1 << 127) - 1,
            255: (1 << 255) - 19,
        }
    )

    # ============================================================
    # Prime property
    # ============================================================

    @property
    def prime(self) -> int:
        """
        Return the prime modulus corresponding to field_bits.
        """

        if self.field_bits not in self.primes:
            raise ValueError(
                f"No prime modulus is defined for "
                f"field_bits={self.field_bits}"
            )

        return self.primes[self.field_bits]

    # ============================================================
    # Output directory preparation
    # ============================================================

    def prepare_output_dir(self) -> Path:
        """
        Create the output directory if it does not exist.

        output_dir may be supplied either as a string
        or as a pathlib.Path object.
        """

        self.output_dir = Path(self.output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        return self.output_dir