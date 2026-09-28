import time

from .algebra import mod_inv, vec_sub, vectors_equal


def _validate_linear_system(A, b, p):
    if not isinstance(p, int) or p <= 1:
        raise ValueError("p must be an integer greater than 1.")

    if not A:
        raise ValueError("A must contain at least one row.")

    m = len(A)
    n = len(A[0])

    if n == 0:
        raise ValueError("A must contain at least one column.")

    if any(len(row) != n for row in A):
        raise ValueError("A must be a rectangular matrix.")

    if len(b) != m:
        raise ValueError(
            "The length of b must equal the number of rows of A."
        )

    return m, n


def _rref_augmented_mod_p(A, b, p):
    """
    Compute the reduced row-echelon form of [A | b] over F_p.

    Returns
    -------
    M : list[list[int]]
        Reduced augmented matrix.

    rank : int
        Rank of A.

    pivot_columns : list[int]
        Pivot-column indices.

    free_columns : list[int]
        Non-pivot-column indices.

    consistent : bool
        True if A x = b is consistent.
    """
    m, n = _validate_linear_system(A, b, p)

    M = [
        [value % p for value in A[i]] + [b[i] % p]
        for i in range(m)
    ]

    pivot_columns = []
    pivot_row = 0

    for col in range(n):
        pivot = None

        for r in range(pivot_row, m):
            if M[r][col] % p != 0:
                pivot = r
                break

        if pivot is None:
            continue

        M[pivot_row], M[pivot] = M[pivot], M[pivot_row]

        inv = mod_inv(
            M[pivot_row][col],
            p
        )

        M[pivot_row] = [
            (value * inv) % p
            for value in M[pivot_row]
        ]

        for r in range(m):
            if r == pivot_row:
                continue

            factor = M[r][col] % p

            if factor == 0:
                continue

            M[r] = [
                (
                    M[r][c]
                    - factor * M[pivot_row][c]
                ) % p
                for c in range(n + 1)
            ]

        pivot_columns.append(col)
        pivot_row += 1

        if pivot_row == m:
            break

    rank = len(pivot_columns)

    free_columns = [
        c
        for c in range(n)
        if c not in pivot_columns
    ]

    consistent = True

    for r in range(m):
        zero_left = all(
            M[r][c] % p == 0
            for c in range(n)
        )

        if zero_left and M[r][n] % p != 0:
            consistent = False
            break

    return (
        M,
        rank,
        pivot_columns,
        free_columns,
        consistent,
    )


def _particular_solution_from_rref(
    M,
    n,
    pivot_columns,
    consistent,
    p,
):
    """
    Recover one solution by setting all free variables to zero.
    """
    if not consistent:
        return None

    x = [0] * n

    for row, col in enumerate(pivot_columns):
        x[col] = M[row][n] % p

    return x


def _nullspace_basis_from_rref(
    M,
    n,
    pivot_columns,
    free_columns,
    p,
):
    """
    Construct a basis of ker(A) from the RREF of [A | b].

    The coefficient part of the RREF is independent of b for a
    consistent system, so it can also be used to construct ker(A).
    """
    basis = []

    for free_col in free_columns:
        vector = [0] * n
        vector[free_col] = 1

        for row, pivot_col in enumerate(pivot_columns):
            vector[pivot_col] = (
                -M[row][free_col]
            ) % p

        basis.append(vector)

    return basis


def solve_linear_system_mod_p(A, b, p):
    """
    Solve

        A x = b

    over the finite field F_p.

    For a consistent underdetermined system, one canonical
    representative is returned by setting all free variables to zero.

    Returns
    -------
    x : list[int] or None
        One compatible solution.

    rank : int
        Rank of A.

    pivot_columns : list[int]
        Pivot columns.

    free_columns : list[int]
        Free columns.
    """
    (
        M,
        rank,
        pivot_columns,
        free_columns,
        consistent,
    ) = _rref_augmented_mod_p(A, b, p)

    n = len(A[0])

    x = _particular_solution_from_rref(
        M,
        n,
        pivot_columns,
        consistent,
        p,
    )

    return (
        x,
        rank,
        pivot_columns,
        free_columns,
    )


def nullspace_basis_mod_p(A, p):
    """
    Compute a basis of ker(A) over F_p.
    """
    if not A:
        raise ValueError("A must contain at least one row.")

    zero_rhs = [0] * len(A)

    (
        M,
        _,
        pivot_columns,
        free_columns,
        consistent,
    ) = _rref_augmented_mod_p(
        A,
        zero_rhs,
        p,
    )

    if not consistent:
        raise RuntimeError(
            "The homogeneous system A x = 0 "
            "must always be consistent."
        )

    n = len(A[0])

    return _nullspace_basis_from_rref(
        M,
        n,
        pivot_columns,
        free_columns,
        p,
    )


def mat_vec_mul_mod_p(A, x, p):
    """
    Compute A x over F_p.
    """
    if not A:
        raise ValueError("A must contain at least one row.")

    n = len(A[0])

    if len(x) != n:
        raise ValueError(
            "Vector length must equal the number "
            "of columns of A."
        )

    return [
        sum(
            (a_ij % p) * (x_j % p)
            for a_ij, x_j in zip(row, x)
        ) % p
        for row in A
    ]


