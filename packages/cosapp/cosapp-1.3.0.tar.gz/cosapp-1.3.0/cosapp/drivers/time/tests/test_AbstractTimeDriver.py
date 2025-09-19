import pytest
from unittest.mock import MagicMock, patch

import logging
import re
import numpy as np

from cosapp.recorders import DataFrameRecorder
from cosapp.drivers.time import base as time_driver_base
from cosapp.drivers.time.base import AbstractTimeDriver
from cosapp.systems import System
from cosapp.drivers import Driver
from cosapp.utils.logging import LogFormat, LogLevel
from cosapp.utils.testing import rel_error, not_raised
from cosapp.core.signal import Slot


@pytest.fixture(autouse=True)
def PatchAbstractTimeDriver():
    """Patch AbstractTimeDriver to make it instanciable for tests"""
    patcher = patch.multiple(
        AbstractTimeDriver,
        __abstractmethods__ = set(),
    )
    patcher.start()
    yield
    patcher.stop()


def test_AbstractTimeDriver_init_default():
    driver = AbstractTimeDriver()
    assert driver.name == "Time driver"
    assert driver.owner is None
    assert driver.dt is None
    assert driver.time_interval is None


@pytest.mark.parametrize("settings, expected", [
    (dict(), dict()),
    (dict(name="John Doe"), dict(name="John Doe")),
    (dict(time_interval=(0, 1)), dict(time_interval=(0, 1))),
    (dict(dt=0.1, time_interval=(0, 1)), dict(dt=0.1, time_interval=(0, 1))),
    (dict(dt=0.1), dict(dt=0.1)),
    (dict(dt=1), dict(dt=1)),
    (dict(dt=0), dict(error=ValueError)),
    (dict(dt=-0.1), dict(error=ValueError)),
    (dict(dt="0.1"), dict(error=TypeError)),
    (dict(time_interval=(2, 1)), dict(error=ValueError)),
    (dict(time_interval=(1, 2, 3)), dict(error=ValueError)),
    (dict(time_interval=2.5), dict(error=TypeError)),
])
def test_AbstractTimeDriver_init_args(settings, expected):
    error = expected.get('error', None)
    if error is None:
        driver = AbstractTimeDriver(**settings)
        assert driver.dt == expected.get('dt', None)
        assert driver.time_interval == expected.get('time_interval', None)
        assert driver.name == expected.get('name', 'Time driver')
    else:
        with pytest.raises(error):
            AbstractTimeDriver(**settings)


@pytest.mark.parametrize("value, expected", [
    (10, dict(value=10)),
    (1e-2, dict(value=1e-2)),
    (1e-12, dict(value=1e-12)),
    (0, dict(error=ValueError, match="dt.*invalid value")),
    (-0.5, dict(error=ValueError, match="dt.*invalid value")),
    ("0.5", dict(error=TypeError, match="got str")),
])
def test_AbstractTimeDriver_dt(value, expected):
    driver = AbstractTimeDriver()
    assert driver.dt is None

    error = expected.get('error', None)
    if error is None:
        driver.dt = value
        assert driver.dt == expected['value']
    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            driver.dt = value


@pytest.mark.parametrize("value, expected", [
    ((0, 1), dict(value=(0, 1))),
    ([0, 1], dict(value=(0, 1))),
    ((0.2, 0.2), dict(value=(0.2, 0.2))),
    ((1, 1.5), dict(value=(1, 1.5))),
    ((-0.5, 0), dict(error=ValueError, match="start time")),
    (('0', 0.2), dict(error=TypeError, match="start time")),
    ((0.2, 0.1), dict(error=ValueError, match="end time")),
    ((0, np.inf), dict(error=ValueError, match="end time")),
    ((0, '0.5'), dict(error=TypeError, match="end time")),
    ((1, 2, 3), dict(error=ValueError, match="time_interval.*invalid")),
    (2.5, dict(error=TypeError, match="got float")),
    ("lifetime", dict(error=TypeError, match="got str")),
])
def test_AbstractTimeDriver_time_interval(value, expected):
    driver = AbstractTimeDriver()
    assert driver.time_interval is None

    error = expected.get('error', None)
    if error is None:
        driver.time_interval = value
        assert driver.time_interval == expected['value']
    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            driver.time_interval = value


