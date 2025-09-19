"""Utility functions for testing purposes"""

import pickle
import numpy
import pytest
import inspect
import warnings
import itertools
from numbers import Number
from contextlib import contextmanager
from typing import Any, Union, Iterable, Optional

from cosapp.base import System, Driver
from cosapp.utils.distributions import Distribution
from cosapp.utils.json import to_json


ArgsKwargs = tuple[tuple[Any, ...], dict[str, Any]]


def has_keys(dictionary: dict, *keys) -> bool:
    """Utility function to test if a dictionary has the given keys"""
    return set(dictionary.keys()) == set(keys)


def assert_keys(dictionary, *keys):
    """Utility function to test dictionary keys"""
    if not has_keys(dictionary, *keys):
        actual = list(dictionary.keys())
        raise KeyError(f"actual: {actual}; expected: {list(keys)}") 


def assert_all_type(collection, dtype):
    """Asserts that all the elements of a collecion are of a given type"""
    def assert_type(name, value):
        if not isinstance(value, dtype):
            actual = type(value).__name__
            raise TypeError(
                f"{name} is of type {actual}; expected {dtype.__name__}"
            ) 
    if isinstance(collection, dict):
        for key, value in collection.items():
            assert_type(f"element with key '{key}'", value)
    else:
        for i, value in enumerate(collection):
            assert_type(f"element #{i}", value)


def rel_error(actual: Union[Number, Iterable], expected: Union[Number, Iterable]) -> Union[float, numpy.ndarray]:
    """Computes the relative error of `actual` compared to `expected`
    """
    error = lambda a, x: abs(a) if x == 0 else abs(a / x - 1)

    if isinstance(actual, Number):
        return error(actual, expected)
    
    actual = numpy.asarray(actual)

    if isinstance(expected, Number):
        iterator = (error(a, expected) for a in actual.flat)
    else:
        iterator = itertools.starmap(error,
            zip(actual.flat, numpy.ravel(expected))
        )
    errors = numpy.fromiter(
        iterator,
        dtype=float,
        count=actual.size,
    )
    return errors.reshape(actual.shape)


def assert_close_dict(actual: dict, expected: dict, abs=None, rel=None) -> None:
    """Assert that `actual` and `expected` dictionaries are identical, within given tolerance bounds.
    Works recursively with nested dictionaries.
    """
    def assert_close(actual: dict, expected: dict, context=""):
        """Recursive test function, with contextual message"""
        assert set(actual) == set(expected), context
        for key, value in expected.items():
            local_context = f"{context}[{key!r}]"
            if isinstance(value, dict):
                assert_close(actual[key], value, context=local_context)
            else:
                try:
                    expected_value = pytest.approx(value, abs=abs, rel=rel)
                except TypeError:
                    expected_value = value
                assert actual[key] == expected_value, f"key {local_context}"

    assert_close(actual, expected)


def get_args(*args, **kwargs) -> ArgsKwargs:
    """Utility function to collect args and kwargs in a tuple"""
    return args, kwargs


@contextmanager
def no_exception():
    """Context manager to assert that a block does not raise any exception"""
    try:
        yield

    except Exception as error:
        raise AssertionError(f"Unexpected exception raised: {error!r}")


@contextmanager
def not_raised(ExpectedException):
    """Context manager to assert that a block does not raise `ExpectedException`"""
    # https://gist.github.com/oisinmulvihill/45c14271fad7794a4a52516ecb784e69
    try:
        yield

    except ExpectedException as error:
        raise AssertionError(f"Raised {error!r} exception when it should not!")

    except Exception as error:
        raise AssertionError(f"Unexpected exception raised: {error!r}")


