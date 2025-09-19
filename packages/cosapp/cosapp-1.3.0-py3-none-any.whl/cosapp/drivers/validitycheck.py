import logging

from cosapp.drivers.optionaldriver import OptionalDriver
from cosapp.utils.validate import validate

logger = logging.getLogger(__name__)


# TODO
# [ ] Quid for vector variables
class ValidityCheck(OptionalDriver):
    """
    When executed, this driver reports in the log the validity status for all variables of the
    driver `System` owner (and its children).

    Parameters
    ----------
    name : str
        Name of the driver
    owner : System
        :py:class:`~cosapp.systems.system.System` to which this driver belong
    **kwargs : Any
        Keyword arguments will be used to set driver options
    """
    
    __slots__ = tuple()

    def compute(self) -> None:
        """Report in the log the validity status for all variables
        recursively collected in owner `System` and its children.
        """
        warnings, errors = validate(self.owner)

        def message(log_dict):
            return "\n" + "\n\t".join(f"{key}{msg}" for key, msg in log_dict.items())

        if warnings:
            logger.warning(message(warnings))

        if errors:
            logger.error(message(errors))