@pytest.mark.parametrize("dt, expected", [(1e-2, 1e-2), (0.1, 0.02), (None, 0.02)])
def test_AbstractTimeDriver_limit_dt(ode_case_1, dt, expected):
    ode, driver = ode_case_1(AbstractTimeDriver, time_interval=[0, 0.1], record_dt=True)
    if dt is not None:
        driver.dt = dt
        assert driver.dt == dt
    else:
        assert driver.dt is None
    ode.tau = 0.1
    ode.run_drivers()
    comment = "Time step should be limited by transient max_time_step"
    assert driver.recorded_dt.min() == pytest.approx(expected, rel=1e-12), comment
    assert driver.recorded_dt.max() == pytest.approx(expected, rel=1e-12), comment


@pytest.mark.parametrize("scenario, ok", [
    # constant value of f.max_time_step
    (dict(values={'sub2.y': 10}), True),
    (dict(values={'sub2.y': 0}), False),
    (dict(values={'sub2.y': -0.1}), False),
    # non-const max_time_step
    (dict(values={'sub2.y': '1 if t < 0.2 else -1'}, time_interval=(0, 0.3)), False),
    (dict(values={'sub2.y': '1 if t < 0.5 else -1'}, time_interval=(0, 0.3)), True),
])
def test_AbstractTimeDriver_dt_RuntimeError(scenario, ok):
    """
    Check that time driver raises RuntimeError when the maximum time step of
    one of the transients is not strictly positive at the beginning of time loop.
    """
    class SubSystem(System):
        def setup(self):
            self.add_inward('x', 1.0)
            self.add_inward('y', 1.0)

    class DynamicSystem(System):
        def setup(self):
            self.add_child(SubSystem('sub1'))
            self.add_child(SubSystem('sub2'))

            self.add_transient('f', der='sub1.x * sub1.y', max_time_step='0.5 * sub2.y')

    # set driver settings
    settings = dict(dt=0.1, time_interval=[0, 0.2])  # default
    for setting in settings:
        try:
            settings[setting] = scenario.pop(setting)
        except KeyError:
            continue

    s = DynamicSystem('s')
    driver = s.add_driver(AbstractTimeDriver(**settings))
    driver.set_scenario(**scenario)

    if ok:
        try:
            s.run_drivers()
        except RuntimeError:
            pytest.fail("Should not raise RuntimeError")
    else:
        with pytest.raises(RuntimeError, match="non-positive value"):
            s.run_drivers()


def test_AbstractTimeDriver_set_time_before_System_init_mode():
    """Check that system time is synchronized with time driver
    when method `System.init_mode` is invoked.
    Related to https://gitlab.com/cosapp/cosapp/-/issues/156
    """
    t_start = 1.25  # arbitrary value

    class DummySystem(System):
        def init_mode(self):
            nonlocal t_start
            if self.time != t_start:
                pytest.fail("System time is not synched with driver time")

    system = DummySystem("dummy")
    driver = system.add_driver(AbstractTimeDriver())

    driver.dt = dt = 1.0
    driver.time_interval = (t_start, t_start + dt)
    # Check that start time is set as driver clock time
    system.run_drivers()

    t_start = 5.0
    # Check that the new start time is set as driver clock time
    driver.time_interval = (t_start, t_start + dt)
    system.run_drivers()


def test_AbstractTimeDriver_is_standalone():
    class StandaloneDriver(Driver):
        """Mock-up standalone driver"""
        def is_standalone(self) -> bool:
            return True

    driver = AbstractTimeDriver()
    assert not driver.is_standalone()

    driver.add_child(StandaloneDriver('standalone'))
    assert driver.is_standalone()

    driver = AbstractTimeDriver()
    sub = driver.add_child(Driver('sub'))
    assert not driver.is_standalone()
    sub.add_child(StandaloneDriver('standalone'))
    assert driver.is_standalone()


