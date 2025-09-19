"""
Basic class handling model tree structure.
"""
from __future__ import annotations
import abc
import logging
from collections import OrderedDict
from collections.abc import Sequence, Generator, MappingView
from numbers import Integral
from typing import Optional, Any, TypeVar

from cosapp.patterns.visitor import Visitor, Component as VisitedComponent
from cosapp.core.signal import Signal
from cosapp.utils.naming import NameChecker, CommonPorts
from cosapp.utils.logging import LoggerContext, LogFormat, LogLevel, HandlerWithContextFilters
from cosapp.utils.helpers import check_arg
from cosapp.utils.state_io import object__getstate__

logger = logging.getLogger(__name__)

ModuleType = TypeVar("ModuleType", bound="Module")


class Module(LoggerContext, VisitedComponent, metaclass=abc.ABCMeta):
    # class Module does not inherit directly from abc.ABC, due to 
    # a bug in Python 3.6 preventing the use of __weakref__ in slots.
    # Ref: https://bugs.python.org/issue30463
    # Here, use of abc.ABCMeta makes the class effectively abstract,
    # by activating decorators of the kind @abc.abstractclass, etc.
    """
    A class to describe generic properties and functions of a component that can be single or
    made of child `Module`.

    Parameters
    ----------
    - name [str]:
        `Module` name

    Attributes
    ----------
    - name [str]:
        `Module` name
    - children [dict[str, Module]]:
        Sub-modules of current `Module`, referenced by names.
    - parent [Module]:
        Parent `Module` of current `Module`; `None` if there is no parent.
    - exec_order [Iterator[str]]:
        Execution order in which sub-modules should be computed.
    - description [str]:
        `Module` description.

    - _active [bool]:
        If False, the `Module` will not execute its `run_once` method
    - _compute_calls [int]:
        Store if the number of times :py:meth:`~cosapp.core.module.Module.compute` was called (due to inhibition of clean status)

    Signals
    -------
    - setup_ran [Signal]:
        Signal emitted after :py:meth:`~cosapp.core.module.Module.call_setup_run` execution
    - computed [Signal]:
        Signal emitted after the :py:meth:`~cosapp.core.module.Module.compute` stack (= after :py:meth:`~cosapp.core.module.Module._post_compute`) execution
    - clean_ran [Signal]:
        Signal emitted after the :py:meth:`~cosapp.core.module.Module.call_clean_run` execution
    """

    __slots__ = (
        '__weakref__', '_name', 'children', 'parent', '_active',
        '_compute_calls', 'setup_ran', 'computed', 'clean_ran',
        '__members', '_desc',
    )

    _name_check = NameChecker(excluded=CommonPorts.names())

    def __init__(self, name: str):
        """`Module` constructor

        Parameters
        ----------
        - name [str]:
            Module name
        """
        self._name = self._name_check(name)
        self._desc = ""
        self.children: dict[str, Module] = OrderedDict()
        self.parent: Optional[Module] = None
        self._active: bool = True
        self._compute_calls: int = 0

        # Signals
        self.setup_ran = Signal(name="cosapp.core.module.Module.setup_ran")
        self.clean_ran = Signal(name="cosapp.core.module.Module.clean_ran")
        self.computed = Signal(name="cosapp.core.module.Module.computed")
        private_prefix = f"_{type(self).__qualname__}__"
        self.__members = set(
            filter(
                lambda name: not name.startswith(private_prefix),
                dir(type(self))
            )
        )

    def __getstate__(self) -> tuple[None, dict[str, Any]]:
        """Creates a state of the object.
        
        The state type depend on the object, see
        https://docs.python.org/3/library/pickle.html#object.__getstate__
        for further details.
        
        Returns
        -------
        tuple[None, dict[str, Any]]:
            state
        """
        
        _, slots = object__getstate__(self)
        slots.pop("_Module__members")
        return None, slots

    def __dir__(self):
        """Collection of all member names (used for autocompletion)"""
        return self.__members

    def tree(self: ModuleType, downwards=False) -> Generator[ModuleType, None, None]:
        """Generator recursively yielding all elements in module tree.
        
        Parameters:
        -----------
        - downwards [bool, optional]:
            If `True`, yields elements from top to bottom.
            If `False` (default), yields elements from bottom to top.
        """
        if downwards:
            yield self
        for child in self.children.values():
            yield from child.tree(downwards)
        if not downwards:
            yield self

    def send_visitor(self, visitor: Visitor, downwards=False) -> None:
        """Recursively accept visitor throughout module tree."""
        for module in self.tree(downwards):
            module.accept(visitor)

    def __getattr__(self, name: str) -> Any:
        try:  # Faster than testing
            return self.children[name]
        except KeyError:
            return super().__getattribute__(name)

    @property
    def contextual_name(self) -> str:
        """str : Name of the module relative to the root one."""
        return "" if self.parent is None else self.full_name(trim_root=True)

    @property
    def compute_calls(self) -> int:
        """int : Number of calls to the compute method at last execution."""
        return self._compute_calls

    @property
    def name(self) -> str:
        """str : `Module` identifier."""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = self._name_check(name)

    @property
    def description(self) -> str:
        """str: Module description"""
        return self._desc

    @description.setter
    def description(self, desc: str) -> None:
        check_arg(desc, 'description', str)
        self._desc = desc

    @property
    def exec_order(self) -> MappingView[str]:
        """MappingView[str]: sub-module execution order, as a name iterator"""
        return self.children.keys()

    @exec_order.setter
    def exec_order(self, namelist: Sequence[str]) -> None:
        if not isinstance(namelist, Sequence):
            raise TypeError("exec_order must be an ordered sequence of strings")
        nameset = set(self.children)
        if set(namelist) != nameset:
            if nameset:
                msg = f"exec_order must be a permutation of {list(self.children)}"
            else:
                msg = f"Can't set exec_order, as {self.name!r} has no children"
            logger.error(f"{msg}; got {namelist}.")
            raise ValueError(msg)
        elif len(namelist) > len(self.children):
            repeated = list(namelist)
            for name in set(namelist):
                repeated.remove(name)
            raise ValueError(f"Repeated items {sorted(set(repeated))}")
        # Rearrange children in a new dictionary
        self.children = OrderedDict(
            (name, self.children[name])
            for name in namelist
        )

    @property
    def size(self) -> int:
        """int: Total number of elements in tree."""
        return sum(1 for _ in self.tree())

    def _add_member(self, name: str) -> None:
        """Add `name` to dynamic member list"""
        if '.' not in name:
            self.__members.add(name)

    def _pop_member(self, name: str) -> None:
        """Remove `name` to dynamic member list"""
        try:
            self.__members.remove(name)
        except:
            pass

    def path_to_root(self: ModuleType) -> Generator[ModuleType, None, None]:
        """Generator recursively yielding all elements up to root module.
        """
        current = self
        yield current
        while current.parent is not None:
            current = current.parent
            yield current

    def root(self: ModuleType) -> ModuleType:
        for root in self.path_to_root():
            continue
        return root

    def path(self: ModuleType) -> list[ModuleType]:
        """Returns full path from root Module as a list.
        
        Returns
        -------
        list[Module]
            Full module list from root to self
        """
        path = list(self.path_to_root())
        return list(reversed(path))

    def path_namelist(self) -> list[str]:
        """Returns full name list from root Module.
        
        Returns
        -------
        list[str]
            The module full name list
        """
        names = [elem.name for elem in self.path_to_root()]
        return list(reversed(names))

    def full_name(self, trim_root=False) -> str:
        """Returns full name from root Module.
        
        Parameters
        ----------
        trim_root : bool (optional, default False)
            Exclude root Module name if True.

        Returns
        -------
        str
            The module full name
        """
        names = self.path_namelist()
        start = 1 if trim_root else 0
        return ".".join(names[start:])

    def call_setup_run(self):
        """Execute `setup_run` recursively on all modules."""
        with self.log_context(" - call_setup_run"):
            logger.debug(f"Call {self.name}.setup_run")
            self._compute_calls = 0  # Reset the counter
            for child in self.children.values():
                child.call_setup_run()
            self.setup_run()
            self.setup_ran.emit()

    def setup_run(self):
        """Method called once before starting any simulation."""
        pass  # pragma: no cover

    def call_clean_run(self):
        """Execute `clean_run` recursively on all modules."""
        with self.log_context(" - call_clean_run"):
            logger.debug(f"Call {self.name}.clean_run")
            self.clean_run()
            for child in self.children.values():
                child.call_clean_run()
            self.clean_ran.emit()

    def clean_run(self):
        """Method called once after any simulation."""
        pass  # pragma: no cover

    def get_path_to_child(self, other: Module, trim_top=True) -> str:
        """
        Returns the relative path to target Module `other`.
        Raises `ValueError` if `other` is not related to current Module.

        Parameters:
        -----------
        - other [Module]:
            sub-module of module tree.
        - trim_top [boll, optional]:
            if `True`, the name of the top module (self) is added to the path.
            Default is `False`.

        Returns
        -------
        str: The relative path to `other`
        """
        path = list()
        child = other
        while child is not self:
            path.append(child.name)
            child = child.parent
            if child is None:
                raise ValueError(
                    f"{other.name!r} is not a child of {self.name!r}."
                )
        if not trim_top:
            path.append(self.name)
        return ".".join(reversed(path))

    def _add_child(self, child: ModuleType, execution_index: Optional[int]=None, desc="", check=True) -> ModuleType:
        """Add a child to the current `Module`.
        
        This method is the internal implementation of `add_child` but also offer
        the capability to perform the operation without checking, which has a huge
        impact on performance (serial/deserial, etc.).

        Parameters
        ----------
        - child [Module]:
            `Module` to add to the current `Module`
        - execution_index [int, optional]:
            Index of the execution order list at which the `Module` should be inserted;
            default latest.
        - desc [str, optional]:
            Module description in the context of its parent module.
        - check [bool]:
            Whether to perform checks (types, pre-existing child, etc.) when adding a new child or not

        Returns
        -------
        `child`
        """
        # Type validation
        check_arg(child, 'child', Module)

        specific_order = None
        if execution_index is not None:
            check_arg(execution_index, 'execution_index', Integral)
            specific_order = list(self.exec_order)
            specific_order.insert(execution_index, child.name)

        if check and child.name in self.children:
            raise ValueError(
                "{} {!r} cannot be added, as Module already contains an object with the same name"
                "".format(type(child).__qualname__, child.name)
            )

        child.parent = self
        child.description = desc
        self.children[child.name] = child
        self._add_member(child.name)

        if specific_order:
            self.exec_order = specific_order

        return child

    def add_child(self, child: ModuleType, execution_index: Optional[int]=None, desc="") -> ModuleType:
        """Add a child `Module` to the current `Module`.

        When adding a child `Module`, it is possible to specified its position
        in the execution order.

        Parameters
        ----------
        - child [Module]:
            `Module` to add to the current `Module`
        - execution_index [int, optional]:
            Index of the execution order list at which the `Module` should be inserted;
            default latest.
        - desc [str, optional]:
            Module description in the context of its parent module.

        Returns
        -------
        `child`
        """
        return self._add_child(child, execution_index, desc, check=True)

    def pop_child(self, name: str) -> Module:
        """Remove submodule `name` from current module.

        Parameters
        ----------
        name: str
            Name of submodule to be removed.

        Returns
        -------
        `Module`
            The removed module.

        Raises
        ------
        `AttributeError` if no match is found.
        """
        try:
            child = self.children.pop(name)
        except KeyError:
            raise AttributeError(f"Component {name} is not a child of {self}.")

        self._pop_member(name)
        child.parent = None

        return child

    def _precompute(self) -> None:
        """Actions performed prior to the `Module.compute` call."""
        pass

    def compute_before(self) -> None:
        """Contains the customized `Module` calculation, to execute before children."""
        pass

    def compute(self) -> None:
        """Contains the customized `Module` calculation, to execute after children."""
        pass

    def _postcompute(self) -> None:
        """Actions performed after the `Module.compute` call."""
        pass

    def run_once(self) -> None:
        """Run the module once.

        Execute the model of this `Module` and its children in the execution order.

        Notes
        -----

        The driver are not executed when calling this method; only the physical model.
        """
        with self.log_context(" - run_once"):
            if self.is_active():
                self._precompute()

                logger.debug(f"Call {self.name}.compute_before()")
                self.compute_before()

                for name, child in self.children.items():
                    logger.debug(f"Call {self.name}.{name}.run_once()")
                    child.run_once()

                logger.debug(f"Call {self.name}.compute()")
                self._compute_calls += 1
                self.compute()

                self._postcompute()
                self.computed.emit()
            
            else:
                logger.debug(f"Skip {self.name} execution - Inactive")

    def is_active(self) -> bool:
        """Is this Module execution activated?

        Returns
        -------
        bool
            Activation status
        """
        return self._active

    @abc.abstractmethod
    def is_standalone(self) -> bool:
        """Is this Module able to solve itself?

        Returns
        -------
        bool
            Ability to solve the module or not.
        """
        pass

    def log_debug_message(
        self,
        handler: HandlerWithContextFilters,
        record: logging.LogRecord,
        format: LogFormat = LogFormat.RAW,
    ) -> bool:
        """Callback method on the module to log more detailed information.
        
        This method will be called by the log handler when :py:meth:`~cosapp.utils.logging.LoggerContext.log_context`
        is active if the logging level is lower or equals to VERBOSE_LEVEL. It allows
        the object to send additional log message to help debugging a simulation.

        .. note::
            logger.log method cannot be used here. Use handler.handle(record)

        Parameters
        ----------
        handler : HandlerWithContextFilters
            Log handler on which additional message should be published.
        record : logging.LogRecord
            Log record
        format : LogFormat
            Format of the message

        Returns
        -------
        bool
            Should the provided record be logged?
        """
        message = record.getMessage()
        emit_record = super().log_debug_message(handler, record, format)

        if message.endswith("call_setup_run"):
            emit_record = False
        elif message.endswith("call_clean_run"):
            emit_record = False
            activate = getattr(record, "activate", None)
            if activate == False:
                # Display the number of system execution
                msg = f"Compute calls for {self.full_name()}: {self.compute_calls}"
                handler.log(LogLevel.DEBUG, msg, name=logger.name)

        return emit_record
