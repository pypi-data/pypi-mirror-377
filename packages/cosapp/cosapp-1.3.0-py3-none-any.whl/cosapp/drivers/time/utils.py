from __future__ import annotations
from collections.abc import MutableMapping
from numbers import Number
from typing import (
    Any, Optional, Callable,
    Iterator, TypeVar, Union,
    Sequence,
    TYPE_CHECKING,
)
import numpy
from numpy.typing import ArrayLike

from cosapp.core.eval_str import EvalString
from cosapp.core.variableref import VariableReference
from cosapp.core.numerics.boundary import AbstractTimeUnknown, TimeUnknown, TimeDerivative
from cosapp.ports.port import ExtensiblePort
from cosapp.systems.system import System
from cosapp.utils.helpers import check_arg
from cosapp.drivers.time.scenario import TimeAssignString
from cosapp.utils.json import jsonify
from cosapp.utils.state_io import object__getstate__
if TYPE_CHECKING:
    from cosapp.drivers.time.base import AbstractTimeDriver


T = TypeVar('T')


class TimeUnknownStack(AbstractTimeUnknown):
    """
    Class representing a group of variables [a, b, c, ...] jointly solved by a time driver, with
    b = da/dt, c = db/dt and so on. By nature, the unknown is therefore an array.
    If variables a, b, c... are arrays themselves, they are automatically flattened.

    Parameters
    ----------
    context : System
        System CoSApp in which all transients to be stacked are defined
    name : str
        Name of this time unknown stack
    transients : list[TimeUnknown]
        Stacked unknowns

    Notes
    -----
    The group variables must all be defined as variables of the same system.
    """
    def __init__(self,
        context: System,
        name: str,
        transients: list[TimeUnknown],
    ):
        super().__init__()
        self.__context = context
        self.__name = name
        self.__value = None
        self.__transients = transients
        self.__init_stack()

    @property
    def name(self) -> str:
        """str: Name of the variable"""
        return self.__name

    @property
    def context(self) -> System:
        """System: Evaluation context of the stacked unknown"""
        return self.__context

    @property
    def der(self) -> EvalString:
        """Expression of time derivative of stacked vector, given as an EvalString"""
        return self.__der

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__name} := {self!s}"

    def __init_stack(self) -> None:
        """
        1. Update the expression of the time derivative vector, and
        the size of individual variables (1 for scalars, n > 1 for vectors).
        It is assumed that all variables in the stack have the same size; in principle,
        this property is satisfied by design, since size consistency between a
        variable and its derivative is checked at declaration of all transient variables.
        
        2. Update the expression of max_time_step, defined as the minimum value of all
        individual maximum time steps (if any) defined by the stacked variables.
        """
        root = self.__transients[0].value

        size = len(root) if isinstance(root, (list, numpy.ndarray)) else 1
        # Init self.__value
        self.reset()

        def get_attribute_expr(attr):
            args = ", ".join([str(getattr(u, attr)) for u in self.__transients])
            if attr == "der":
                return EvalString(f"asarray([{args}])", self.__context)
            else:
                return EvalString(f"min([{args}])", self.__context)

        self.__der = get_attribute_expr("der")
        self.__max_dt = get_attribute_expr("max_time_step_expr")
        self.__max_dx = get_attribute_expr("max_abs_step_expr")

    @property
    def value(self) -> numpy.ndarray:
        """numpy.ndarray: Value of the time unknown"""
        return self.__value

    @value.setter
    def value(self, new: Union[list[float], numpy.ndarray]) -> None:
        self.__value = numpy.array(new)
        # Update original system variables
        for i, unknown in enumerate(self.__transients):
            value = self.__value[i]
            unknown.update_value(value, checks=False)

    def reset(self) -> None:
        """Reset stack value from original system variables"""
        self.__value = numpy.asarray([var.value for var in self.__transients])
        self.touch()

    def touch(self) -> None:
        """Set owner systems as 'dirty'."""
        for unknown in self.__transients:
            unknown.touch()

    @property
    def max_time_step_expr(self) -> EvalString:
        """EvalString: Expression of the maximum time step allowed for the instantaneous time evolution of the stacked variable"""
        return self.__max_dt

    @property
    def max_abs_step_expr(self) -> EvalString:
        """EvalString: Expression of the maximum step allowed for the stacked variable"""
        return self.__max_dx