def test_AbstractTimeDriver_ode_run_driver(ode_case_1):
    ode, driver = ode_case_1(AbstractTimeDriver, record_dt=True)
    assert driver.owner is ode
    assert driver.dt is None
    assert driver.time_interval is None
    with pytest.raises(ValueError, match="Time interval.*not specified"):
        ode.run_drivers()
    driver.time_interval = (0, 1)
    assert driver.dt is None
    ode.tau = 0.1
    ode.run_drivers()
    # Check that time step was set by max_time_step of transient 'ode.f'
    assert driver.recorded_dt.min() == pytest.approx(0.02, rel=1e-12)
    assert driver.recorded_dt.max() == pytest.approx(0.02, rel=1e-12)

    ode, driver = ode_case_1(AbstractTimeDriver, dt=1e-2)
    assert driver.owner is ode
    assert driver.dt == 1e-2
    assert driver.time_interval is None
    with pytest.raises(ValueError, match="Time interval.*not specified"):
        ode.run_drivers()

    ode, driver = ode_case_1(AbstractTimeDriver, dt=1e-2, time_interval=[0, 1])
    assert driver.owner is ode
    assert driver.dt == 1e-2
    assert driver.time_interval == (0, 1)


def test_AbstractTimeDriver_dt_None():
    """Expected behaviour:
    ValueError exception raised when driver.dt is None, and `max_time_step` is not given by system transients"""
    class PlainSystem(System):
        def setup(self):
            self.add_inward('a', 1.0)
            self.add_transient('A', der='a')  # max_time_step unspecified

    system = PlainSystem('plain')
    driver = system.add_driver(AbstractTimeDriver(time_interval=(0, 1)))
    assert driver.dt is None
    assert driver.time_interval == (0, 1)
    with pytest.raises(ValueError, match="Time step.*not specified.*and could not be determined from transient variables"):
        system.run_drivers()


def test_AbstractTimeDriver_ode_add_scenario(ode_case_1):
    ode, driver = ode_case_1(AbstractTimeDriver)
    driver.set_scenario()
    assert driver.scenario.name == "scenario"
    assert driver.scenario.context is ode
    driver.set_scenario("test")
    assert driver.scenario.name == "test"
    assert driver.scenario.context is ode
    driver.set_scenario("final")
    assert driver.scenario.name == "final"
    assert driver.scenario.context is ode


@pytest.mark.parametrize("driver_settings, period, expected", [
    (dict(), None, dict(period=None)),
    (dict(), 0.1, dict(period=0.1)),
    (dict(dt=1e-2), None, dict(period=None)),
    (dict(time_interval=[0, 2]), 0.1, dict(period=0.1)),
    (dict(dt=1e-1, time_interval=[0, 2]), 0.01, dict(period=0.01)),
    (dict(dt=1e-2, time_interval=[0, 2]), 0.1, dict(period=0.1)),
    (dict(dt=1e-2, time_interval=[0, 2]), 1, dict(period=1)),
    (dict(dt=1e-2, time_interval=[0, 2]), 100, dict(period=2)),
    (dict(dt=1e-2, time_interval=[0, 2]), 0, dict(error=ValueError, match="period.* invalid value")),
    (dict(dt=1e-2, time_interval=[0, 2]), -1, dict(error=ValueError, match="period.* invalid value")),
    (dict(dt=1e-2, time_interval=[0, 2]), '0.1', dict(error=TypeError)),
])
def test_AbstractTimeDriver_add_recorder(two_tank_case, driver_settings, period, expected):
    """Test `add_recorder` method before driver execution"""
    system, driver = two_tank_case(AbstractTimeDriver, **driver_settings)
    assert driver.recorder is None

    rec_options = dict(includes='tank?.height')
    error = expected.get('error', None)

    if error is None:
        driver.add_recorder(DataFrameRecorder(**rec_options), period)
        assert driver.recording_period == expected['period']
        assert driver.recorder is not None
        assert 'time' in driver.recorder.field_names()

    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            driver.add_recorder(DataFrameRecorder(**rec_options), period)


