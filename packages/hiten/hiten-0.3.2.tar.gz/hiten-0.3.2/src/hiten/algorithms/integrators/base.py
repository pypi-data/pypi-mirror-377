"""Provide abstract interfaces for numerical time integration.

References
----------
Hairer, E., Norsett, S. P., & Wanner, G. (1993). "Solving Ordinary
Differential Equations I: Non-stiff Problems".
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Union

import numpy as np

from hiten.algorithms.dynamics.base import _DynamicalSystemProtocol


@dataclass
class _Solution:
    """Store a discrete solution returned by an integrator.

    Parameters
    ----------
    times : numpy.ndarray, shape (n,)
        Monotonically ordered time grid.
    states : numpy.ndarray, shape (n, d)
        State vectors corresponding to *times*.
    derivatives : numpy.ndarray or None, optional, shape (n, d)
        Evaluations of f(t,y) at the stored nodes. When
        available a cubic Hermite interpolant is employed by
        :func:`~hiten.algorithms.integrators.base._Solution.interpolate`; otherwise linear interpolation is used.

    Raises
    ------
    ValueError
        If the lengths of *times*, *states*, or *derivatives* (when provided)
        are inconsistent.

    Notes
    -----
    The class is a :class:`~dataclasses.dataclass` and behaves like an
    immutable record.
    """
    times: np.ndarray
    states: np.ndarray
    derivatives: Optional[np.ndarray] = None
    
    def __post_init__(self):
        """Validate the consistency of times, states, and derivatives arrays"""
        if len(self.times) != len(self.states):
            raise ValueError(
                f"Times and states must have same length: "
                f"{len(self.times)} != {len(self.states)}"
            )
        if self.derivatives is not None and len(self.derivatives) != len(self.times):
            raise ValueError(
                "If provided, derivatives must have the same length as times "
                f"({len(self.derivatives)} != {len(self.times)})"
            )

    def interpolate(self, t: Union[np.ndarray, float]) -> np.ndarray:
        """Evaluate the trajectory at intermediate time points.

        If :attr:`~hiten.algorithms.integrators.base._Solution.derivatives` 
        are provided a cubic Hermite scheme of order three is employed on every step; 
        otherwise straight linear interpolation is used.

        Parameters
        ----------
        t : float or array_like
            Query time or array of times contained in
            [times[0], times[-1]].

        Returns
        -------
        numpy.ndarray
            Interpolated state with shape (d,) when *t* is scalar or
            (m, d) when *t* comprises m points.

        Raises
        ------
        ValueError
            If any entry of *t* lies outside the stored integration interval.

        Examples
        --------
        >>> sol = integrator.integrate(sys, y0, np.linspace(0, 10, 11))
        >>> y_mid = sol.interpolate(5.5)
        """
        t_arr = np.atleast_1d(t).astype(float)

        if np.any(t_arr < self.times[0]) or np.any(t_arr > self.times[-1]):
            raise ValueError("Interpolation times must lie within the solution interval.")

        # Pre-allocate output array.
        n_dim = self.states.shape[1]
        y_out = np.empty((t_arr.size, n_dim), dtype=self.states.dtype)

        # For each query time, locate the bracketing interval.
        idxs = np.searchsorted(self.times, t_arr, side="right") - 1
        idxs = np.clip(idxs, 0, len(self.times) - 2)

        t0 = self.times[idxs]
        t1 = self.times[idxs + 1]
        y0 = self.states[idxs]
        y1 = self.states[idxs + 1]

        h = (t1 - t0)
        s = (t_arr - t0) / h  # Normalised position in interval, 0 <= s <= 1

        if self.derivatives is None:
            # Linear interpolation.
            y_out[:] = y0 + ((y1 - y0).T * s).T
        else:
            f0 = self.derivatives[idxs]
            f1 = self.derivatives[idxs + 1]

            s2 = s * s
            s3 = s2 * s
            h00 = 2 * s3 - 3 * s2 + 1
            h10 = s3 - 2 * s2 + s
            h01 = -2 * s3 + 3 * s2
            h11 = s3 - s2

            # Broadcast the Hermite basis functions to match state dimensions.
            y_out[:] = (
                (h00[:, None] * y0) +
                (h10[:, None] * (h[:, None] * f0)) +
                (h01[:, None] * y1) +
                (h11[:, None] * (h[:, None] * f1))
            )

        # Return scalar shape if scalar input.
        if np.isscalar(t):
            return y_out[0]
        return y_out


class _Integrator(ABC):
    """Define the minimal interface that every concrete integrator must satisfy.

    Parameters
    ----------
    name : str
        Human-readable identifier of the method.
    **options
        Extra keyword arguments left untouched and stored in
        :attr:`~hiten.algorithms.integrators.base._Integrator.options` for later use by subclasses.

    Notes
    -----
    Subclasses *must* implement the abstract members :func:`~hiten.algorithms.integrators.base._Integrator.order` and
    :func:`~hiten.algorithms.integrators.base._Integrator.integrate`.

    Examples
    --------
    Creating a dummy first-order explicit Euler scheme::

        class Euler(_Integrator):
            @property
            def order(self):
                return 1

            def integrate(self, system, y0, t_vals, **kwds):
                y = [y0]
                for t0, t1 in zip(t_vals[:-1], t_vals[1:]):
                    dt = t1 - t0
                    y.append(y[-1] + dt * hiten.system.rhs(t0, y[-1]))
                return _Solution(np.asarray(t_vals), np.asarray(y))
    """
    
    def __init__(self, name: str, **options):
        self.name = name
        self.options = options
    
    @property
    @abstractmethod
    def order(self) -> Optional[int]:
        """Order of accuracy of the integrator.
        
        Returns
        -------
        int or None
            Order of the method, or None if not applicable
        """
        pass
    
    @abstractmethod
    def integrate(
        self,
        system: _DynamicalSystemProtocol,
        y0: np.ndarray,
        t_vals: np.ndarray,
        **kwargs
    ) -> _Solution:
        """Integrate the dynamical system from initial conditions.
        
        Parameters
        ----------
        system : _DynamicalSystemProtocol
            The dynamical system to integrate
        y0 : numpy.ndarray
            Initial state vector, shape (hiten.system.dim,)
        t_vals : numpy.ndarray
            Array of time points at which to evaluate the solution
        **kwargs
            Additional integration options
            
        Returns
        -------
        :class:`~hiten.algorithms.integrators.base._Solution`
            Integration results containing times and states
            
        Raises
        ------
        ValueError
            If the system is incompatible with this integrator
        """
        pass
    
    def validate_system(self, system: _DynamicalSystemProtocol) -> None:
        """Check that *system* complies with :class:`~hiten.algorithms.dynamics.base._DynamicalSystemProtocol`.

        Parameters
        ----------
        system : :class:`~hiten.algorithms.dynamics.base._DynamicalSystemProtocol`
            Candidate system whose suitability is being tested.

        Raises
        ------
        ValueError
            If the required attribute :attr:`~hiten.algorithms.integrators.base._DynamicalSystem.rhs` is absent.
        """
        if not hasattr(system, 'rhs'):
            raise ValueError(f"System must implement 'rhs' method for {self.name}")
    
    def validate_inputs(
        self,
        system: _DynamicalSystemProtocol,
        y0: np.ndarray,
        t_vals: np.ndarray
    ) -> None:
        """Validate that the input arguments form a consistent integration task.

        Parameters
        ----------
        system : :class:`~hiten.algorithms.dynamics.base._DynamicalSystemProtocol`
            System to be integrated.
        y0 : numpy.ndarray
            Initial state vector of length :attr:`~hiten.system.dim`.
        t_vals : numpy.ndarray
            Strictly monotonic array of time nodes with at least two entries.

        Raises
        ------
        ValueError
            If any of the following conditions holds:
            - ``len(y0)`` differs from :attr:`~hiten.system.dim`.
            - ``t_vals`` contains fewer than two points.
            - ``t_vals`` is not strictly monotonic.
        """
        self.validate_system(system)
        
        if len(y0) != system.dim:
            raise ValueError(
                f"Initial state dimension {len(y0)} != system dimension {system.dim}"
            )
        
        if len(t_vals) < 2:
            raise ValueError("Must provide at least 2 time points")
        
        # Check that time values are monotonic (either strictly increasing or decreasing)
        dt = np.diff(t_vals)
        if not (np.all(dt > 0) or np.all(dt < 0)):
            raise ValueError("Time values must be strictly monotonic (either increasing or decreasing)")
