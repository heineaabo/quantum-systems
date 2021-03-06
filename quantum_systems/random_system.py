from quantum_systems import QuantumSystem


class RandomSystem(QuantumSystem):
    """A system consisting of random matrix elements satisfying the symmetries
    of the second quantized integral elements. The purpose of this system is for
    unit testing of purely mathematical methods ignoring inherent symmetries in
    specific systems.
    """

    def setup_system(self, **kwargs):
        """Function creating a system consisting of random matrix elements."""

        u_kwargs = kwargs.copy()

        # Remove the anti-symmetrize argument for the one-body integrals
        if kwargs.get("anti_symmetrize") is not None:
            kwargs.pop("anti_symmetrize")

        self.set_h(**kwargs)
        self.set_u(**u_kwargs)
        self.set_s(**kwargs)
        self.set_dipole_moment(**kwargs)
        self.set_nuclear_repulsion_energy()

    def set_h(self, **kwargs):
        """Function setting up random one-body Hamiltonian matrix elements. The
        arguments are the same as for the QuantumSystem-class.

        See Also
        --------
        QuantumSystem.set_h : Set one-body Hamiltonian.
        """

        shape = (self.l, self.l)

        if kwargs.get("add_spin"):
            shape = (self.l // 2, self.l // 2)

        args = [get_random_elements(shape, self.np)]
        super().set_h(*args, **kwargs)

    def set_u(self, **kwargs):
        """Function setting up random two-body Hamiltonian matrix elements. The
        arguments are the same as for the QuantumSystem-class.

        See Also
        --------
        QuantumSystem.set_u : Set two-body Hamiltonian.
        """

        shape = [self.l for i in range(4)]

        if kwargs.get("add_spin"):
            shape = [self.l // 2 for i in range(4)]

        u = get_random_elements(shape, self.np)
        u = 0.5 * (u + u.transpose(1, 0, 3, 2))

        args = [u]
        super().set_u(*args, **kwargs)

    def set_s(self, *args, **kwargs):
        """Function setting up random overlap matrix elements. The arguments
        are the same as for the QuantumSystem-class.

        See Also
        --------
        QuantumSystem.set_s : Set overlap matrix elements.
        """

        shape = (self.l, self.l)

        if kwargs.get("add_spin"):
            shape = (self.l // 2, self.l // 2)

        args = [get_random_elements(shape, self.np)]
        super().set_s(*args, **kwargs)

    def set_dipole_moment(self, *args, dim=3, **kwargs):
        """Function setting up random dipole moment matrix elements. The
        arguments are the same as for the QuantumSystem-class.

        Parameters
        ----------
        dim : int
            The number of dimensions of the system.

        See Also
        --------
        QuantumSystem.set_dipole_moment : Set dipole moment matrix elements.
        """

        shape = (dim, self.l, self.l)

        if kwargs.get("add_spin"):
            shape = (dim, self.l // 2, self.l // 2)

        args = [get_random_elements(shape, self.np)]
        super().set_dipole_moment(*args, **kwargs)

    def set_nuclear_repulsion_energy(self, *args, **kwargs):
        """Function setting up a random nuclear repulsion energy. The arguments
        are the same as for the QuantumSystem-class.

        See Also
        --------
        QuantumSystem.set_nuclear_repulsion_energy : Set nuclear repulsion
        energy.
        """
        if len(args) == 0:
            args = [self.np.random.random()]

        super().set_nuclear_repulsion_energy(*args, **kwargs)


def get_random_elements(shape, np):
    """Function creating a complex array representing random matrix elements of
    a given shape.

    Parameters
    ----------
    shape : tuple or int
        The shape of the array.
    np : array module

    Returns
    -------
    out : ndarray
        A complex, random array of given shape.
    """

    return np.random.random(shape) + 1j * np.random.random(shape)