@pytest.mark.parametrize("driver_settings, period, expected", [
    (dict(), None, dict(error=ValueError, match="Time interval was not specified")),
    (dict(), 0.1, dict(error=ValueError, match="Time interval was not specified")),
    (dict(dt=1e-2), None, dict(error=ValueError, match="Time interval was not specified")),
    (dict(time_interval=[0, 2]), 0.1, dict(period=0.1)),
    (dict(time_interval=[0, 2]), None, dict(period=None, warnings=["all time steps will be recorded"])),
    (dict(dt=1e-1, time_interval=[0, 2]), 0.01, dict(period=0.01)),
    (dict(dt=1e-2, time_interval=[0, 2]), 0.1, dict(period=0.1)),
    (dict(dt=1e-2, time_interval=[0, 2]), 1, dict(period=1)),
    (dict(dt=1e-2, time_interval=[0, 2]), 100, dict(period=2)),
])
def test_AbstractTimeDriver_recorder(ode_case_1, caplog, driver_settings, period, expected):
    """Test recorder behaviour during driver execution, assuming `add_recorder` is correct"""
    system, driver = ode_case_1(AbstractTimeDriver, **driver_settings)

    driver.add_recorder(DataFrameRecorder(includes='*'), period)
    driver.set_scenario(init={'f': 0}, values={'tau': 0.5})

    error = expected.get('error', None)

    if error is None:
        # run simulation and capture potential warnings
        caplog.clear()
        with caplog.at_level(logging.WARNING, logger=time_driver_base.__name__):
            system.run_drivers()

        assert driver.recording_period == expected['period']

        warnings = expected.get('warnings', [])
        assert len(caplog.records) == len(warnings)
        for warning, record in zip(warnings, caplog.records):
            assert warning in record.message
    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            system.run_drivers()


@pytest.mark.parametrize("dt, tol", [
    (1e-1, 1e-1),
    (1e-2, 1e-2),
])
def test_AbstractTimeDriver_rate_singleTimeStep(rate_case_1, dt, tol):
    settings = dict(time_interval=(0, dt), dt=dt)
    system, driver = rate_case_1(AbstractTimeDriver, **settings)
    assert driver.dt == driver.time_interval[1]

    driver.set_scenario(
        values = {'k': 1.5, 'U': 'exp(k * t)'}
    )
    system.run_drivers()

    assert system.k == 1.5
    solution = lambda t: system.k * np.exp(system.k * t)
    assert system.dU_dt == pytest.approx(solution(dt), rel=tol)


@pytest.mark.parametrize("dt, tol", [
    (1e-1, 1e-1),
    (1e-2, 1e-2),
])
def test_AbstractTimeDriver_rate(rate_case_1, dt, tol):
    settings = dict(time_interval=(0, 1), dt=dt)
    system, driver = rate_case_1(AbstractTimeDriver, **settings)

    driver.set_scenario(
        values = {'k': 1.5, 'U': 'exp(k * t)'}
    )
    driver.add_recorder(DataFrameRecorder(includes=['dU_dt']), period=0.1)

    system.run_drivers()

    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    exact = system.k * np.exp(system.k * time)
    error = rel_error(data['dU_dt'], exact)
    assert error.max() < tol


def test_AbstractTimeDriver_rate_no_initial_value():
    """
    Same as `test_AbstractTimeDriver_rate`, except rate `dU_dt`
    is not given any initial value.
    This test checks that `dU_dt` is correctly set by an explicit
    initial condition in `set_scenario`.
    Note: fixes bug reported in issue #193, "Bug in rate initialization".
    """
    class RateSystem(System):
        def setup(self):
            self.add_inward("k", 1.0)
            self.add_inward("U", 0.0)
            self.add_rate("dU_dt", source="U")

    system = RateSystem("system")
    driver = system.add_driver(AbstractTimeDriver(time_interval=(0, 0.1), dt=0.1))

    driver.set_scenario(
        init = {'dU_dt': 'k'},
        values = {
            'U': 'exp(k * t)',
            'k': -3.6,  # should initialize `dU_dt`
        }
    )

    driver.add_recorder(DataFrameRecorder(includes=['dU_dt']))

    system.run_drivers()

    data = driver.recorder.export_data()
    result = np.asarray(data['dU_dt'], dtype=float)
    assert system.k == -3.6
    assert result[0] == system.k
    assert result[1] == pytest.approx((np.exp(system.k * driver.dt) - 1) / driver.dt, rel=1e-14)


