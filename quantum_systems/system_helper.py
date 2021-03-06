import numba


def check_axis_lengths(arr, length):
    return [length == axis for axis in arr.shape]


def change_module(arr, np):
    return np.asarray(arr) if arr is not None else None


@numba.njit(cache=True)
def delta(p, q):
    return p == q


@numba.njit(cache=True)
def spin_delta(p, q):
    return ((p & 0x1) ^ (q & 0x1)) ^ 0x1


def transform_spf(spf, c, np):
    return np.tensordot(c, spf, axes=((0), (0)))


def transform_bra_spf(bra_spf, c_tilde, np):
    return np.tensordot(c_tilde, bra_spf, axes=((1), (0)))


def transform_one_body_elements(h, c, np, c_tilde=None):
    if c_tilde is None:
        c_tilde = c.conj().T

    return c_tilde @ h @ c


def transform_two_body_elements(u, c, np, c_tilde=None):
    if c_tilde is None:
        c_tilde = c.conj().T

    # abcd, ds -> abcs
    _u = np.tensordot(u, c, axes=(3, 0))
    # abcs, cr -> absr -> abrs
    _u = np.tensordot(_u, c, axes=(2, 0)).transpose(0, 1, 3, 2)
    # abrs, qb -> arsq -> aqrs
    _u = np.tensordot(_u, c_tilde, axes=(1, 1)).transpose(0, 3, 1, 2)
    # pa, aqrs -> pqrs
    _u = np.tensordot(c_tilde, _u, axes=(1, 0))

    return _u


def get_spin_block_slices(n, n_a, l):
    """Function computing the spin-block slicing. We assume that there is an
    equal amount of alpha spin and beta spin orbitals, i.e.,
    `l == l_a * 2 == l_b * 2`, but allow for unequal number of occupied
    orbitals.

    We use an even-odd ordering of the spin-orbitals where alpha orbitals are
    given even indices and beta orbitals are given odd indices.

    Parameters
    ----------
    n : int
        The number of occupied orbitals.
    n_a : int
        The number of occupied orbitals with alpha spin. Note that we require
        `n >= n_a`.
    l : int
        The total number of spin-orbitals.

    Returns
    -------
    tuple
        Collection of the spin-block slices in the ordering (occupied alpha,
        occupied beta, virtual alpha, virtual down).
    """

    assert n >= n_a

    n_b = n - n_a
    l_a = l_b = l // 2

    m_a = l_a - n_a
    m_b = l_b - n_b

    o_a = slice(0, 2 * n_a, 2)
    o_b = slice(1, 2 * n_b + 1, 2)
    v_a = slice(2 * n_a, l, 2)
    v_b = slice(2 * n_b + 1, l, 2)

    assert (o_a.stop - o_a.start) // 2 == n_a
    assert (o_b.stop - o_b.start) // 2 == n_b
    assert (v_a.stop - v_a.start) // 2 == m_a
    assert (v_b.stop - v_b.start) // 2 + 1 == m_b

    return o_a, o_b, v_a, v_b


def add_spin_spf(spf, np):
    new_shape = [spf.shape[0] * 2, *spf.shape[1:]]
    new_spf = np.zeros(tuple(new_shape), dtype=spf.dtype)

    new_spf[::2] = spf
    new_spf[1::2] = spf

    return new_spf


def add_spin_bra_spf(bra_spf, np):
    if bra_spf is None:
        return None

    return add_spin_spf(bra_spf, np)


def add_spin_one_body(h, np):
    return np.kron(h, np.eye(2))


def add_spin_two_body(_u, np):
    u = _u.transpose(1, 3, 0, 2)
    u = np.kron(u, np.eye(2))
    u = u.transpose(2, 3, 0, 1)
    u = np.kron(u, np.eye(2))
    u = u.transpose(0, 2, 1, 3)

    return u


def anti_symmetrize_u(_u):
    return _u - _u.transpose(0, 1, 3, 2)


def compute_particle_density(rho_qp, ket_spf, bra_spf, np):
    assert bra_spf.shape == ket_spf.shape
    assert bra_spf.dtype == ket_spf.dtype

    rho = np.zeros(ket_spf.shape[1:], dtype=ket_spf.dtype)

    for p in range(bra_spf.shape[0]):
        phi_tilde_p = bra_spf[p]

        for q in range(ket_spf.shape[0]):
            phi_q = ket_spf[q]
            rho += phi_tilde_p * rho_qp[q, p] * phi_q

    return rho