class TimeUnknownDict(MutableMapping):
    """
    Dictionary of AbstractTimeUnknown objects, mapped to str variable names.
    Automatically updates a dictionary of time step constrained variables,
    accessible with read-only property `constrained`.
    """
    def __init__(self, **mapping):
        super().__init__()
        self.__transients: dict[str, AbstractTimeUnknown] = {}
        self.__constrained: dict[str, AbstractTimeUnknown] = {}
        self.update(mapping)

    def __str__(self) -> str:
        return str(self.__transients)

    def __repr__(self) -> str:
        return repr(self.__transients)

    def __len__(self) -> int:
        """int: length of the collection"""
        return len(self.__transients)

    def __getitem__(self, key: str) -> AbstractTimeUnknown:
        return self.__transients[key]

    def __setitem__(self, key: str, value: AbstractTimeUnknown) -> None:
        if not isinstance(key, str):
            raise TypeError(
                f"Keys of TimeUnknownDict must be strings; invalid key {key!r}"
            )
        if not isinstance(value, AbstractTimeUnknown):
            raise TypeError(
                "Elements of TimeUnknownDict must be of type AbstractTimeUnknown"
                f"; invalid item {key!r}: {type(value).__qualname__}"
            )
        self.__transients[key] = value
        if value.constrained:
            self.__constrained[key] = value
        else:
            self.__constrained.pop(key, None)

    def __delitem__(self, key: str) -> None:
        self.__transients.__delitem__(key)
        try:
            self.__constrained.__delitem__(key)
        except KeyError:
            pass

    def __contains__(self, key: str) -> bool:
        return key in self.__transients

    def __iter__(self) -> Iterator[str]:
        """Iterator on dictionary keys."""
        return iter(self.__transients)

    def __str__(self) -> str:
        return str(self.__transients)

    def __repr__(self) -> repr:
        return str(self.__transients)

    def keys(self, constrained=False) -> Iterator[str]:
        """Iterator on dictionary keys, akin to dict.keys().
        If `constrained` is True, the iterator applies only to time step constrained variables."""
        return self.__constrained.keys() if constrained else self.__transients.keys()

    def values(self, constrained=False) -> Iterator[AbstractTimeUnknown]:
        """Iterator on dictionary values, akin to dict.values().
        If `constrained` is True, the iterator applies only to time step constrained variables."""
        return self.__constrained.values() if constrained else self.__transients.values()

    def items(self, constrained=False) -> Iterator[tuple[str, AbstractTimeUnknown]]:
        """Iterator on (key, value) tuples, akin to dict.items().
        If `constrained` is True, the iterator applies only to time step constrained variables."""
        return self.__constrained.items() if constrained else self.__transients.items()

    def get(self, key: str, *default: Optional[Any]) -> AbstractTimeUnknown:
        """Get value associated to `key`. Behaves as dict.get()."""
        return self.__transients.get(key, *default)

    def pop(self, key: str, *default: Optional[Any]) -> AbstractTimeUnknown:
        """Pop value associated to `key`. Behaves as dict.pop()."""
        try:
            self.__constrained.pop(key)
        except KeyError:
            pass
        finally:
            return self.__transients.pop(key, *default)

    def update(self, mapping: dict[str, Any]) -> None:
        for key, value in mapping.items():
            self.__setitem__(key, value)

    def clear(self) -> None:
        self.__transients.clear()
        self.__constrained.clear()

    def max_time_step(self) -> float:
        """
        Compute maximum admissible time step, from transients' max_time_step (inf by default).
        Raises ValueError if any transients' max_time_step is not strictly positive.
        """
        dt = numpy.inf
        for name, transient in self.__constrained.items():
            max_dt = transient.max_time_step
            if max_dt <= 0:
                raise RuntimeError(
                    f"The maximum time step of {name} was evaluated to non-positive value {max_dt}"
                )
            dt = min(dt, max_dt)
        return dt

    @property
    def constrained(self) -> dict[str, AbstractTimeUnknown]:
        """dict[str, AbstractTimeUnknown]: shallow copy of the subset of time step constrained variables."""
        return self.__constrained.copy()
    
    def __json__(self) -> dict[str, Any]:
        """Creates a JSONable dictionary representation of the object.
        
        Returns
        -------
        dict[str, Any]
            The dictionary
        """
        return object__getstate__(self).copy()


