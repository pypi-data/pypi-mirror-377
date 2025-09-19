import abc
import logging
import numpy
import pandas
import copy
from io import StringIO
from numbers import Number
from typing import Union, Optional, Any
from collections.abc import Collection

from cosapp.core.time import UniversalClock
from cosapp.core.signal import Signal
from cosapp.drivers.driver import Driver, System, AnyRecorder
from cosapp.drivers.time.utils import (
    TimeUnknown,
    TimeUnknownDict,
    TimeVarManager,
    TimeStepManager,
    TwoPointCubicPolynomial,
)
from cosapp.drivers.time.scenario import Scenario
from cosapp.multimode.discreteStepper import DiscreteStepper, EventRecord
from cosapp.multimode.event import Event
from cosapp.recorders import DataFrameRecorder
from cosapp.utils.helpers import check_arg
from cosapp.utils.logging import LogFormat, LogLevel, HandlerWithContextFilters

logger = logging.getLogger(__name__)


class AbstractTimeDriver(Driver):
    """
    Generic implementation of a time driver with managed time step.
    Specialization of derived classes is achieved by the implementation of abstract method `_update_transients`
    """

    __slots__ = (
        '__time_interval', '__clock', '__recordPeriod',
        '_transients', '_rates', '_dt_manager', '_var_manager',
        '__scenario', 'record_dt', '__recorded_dt', '__stepper',
        '__event_data', '__recorded_events', '_tr_data',
        '_transitioning', '_system_update_signal',
    )

    def __init__(self,
        name = "Time driver",
        owner: Optional[System] = None,
        time_interval: Optional[tuple[float, float]] = None,
        dt: Optional[float] = None,
        record_dt: bool = False,
        **options,
    ):
        """Initialization of the driver

        Parameters
        ----------
        name : str, optional
            Driver's name; default: "Explicit time driver"
        owner : System, optional
            :py:class:`~cosapp.systems.system.System` to which this driver belongs; default None
        time_interval : tuple[float, float]
            Time interval [t_begin, t_end], with t_end > t_begin; defaut None
        dt : float
            Time step; defaut None. If None, will be tentatively determined
            from system transient variables.
        record_dt : bool
            If True, driver will store actual time steps used in simulation; default False.
            This option is only useful for post-run analysis, when `dt` is unspecified.
        **options : dict[str, Any]
            Optional keywords arguments for generic `Driver` objects
        """
        dt_growth_rate = options.pop('max_dt_growth_rate', 2.0)

        super().__init__(name, owner, **options)

        self.__time_interval = None
        self.__recorded_dt = numpy.array([])
        self.__clock = UniversalClock()
        self.__recordPeriod = None
        self._transitioning = False
        self._dt_manager = TimeStepManager(max_growth_rate=dt_growth_rate)
        self._var_manager: TimeVarManager = None
        self._transients = TimeUnknownDict()
        self._rates = dict()
        self._tr_data = dict()
        self.dt = dt
        self.time_interval = time_interval
        self.record_dt = record_dt
        self.__scenario = Scenario("empty", self)
        self.__stepper: DiscreteStepper = None
        self.__event_data: pandas.DataFrame = None
        self.__recorded_events: list[EventRecord] = []
        self._system_update_signal = Signal(name="AbstracTimeDriver.system_update_signal")

    @property
    def dt(self) -> Union[None, Number]:
        """Nominal time step (None if unspecified)"""
        return self._dt_manager.nominal_dt

    @dt.setter
    def dt(self, value: Number) -> None:
        self._dt_manager.nominal_dt = value

    @property
    def time(self) -> Number:
        """Current simulation time"""
        return self.__clock.time

    @property
    def time_interval(self) -> tuple[Number, Number]:
        """Time interval covered by driver"""
        return self.__time_interval

    @time_interval.setter
    def time_interval(self, interval: tuple[Number, Number]) -> None:
        if interval is not None:
            check_arg(interval, 'time_interval', (tuple, list), lambda it: len(it) == 2)
            interval = tuple(interval)
            start, end = interval
            check_arg(start, 'start time', Number, value_ok = lambda t: t >= 0)
            check_arg(end, 'end time', Number, value_ok = lambda t: t >= start and numpy.isfinite(t))
        self.__time_interval = interval

    @property
    def event_data(self) -> pandas.DataFrame:
        """pandas.DataFrame: DataFrame detailing all event cascades occurring during simulation"""
        return self.__event_data

    @property
    def recorded_events(self) -> list[EventRecord]:
        """list[EventRecord]: list of recorded event cascades"""
        return self.__recorded_events

    # @property
    # def start_time(self):
    #     return self.__time_interval[0]

    # @property
    # def end_time(self):
    #     return self.__time_interval[1]

    def set_scenario(self,
        name = "scenario",
        init: dict[str, Any] = dict(),
        values: dict[str, Any] = dict(),
        stop: Optional[Union[str, Event]] = None,
    ) -> None:
        """
        Define a simulation scenario, from initial and boundary conditions.

        Parameters
        ----------
        init : dict
            Dictionary of initial conditions, of the kind {variable: value}
        values : dict
            Dictionary of boundary conditions, of the kind {variable: value}
            Explicit time dependency may be specified, as {variable: 'cos(omega * t)'}, for example
        name : str
            Name of the scenario (by default, 'scenario')
        """
        self.__scenario = scenario = Scenario.make(name, self, init, values)
        if stop is not None:
            scenario.stop.trigger = stop

    @property
    def scenario(self) -> Scenario:
        """Scenario: the simulation scenario, defining initial and boundary conditions"""
        return self.__scenario

    def add_recorder(self, recorder: AnyRecorder, period: Optional[Number] = None) -> AnyRecorder:
        """Add an internal recorder storing the time evolution of values of interest.

        Parameters
        ----------
        - recorder [BaseRecorder]:
            The recorder to be added.
        - period [Number, optional]:
            Recording period. If `None` (default), data are recorded at all time steps.
        """
        if 'time' not in recorder:
            cls = type(recorder)
            recorder = cls.extend(recorder, includes='time')
        super().add_recorder(recorder)
        if period is not None:
            self.recording_period = period
        return self.recorder

    def setup_run(self) -> None:
        """Setup the driver once before starting the simulation and before
        calling the systems `setup_run`.
        """
        super().setup_run()

        if self.__time_interval is None:
            raise ValueError("Time interval was not specified")

        self.__stepper = DiscreteStepper(self)
        self._var_manager = TimeVarManager(self.owner)
        self.__reset_time_variables()
        self.__reset_time()

    def _reset_time_problem(self) -> None:
        self.__stepper.update_sysview()
        self._var_manager.update_transients()
        self.__reset_time_variables()
        self.__update_transient_dict()

    def __reset_time_variables(self) -> None:
        manager = self._var_manager
        self._dt_manager.transients = manager.transients
        self._transients = manager.transients
        self._rates = manager.rates
        logger.debug(f"Transient variables: {self._transients!r}")
        logger.debug(f"Rate variables: {self._rates!r}")

    def run_once(self) -> None:
        """Run time driver once, assuming driver has already been initialized.
        """
        with self.log_context(" - run_once"):
            if self.is_active():
                self._precompute()

                # Sub-drivers are executed at each time step in `compute`,
                # so the child loop before `self.compute()` is omitted.
                logger.debug(f"Call {self.name}.compute")
                self._compute_calls += 1
                self.compute()

                self._postcompute()
                self.computed.emit()

            else:
                logger.debug(f"Skip {self.name} execution - Inactive")

    def compute(self) -> None:
        """Simulate the time-evolution of owner System over a prescribed time interval"""
        self._initialize()

        t0, t_end = self.__time_interval
        dt_manager = self._dt_manager
        dt = self.dt or dt_manager.time_step()
        record_all = False
        t_record = numpy.inf
        recorder = self._recorder

        if recorder is None:
            must_record = lambda t, t_record: False
            record_data = lambda *args, **kwargs: None
            event_rec_options = dict(includes='time')

        else:
            if self.recording_period is None:
                if self.dt is None:
                    logger.warning(
                        "Unspecified recording period and time step"
                        "; all time steps will be recorded"
                    )
                record_all = True
            eps = min(1e-8, dt / 100)
            must_record = lambda t, t_record: abs(t - t_record) < eps
            def record_data(stamp=None):
                if stamp is None:
                    stamp = f"t={float(self.time):.14}"
                recorder.record_state(stamp, self.status, self.error_code)
            t_record = numpy.inf if record_all else t0
            event_rec_options = dict(
                (attr, getattr(recorder,attr))
                for attr in (
                    "includes",
                    "excludes",
                    "section",
                    "precision",
                    "hold",
                )
            )
            event_rec_options["numerical_only"] = recorder._numerical_only
            event_rec_options["raw_output"] = recorder._raw_output #TODO: Expose both to the API?

        event_rec = DataFrameRecorder(**event_rec_options)
        event_rec.watched_object = self.owner
        def record_event(stamp=None):
            if stamp is None:
                stamp = f"t={float(self.time):.14}"
            event_rec.record_state(stamp, self.status, self.error_code)

        recorded_dt = []
        if self.record_dt:
            record_dt = lambda dt: recorded_dt.append(dt)
        else:
            record_dt = lambda dt: None
        
        t = t0
        n_record = 0
        prev_dt = None
        self._set_time(t0)
        self._system_update_signal.emit()

        stepper = self.__stepper
        self.__recorded_events = []
        stepper.initialize()

        self._tr_data = {}
        self.__update_transient_dict()

        def update_system(t, dt) -> float:
            """Continuously update owner system over one time step,
            and check for any event occurrence afterwards.
            """
            self._transitioning = False
            self._update_transients(dt)
            self._set_time(t + dt)
            # Store transient values and derivatives @ t + dt
            self.__update_transient_data()
            
            if stepper.event_detected():
                stepper.set_data(
                    interval = (t, t + dt),
                    interpol = {
                        name: TwoPointCubicPolynomial(
                            xs = (t, t + dt),
                            ys = data[0::2],  # values
                            dy = data[1::2],  # derivatives
                        )
                        for name, data in self._tr_data.items()
                    }
                )
                self._transitioning = True
                record = stepper.first_discrete_step()  # first step: root finding + non-primitive events
                n_primitives = len(record.events)
                record_data()
                record_event()
                stepper.reevaluate_primitive_events()
                self._system_update_signal.emit()  # signal emission before transition
                self._pre_transition()
                self.transition(record.time, record.events)
                record_event(", ".join(event.contextual_name for event in record.events))
                event_cascade = set(stepper.present_events())
                stepper.tick()
                stepper.update_events()

                while stepper.event_detected():  # following steps: event cascade
                    new_events = set(stepper.discrete_step()) - event_cascade
                    self.transition(record.time, new_events)
                    event_cascade.update(new_events)
                    stamp = ", ".join(event.contextual_name for event in new_events)
                    record_event(stamp)
                    stepper.tick()
                    stepper.update_events()

                record.events.extend(event_cascade.difference(record.events))
                self.__recorded_events.append(record)
                stamp = ", ".join(event.contextual_name for event in record.events[:n_primitives])
                record_data(stamp)
                must_stop = any(event.final for event in event_cascade)
                next_t = record.time
                dt = next_t - t

                # Reevaluate transient values and derivatives @ record.time,
                # in case one or more primitive events were cancelled
                self._post_transition(dt)
                self.__update_transient_data()

            else:
                next_t = t + dt
                stepper.reevaluate_primitive_events()
                stepper.shift()
                must_stop = False

            record_dt(dt)
            self.__shift_transient_data()

            return next_t, must_stop

        stopped = False

        while not stopped:  # time loop
            if record_all:
                record_data()
            elif must_record(t, t_record):
                record_data()
                n_record += 1
                t_record = t0 + n_record * self.recording_period
            dt = dt_manager.time_step(prev_dt)
            next_t = t + dt
            # Update previous dt, unless current dt is artificially
            # limited by recording timestamp `t_record`
            t_record = min(t_end, t_record)
            if next_t > t_record:
                next_t = t_record
                remaining = t_end - t
                if remaining < 1e-3 * dt:
                    break
                dt = next_t - t
            else:
                prev_dt = dt
            t, stopped = update_system(t, dt)
            self._system_update_signal.emit()

        self.__recorded_dt = numpy.asarray(recorded_dt)
        self.__event_data = event_rec.export_data()
        try:
            last_record = self.__recorded_events[-1]
        except IndexError:
            pass
        else:
            if self.__scenario.stop in last_record.events:
                logger.info(
                    f"Stop criterion met at t = {last_record.time}"
                )

    @property
    def system_update_signal(self):
        """Signal emitted after the owner system is updated, at each time step"""
        return self._system_update_signal

    def transition(self, time: float, events: Collection[Event]=()) -> None:
        """Execute owner system transition and reinitialize sub-drivers"""
        owner = self.owner
        modified_structure = owner.tree_transition()
        if modified_structure:
            logger.info(
                f"System structure changed during transition @t={time}"
                f"; reopen loops and reinitialize sub-drivers (if any)"
            )
            owner.close_loops()
            owner.open_loops()
            # Reset time problem & Reinitialize sub-drivers
            self._reset_time_problem()
            for driver in self.children.values():
                driver.call_setup_run()
        for transient in self._transients.values():
            transient.touch()
        for event in events:
            event.context.touch()
        self._set_time(time)
        self._synch_transients()

    def _pre_transition(self) -> None:
        """Hook function for pre-transition actions"""

    def _post_transition(self, dt: float) -> None:
        """Hook function for post-transition actions"""

    def _set_time(self, t: Number) -> None:
        """Set clock time at `t`."""
        dt = t - self.time
        self.__clock.time = t
        self.__scenario.update_values()
        if self._transitioning:
            self._pre_update_system()
        self._update_system()
        self._update_rates(dt)

    def _pre_update_system(self) -> None:
        """Hook function called before `_update_system` during transitions"""
        pass

    def __reset_time(self) -> None:
        """Reset clock time to driver start time"""
        time = self.__time_interval[0]
        logger.debug(f"Reset time to {time}")
        self.__clock.reset(time)

    def _initialize(self):
        self.__reset_time()
        self.__scenario.apply_init_values()
        self.__scenario.update_values()
        self.owner.tree_init_mode()
        self._synch_transients()
        self._transitioning = False
        logger.debug("Reset rates")
        for rate in self._rates.values():
            rate.reset()

    def _synch_transients(self):
        """Re-synch stacked unknowns with root variables"""
        for transient in self._transients.values():
            transient.reset()

    def _update_system(self) -> None:
        """Update owner system by executing sub-drivers, if any, or owner's subsystem drivers"""
        if self.children:
            for driver in self.children.values():
                logger.debug(f"Call {driver.name}.run_once()")
                driver.run_once()
        else:
            self.owner.run_children_drivers()

    def _update_rates(self, dt: Number) -> None:
        """Update rate-of-changes over time interval dt"""
        if dt == 0:
            return
        synch_needed = False
        for rate in self._rates.values():
            rate.update(dt)
            synch_needed = True
        if synch_needed:
            # Re-run dynamic system with updated (synchronized) rates
            # Equivalent to a single step fixed-point solver
            self._update_system()

    @abc.abstractmethod
    def _update_transients(self, dt: Number) -> None:
        """
        Time integration of transient variables over time step `dt`.
        Actual implementation depends on chosen numerical scheme.
        """
        pass

    @property
    def recording_period(self) -> Number:
        """float: Recording period of time driver's internal recorder"""
        return self.__recordPeriod

    @recording_period.setter
    def recording_period(self, value: Number):
        check_arg(value, 'recording_period', Number, lambda t: t > 0)
        interval = self.time_interval
        if interval is None:
            self.__recordPeriod = value
        else:
            self.__recordPeriod = min(value, interval[1] - interval[0])

    @property
    def recorded_dt(self) -> numpy.ndarray:
        """numpy.ndarray: list of time steps recorded during driver execution"""
        return self.__recorded_dt

    def log_debug_message(self, handler: HandlerWithContextFilters, record: logging.LogRecord, format=LogFormat.RAW) -> bool:
        """Callback method on the system to log more detailed information.
        
        This method will be called by the log handler when :py:meth:`~cosapp.utils.logging.LoggerContext.log_context`
        is active if the logging level is lower or equals to VERBOSE_LEVEL. It allows
        the object to send additional log message to help debugging a simulation.

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
        activate = getattr(record, "activate", None)
        emit_record = super().log_debug_message(handler, record, format)

        if message.endswith("call_setup_run") or message.endswith("call_clean_run"):
            emit_record = False

        elif activate == True:
            self.record_dt = True
            emit_record = False

        elif activate == False:
            self.record_dt = False
            emit_record = False
            container = StringIO()
            numpy.savetxt(container, self.recorded_dt, delimiter=",")
            dts = container.getvalue()
            
            message = f"Time steps:\n{dts}"
            handler.log(
                LogLevel.FULL_DEBUG,
                message,
                name=logger.name,
            )

        return emit_record

    @staticmethod
    def value_and_derivative(var: TimeUnknown) -> Union[tuple[float, float], tuple[numpy.ndarray, numpy.ndarray]]:
        return (
            copy.copy(var.value),
            copy.copy(var.d_dt),
        )

    def __update_transient_dict(self) -> None:
        """Update (in place) the collectin of transient data."""
        transient_data = self._tr_data
        owner_transients = self._var_manager.problem.transients
        value_and_derivative = self.value_and_derivative
        new_data = dict(
            (key, [*value_and_derivative(var), None, None])
            for key, var in owner_transients.items()
        )
        self._intersect_dict(transient_data, new_data)

    @staticmethod
    def _intersect_dict(old: dict, new: dict) -> None:
        old_keys = set(old.keys())
        new_keys = set(new.keys())
        for key in old_keys - new_keys:
            old.pop(key)
        for key in new_keys - old_keys:
            old[key] = new[key]

    def __update_transient_data(self) -> None:
        """Update transient data from current values."""
        transient_data = self._tr_data
        owner_transients = self._var_manager.problem.transients
        value_and_derivative = self.value_and_derivative
        for key, var in owner_transients.items():
            transient_data[key][2:4] = value_and_derivative(var)

    def __shift_transient_data(self) -> None:
        """Shift transient data from previous time step."""
        for data in self._tr_data.values():
            data[0:2] = data[2:4]

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
        _, slots = super().__getstate__()

        slots.pop("_system_update_signal")

        return None, slots
