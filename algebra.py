import random
from dataclasses import dataclass


def mod_inv(a: int, p: int) -> int:
    a %= p
    if a == 0:
        raise ZeroDivisionError("Inverse of zero does not exist.")
    return pow(a, p - 2, p)


def vec_add(a, b, p):
    return [(x + y) % p for x, y in zip(a, b)]


def vec_sub(a, b, p):
    return [(x - y) % p for x, y in zip(a, b)]


def scalar_mul(c, a, p):
    c %= p
    return [(c * x) % p for x in a]


def random_vector(n, p, rng: random.Random):
    return [rng.randrange(p) for _ in range(n)]


def vectors_equal(a, b):
    return all(x == y for x, y in zip(a, b))


@dataclass
class Class2LieAlgebra:
    n: int
    p: int
    vdim: int
    zdim: int
    structure: dict

    @classmethod
    def random_algebra(cls, n, p, rng, center_fraction=0.25, density=0.35):
        zdim = max(1, int(round(n * center_fraction)))
        vdim = n - zdim
        if vdim < 2:
            raise ValueError("V must have dimension at least 2.")

        structure = {}
        for i in range(vdim):
            for j in range(i + 1, vdim):
                if rng.random() <= density:
                    z = [rng.randrange(p) for _ in range(zdim)]
                    if all(value == 0 for value in z):
                        z[rng.randrange(zdim)] = rng.randrange(1, p)
                    structure[(i, j)] = z

        if not structure:
            structure[(0, 1)] = [rng.randrange(1, p)] + [0] * (zdim - 1)

        return cls(n=n, p=p, vdim=vdim, zdim=zdim, structure=structure)

    def bracket(self, x, y):
        result = [0] * self.n
        for (i, j), zvec in self.structure.items():
            coeff = (x[i] * y[j] - x[j] * y[i]) % self.p
            if coeff == 0:
                continue
            for k in range(self.zdim):
                idx = self.vdim + k
                result[idx] = (result[idx] + coeff * zvec[k]) % self.p
        return result

    def phi(self, x, g):
        return vec_add(g, self.bracket(x, g), self.p)

    def basis_vector(self, i):
        e = [0] * self.n
        e[i] = 1
        return e

    def matrix_Ag(self, g):
        columns = [self.bracket(self.basis_vector(i), g) for i in range(self.n)]
        return [[columns[col][row] for col in range(self.n)] for row in range(self.n)]