class TimeVarManager:
    """
    Class dedicated to the analysis of a system's independent transient variables.
    For example, in a system where

    .. math::

       dH/dt = f(a, b),

       dx/dt = v,

       dv/dt = a,

    the manager will identify two independent variables H and [x, v], with time derivatives
    f(a, b) and [v, a], respectively. Variable [x, v] and its derivative are handled by class
    `TimeUnknownStack`.
    """
    def __init__(self, context: System):
        self.context = context

    def __json__(self) -> dict[str, Any]:
        """Creates a JSONable dictionary representation of the object.

        Returns
        -------
        dict[str, Any]
            The dictionary
        """
        state = object__getstate__(self).copy()
        state.pop("_TimeVarManager__context")
        return jsonify(state)

    @property
    def context(self) -> System:
        """System handled by manager"""
        return self.__context

    @property
    def problem(self):
        """Time problem handled by manager"""
        return self.__problem

    @context.setter
    def context(self, context: System):
        if not isinstance(context, System):
            raise TypeError("TimeVarManager context must be a system")
        self.__context = context
        self.update_transients()

    @property
    def transients(self) -> TimeUnknownDict:
        """
        Dictionary of all transient variables in current system, linking each
        variable (key) to its associated time unknown (value).
        For stand-alone, order-1 derivatives, transient unknowns are of type `TimeUnknown`.
        For higher-order derivatives, related variables are gathered into a `TimeUnknownStack` object.
        """
        return self.__transients

    @property
    def rates(self) -> dict[str, TimeDerivative]:
        """
        Dictionary of all rate variables in current system, linking each
        variable (key) to its associated TimeDerivative object (value).
        """
        return self.__problem.rates

    def update_transients(self) -> None:
        """Update the transient variable dictionary (see property `transients` for details)"""
        context = self.__context
        problem = context.assembled_time_problem()
        context_transients = problem.transients
        ders = dict()
        reference2name = dict()
        for name, unknown in context_transients.items():
            unknown.update_shape()
            reference = unknown.pulled_from or unknown.context.name2variable[unknown.name]
            reference2name[reference] = name
            der_context = unknown.der.eval_context
            derivative_expr = str(unknown.der)
            try:
                ders[reference] = der_context.name2variable[derivative_expr]
            except KeyError:   # Complex derivative expression
                ders[reference] = VariableReference(context=der_context, mapping=None, key=derivative_expr)

        transients = TimeUnknownDict()
        # Comparison is done with VariableReference as
        # syst.name2variable["phi"] == syst.name2variable["inwards.phi"]
        tree = self.get_tree(ders)
        for root, branch in tree.items():
            if len(branch) > 2:  # second- or higher-order derivative -> build unknown stack
                stack_context = root.context
                branches = list(map(TimeVarManager._get_variable_fullname, branch[:-1]))
                root_stack_name = ", ".join(branches).join("[]")
                context_name = context.get_path_to_child(stack_context)
                stack_name = f"{context_name}{root_stack_name}"
                transients_stack = map(
                    lambda name: context_transients[name], 
                    map(lambda reference: reference2name[reference], branch[:-1])
                )
                transients[stack_name] = TimeUnknownStack(stack_context, stack_name, list(transients_stack))
            else:  # first-order time derivative -> use current unknown
                root_name = reference2name[root]
                transients[root_name] = context_transients[root_name]

        self.__transients = transients
        self.__problem = problem

    @staticmethod
    def _get_variable_fullname(ref: VariableReference) -> str:
        """Built the variable fullname for its reference.
        
        Parameters
        ----------
        ref : VariableReference
            Reference to the variable
        
        Returns
        -------
        str
            The variable fullname
        """
        # First condition is to handle complex derivative expression see previous loop
        if ref.mapping is None or isinstance(ref.mapping, ExtensiblePort):
            return ref.key
        else:
            return f"{ref.mapping.name}.{ref.key}"

    @staticmethod
    def get_tree(ders: dict[T, T]) -> dict[T, list[T]]:
        """
        Parse a dictionary of the kind (var, d(var)/dt), to detect a dependency
        chain from one root variable to its successive time derivatives.
        Returns a dictionary of the kind:
        (root var 'X', [X_0, X_1, .., X_n]), where X_n is the expression of
        the nth-order time derivative of X.
        """
        var_list = ders.keys()
        der_list = ders.values()
        roots = list(filter(lambda var: var not in der_list, var_list))
        leaves = list(filter(lambda der: der not in var_list, der_list))
        tree: dict[T, list[T]] = {}
        for root in roots:
            tree[root] = [root]
            var = root
            while ders[var] not in leaves:
                der = ders[var]
                tree[root].append(der)
                var = der
            tree[root].append(ders[var])
        return tree

    def max_time_step(self) -> float:
        """
        Compute maximum admissible time step, from transients' `max_time_step` (numpy.inf by default).
        Raises ValueError if any transients' max_time_step is not strictly positive.
        """
        return self.__transients.max_time_step()


