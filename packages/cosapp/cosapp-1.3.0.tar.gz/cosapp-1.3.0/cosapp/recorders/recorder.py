"""Base class for recording data."""
from __future__ import annotations
import abc
import copy
import pandas
import warnings
from typing import Union, Optional, NamedTuple, Any, TYPE_CHECKING

from cosapp.core.signal import Signal
from cosapp.core.eval_str import EvalString
from cosapp.core.execution import ExecutionType
from cosapp.utils.helpers import is_numerical, check_arg
from cosapp.utils.find_variables import SearchPattern, make_wishlist, find_variables
from cosapp.utils.state_io import object__getstate__
if TYPE_CHECKING:
    from cosapp.systems import System


class SpecialColumns(NamedTuple):
    section: str
    status: str
    code: str
    reference: str


def is_cosapp_object(obj: Any) -> bool:
    """Returns `True` if `obj` is either a port,
    a system or a driver; `False` otherwise."""
    from cosapp.base import Port, System, Driver
    return isinstance(obj, (Port, System, Driver))


def any_forbidden_object(collection: Any) -> bool:
    """Returns `True` if argument is either an iterator,
    a cosapp object, or a collection thereof; `False` otherwise."""
    if isinstance(collection, str):
        return False
    try:
        iterator = iter(collection)
    except:
        pass
    else:
        if iterator is collection:
            # collection is an iterator; leave it untouched
            return True
    try:
        return any(map(is_cosapp_object, collection))
    except TypeError:
        return is_cosapp_object(collection)


def no_forbidden_objects(dict_item: tuple) -> bool:
    """Filter function for dictionary items, to
    exclude entries that match `any_forbidden_object`."""
    return not any_forbidden_object(dict_item[1])