@pytest.mark.parametrize("options, recorder_period, expected", [
    (dict(), 0.1, dict(period=0.1)),
    (dict(dt=1e-2), None, dict(period=None)),
    (dict(dt=1e-2, time_interval=[0, 2]), 0.1, dict(period=0.1)),
    (dict(dt=1e-1, time_interval=[0, 2]), 1, dict(period=1)),
    (dict(dt=1e-1, time_interval=[0, 2]), 100, dict(period=2)),
])
def test_AbstractTimeDriver_recorded_times(two_tank_case, options, recorder_period, expected):
    driver_settings = dict(dt=1e-1, time_interval=[0, 1])
    driver_settings.update(options)
    system, driver = two_tank_case(AbstractTimeDriver, **driver_settings)

    driver.add_recorder(DataFrameRecorder(includes='tank1.height'), recorder_period)

    system.run_drivers()

    period = driver.recording_period
    assert period == expected['period']
    t0, tn = driver.time_interval
    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    if period is not None:
        assert time == pytest.approx(np.arange(t0, tn + period / 2, period), abs=1e-12)


@pytest.mark.parametrize("format", LogFormat)
@pytest.mark.parametrize("msg, kwargs, to_log, emitted", [
    ("zombie call_setup_run", dict(), False, None),
    ("useless start call_clean_run", dict(activate=True), False, None),
    (
        f"{System.CONTEXT_EXIT_MESSAGE} call_clean_run",
        dict(activate=False),
        False,
        dict(levelno=LogLevel.DEBUG, pattern=r"Compute calls for [\w\.]+: \d+")
    ),
    (
        "other message with activation",
        dict(activate=True),
        False,
        None,
    ),
    (
        "second message with deactivation",
        dict(activate=False),
        False, 
        dict(levelno=LogLevel.FULL_DEBUG, pattern=r"Time steps:\n")
    ),
    ("common message", dict(), True, None),
])
def test_AbstractTimeDriver_log_debug_message(format, msg, kwargs, to_log, emitted):
    # Attribute of a mock object can be created by passing them as kwargs.
    # Here, we get an object in the variable handler with two members:
    # an attribute level == LogLevel.DEBUG and an mocked attribute log
    handler = MagicMock(level=LogLevel.DEBUG, log=MagicMock())
    rec = logging.getLogRecordFactory()("log_test", LogLevel.INFO, __file__, 22, msg, (), None)
    for key, value in kwargs.items():
        setattr(rec, key, value)

    d = AbstractTimeDriver("dummy")

    assert d.log_debug_message(handler, rec, format) == to_log

    if "activate" in kwargs and not msg.endswith("_run"):
        assert d.record_dt == kwargs["activate"]

    if emitted:
        handler.log.assert_called_once()
        args = handler.log.call_args[0]
        assert args[0] == emitted["levelno"]
        assert re.match(emitted["pattern"], args[1]) is not None
    else:
        handler.log.assert_not_called()


def test_AbstractTimeDriver_init_conditions():
    """
    Test checking that initial conditions are applied before any system compute.
    Related to https://gitlab.com/cosapp/cosapp/-/issues/20
    """
    class Dummy(System):
        def setup(self):
            self.add_inward('c', 1.0)
            self.add_transient('x', der='c - c')

        def compute(self):
            if self.x <= 0:
                raise RuntimeError("x must be positive")
            if self.c >= 0:
                raise RuntimeError("c must be negative")

    system = Dummy('dummy')
    driver = system.add_driver(AbstractTimeDriver(dt=0.1, time_interval=[0, 0.1]))

    driver.set_scenario(
        init = {'x': 1.0},  # valid initial value for x
        values = {'c': '-(1 + t**2)'},  # valid c(t) value
    )

    system.x = system.c = -1.0
    with pytest.raises(RuntimeError, match="x must be positive"):
        system.run_once()

    system.x = system.c = 1.0
    with pytest.raises(RuntimeError, match="c must be negative"):
        system.run_once()

    system.c, system.x = 1.0, -1.0  # both invalid
    with pytest.raises(RuntimeError):
        system.run_once()
    
    # Running the time driver should not raise RuntimeError,
    # as both x and c are expected to be set at valid values
    with not_raised(RuntimeError):
        system.run_drivers()

    assert system.x == 1
    assert system.c == pytest.approx(-1.01)