def DummySystemFactory(
    classname: str,
    base: Optional[type[System]]=None,
    **settings
) -> type[System]:
    """Factory creating a dummy system class with custom attributes.
    System is "dummy" in the sense it has no compute, and no connectors.
    
    Parameters:
    -----------
    - classname [str]: Output class name
    - base [type[System], optional]:
        Base class, derived from `System`. If not provided (default), base is `System`.
    - **settings [dict[str, args_kwargs]]:
        Class characteristics, as a dictionary. Keys are attribute names (e.g. inputs);
        values are (args, kwargs) forwarded to the associated method (e.g. `add_input`).
    
    Possible Attributes:
    --------------------
    - inputs
    - outputs
    - inwards
    - outwards
    - modevars_in
    - modevars_out
    - transients
    - rates
    - properties
    - children
    - events
    - unknowns
    - equations
    - targets
    - design_methods

    Examples:
    ---------
    >>> from cosapp.utils.testing import DummySystemFactory, get_args
    >>> 
    >>> Dummy = DummySystemFactory(
    >>>     inwards=[
    >>>         get_args('h', 0.1, unit='m'),
    >>>         get_args('L', 2.0, unit='m'),
    >>>     ],
    >>>     outwards=[
    >>>         get_args('b_ratio', 0.0),
    >>>     ],
    >>>     events=[
    >>>         get_args('kaboom', trigger='h > L / 2')
    >>>     ],
    >>>     properties=[
    >>>         get_args('n', 12),
    >>>     ],
    >>>     equations=[
    >>>         "b_ratio == 1",
    >>>     ],
    >>>     unknowns=[
    >>>         "h",
    >>>     ],
    >>> )
    >>> 
    >>> s = Dummy('s')
    >>> assert s.assembled_problem().shape == (1, 1)
    """
    # mapping option / method
    # for example: `inputs` <-> `add_input`
    method_mapping = {
        "inputs": "add_input",
        "outputs": "add_output",
        "inwards": "add_inward",
        "outwards": "add_outward",
        "modevars_in": "add_inward_modevar",
        "modevars_out": "add_outward_modevar",
        "transients": "add_transient",
        "rates": "add_rate",
        "properties": "add_property",
        "children": "add_child",
        "events": "add_event",
        "unknowns": "add_unknown",
        "equations": "add_equation",
        "targets": "add_target",
        "design_methods": "add_design_method",
    }
    unknown_keys = set(settings).difference(method_mapping)

    if unknown_keys:
        warnings.warn(
            f"settings {sorted(unknown_keys)} are not supported."
        )

    methods = {
        method_mapping[name]: ctor_data
        for name, ctor_data in settings.items() if name in method_mapping
    }

    base_message = "argument `base` must be a type derived from `System`"

    if base is None:
        base = System
    elif not inspect.isclass(base):
        raise TypeError(
            f"{base_message}; got {base!r}."
        )
    elif not issubclass(base, System):
        raise ValueError(
            f"{base_message}; got class `{base.__name__}`."
        )

    class Prototype(base):
        def setup(self, **kwargs):
            super().setup(**kwargs)

            for method_name, values in methods.items():
                if values is None:
                    continue
                if not isinstance(values, list):
                    values = [values]
                for info in values:
                    try:
                        args, kwargs = info  # expects a list of (tuple, dict)
                    except ValueError:
                        args, kwargs = [info], {}  # fallback
                    getattr(self, method_name)(*args, **kwargs)
    
    return type(classname, (Prototype,), {})


def are_same(o1: Union[Driver, System, Distribution], o2: Union[Driver, System, Distribution]) -> bool:
    """Utility function to compare two objects for equality.
    It serializes both objects to JSON and compares the resulting strings.
    """
    j1 = to_json(o1)
    j2 = to_json(o2)
    are_equal = (j1 == j2)
    # if not are_equal:
    #     print(j1)
    #     print(j2)
    return are_equal


def pickle_roundtrip(s: System) -> System:
    """Utility function to pickle and unpickle a System object.
    This is useful for testing serialization and deserialization of systems.
    """
    return pickle.loads(pickle.dumps(s))
