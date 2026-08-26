import hashlib

from .algebra import random_vector, scalar_mul, vec_add, vec_sub, vectors_equal


def field_byte_length(p):
    return (p.bit_length() + 7) // 8


def serialize_vector(v, p):
    width = field_byte_length(p)
    return b"".join(int(x % p).to_bytes(width, "big") for x in v)


def hash_to_field(message, t, p):
    digest = hashlib.sha256(message + serialize_vector(t, p)).digest()
    return int.from_bytes(digest, "big") % p


class DigitalSignatureScheme:
    def __init__(self, algebra, rng):
        self.algebra = algebra
        self.rng = rng

    def keygen(self):
        x = random_vector(self.algebra.n, self.algebra.p, self.rng)
        g = random_vector(self.algebra.n, self.algebra.p, self.rng)
        y = self.algebra.phi(x, g)
        params = {
            "p": self.algebra.p,
            "n": self.algebra.n,
            "c": 2,
            "vdim": self.algebra.vdim,
            "zdim": self.algebra.zdim,
        }
        return {"g": g, "y": y, "params": params}, x

    def sign(self, k_pub, k_priv, message):
        g = k_pub["g"]
        r = random_vector(self.algebra.n, self.algebra.p, self.rng)
        t = self.algebra.phi(r, g)
        h = hash_to_field(message, t, self.algebra.p)
        s = vec_add(r, scalar_mul(h, k_priv, self.algebra.p), self.algebra.p)
        return {"t": t, "s": s}

    def verify(self, k_pub, message, sigma):
        g, y = k_pub["g"], k_pub["y"]
        t, s = sigma["t"], sigma["s"]
        h = hash_to_field(message, t, self.algebra.p)
        u = self.algebra.phi(s, g)
        y_minus_g = vec_sub(y, g, self.algebra.p)
        rhs = vec_add(t, scalar_mul(h, y_minus_g, self.algebra.p), self.algebra.p)
        return vectors_equal(u, rhs)