class LinearizationAttack:
    """
    Public-key-only linearization attack for the class-2
    nilpotent Lie algebra signature construction.

    For fixed public element g, define

        T_g(x) = [x, g].

    With the standard column-vector convention, the i-th
    column of A_g is the coordinate vector of

        [e_i, g].

    Therefore,

        [x, g]_B = A_g x.

    Since

        y = g + [x, g],

    public-key inversion reduces to

        A_g x' = b,

    where

        b = (y - g)_B.

    Because the Lie bracket is alternating,

        [g, g] = 0,

    and therefore

        g in ker(T_g).

    Hence, for every nonzero g, A_g is necessarily singular.
    If g = 0, then T_g is the zero map and A_g is the zero
    matrix.

    For a valid public key the system remains consistent.
    Its complete solution set is the affine space

        x_0 + ker(T_g)
        = x_0 + C_L(g).
    """

    def __init__(self, algebra):
        self.algebra = algebra

    def run(self, k_pub):
        g = k_pub["g"]
        y = k_pub["y"]

        p = self.algebra.p
        n = self.algebra.n

        if len(g) != n:
            raise ValueError(
                "The public element g must have length algebra.n."
            )

        if len(y) != n:
            raise ValueError(
                "The public element y must have length algebra.n."
            )

        # --------------------------------------------------------
        # Matrix construction
        # --------------------------------------------------------
        start_matrix = time.perf_counter_ns()

        # matrix_Ag uses the correct column convention:
        #
        #   [e_i, g] = sum_j a_{ji} e_j
        #
        # and the i-th column of A_g is
        #
        #   ([e_i, g])_B.
        #
        # Hence:
        #
        #   [x, g]_B = A_g x.
        A_g = self.algebra.matrix_Ag(g)

        b = vec_sub(
            y,
            g,
            p,
        )

        end_matrix = time.perf_counter_ns()

        # --------------------------------------------------------
        # Solve A_g x' = b
        # --------------------------------------------------------
        start_solve = time.perf_counter_ns()

        (
            rref,
            rank,
            pivots,
            free_cols,
            consistent,
        ) = _rref_augmented_mod_p(
            A_g,
            b,
            p,
        )

        x_prime = _particular_solution_from_rref(
            rref,
            n,
            pivots,
            consistent,
            p,
        )

        end_solve = time.perf_counter_ns()

        # --------------------------------------------------------
        # Timings
        # --------------------------------------------------------
        matrix_ms = (
            end_matrix - start_matrix
        ) / 1_000_000

        solve_ms = (
            end_solve - start_solve
        ) / 1_000_000

        total_ms = matrix_ms + solve_ms

        # --------------------------------------------------------
        # Rank / nullity / singularity
        # --------------------------------------------------------
        nullity = n - rank

        is_singular = rank < n

        # --------------------------------------------------------
        # Kernel / centralizer basis
        # --------------------------------------------------------
        kernel_basis = _nullspace_basis_from_rref(
            rref,
            n,
            pivots,
            free_cols,
            p,
        )

        zero = [0] * n

        kernel_basis_valid = all(
            vectors_equal(
                mat_vec_mul_mod_p(
                    A_g,
                    vector,
                    p,
                ),
                zero,
            )
            for vector in kernel_basis
        )

        # --------------------------------------------------------
        # Verify the structural fact g in ker(T_g)
        # --------------------------------------------------------
        A_g_times_g = mat_vec_mul_mod_p(
            A_g,
            g,
            p,
        )

        g_in_kernel = vectors_equal(
            A_g_times_g,
            zero,
        )

        g_is_zero = vectors_equal(
            [value % p for value in g],
            zero,
        )

        # --------------------------------------------------------
        # Verify recovered compatible secret
        # --------------------------------------------------------
        solution_verified = False
        public_relation_verified = False
        success = False

        if x_prime is not None:
            Ax_prime = mat_vec_mul_mod_p(
                A_g,
                x_prime,
                p,
            )

            solution_verified = vectors_equal(
                Ax_prime,
                [value % p for value in b],
            )

            recovered_y = self.algebra.phi(
                x_prime,
                g,
            )

            public_relation_verified = vectors_equal(
                recovered_y,
                y,
            )

            success = (
                consistent
                and solution_verified
                and public_relation_verified
            )

        # --------------------------------------------------------
        # Structural consistency checks
        # --------------------------------------------------------
        expected_singular = True

        singularity_verified = (
            is_singular
            and g_in_kernel
        )

        affine_dimension = nullity

        # Number of compatible representatives is p^nullity.
        # This can be extremely large, so both the dimension and
        # exact integer count are returned.
        compatible_secret_count = pow(
            p,
            nullity,
        )

        return {
            # Recovered compatible secret
            "x_prime": x_prime,

            # Public linear system
            "A_g": A_g,
            "b": b,

            # Linear-algebra properties
            "rank": rank,
            "nullity": nullity,
            "pivots": pivots,
            "free_cols": free_cols,

            # Affine solution / centralizer information
            "kernel_basis": kernel_basis,
            "centralizer_basis": kernel_basis,
            "affine_dimension": affine_dimension,
            "compatible_secret_count": compatible_secret_count,

            # Structural diagnostics
            "consistent": consistent,
            "is_singular": is_singular,
            "expected_singular": expected_singular,
            "singularity_verified": singularity_verified,
            "g_is_zero": g_is_zero,
            "g_in_kernel": g_in_kernel,
            "kernel_basis_valid": kernel_basis_valid,

            # Recovery verification
            "solution_verified": solution_verified,
            "public_relation_verified": public_relation_verified,
            "success": success,

            # Timing
            "matrix_ms": matrix_ms,
            "solve_ms": solve_ms,
            "total_ms": total_ms,
        }