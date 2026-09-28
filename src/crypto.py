
import hashlib

from .algebra import (
    random_vector,
    scalar_mul,
    vec_add,
    vec_sub,
    vectors_equal,
)


def field_byte_length(p):
    return (
        p.bit_length() + 7
    ) // 8


def serialize_vector(v, p):
    """
    Canonical encoding of a vector
    over F_p.

    The basis order is fixed.

    Every coefficient is first mapped
    to its unique representative in

        {0, ..., p-1}

    and then encoded using a fixed-width
    unsigned big-endian representation.

    For

        p = 2^61 - 1

    this gives exactly 8 bytes per
    coefficient.
    """

    if p <= 1:
        raise ValueError(
            "p must be greater than 1."
        )

    width = field_byte_length(p)

    return b"".join(
        int(
            x % p
        ).to_bytes(
            width,
            "big",
            signed=False,
        )
        for x in v
    )


def hash_to_field(
    message,
    t,
    p,
):
    if not isinstance(
        message,
        (
            bytes,
            bytearray,
        )
    ):
        raise TypeError(
            "message must be "
            "bytes-like."
        )

    encoded_t = serialize_vector(
        t,
        p,
    )

    digest = hashlib.sha256(
        bytes(message)
        + encoded_t
    ).digest()

    return (
        int.from_bytes(
            digest,
            "big"
        )
        % p
    )


class DigitalSignatureScheme:

    def __init__(
        self,
        algebra,
        rng,
    ):
        self.algebra = algebra
        self.rng = rng

    def _validate_element(
        self,
        x,
        name,
    ):
        if (
            len(x)
            != self.algebra.n
        ):
            raise ValueError(
                f"{name} must contain "
                f"{self.algebra.n} "
                f"coordinates."
            )

    def keygen(self):
        x = random_vector(
            self.algebra.n,
            self.algebra.p,
            self.rng,
        )

        g = random_vector(
            self.algebra.n,
            self.algebra.p,
            self.rng,
        )

        y = self.algebra.phi(
            x,
            g,
        )

        params = {
            "p": self.algebra.p,
            "n": self.algebra.n,
            "c": 2,
            "vdim": (
                self.algebra.vdim
            ),
            "zdim": (
                self.algebra.zdim
            ),
            "basis_order": tuple(
                range(
                    self.algebra.n
                )
            ),
            "encoding": {
                "byte_order": (
                    "big"
                ),
                "coefficient_width": (
                    field_byte_length(
                        self.algebra.p
                    )
                ),
                "canonical_representatives": (
                    "0,...,p-1"
                ),
            },
        }

        return {
            "g": g,
            "y": y,
            "params": params,
        }, x

    def sign(
        self,
        k_pub,
        k_priv,
        message,
    ):
        g = k_pub["g"]

        self._validate_element(
            g,
            "g"
        )

        self._validate_element(
            k_priv,
            "k_priv"
        )

        r = random_vector(
            self.algebra.n,
            self.algebra.p,
            self.rng,
        )

        t = self.algebra.phi(
            r,
            g,
        )

        h = hash_to_field(
            message,
            t,
            self.algebra.p,
        )

        hx = scalar_mul(
            h,
            k_priv,
            self.algebra.p,
        )

        s = vec_add(
            r,
            hx,
            self.algebra.p,
        )

        return {
            "t": t,
            "s": s,
        }

    def verify(
        self,
        k_pub,
        message,
        sigma,
    ):
        g = k_pub["g"]
        y = k_pub["y"]

        t = sigma["t"]
        s = sigma["s"]

        self._validate_element(
            g,
            "g"
        )

        self._validate_element(
            y,
            "y"
        )

        self._validate_element(
            t,
            "t"
        )

        self._validate_element(
            s,
            "s"
        )

        h = hash_to_field(
            message,
            t,
            self.algebra.p,
        )

        u = self.algebra.phi(
            s,
            g,
        )

        y_minus_g = vec_sub(
            y,
            g,
            self.algebra.p,
        )

        rhs = vec_add(
            t,
            scalar_mul(
                h,
                y_minus_g,
                self.algebra.p,
            ),
            self.algebra.p,
        )

        return vectors_equal(
            u,
            rhs,
        )