class TimeStepManager:
    """
    Class dedicated to the management of time step for time drivers.
    """
    def __init__(self, transients=TimeUnknownDict(), dt=None, max_growth_rate=None):
        self.__dt = None
        self.__nominal_dt = None
        self.__transients = None
        self.__growthrate = None
        # Assign initial values
        self.transients = transients
        self.nominal_dt = dt
        self.max_growth_rate = max_growth_rate

    @property
    def transients(self):
        return self.__transients

    @transients.setter
    def transients(self, transients: TimeUnknownDict):
        check_arg(transients, "transients", TimeUnknownDict)
        self.__transients = transients

    @property
    def nominal_dt(self) -> Number:
        """Time step"""
        return self.__nominal_dt

    @nominal_dt.setter
    def nominal_dt(self, value: Number) -> None:
        if value is not None:
            check_arg(value, 'dt', Number, value_ok = lambda dt: dt > 0)
        self.__nominal_dt = value

    @property
    def max_growth_rate(self) -> Number:
        """Maximum growth rate of time step"""
        return self.__growthrate

    @max_growth_rate.setter
    def max_growth_rate(self, value: Number) -> None:
        if value is None:
            self.__growthrate = numpy.inf
        else:
            check_arg(value, 'max_growth_rate', Number, value_ok = lambda x: x > 1)
            self.__growthrate = value

    def max_time_step(self) -> float:
        """
        Compute maximum admissible time step, from transients' max_time_step (inf by default).
        Raises ValueError if any transients' max_time_step is not strictly positive.
        """
        return self.__transients.max_time_step()

    def time_step(self, previous=None) -> float:
        """
        Compute time step, making sure that it does not exceed any transient's `max_time_step`
        (numpy.inf by default), and that all transient max_time_step are strictly positive.
        If `previous` is specified, the returned time step is bounded by max_growth_rate * previous.

        An exception is raised if time step is ultimately found to be infinity.
        """
        dt = self.__nominal_dt or numpy.inf
        dt = min(dt, self.max_time_step())
        if previous is not None and previous > 0:
            dt = min(dt, self.__growthrate * previous)

        if not numpy.isfinite(dt):
            raise ValueError("Time step was not specified, and could not be determined from transient variables")

        return dt
    
    def __json__(self) -> dict[str, Any]:
        """Creates a JSONable dictionary representation of the object.
        
        Returns
        -------
        dict[str, Any]
            The dictionary
        """
        return object__getstate__(self).copy()


