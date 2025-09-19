from __future__ import annotations
import abc
import json
import copy
import logging
import warnings
from collections import OrderedDict
from collections.abc import Iterator, Generator
from typing import (
    Any, Optional, Union, Callable,
    TypeVar, TYPE_CHECKING,
)
from types import MappingProxyType

from cosapp.patterns import visitor
from cosapp.ports.enum import PortType, Scope, Validity
from cosapp.ports.exceptions import ScopeError
from cosapp.ports.variable import RangeValue, Types, BaseVariable, Variable
from cosapp.ports.mode_variable import ModeVariable
from cosapp.utils.distributions import Distribution
from cosapp.utils.helpers import check_arg
from cosapp.utils.naming import NameChecker
from cosapp.utils.json import jsonify
from cosapp.utils.deprecation import deprecated

if TYPE_CHECKING:
    from cosapp.systems import System

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BasePort(visitor.Component, metaclass=abc.ABCMeta):
    """Base class for ports, containers gathering variables.

    Common users should not use this class directly.

    Parameters
    ----------
    name : str
        Port name
    direction : {PortType.IN, PortType.OUT}
        Port direction
    """

    _name_check = NameChecker()

    def __init__(self, name: str, direction: PortType) -> None:
        """`BasePort` constructor.

        Parameters
        ----------
        name : str
            Port name
        direction : {PortType.IN, PortType.OUT}
            Port direction
        """
        if not isinstance(direction, PortType):
            raise TypeError(f"Direction must be PortType; got {direction!r}.")

        self.__is_clean = False
        self._variables: dict[str, BaseVariable] = OrderedDict()
        self._name: str = self._name_check(name)
        self._desc: str = ""
        self._direction: PortType = direction
        self._owner: Optional[System] = None
        self.__clearance: Scope = None
        self.scope_clearance = Scope.PRIVATE

    def accept(self, visitor: visitor.Visitor) -> None:
        """Specifies course of action when visited by `visitor`"""
        visitor.visit_port(self)

    @property
    def owner(self) -> System:
        """System : `System` owning the port."""
        return self._owner

    @owner.setter
    def owner(self, new_owner: System):
        from cosapp.systems import System

        if not isinstance(new_owner, System):
            raise TypeError(f"Port owner must be a `System`; got {new_owner!r}.")
        self._owner = new_owner
        self.__update_filter()

    @property
    def name(self) -> str:
        """str : Port name"""
        return self._name

    @property
    def contextual_name(self) -> str:
        """str : Join port owner name and port name.

        If the port has no owner, the port name is returned.
        """
        owner = self._owner
        return self._name if owner is None else f"{owner.name}.{self._name}"

    def full_name(self, trim_root=False) -> str:
        """Returns full name up to root owner.
        
        Parameters
        ----------
        trim_root : bool (optional, default False)
            Exclude root owner name if True.

        Returns
        -------
        str
            The port full name
        """
        owner = self.owner
        path = []
        if owner is not None:
            path = owner.path_namelist()
            if trim_root:
                path = path[1:]
        path.append(self.name)
        return ".".join(path)

    @property
    def description(self) -> str:
        """str: Port description"""
        return self._desc

    @description.setter
    def description(self, desc: str) -> None:
        check_arg(desc, 'description', str)
        self._desc = desc

    @property
    def direction(self) -> PortType:
        """:obj:`PortType.IN` or :obj:`PortType.OUT` : Port direction"""
        return self._direction

    @property
    def is_input(self) -> bool:
        """bool: True if port is an input, False otherwise."""
        return self._direction == PortType.IN

    @property
    def is_output(self) -> bool:
        """bool: True if port is an output, False otherwise."""
        return self._direction == PortType.OUT

    @property
    def is_clean(self) -> bool:
        return self.__is_clean

    def set_clean(self) -> None:
        """Set port as 'clean'."""
        self.__is_clean = True

    def touch(self) -> None:
        """Set port as 'dirty'."""
        self.__is_clean = False
        if self._owner and self.is_input:
            self._owner.touch()

    def __repr__(self) -> str:
        return f"{type(self).__name__}: {self.serialize_data()!r}"

    def _repr_markdown_(self) -> str:
        """Returns the representation of this port variables in Markdown format.

        Returns
        -------
        str
            Markdown formatted representation
        """
        from cosapp.tools.views.markdown import port_to_md

        return port_to_md(self)

    def __json__(self) -> dict[str, Any]:
        """Creates a JSONable dictionary representation of the object.
        
        Break circular dependencies by not relying
        on a `__getstate__` call.

        Returns
        -------
        dict[str, Any]
            The dictionary
        """
        return jsonify(dict((name, variable.__json__()) for name, variable in self._variables.items()))

    def __reduce_ex__(self, _: Any) -> tuple[Callable, tuple, dict]:
        """Defines how to serialize/deserialize the object.
        
        Parameters
        ----------
        _ : Any
            Protocol used

        Returns
        -------
        tuple[Callable, tuple, dict]
            A tuple of the reconstruction method, the arguments to pass to
            this method, and the state of the object
        """
        state = {"owner": self._owner}
        state.update(
            (key, (val, self._variables[key]))
            for (key, val) in self.items()
        )
        return (type(self), (self._name, self._direction), state)

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Sets the object from a provided state.

        Parameters
        ----------
        state : dict[str, Any]
            State
        """
        self._owner = state.pop("owner")

        for name, (val, var) in state.items():
            try:
                self.add_variable(name, val)
            except:
                pass
            self._variables[name] = var
            setattr(self, name, val)

    def serialize_data(self) -> dict[str, Any]:
        """Serialize the variable values in a dictionary.
        
        Returns
        -------
        dict[str, Any]
            The dictionary (variable name, value)
        """
        return dict(self.items())

    def add_variable(
        self,
        name: str,
        value: Any = 1,
        unit: str = "",
        dtype: Types = None,
        valid_range: RangeValue = None,
        invalid_comment: str = "",
        limits: RangeValue = None,
        out_of_limits_comment: str = "",
        desc: str = "",
        distribution: Optional[Distribution] = None,
        scope: Scope = Scope.PRIVATE,
    ) -> None:
        """Add a variable to the port.

        The `valid_range` defines the range of value for which a model is known to behave correctly.
        The `limits` are at least as large as the validity range.

        Parameters
        ----------
        name : str
            Name of the variable
        value : Any, optional
            Value of the variable; default 1
        unit : str, optional
            Variable unit; default empty string (i.e. dimensionless)
        dtype : type or iterable of type, optional
            Variable type; default None (i.e. type of initial value)
        valid_range : tuple[Any, Any] or tuple[tuple], optional
            Validity range of the variable; default None (i.e. all values are valid)
        invalid_comment : str, optional
            Comment to show in case the value is not valid; default ''
        limits : tuple[Any, Any] or tuple[tuple], optional
            Limits over which the use of the model is wrong; default valid_range
        out_of_limits_comment : str, optional
            Comment to show in case the value is not valid; default ''
        desc : str, optional
            Variable description; default ''
        distribution : Distribution, optional
            Probability distribution of the variable; default None (no distribution)
        scope : Scope {PRIVATE, PROTECTED, PUBLIC}, optional
            Variable visibility; default PRIVATE
        """
        if name in self:
            logger.warning(
                f"Variable {name} already exists in port {self.contextual_name}."
                " It will be overwritten."
            )

        # Value must be set before creating variable as validation in Variable needs it
        self._variables[name] = variable = Variable(
            name,
            self,
            value,
            unit,
            dtype,
            valid_range,
            invalid_comment,
            limits,
            out_of_limits_comment,
            desc,
            distribution,
            scope,
        )
        value = variable.filter_value(value)

        # For efficiency reasons, values are stored as port attributes
        setattr(self, name, value)

    # TODO should we override __setattr__ to forward setting to the source port? and/or raise an
    #   error if it is not possible - for example if the source is an output variable
    def __set_notype_checking(self, name: str, value: Any):
        super().__setattr__(name, value)

        if self.__is_clean and name in self._variables:
            self.touch()

    def validate(self, key: str, value: Any) -> None:
        """Check if a variable is in the scope of the user and the type is valid.
        
        Parameters
        ----------
        key : str
            Name of the variable to test
        value : Any
            Value to validate

        Raises
        ------
        ScopeError
            If the variable is not visible for the user
        TypeError
            If the value has an unauthorized type
        """
        # Check scope
        if self.__out_of_scope(key):
            raise ScopeError(f"Cannot set out-of-scope variable {key!r}.")

        if value is not None:
            var_type = self._variables[key].dtype
            ok = var_type is None or isinstance(value, var_type)
            if not ok:
                raise TypeError(
                    "Trying to set {}.{} of type {} with {}.".format(
                        self.contextual_name, key, var_type, type(value)
                    )
                )

    def __set_variable(self, name: str, value: Any):
        """Set the variable `name` with `value`.
        
        Parameters
        ----------
        name : str
            Name of the variable to be set
        value : Any
            Value to set
        """
        if name.startswith("_"):
            super().__setattr__(name, value)
        elif name in self._variables:
            self.validate(name, value)
            self.__set_notype_checking(name, value)
        elif hasattr(self, name):
            super().__setattr__(name, value)
        else:
            raise AttributeError(
                f"Port variable {self.contextual_name}.{name} can only be created using method 'add_variable'."
            )

    __setattr__ = __set_variable

    @staticmethod
    def set_type_checking(activate: bool) -> None:
        """(Un)set type checking when affecting port variables.

        By default type checking is activated.

        Parameters
        ----------
        activate : bool
            True to activate type checking, False to deactivate
        """
        if activate:
            BasePort.__setattr__ = BasePort.__set_variable
        else:
            BasePort.__setattr__ = BasePort.__set_notype_checking

    def __contains__(self, item: str) -> bool:
        return item in self._variables

    def __getitem__(self, item: str) -> Any:
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(f"Variable or property {item} does not exist in Port {self}.")

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._variables:
            setattr(self, key, value)
        else:
            raise KeyError(f"Variable {key} does not exist in Port {self}.")

    def __iter__(self) -> Iterator[str]:
        return iter(self._variables)

    def __len__(self) -> int:
        return len(self._variables)

    def items(self) -> Generator[tuple[str, Any], None, None]:
        """Dictionary-like item generator yielding (name, value) tuples
        for all port variables."""
        for name in self._variables:
            yield (name, getattr(self, name))

    def set_values(self, **modifications) -> None:
        """Generic setter for port variable values, offering a
        convenient way of modifying multiple variables at once.

        Parameters:
        -----------
        **modifications:
            Variable names and values given as keyword arguments.
        
        Examples:
        ---------
        >>> from cosapp.base import Port, System
        >>>
        >>> class DummyPort(Port):
        >>>     def setup(self):
        >>>         self.add_variable('a')
        >>>         self.add_variable('b')
        >>>
        >>> class DummySystem(System):
        >>>     def setup(self):
        >>>         self.add_input(DummyPort, 'p_in')
        >>>         self.add_output(DummyPort, 'p_out')
        >>>
        >>>     def compute(self):
        >>>         p_in = self.p_in
        >>>         self.p_out.set_values(
        >>>             a = p_in.b,
        >>>             b = p_in.a - p_in.b,
        >>>         )
        """
        for name, value in modifications.items():
            setattr(self, name, value)

    @property
    def scope_clearance(self) -> Scope:
        """Scope: Current clearance level of the port.
        Determines the set of read-only port variables."""
        return self.__clearance

    @scope_clearance.setter
    def scope_clearance(self, user_scope: Scope) -> None:
        check_arg(user_scope, "scope_clearance", Scope)
        self.__clearance = user_scope
        self.__update_filter()

    def __update_filter(self) -> None:
        """Update the implementation of method `out_of_scope`
        according to port's clearance level and owner."""
        if self._owner is None:
            criterion = lambda name: False
        else:
            read_only = [
                name for (name, variable) in self._variables.items()
                if variable.scope > self.__clearance
            ]
            criterion = lambda name: not self._owner.is_running() and name in read_only
        self.__out_of_scope = criterion

    def out_of_scope(self, name: str) -> bool:
        """
        Asserts if current scope `scope_clearance` is high enough to
        allow the modification of port variable `name`.

        Parameters
        ----------
        name : str
            Variable name to test

        Returns
        -------
        bool
            Is modification forbidden?

        The behavior of this function is set by method `scope_clearance()`.
        By default, clearance level is set to `Scope.PUBLIC`.

        Examples
        --------
        >>> port = Port("myPort", PortType.IN)
        >>> port.add_variable("x", 1.5, scope=Scope.PUBLIC)
        >>> port.add_variable("y", 0.2, scope=Scope.PROTECTED)
        >>> port.add_variable("z", 0.3, scope=Scope.PRIVATE)
        >>>
        >>> port.scope_clearance(Scope.PROTECTED)  # only `port.x` and `port.y` can be modified
        >>> assert not port.out_of_scope("x")
        >>> assert not port.out_of_scope("y")
        >>> assert port.out_of_scope("z")
        >>>
        >>> port.scope_clearance(Scope.PUBLIC)     # only `port.x` can be modified
        >>> assert not port.out_of_scope("x")
        >>> assert port.out_of_scope("y")
        >>> assert port.out_of_scope("z")
        """
        return self.__out_of_scope(name)

    @deprecated("use `get_variable(varname)` or `variable_dict()` instead")
    def get_details(self, varname: Optional[str]=None) -> Union[dict[str, BaseVariable], BaseVariable]:
        """Return the variable named `varname` (if prescribed),
        or an immutable variable dictionary of the kind {varname: variable}.

        Deprecated: use `get_variable(varname)` or `variable_dict()` instead.
        """
        if varname is None:
            return self.variable_dict()
        else:
            return self.get_variable(varname)

    def get_variable(self, varname: str) -> BaseVariable:
        """Return the variable named `varname`.
        
        Parameters
        ----------
        name: str
            Name of the variable.

        Returns
        -------
        cosapp.ports.variable.Variable

        Raises
        ------
        `AttributeError` if the variable does not exist in the port
        """
        try:
            return self._variables[varname]
        except KeyError:
            raise AttributeError(
                f"Variable {varname!r} does not exist in port {self.contextual_name}"
            )

    def variable_dict(self) -> dict[str, BaseVariable]:
        """Return an immutable variable dictionary of the kind {varname: variable}.
        
        Returns
        -------
        types.MappingProxyType[str, cosapp.ports.variable.Variable]
            Read-only view on all port variables.
        """
        return MappingProxyType(self._variables)

    def variables(self) -> Iterator[BaseVariable]:
        """Iterator over port `BaseVariable` instances."""
        return self._variables.values()

    def check(self, name: Optional[str] = None) -> Union[dict[str, Validity], Validity]:
        """Get the variable value validity.

        If `name` is not provided, returns a dictionary with the validity of all variables. Else
        only, the validity for the given variable will be returned.

        Parameters
        ----------
        name : str, optional
            Variable name; default None = All variables will be tested

        Returns
        -------
        dict[str, Validity] or Validity
            (Dictionary of) the variable(s) value validity
        """
      
        if name is None:
            return dict(
                (name, variable.is_valid())
                for name, variable in self._variables.items()
            )
        else:           
            return self._variables[name].is_valid()

    def get_validity_ground(self,
        status: Validity,
        name: Optional[str] = None,
    ) -> Union[dict[str, str], str]:
        # TODO unit tests
        """Get the ground arguments used to established the variable validity range.

        The status `Validity.OK` has no ground arguments.

        Parameters
        ----------
        status : Validity.{OK, WARNING, ERROR}
            Validity status for which the reasons are looked for.
        name : str, optional
            Variable name; default None = All variables will be tested

        Returns
        -------
        dict[str, str] or str
            (Dictionary of) the variable(s) validity ground
        """
        if name is None:
            return dict(
                (name, variable.get_validity_comment(status))
                for name, variable in self._variables.items()
            )
        else:
            return self._variables[name].get_validity_comment(status)

    def copy(
        self,
        name: Optional[str] = None,
        direction: Optional[PortType] = None,
    ):
        """Duplicates the port.

        Parameters
        ----------
        name : str, optional
            Name of the duplicated port; default original port name
        direction : {PortType.IN, PortType.OUT}, optional
            Direction of the duplicated port; default original direction

        Returns
        -------
        Port
            The copy of the current port
        """
        cls = type(self)
        port = cls(
            name or self.name,
            direction or self.direction,
        )
        for name in self._variables:
            port.copy_variable_from(self, name)

        return port

    def copy_variable_from(self, port: BasePort, name: str, alias: Optional[str]=None) -> None:
        """Copy variable `name` from another port into variable `alias`.

        Parameters
        ----------
        port : BasePort
            Port from which variable is copied
        name : str
            Variable name from source port.
        alias : str, optional
            Variable name in current port (same as `name` if not specified).
        """
        if alias is None:
            alias = name
        variable = port._variables[name]
        value = getattr(port, name)
        self._variables[alias] = variable.copy(self, alias)
        setattr(self, alias, copy.copy(value))

    def morph_as(self, port: BasePort) -> None:
        """Morph this port into the provided port.

        Morphing a port is useful when converting a `System` in something equivalent. The morphing
        goal is to preserve connections and adapt the port content if needed.

        Parameters
        ----------
        port [BasePort]:
            The port to morph into
        """
        # TODO unit test for variable details when morphing
        for varname in set(self) - set(port):
            self.pop_variable(varname)

        new_varnames = set(port) - set(self)

        for varname in new_varnames:
            variable = port._variables[varname]

            self.add_variable(
                varname,
                getattr(port, varname),
                unit=variable.unit,
                dtype=variable.dtype,
                desc=variable.description,
                valid_range=variable.valid_range,
                invalid_comment=variable.invalid_comment,
                limits=variable.limits,
                out_of_limits_comment=variable.out_of_limits_comment,
                distribution=variable.distribution,
                scope=variable.scope,
            )

    def pop_variable(self, varname: str) -> BaseVariable:
        """Removes a variable from the port.

        Parameters
        ----------
        - varname [str]:
            Name of the variable to be removed

        Returns
        -------
        - variable [BaseVariable]:
            The popped variable

        Raises
        ------
        `AttributeError` if the variable does not exist.
        """
        try:
            variable = self._variables.pop(varname)
        except KeyError:
            raise AttributeError(
                f"Variable {varname!r} does not exist in port {self.contextual_name}"
            )
        delattr(self, varname)
        return variable

    def to_dict(
        self, *, with_types: bool, value_only: bool
    ) -> dict[str, Union[str, tuple[dict[str, str], str]]]:
        """Convert this port in a dictionary.

        Parameters
        ----------
        with_types : bool
            Flag to export also output ports and its class name (default: False).

        Returns
        -------
        dict
            The dictionary representing this port.
        """

        state = {"name": self.name}
        if with_types and self.name not in ["inwards", "outwards"]:
            state["__class__"] = self.__class__.__qualname__

        if value_only:
            state["variables"] = {name: value for name, value in self.items()}
        else:
            state["variables"] = {name: var.to_dict() for name, var in self._variables.items()}

        return state

    def to_json(self, indent=2, sort_keys=True) -> str:
        """Return a string in JSON format representing the `System`.

        Parameters
        ----------
        indent : int, optional
            Indentation of the JSON string (default: 2)
        sort_keys : bool, optional
            Sort keys in alphabetic order (default: True)

        Returns
        -------
        str
            String in JSON format
        """

        return json.dumps(self.__json__(), indent=indent, sort_keys=sort_keys)


