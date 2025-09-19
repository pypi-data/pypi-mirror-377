import numpy
from numbers import Number
from typing import Optional

from cosapp.drivers.time.base import AbstractTimeDriver, System
from cosapp.drivers.time.implicit import ImplicitTimeDriver


class EulerExplicit(AbstractTimeDriver):
    def __init__(
        self,
        name="Euler",
        owner: Optional[System] = None,
        **options
    ):
        """Initialize driver

        Parameters
        ----------
        owner: System, optional
            :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
        name: str, optional
            Name of the `Driver`.
        **options : Dict[str, Any]
            Optional keywords arguments; may contain time step and interval, with keys `dt` and `time_interval`
        """
        super().__init__(name, owner, **options)

    def _update_transients(self, dt: Number) -> None:
        """
        Time integration of transient variables over time step `dt` by explicit Euler scheme.
        """
        for x in self._transients.values():
            x.value += x.d_dt * dt


class EulerImplicit(ImplicitTimeDriver):
    def __init__(
        self,
        name="Implicit Euler",
        owner: Optional[System] = None,
        **options
    ):
        """Initialize driver

        Parameters
        ----------
        owner: System, optional
            :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
        name: str, optional
            Name of the `Driver`.
        **options : Dict[str, Any]
            Optional keywords arguments; may contain time step and interval, with keys `dt` and `time_interval`
        """
        super().__init__(name, owner, **options)

    def _time_residues(self, dt: float, current: bool):
        """Computes and returns the current- or next-time component
        of the transient problem residue vector.
        
        Parameters:
        -----------
        - dt [float]:
            Time step
        - current [bool]:
            If `True`, compute the current time (n) part of the residues.
            If `False`, compute the time (n + 1) part of the residues.
        """
        time_problem = self._var_manager.problem
        residues = []
        
        if not current:
            for transient in time_problem.transients.values():
                r = transient.value - dt * numpy.ravel(transient.d_dt)
                residues.extend(numpy.ravel(r))

        else:
            for transient in time_problem.transients.values():
                residues.extend(numpy.ravel(transient.value))

        return numpy.array(residues)