class Polynomial:
    """Polynomial function that accepts array coefficients,
    in order to fit array quantities over a one-dimensional interval.
    """
    def __init__(self, coefs: ArrayLike, shift=0.0):
        self._coefs = numpy.array(coefs)
        self._shift = shift

    def __call__(self, x: float) -> Union[float, numpy.ndarray]:
        coefs = self._coefs
        x = x - self._shift
        y = coefs[-1]
        for c in coefs[-2::-1]:
            y = c + x * y
        return y

    def degree(self) -> int:
        return len(self._coefs) - 1

    def deriv(self) -> Polynomial:
        """Derivative of the polynomial"""
        der_coefs = [n * cn for (n, cn) in enumerate(self._coefs[1:], start=1)]
        return Polynomial(der_coefs, self._shift)


def TwoPointCubicPolynomial(
    xs: tuple[float, float],
    ys: tuple[float, float] | numpy.ndarray,
    dy: tuple[float, float] | numpy.ndarray,
) -> Polynomial:
    """Function returning a cubic polynomial interpolating
    two end points (x, y), with imposed derivatives dy/dx.

    y(x) can be either a scalar or a multi-dimensional quantity, based on
    the format of input arrays `ys` and `dy`. If `ys` and `dy` are tuples
    of floats or 1D arrays (resp. ND), they are interpreted as the values
    and derivatives of a scalar (resp. vector) quantity at end points `xs`.

    Parameters
    ----------
    - xs, tuple[float, float]: end point abscissa.
    - ys, tuple[float, float] | numpy.ndarray: end point values as a one- or multi-dimensional array.
    - dy, tuple[float, float] | numpy.ndarray: end point derivatives as a one- or multi-dimensional array.

    Returns
    -------
    poly: cubic polynomial function returning either
        a float or a numpy array of floats, depending on
        the dimension of input data `ys` and `dy`.
    """
    h = xs[1] - xs[0]
    h2 = h * h
    ys = numpy.asarray(ys)
    dy = numpy.asarray(dy)
    d2 = (ys[1] - ys[0]) / h2
    a2 = 3 * d2 - (dy[1] + 2 * dy[0]) / h
    a3 = (d2 - a2 - dy[0] / h) / h
    coefs = [ys[0], dy[0], a2, a3]
    return Polynomial(coefs, shift=xs[0])


class SystemInterpolator:
    """Class providing a continuous time view on a system,
    by replacing transient variables by time functions.
    """
    def __init__(self, driver: AbstractTimeDriver):
        from cosapp.drivers.time.base import AbstractTimeDriver
        check_arg(driver, 'driver', AbstractTimeDriver)
        self.__owner = driver
        self.__system = system = driver.owner
        problem = system.assembled_time_problem()
        self.__transients = transients = problem.transients
        self.__interp = dict.fromkeys(transients, None)

    def __json__(self) -> dict[str, Any]:
        """Creates a JSONable dictionary representation of the object.

        Returns
        -------
        dict[str, Any]
            The dictionary
        """
        state = object__getstate__(self).copy()
        state.pop("_SystemInterpolator__owner")
        state.pop("_SystemInterpolator__system")
        return jsonify(state)

    @property
    def system(self) -> System:
        """System modified by interpolator"""
        return self.__system

    @property
    def transients(self) -> dict[str, TimeUnknown]:
        return self.__transients

    @property
    def interp(self) -> dict[str, Callable]:
        """dict[str, Callable]: interpolant dictionary"""
        return self.__interp

    @interp.setter
    def interp(self, interp: dict[str, Callable]):
        check_arg(
            interp, "interp", dict,
            lambda d: set(d) == set(self.__transients)
        )
        context = self.system
        for key, func in interp.items():
            self.__interp[key] = TimeAssignString(key, func, context)

    def exec(self, t: float) -> None:
        for assignment in self.__interp.values():
            assignment.exec(t)
        self.__owner._set_time(t)

    def refresh(self) -> None:
        """Reanalyse the system of interest, in case it has changed."""
        problem = self.__system.assembled_time_problem()
        transients = self.__transients
        transients.clear()
        transients.update(problem.transients)
        self.__interp = dict.fromkeys(transients, None)