class ModeVarPort(BasePort):
    """Class used for the local storage of mode variables."""

    # TODO: Forbid the use of add_variable
    # TODO: Redefine exports/serializations
    # TODO: Typing of _variables is ambiguous

    def add_mode_variable(
        self,
        name: str,
        value: Optional[Any] = None,
        unit: str = "",
        dtype: Types = None,
        desc: str = "",
        init: Optional[Any] = None,
        scope: Scope = Scope.PRIVATE,
    ) -> None:
        """Add a mode variable to the port.

        Parameters
        ----------
        name : str
            Name of the variable
        value : Any, optional
            Value of the variable; default 1
        unit : str, optional
            Variable unit; default empty string (i.e. dimensionless)
        dtype : type or iterable of type, optional
            Variable type; default None (i.e. type of initial value)
        desc : str, optional
            Variable description; default ''
        scope : Scope {PRIVATE, PROTECTED, PUBLIC}, optional
            Variable visibility; default PRIVATE
        """
        if name in self:
            logger.warning(
                f"Variable {name} already exists in multimode port {self.contextual_name}."
                " It will be overwritten."
            )
        # Value must be set before creating variable as validation in Variable needs it
        if init is not None and value is not None and self.is_input:
            logger.warning(
                f"Initial value {init} is discarded for input mode variable {name!r}"
            )
            init = None
        
        self._variables[name] = variable = ModeVariable(
            name = name,
            port = self,
            value = value,
            unit = unit,
            dtype = dtype,
            desc = desc,
            init = init,
            scope = scope,
        )
        if value is None:
            value = variable.init_value()
        value = variable.filter_value(value)

        # For efficiency reasons, variables are stored as port attributes
        setattr(self, name, value)


