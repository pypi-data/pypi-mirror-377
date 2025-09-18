"""Functional operators."""

import abc

from geomfum._registry import (
    FaceDivergenceOperatorRegistry,
    FaceOrientationOperatorRegistry,
    FaceValuedGradientRegistry,
    WhichRegistryMixins,
)
from geomfum.laplacian import LaplacianFinder, LaplacianSpectrumFinder

# TODO: remove functional; simply use operator


class FunctionalOperator(abc.ABC):
    """Functional operator."""

    # TODO: move to operator
    def __init__(self, shape):
        self._shape = shape

    @abc.abstractmethod
    def __call__(self, point):
        """Apply operator.

        Parameters
        ----------
        point : array-like, shape=[..., n_vertices]
        """
        # TODO: update docstrings


class VectorFieldOperator(abc.ABC):
    """Vector field operator."""

    # TODO: really needed?
    def __init__(self, shape):
        self._shape = shape

    @abc.abstractmethod
    def __call__(self, vector):
        """Apply operator.

        Parameters
        ----------
        point : array-like, shape=[..., n_faces, 3]
        """
        # TODO: update docstrings


class Laplacian(FunctionalOperator):
    """Laplacian.

    Check [P2016]_ for representation choice.

    Parameters
    ----------
    stiffness_matrix : array-like, shape=[n_vertices, n_vertices]
        Stiffness matrix.
    mass_matrix : array-like, shape=[n_vertices, n_vertices]
        Diagonal lumped mass matrix.

    References
    ----------
    .. [P2016] Giuseppe Patané. “STAR - Laplacian Spectral Kernels and Distances
        for Geometry Processing and Shape Analysis.” Computer Graphics Forum 35,
        no. 2 (2016): 599–624. https://doi.org/10.1111/cgf.12866.
    """

    def __init__(self, shape, stiffness_matrix=None, mass_matrix=None):
        super().__init__(shape)
        self._stiffness_matrix = stiffness_matrix
        self._mass_matrix = mass_matrix

        self._basis = None

    @property
    def stiffness_matrix(self):
        """Stiffness matrix.

        Returns
        -------
        stiffness_matrix : array-like, shape=[n_vertices, n_vertices]
            Stiffness matrix.
        """
        if self._stiffness_matrix is None:
            self.find()

        return self._stiffness_matrix

    @property
    def mass_matrix(self):
        """Mass matrix.

        Returns
        -------
        mass_matrix : array-like, shape=[n_vertices, n_vertices]
            Mass matrix.
        """
        if self._mass_matrix is None:
            self.find()

        return self._mass_matrix

    @property
    def basis(self):
        """Laplace eigenbasis.

        Returns
        -------
        basis : LaplaceEigenBasis
            Laplace eigenbasis.
        """
        if self._basis is None:
            self.find_spectrum()

        return self._basis

    def find(self, laplacian_finder=None, recompute=False):
        """Find Laplacian.

        Parameters
        ----------
        laplacian_finder : BaseLaplacianFinder
            Algorithm to find the Laplacian.
        recompute : bool
            Whether to recompute Laplacian if information is cached.

        Returns
        -------
        stiffness_matrix : array-like, shape=[n_vertices, n_vertices]
            Stiffness matrix.
        mass_matrix : array-like, shape=[n_vertices, n_vertices]
            Diagonal lumped mass matrix.
        """
        if (
            not recompute
            and self._stiffness_matrix is not None
            and self._mass_matrix is not None
        ):
            return self._stiffness_matrix, self._mass_matrix

        if laplacian_finder is None:
            laplacian_finder = LaplacianFinder.from_registry(
                mesh=self._shape.is_mesh, which="robust"
            )

        self._stiffness_matrix, self._mass_matrix = laplacian_finder(self._shape)

        return self._stiffness_matrix, self._mass_matrix

    def find_spectrum(
        self,
        spectrum_size=100,
        laplacian_spectrum_finder=None,
        set_as_basis=True,
        recompute=False,
    ):
        """Find Laplacian spectrum.

        Parameters
        ----------
        spectrum_size : int
            Spectrum size. Ignored if ``laplacian_spectrum_finder`` is not None.
        laplacian_spectrum_finder : LaplacianSpectrumFinder
            Algorithm to find Laplacian spectrum.
        set_as_basis : bool
            Whether to set spectrum as basis.
        recompute : bool
            Whether to recompute spectrum if information is cached in basis.

        Returns
        -------
        eigenvals : array-like, shape=[spectrum_size]
            Eigenvalues.
        eigenvecs : array-like, shape=[n_vertices, spectrum_size]
            Eigenvectors.
        """
        if not recompute and self._basis is not None:
            if set_as_basis:
                self._shape.set_basis(self.basis)

            return self.basis.full_vals, self.basis.full_vecs

        if laplacian_spectrum_finder is None:
            laplacian_spectrum_finder = LaplacianSpectrumFinder(
                spectrum_size=spectrum_size,
                nonzero=False,
                fix_sign=False,
            )

        self._basis = laplacian_spectrum_finder(self._shape, as_basis=True)

        if set_as_basis:
            self._shape.set_basis(self.basis)

        return self.basis.full_vals, self.basis.full_vecs

    def __call__(self, point):
        """Apply operator.

        Parameters
        ----------
        point : array-like, shape=[..., n_vertices]
        """
        raise NotImplementedError("Not implemented yet.")


class FaceValuedGradient(WhichRegistryMixins, FunctionalOperator):
    """Gradient of a function on a mesh.

    Computes the gradient of a function on f using linear
    interpolation between vertices.
    """

    _Registry = FaceValuedGradientRegistry


class FaceDivergenceOperator(WhichRegistryMixins, VectorFieldOperator):
    """Divergence of a function on a mesh."""

    _Registry = FaceDivergenceOperatorRegistry


class FaceOrientationOperator(WhichRegistryMixins, VectorFieldOperator):
    r"""Orientation operator associated to a gradient field.

    For a given function :math:`g` on the vertices, this operator linearly computes
    :math:`< \grad(f) x \grad(g)`, n> for each vertex by averaging along the adjacent
    faces.
    In practice, we compute :math:`< n x \grad(f), \grad(g) >` for simpler computation.
    """

    _Registry = FaceOrientationOperatorRegistry