@pytest.mark.parametrize("with_recorder", [True, False])
def test_AbstractTimeDriver_event_data(with_recorder):

    class EventSystem(System):
        def setup(self):
            self.add_inward("x", 0.0)
            self.add_inward("y", 1.0)
            self.add_inward("z", 2.0)
            self.add_event("crossing", trigger="x == y")

    s = EventSystem('s')

    driver = s.add_driver(
        AbstractTimeDriver(dt=0.05, time_interval=[0, 1])
    )
    driver.set_scenario(
        values={
            'x': 'exp(-2 * t)',
            'y': 'sin(10 * t)',
            'z': 't',
        },
    )
    if with_recorder:
        driver.add_recorder(
            DataFrameRecorder(includes=['x', 'y']),
            period=0.05,
        )
    s.run_drivers()

    # Retrieve event data
    event_data = driver.event_data
    assert 'time' in event_data.columns

    if with_recorder:
        # Check that event_data records the same fields as the recorder
        data = driver.recorder.export_data()
        assert list(data.columns) == list(event_data.columns)
        assert 'x' in event_data.columns
        assert 'y' in event_data.columns
        assert 'z' not in event_data.columns

    else:
        assert 'x' not in event_data.columns
        assert 'y' not in event_data.columns
        assert 'z' not in event_data.columns
        assert driver.recorder is None

    # `driver.event_data` contains twice as many entries as
    # `driver.recorded_events`, since it captures the system
    # state before and after each event occurrence.
    assert len(event_data) == 2 * len(driver.recorded_events)

    # Check event times
    event_times = np.array([
        record.time for record in driver.recorded_events
    ])
    xs = np.exp(-2 * event_times)
    ys = np.sin(10 * event_times)
    assert event_times == pytest.approx([
        0.09683198,
        0.24880810,
        0.65560525,
        0.92674399,
    ])
    assert np.allclose(xs, ys, atol=1e-12)
    assert np.array_equal(
        event_times,
        np.unique(event_data['time'])
    )


def test_AbstractTimeDriver_subdriver_setup():
    s = System('s')

    driver = s.add_driver(AbstractTimeDriver('driver', time_interval=[0, 1], dt=0.5))
    nested = driver.add_child(Driver('nested'))

    with patch("cosapp.core.signal.signal.inspect"):
        # Add bogus slots to `setup_run` and `compute` signals
        setup_run_callback = MagicMock()
        compute_callback = MagicMock()
        nested.setup_ran.connect(Slot(setup_run_callback))
        nested.computed.connect(Slot(compute_callback))

        s.run_drivers()
        assert setup_run_callback.call_count == 1
        assert compute_callback.call_count == 3


@pytest.mark.parametrize(
    "trigger, expected", [
        (None, 5),
        ("t > 2", 5),
        ("t > 0.235", 7),
    ]
)
def test_AbstractTimeDriver_system_update_signal(trigger, expected):
    """Test signal `AbstractTimeDriver.system_update_signal`
    """
    class Bogus(System):
        def setup(self):
            self.add_event("tada")
    
    system = Bogus("system")
    system.tada.trigger = trigger

    driver = system.add_driver(AbstractTimeDriver("driver", time_interval=[0, 1], dt=0.25))

    with patch("cosapp.core.signal.signal.inspect"):
        # Add bogus slot to `system_update_signal`
        update_callback = MagicMock()
        driver.system_update_signal.connect(Slot(update_callback))

        system.run_drivers()
        assert update_callback.call_count == expected


def test_AbstractTimeDriver_global_max():
    """Use signal `AbstractTimeDriver.system_update_signal`
    to compute the maximum value of a variable over time.
    """
    class Bogus(System):
        def setup(self):
            self.add_inward("x", 0.0)
            self.add_outward("x_max", 0.0)
    
        def init_mode(self):
            self.x_max = -np.inf

        def update_x_max(self):
            self.x_max = max(self.x, self.x_max)

    system = Bogus("system")

    driver = system.add_driver(AbstractTimeDriver("driver", time_interval=[0, 2], dt=0.1))

    driver.set_scenario(values={"x": "sin(t)"})

    driver.system_update_signal.connect(system.update_x_max)

    system.x_max = np.inf
    system.run_drivers()
    
    assert system.x == pytest.approx(np.sin(2))
    assert system.x_max == pytest.approx(1, abs=1e-3)