class ExtensiblePort(BasePort):
    """Class describing ports with a varying number of variables."""
    pass


class Port(BasePort):
    """A `Port` is a container gathering variables tightly linked.

    An optional dictionary may be specified to overwrite variable value and some of their
    metadata. Values of the dictionary may be of two kinds:
    - Only the new value
    - A dictionary with new value and/or new details

    If the value or a metadata is set to `None`, the default value will be kept.

    Parameters
    ----------
    name : str
        `Port` name
    direction : {PortType.IN, PortType.OUT}
        `Port` direction
    variables : dict[str, Any], optional
        Dictionary of variables with their value and details; default: None = default value

    Attributes
    ----------
    _locked : bool
        if True, `add_variable` is deactivated. This is the default behavior outside the `setup`
        function.

    Examples
    --------

    Use this class by subclassing it:

    >>> class FlowPort(Port):
    >>>     def setup(self):
    >>>         self.add_variable('Pt', 101325., unit='Pa')
    >>>         self.add_variable('Tt', 273.15, unit='K')
    >>>         self.add_variable('W', 1.0, unit='kg/s')
    >>>
    >>> p = FlowPort('myPort', PortType.IN)
    >>> # Overwrite value and some details
    >>> f = FlowPort(
    >>>     'myPort2', 
    >>>     PortType.OUT,
    >>>     {
    >>>         'Pt': 10e6,
    >>>         'W': {
    >>>             'value': 10.,  # New value
    >>>             'unit': 'lbm/s',  # New unit - should be compatible of the original one
    >>>             'valid_range': (0., None),  # Updated validated range
    >>>             'invalid_comment': 'Flow should be positive',  # Comment if out of validated range
    >>>             'limits': None,  # Limits
    >>>             'out_of_limits_comment': '',  # Comment if out of limits
    >>>         }
    >>>     }
    >>> )
    """
    def __init__(
        self,
        name: str,
        direction: PortType,
        variables: Optional[dict[str, Any]] = None,
    ) -> None:
        """`Port` constructor.

        An optional dictionary may be specified to overwrite variable value and some of their
        metadata. Values of the dictionary may be of two kinds:
        - Only the new value
        - A dictionary with new value and/or new details

        Parameters
        ----------
        name : str
            `Port` name
        direction : {PortType.IN, PortType.OUT}
            `Port` direction
        variables : dict[str, Any], optional
            Dictionary of variables with their value and details; default: None = default value
        """
        super().__init__(name, direction)
        self.__locked = False  # type: bool

        self.setup()

        if variables is not None:
            check_arg(variables, "variables", dict)
            for name, value in variables.items():
                variable_value = value
                if isinstance(value, dict):
                    variable = self.get_variable(name)
                    variable_value = value.pop("value", None)
                    try:
                        for field, param in value.items():
                            setattr(variable, field, param)
                    except AttributeError:  # Unexpected keyword for details
                        # If current variable is of type dict
                        if isinstance(self[name], dict):
                            if variable_value is not None:
                                value["value"] = variable_value
                            variable_value = value
                        else:
                            raise

                if variable_value is not None:
                    self[name] = variable_value

        self.__locked = True

    def setup(self) -> None:
        """`Port` variables are defined in this function by calling `add_variable`.

        This function allows to populate a customized `Port` class. The `add_variable`
        function is only callable in the frame of this function.

        Examples
        --------

        Here is an example of `Port` subclassing:

        >>> class FlowPort(Port):
        >>>     def setup(self):
        >>>         self.add_variable('Pt', 101325.)
        >>>         self.add_variable('Tt', 273.15)
        >>>         self.add_variable('W', 1.0)
        """
        pass  # pragma: no cover

    def add_variable(
        self,
        name: str,
        value: Any = 1,
        unit: str = "",
        dtype: Types = None,
        valid_range: RangeValue = None,
        invalid_comment: str = "",
        limits: RangeValue = None,
        out_of_limits_comment: str = "",
        desc: str = "",
        distribution: Optional[Distribution] = None,
        scope=Scope.PUBLIC,
    ) -> None:
        """Add a variable to the port.

        The `valid_range` defines the range of value for which a model is known to behave correctly.
        The `limits` are at least as large as the validity range.

        Notes
        -----
        The default visibility of a `Port` variable is `Scope.PUBLIC`.
        This is a difference compared to `BasePort`.

        Parameters
        ----------
        name : str
            Name of the variable
        value : Any, optional
            Value of the variable; default 1
        unit : str, optional
            Variable unit; default empty string (i.e. dimensionless)
        dtype : type or iterable of type, optional
            Variable type; default None (i.e. type of initial value)
        valid_range : tuple[Any, Any] or tuple[tuple], optional
            Validity range of the variable; default None (i.e. all values are valid)
        invalid_comment : str, optional
            Comment to show in case the value is not valid; default ''
        limits : tuple[Any, Any] or tuple[tuple], optional
            Limits over which the use of the model is wrong; default valid_range
        out_of_limits_comment : str, optional
            Comment to show in case the value is not valid; default ''
        desc : str, optional
            Variable description; default ''        
        distribution : Distribution, optional
            Probability distribution of the variable; default None (no distribution)
        scope : Scope {PRIVATE, PROTECTED, PUBLIC}, optional
            Variable visibility; default PUBLIC
        """
        if self.__locked:
            raise AttributeError("add_variable cannot be called outside `setup`.")

        super().add_variable(
            name,
            value=value,
            unit=unit,
            dtype=dtype,
            valid_range=valid_range,
            invalid_comment=invalid_comment,
            limits=limits,
            out_of_limits_comment=out_of_limits_comment,
            desc=desc,
            distribution=distribution,
            scope=scope,
        )

    def copy(
        self, 
        name: Optional[str] = None,
        direction: Optional[PortType] = None,
    ):
        """Duplicates the port.

        Parameters
        ----------
        name : str, optional
            Name of the duplicated port; default original port name
        direction : {PortType.IN, PortType.OUT}, optional
            Direction of the duplicated port; default original direction

        Returns
        -------
        Port
            The copy of the current port
        """
        cls = type(self)
        new_port = cls(
            name or self.name,
            direction or self.direction,
        )
        new_port.set_from(self, copy.copy)
        return new_port

    def set_from(self,
        source: BasePort,
        transfer: Callable[[T], T] = lambda x: x,
        check_names: bool = True,
    ) -> None:
        """Set values from another port.

        Parameters:
        -----------
        - source [BasePort]:
            Source port.
        - transfer [Callable[[T], T], optional]:
            Transfer function to pass values. By default, `transfer` is the identity
            function, which corresponds to plain assignment target.var = source.var.
            Copies can be performed by setting `transfer = copy.copy`, e.g.
        - check_names [bool, optional]:
            If `True` (default), figure out common variables before transfering values.
            If current and source ports are of the same type, no check is performed.
        
        Examples:
        ---------
        >>> from cosapp.base import Port, System
        >>> import copy
        >>>
        >>> class DummyPort(Port):
        >>>     def setup(self):
        >>>         self.add_variable('a')
        >>>         self.add_variable('b')
        >>>
        >>> class DummySystem(System):
        >>>     def setup(self):
        >>>         self.add_inward('a')
        >>>         self.add_inward('x')
        >>>         self.add_input(DummyPort, 'p_in')
        >>>         self.add_output(DummyPort, 'p_out')
        >>>
        >>>     def compute(self):
        >>>         self.p_out.set_from(self.p_in)     # peer-to-peer: no check
        >>>         self.p_out.set_from(self.inwards)  # will transfer `self.a`
        >>>         # Peer-to-peer, with deepcopy:
        >>>         self.p_out.set_from(self.p_in, copy.deepcopy)
        >>>         # Transfer `inwards` into `p_out`, with no name check:
        >>>         # raises AttributeError, as `DummyPort` has no variable `x`
        >>>         self.p_out.set_from(
        >>>             self.inwards,
        >>>             check_names=False,
        >>>         )
        """
        peers = type(source) is type(self)  # most likely usage

        if peers or not check_names:  # faster
            common = iter(source) 
        else:
            common = set(source).intersection(self)
            if not common:
                logger.warning(
                    f"{self.contextual_name!r} and {source.contextual_name!r} have no common variables."
                )
        for name in common:
            value = getattr(source, name)
            setattr(self, name, transfer(value))

    def pop_variable(self, varname: str) -> None:
        raise NotImplementedError(
            f"cannot remove variables from fixed-size port {type(self).__name__}."
        )
