
import math
import random
from dataclasses import dataclass


def mod_inv(a: int, p: int) -> int:
    a %= p

    if a == 0:
        raise ZeroDivisionError(
            "Inverse of zero does not exist."
        )

    return pow(a, p - 2, p)


def _validate_same_length(
    a,
    b,
    name_a="a",
    name_b="b",
):
    if len(a) != len(b):
        raise ValueError(
            f"{name_a} and {name_b} must have "
            f"the same length "
            f"({len(a)} != {len(b)})."
        )


def vec_add(a, b, p):
    _validate_same_length(a, b)

    return [
        (x + y) % p
        for x, y in zip(a, b)
    ]


def vec_sub(a, b, p):
    _validate_same_length(a, b)

    return [
        (x - y) % p
        for x, y in zip(a, b)
    ]


def scalar_mul(c, a, p):
    c %= p

    return [
        (c * x) % p
        for x in a
    ]


def random_vector(
    n,
    p,
    rng: random.Random,
):
    if n <= 0:
        raise ValueError(
            "n must be positive."
        )

    if p <= 1:
        raise ValueError(
            "p must be greater than 1."
        )

    return [
        rng.randrange(p)
        for _ in range(n)
    ]


def vectors_equal(a, b):
    return (
        len(a) == len(b)
        and all(
            x == y
            for x, y in zip(a, b)
        )
    )


def field_byte_length(p):
    return (
        p.bit_length() + 7
    ) // 8


@dataclass
class Class2LieAlgebra:
    n: int
    p: int
    vdim: int
    zdim: int
    structure: dict

    def __post_init__(self):
        if self.n <= 0:
            raise ValueError(
                "n must be positive."
            )

        if self.p <= 2:
            raise ValueError(
                "p must be an odd prime."
            )

        if (
            self.vdim < 0
            or self.zdim < 0
        ):
            raise ValueError(
                "vdim and zdim must be "
                "non-negative."
            )

        if (
            self.vdim + self.zdim
            != self.n
        ):
            raise ValueError(
                "vdim + zdim must equal n."
            )

    @classmethod
    def random_algebra(
        cls,
        n,
        p,
        rng,
        center_fraction=0.25,
        density=0.35,
    ):
        if not (
            0 < center_fraction < 1
        ):
            raise ValueError(
                "center_fraction must lie "
                "strictly between 0 and 1."
            )

        if not (
            0 <= density <= 1
        ):
            raise ValueError(
                "density must lie in [0, 1]."
            )

        zdim = max(
            1,
            int(
                round(
                    n
                    * center_fraction
                )
            )
        )

        vdim = n - zdim

        if vdim < 2:
            raise ValueError(
                "V must have dimension "
                "at least 2."
            )

        structure = {}

        for i in range(vdim):
            for j in range(
                i + 1,
                vdim
            ):
                if (
                    rng.random()
                    <= density
                ):
                    z = [
                        rng.randrange(p)
                        for _ in range(
                            zdim
                        )
                    ]

                    if all(
                        value == 0
                        for value in z
                    ):
                        z[
                            rng.randrange(
                                zdim
                            )
                        ] = rng.randrange(
                            1,
                            p
                        )

                    structure[
                        (i, j)
                    ] = z

        # Prevent a completely abelian
        # experimental instance.
        if not structure:
            structure[
                (0, 1)
            ] = (
                [
                    rng.randrange(
                        1,
                        p
                    )
                ]
                + [0]
                * (zdim - 1)
            )

        return cls(
            n=n,
            p=p,
            vdim=vdim,
            zdim=zdim,
            structure=structure,
        )

    def _validate_vector(
        self,
        x,
        name="vector",
    ):
        if len(x) != self.n:
            raise ValueError(
                f"{name} must contain "
                f"exactly {self.n} "
                f"coordinates; received "
                f"{len(x)}."
            )

    def bracket(self, x, y):
        self._validate_vector(
            x,
            "x"
        )

        self._validate_vector(
            y,
            "y"
        )

        result = [
            0
        ] * self.n

        for (
            (i, j),
            zvec
        ) in self.structure.items():

            coeff = (
                x[i] * y[j]
                - x[j] * y[i]
            ) % self.p

            if coeff == 0:
                continue

            for k in range(
                self.zdim
            ):
                idx = (
                    self.vdim + k
                )

                result[idx] = (
                    result[idx]
                    + coeff
                    * zvec[k]
                ) % self.p

        return result

    def phi(self, x, g):
        self._validate_vector(
            x,
            "x"
        )

        self._validate_vector(
            g,
            "g"
        )

        return vec_add(
            g,
            self.bracket(
                x,
                g
            ),
            self.p,
        )

    def basis_vector(self, i):
        if not (
            0 <= i < self.n
        ):
            raise IndexError(
                "basis index out of range."
            )

        e = [
            0
        ] * self.n

        e[i] = 1

        return e

    def matrix_Ag(self, g):
        """
        Matrix representation of

            T_g(x) = [x, g].

        Column-vector convention:

            [e_i, g]
            =
            sum_j a_{ji} e_j.

        Therefore the i-th column
        of A_g is the coordinate
        vector of [e_i, g].

        Hence

            [x, g]_B = A_g x.
        """

        self._validate_vector(
            g,
            "g"
        )

        columns = [
            self.bracket(
                self.basis_vector(i),
                g
            )
            for i in range(
                self.n
            )
        ]

        return [
            [
                columns[col][row]
                for col
                in range(self.n)
            ]
            for row
            in range(self.n)
        ]

    def dense_structure_size_bytes(
        self
    ):
        """
        Dense canonical storage for
        the structure constants of

            L = V direct-sum Z

        with

            [V,V] subset Z.

        Number of field elements:

            C(vdim,2) * zdim.
        """

        coefficients = (
            math.comb(
                self.vdim,
                2
            )
            * self.zdim
        )

        return (
            coefficients
            * field_byte_length(
                self.p
            )
        )

    def sparse_structure_size_bytes(
        self
    ):
        """
        Approximate serialized storage
        for the sparse representation.

        Python object overhead is not
        included.
        """

        index_width = max(
            1,
            (
                max(
                    self.vdim - 1,
                    0
                ).bit_length()
                + 7
            )
            // 8
        )

        coefficient_width = (
            field_byte_length(
                self.p
            )
        )

        per_entry = (
            2 * index_width
            + self.zdim
            * coefficient_width
        )

        return (
            len(self.structure)
            * per_entry
        )

    def bracket_density(self):
        possible = math.comb(
            self.vdim,
            2
        )

        if possible == 0:
            return 0.0

        return (
            len(self.structure)
            / possible
        )