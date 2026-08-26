import time

from .algebra import mod_inv, vec_sub, vectors_equal


def solve_linear_system_mod_p(A, b, p):
    m, n = len(A), len(A[0])
    M = [[value % p for value in A[i]] + [b[i] % p] for i in range(m)]
    pivot_columns = []
    row = 0

    for col in range(n):
        pivot = next((r for r in range(row, m) if M[r][col] % p != 0), None)
        if pivot is None:
            continue
        M[row], M[pivot] = M[pivot], M[row]
        inv = mod_inv(M[row][col], p)
        M[row] = [(value * inv) % p for value in M[row]]

        for r in range(m):
            if r == row:
                continue
            factor = M[r][col] % p
            if factor == 0:
                continue
            M[r] = [(M[r][c] - factor * M[row][c]) % p for c in range(n + 1)]

        pivot_columns.append(col)
        row += 1
        if row == m:
            break

    rank = len(pivot_columns)
    for r in range(rank, m):
        if all(M[r][c] % p == 0 for c in range(n)) and M[r][n] % p != 0:
            return None, rank, pivot_columns, []

    free_columns = [c for c in range(n) if c not in pivot_columns]
    x = [0] * n
    for r, col in enumerate(pivot_columns):
        x[col] = M[r][n] % p
    return x, rank, pivot_columns, free_columns


class LinearizationAttack:
    def __init__(self, algebra):
        self.algebra = algebra

    def run(self, k_pub):
        g, y = k_pub["g"], k_pub["y"]

        start_matrix = time.perf_counter_ns()
        A_g = self.algebra.matrix_Ag(g)
        b = vec_sub(y, g, self.algebra.p)
        end_matrix = time.perf_counter_ns()

        start_solve = time.perf_counter_ns()
        x_prime, rank, pivots, free_cols = solve_linear_system_mod_p(A_g, b, self.algebra.p)
        end_solve = time.perf_counter_ns()

        matrix_ms = (end_matrix - start_matrix) / 1_000_000
        solve_ms = (end_solve - start_solve) / 1_000_000
        success = False
        if x_prime is not None:
            success = vectors_equal(self.algebra.phi(x_prime, g), y)

        return {
            "x_prime": x_prime,
            "A_g": A_g,
            "b": b,
            "rank": rank,
            "nullity": self.algebra.n - rank,
            "matrix_ms": matrix_ms,
            "solve_ms": solve_ms,
            "total_ms": matrix_ms + solve_ms,
            "success": success,
            "pivots": pivots,
            "free_cols": free_cols,
        }