class BaseRecorder(abc.ABC):
    """Abstract base class for recorders.

    Matching pattern are case sensitive and support the following special patterns:

    ========  ================================
    Pattern   Meaning
    ========  ================================
    `*`       matches everything
    `?`       matches any single character
    `[seq]`   matches any character in seq
    `[!seq]`  matches any character not in seq
    ========  ================================

    Excluding pattern are shadowing includes one; e.g. if `includes='*port_in.*' and `excludes='*.Pt'`, for a port
    having variables named `Tt` and `Pt`, only `Tt` will be recorded.

    Parameters
    ----------
    includes : str or list of str, optional
        Variables matching these patterns will be included; default `'*'` (i.e. all variables).
    excludes : str or list of str or None, optional
        Variables matching these patterns will be excluded; default `None` (i.e. nothing is excluded).
    numerical_only : bool, optional
        Keep only numerical variables (i.e. number or numerical vector); default False.
    section : str, optional
        Current section name; default `''`.
    precision : int, optional
        Precision digits when writing floating point number; default 9 (i.e. 10 figures will be written).
    hold : bool, optional
        Append the new data or not; default `False`.
    raw_output : bool, optional
        Raw output; default `False`.

    Signals
    -------
    state_recorded : Signal(time_ref: Union[float, str], status: str, error_code: str)
        Signal emitted after `record_state` execution
    cleared : Signal()
        Signal emitted after `clear` execution
    """

    SPECIALS = SpecialColumns(
        section="Section",
        status="Status",
        code="Error code",
        reference="Reference",
    )

    def __init__(
        self,
        includes: SearchPattern = "*",
        excludes: Optional[SearchPattern] = None,
        # metadata: Optional[SearchPattern] = None,  # TODO?
        numerical_only = False,
        section = "",
        precision = 9,
        hold = False,
        raw_output = False,
    ):
        check_arg(raw_output, "raw_output", bool)
        check_arg(numerical_only, "numerical_only", bool)

        self.__includes = make_wishlist(includes, "includes")
        self.__excludes = make_wishlist(excludes, "excludes")
        self._numerical_only = numerical_only
        # self.__metadata: list[str] = metadata
        self.__section = ""
        self.section = section
        self.__hold = False
        self.hold = hold
        self.__precision = 9
        self.precision = precision
        self._raw_output = raw_output
        self.__variables: list[str] = []
        self.__expressions: EvalString = None
        self._watch_object: System = None
        self._owner: Optional[str] = None
        self.paused = False

        # Signal
        self.state_recorded = Signal(
            args=["time_ref", "status", "error_code"],
            name="cosapp.recorders.recorder.BaseRecorder.state_recorded",
        )
        self.cleared = Signal(name="cosapp.recorders.recorder.BaseRecorder.cleared")

    def __getstate__(self) -> dict[str, Any]:
        """Creates a state of the object.

        The state type depend on the object, see
        https://docs.python.org/3/library/pickle.html#object.__getstate__
        for further details.

        Returns
        -------
        dict[str, Any]:
            state
        """
        state = object__getstate__(self).copy()
        return state

    def __json__(self) -> dict[str, Any]:
        """Creates a JSONable dictionary representation of the object.

        Returns
        -------
        dict[str, Any]
            The dictionary
        """
        qualname = f"{self.__module__}.{self.__class__.__qualname__}"
        state = self.__getstate__()

        state.pop("_watch_object")
        state.pop("_owner")
        state.pop("state_recorded")
        state.pop("cleared")

        return {
            "__class__": qualname,
            **state,
        }

    @classmethod
    def from_dict(cls, state):
        rec = cls()
        for key, val in state.items():
            setattr(rec, key, val)
        return rec

    @classmethod
    def extend(
        cls, recorder, includes: SearchPattern = [], excludes: SearchPattern = []
    ) -> BaseRecorder:
        """
        Factory returning a new recorder, with similar attributes as
        `recorder`, but extended `includes` and `excludes` fields.

        Parameters
        ----------
        includes : str, list of str, or None, optional
            Variables patterns extending `recorder` inclusion patterns; default `[]` (i.e. no change).
        excludes : str, list of str, or None, optional
            Variables patterns extending `recorder` exclusion patterns; default `[]` (i.e. no change).
        """
        new = cls(
            recorder.includes + make_wishlist(includes, "includes"),
            recorder.excludes + make_wishlist(excludes, "excludes"),
            recorder._numerical_only,
            recorder.section,
            recorder.precision,
            recorder.hold,
            recorder._raw_output,
        )
        new.watched_object = recorder.watched_object
        return new

    @property
    def watched_object(self) -> Optional[System]:
        """System : The object from which data are read."""
        return self._watch_object

    @watched_object.setter
    def watched_object(self, module: System):
        from cosapp.base import System

        if not (module is None or isinstance(module, System)):
            typename = type(module).__qualname__
            raise TypeError(
                f"Recorder must be attached to a System or a Driver; got {typename}."
            )
        is_new = module is not self._watch_object
        
        if self._watch_object is None or is_new:
            self.__variables = []
            self.__expressions = None
            self._watch_object = module

    @property
    @abc.abstractmethod
    def _raw_data(self) -> list[list[Any]]:
        """Returns a raw/unformated version of records.

        Returns
        -------
        list[list[Any]]
            Records of `watched_object` for variables given by method `field_names()`
        """
        pass

    @abc.abstractmethod
    def export_data(self) -> pandas.DataFrame:
        """Export recorded results into a pandas.DataFrame object."""
        pass

    @property
    def includes(self) -> list[str]:
        """str or list of str : Variables matching these patterns will be included."""
        return self.__includes

    @property
    def excludes(self) -> list[str]:
        """str or list of str: Variables matching these patterns will be excluded."""
        return self.__excludes

    @property
    def section(self) -> str:
        """str : Current section name."""
        return self.__section

    @section.setter
    def section(self, section: str):
        check_arg(section, "section", str)
        self.__section = section

    @property
    def hold(self) -> bool:
        """bool : Append the new data or not."""
        return self.__hold

    @hold.setter
    def hold(self, value: bool):
        check_arg(value, "hold", bool)
        self.__hold = value

    @property
    def precision(self) -> int:
        """int : Precision digits when writing floating point number."""
        return self.__precision

    @precision.setter
    def precision(self, value: int):
        check_arg(value, "precision", int, lambda n: n > 0)
        self.__precision = value

    def field_names(self) -> list[str]:
        """Returns list of requested variables and expressions.

        Returns
        -------
        list[str]
            Variable names matching the includes/excludes patterns of the user in the watched object.

        .. note::
            Inward and outward variables will appear without the prefix `inwards.` or `outwards.`.
        """
        if not self.__variables and self.watched_object:
            self.__update_varlist()
        return self.__variables

    def __contains__(self, field: str) -> bool:
        return field in self.field_names()

    def __update_varlist(self) -> None:
        """Update the list of fields to be recorded"""
        includes = []
        evaluables = {}
        context = self.watched_object
        for expression in set(self.__includes):
            try:
                evaluable = EvalString(expression, context)
                evaluable.eval()
            except:
                includes.append(expression)
            else:
                if expression in context:
                    # Keep expression in search list,
                    # in case it matches an exclusion pattern
                    includes.append(expression)
                else:
                    evaluables[expression] = evaluable.eval()
        
        if self._numerical_only:
            criterion = is_numerical
        else:
            criterion = lambda x: True
        
        variables = find_variables(
            context,
            includes,
            self.__excludes,
            advanced_filter=criterion,
            include_const=True,
        )
        variables.update(evaluables)

        # Filter out attributes containing forbidden objects
        # such as non-copyable CoSApp objects or iterators
        variables = dict(
            filter(no_forbidden_objects, variables.items())
        )
        self.__variables = variables = sorted(variables)
        self.__expressions = EvalString(", ".join(variables).join("[]"), context)

    def _get_units(self, varnames: Optional[list[str]] = None) -> list[str]:
        """Generate the list of units associated with the requested variables.

        Parameters
        ----------
        vars : list of str, optional
            list of the variables to get the units; if not provided, takes field_names

        Returns
        -------
        list[str]
            Variable units for the variables matching the includes/excludes patterns of the user.
        """
        if varnames is None:
            varnames = self.field_names()

        units = []
        if (system := self.watched_object):
            for varname in varnames:
                try:
                    variable = system.get_variable(varname)
                except:
                    unit = ""
                else:
                    unit = variable.unit
                units.append(unit or "-")

        return units

    def start(self):
        """Initialize recording support."""
        if self.watched_object is None:
            raise RuntimeError("A recorder should be watching a Driver.")

    def record_state(self, time_ref: Union[float, str], status="", error_code="0") -> None:
        """Record the watched object at the provided status.

        Parameters
        ----------
        time_ref : float or str
            Current simulation time (float) or point reference (str)
        status : str, optional
            Status of the simulation; default `''`.
        error_code : str, optional
            Error code; default `'0'`.
        """
        if self.paused:
            return

        line = [self.section, status, error_code, str(time_ref)] + self.formatted_data()
        self._record(line)
        self.state_recorded.emit(time_ref=time_ref, status=status, error_code=error_code)

    @abc.abstractmethod
    def formatted_data(self) -> list[Any]:
        """Returns collected data from watched object as a formatted list."""
        pass

    def collected_data(self) -> list[Any]:
        """Collects and returns recorded data from watched object as a list."""
        if self.__expressions is None:
            self.__update_varlist()
        return self.__expressions.eval()

    @abc.abstractmethod
    def _record(self, line: list[Any]) -> None:
        """
        Internally record data collected into list `line`.
        Required by `record_state` method.
        """
        pass

    @abc.abstractmethod
    def _batch_record(self, lines: list[list[Any]]) -> None:
        """Records multiple lines at a time.

        Internal API allowing efficient concatenation of recorders.
        """
        pass

    @abc.abstractmethod
    def _enable_parallel_execution(self, exec_type: ExecutionType, chunk_id: int) -> None:
        """Enables the use of this `Recorder` in parallel execution.
        
        This method must perform the necessary changes to allow parallel
        execution in a multithreading or multiprocessing context.

        Parameters
        ----------
        exec_type : ExecutionType
            Type of parallel execution
        chunk_id : int
            Identifier of the chunk to be handled by this recorder
        """
        pass

    @abc.abstractmethod
    def _disable_parallel_execution(self, exec_type: ExecutionType, chunk_id: int) -> None:
        """Disables the use of this `Recorder` in parallel execution.
        
        This method rollbacks the changes made to the `Recorder` to handle parallel
        execution.

        Parameters
        ----------
        exec_type : ExecutionType
            Type of parallel execution
        chunk_id : int
            Identifier of the chunk to be handled by this recorder
        """
        pass

    def _set_parallel_execution(self, chunck_id: int) -> None:
        """"""

    def clear(self):
        """Clear all previously stored data."""
        self.cleared.emit()

    @abc.abstractmethod
    def exit(self):
        """Close recording session."""
        pass

    def restore(self, index: int):
        """Restore the watch object state from the recorded data.

        Parameters
        ----------
        index : int
            Index of the record as iloc in the Pandas DataFrame
        """
        check_arg(index, "index", int)

        data = self._raw_data
        if index < 0 or index > len(data) - 1:
            raise IndexError(f"Index {index} does not exist in this Recorder")

        inputs = find_variables(
            self._watch_object, includes=["*"], excludes=[], outputs=False
        )

        recording = data[index][4:]

        for idx, var in [
            (idx, var)
            for idx, var in enumerate(self.field_names())
            if var in inputs
        ]:
            try:
                self._watch_object[var] = copy.deepcopy(recording[idx])
            except KeyError:
                pass

    def check(self) -> None:
        try:
            self.formatted_data()
        except Exception as ex:
            warnings.warn(
                f"Captured exception {ex!r} while trying to collect data in {self.watched_object}"
                "; recorder may fail.",
                RuntimeWarning
            )
