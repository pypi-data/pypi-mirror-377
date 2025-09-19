import numpy
from copy import deepcopy
from typing import Any, Optional

from cosapp.core.numerics.basics import MathematicalProblem
from cosapp.core.numerics.boundary import Boundary
from cosapp.drivers.driver import Driver, System

import logging
logger = logging.getLogger(__name__)


class RunOnce(Driver):
    """Driver running the model on its `System` owner.

    Parameters
    ----------
    name : str
        Name of the driver
    owner : System, optional
        :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
    **kwargs : Any
        Keyword arguments will be used to set driver options
    """

    __slots__ = ('initial_values', 'solution')

    def __init__(
        self,
        name: str,
        owner: Optional[System] = None,
        **options
    ) -> None:
        """Initialize driver

        Parameters
        ----------
        name: str, optional
            Name of the `Driver`.
        owner: System, optional
            :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`.
        **kwargs:
            Additional keywords arguments forwarded to base class.
        """
        super().__init__(name, owner, **options)
        
        self.initial_values: dict[str, Boundary] = dict()  # Initial guess for the iteratives
        self.solution: dict[str, float] = dict()  # Dictionary (name, value) of the latest solution reached

    def set_init(self, modifications: dict[str, Any]) -> None:
        """Define initial values for one or more variables.

        The variable can be contextual `child1.port2.var`. The only rule is that it should belong to
        the owner `System` of this driver or any of its descendants.

        Parameters
        ----------
        modifications : dict[str, Any]
            Dictionary of (variable name, value)

        Examples
        --------
        >>> driver.set_init({'myvar': 42, 'dummy': 'banana'})
        """
        if self.owner is None:
            raise AttributeError(
                f"Driver {self.name!r} must be attached to a System to be assigned initial values."
            )

        if not isinstance(modifications, dict):
            raise TypeError(
                "Initial values must be specified through a dictionary of the kind {varname: value}."
            )

        for variable, value in modifications.items():
            boundary = Boundary(self.owner, variable, default=value, inputs_only=False)

            self.initial_values[boundary.name] = boundary
            boundary.set_to_default()

            # Setting a new initial value implies, we will use the init and so the solution is cleared
            self.solution.clear()

    def get_init(self, force_init: bool = False) -> numpy.ndarray:
        """Get the System iteratives initial values for this driver.

        Parameters
        ----------
        force_init : bool, optional
            Force the initial values to be used. Default is False.

        Returns
        -------
        numpy.ndarray
            List of iteratives initial values,
            in the same order as the unknowns in `get_problem()`.
        """
        full_init = numpy.empty(0)
        problem = self.get_problem()

        for name, unknown in problem.unknowns.items():
            if not force_init and name in self.solution:
                # We ran successfully at least once and are environmental friendly
                data = self.solution[name]
            else:  # User wants the init or first simulation or crash
                if name.startswith(self.name):
                    name = name[len(self.name) + 1 : -1]

                if name in self.initial_values:
                    boundary = self.initial_values[name]
                    umask = unknown.mask if not unknown._is_scalar else numpy.empty(0)
                    bmask = boundary.mask if not boundary._is_scalar else numpy.empty(0)
                    if not numpy.array_equal(umask, bmask):
                        raise ValueError(
                            f"Unknown and initial conditions on {unknown.name!r} are not masked equally"
                        )
                    data = deepcopy(boundary.default_value)
                    self.initial_values[name] = boundary
                else:
                    data = deepcopy(unknown.value)

            full_init = numpy.append(full_init, data)

        return full_init

    def get_problem(self) -> MathematicalProblem:
        """Returns the full mathematical for the case.

        Returns
        -------
        MathematicalProblem
            The full mathematical problem to solve for the case
        """
        return self.owner.assembled_problem()

    def setup_run(self):
        """Method called once before starting any simulation."""
        super().setup_run()
        owner = self.owner

        if not owner.is_standalone() and owner.parent is None:
            owner.open_loops()  # Force loops opening to test if the owner needs a solver
            problem = self.get_problem()

            if not problem.is_empty():
                logger.warning(
                    f"A mathematical problem on system {owner.full_name()!r} was detetected,"
                    f" but will not be solved by {type(self).__qualname__} driver {self.full_name()!r}."
                )
                logger.debug(f"Problem:\n{problem}")

            owner.close_loops()

    def _precompute(self):
        """Set execution order and start the recorder."""
        super()._precompute()
        # Solution cannot be cleared in setup_run otherwise it won't be available when get_init is called.
        self.solution.clear()

    def compute(self) -> None:
        """Execute drivers on all child `System` belonging to the driver `System` owner.
        """
        if len(self.children) == 0:
            self.owner.run_children_drivers()

        if self._recorder is not None:
            self._recorder.record_state(self.name)

    def _postcompute(self):
        """Actions performed after the `Module.compute` call."""
        # Should be called in _postcompute and not clean_run otherwise it won't work for multi-points cases
        self.solution = dict(
            (key, deepcopy(unknown.value))
            for key, unknown in self.get_problem().unknowns.items()
        )
        super()._postcompute()
