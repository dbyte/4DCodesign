""" Utilities and customizing for Python's standard logging library.
Should be referenced everywhere instead of the pure Python 'logging' library.
"""

import logging
import sys
from typing import Final, Callable

from core import IS_RUNNING_AZURE_PIPELINE

LOGGING: Final = logging
""" Just an indirection to avoid additional imports of python's 'logging'
module in other modules. Use this at the top of a module to init a logger,
for example: logger = LOGGING.getLogger(__name__)

:meta hide-value:
"""

_is_configured: bool = False
""" Signals that logging is configured. Set to True after function _configure(...) successfully ran once.
"""

# Initialize a logger for this module itself and keep it private
__logger = LOGGING.getLogger(__name__)


class AzureLogFormatter(LOGGING.Formatter):
    """Custom Azure Pipeline logging Formatter.
    See also: https://docs.microsoft.com/en-us/azure/devops/pipelines/scripts/logging-commands?view=azure-devops
    """

    # These are used for the Formatter.
    DEBUG_PREFIX: Final[str] = '##[debug]'
    WARNING_PREFIX: Final[str] = '##[warning]'
    ERROR_PREFIX: Final[str] = '##[error]'

    def __init__(self, fmt: str, datefmt: str | None):
        super().__init__()

        self.fmt = fmt
        self.datefmt = datefmt  # Note: is the same for all levels

        self.FORMATS = {
            LOGGING.DEBUG: self.fmt,
            LOGGING.INFO: self.fmt,
            LOGGING.WARNING: self.WARNING_PREFIX + self.fmt,
            LOGGING.ERROR: self.ERROR_PREFIX + self.fmt,
            LOGGING.CRITICAL: self.ERROR_PREFIX + self.fmt
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = LOGGING.Formatter(fmt=log_fmt, datefmt=self.datefmt)
        return formatter.format(record)

    @staticmethod
    def check_emit(emitter: Callable):
        """ Decorator which checks if a dedicated Azure log command
        should be emitted and emits it if true. """

        def inner(*args, **kwargs):
            if IS_RUNNING_AZURE_PIPELINE: emitter(*args, **kwargs)

        return inner

    @staticmethod
    @check_emit
    def group_start(name: str):
        """ Marks the beginning of a log-output group """
        print(f'##[group]{name}')

    @staticmethod
    @check_emit
    def group_end():
        """ Marks the end of a log-output group """
        print('##[endgroup]')

    @staticmethod
    @check_emit
    def section_start(name: str):
        """ Marks the start of a section """
        print(f'##[section]{name}')


# -------------------------------------------------------------------------------------------------
#   Configuration
# -------------------------------------------------------------------------------------------------


def set_root_loglevel(name: str):
    """ Sets the root logger's log level filter by name. If the given name
    can't be resolved to an existing log level, log level falls back to a
    defined default level.

    :param name: Name of the log level defined in the python 'logging' module.
        Constraints: FATAL, ERROR, WARNING, INFO, DEBUG, NOTSET
    """
    default_level: int = LOGGING.INFO

    try:
        loglevel: int = LOGGING.getLevelName(name.upper())  # may raise
        _configure(loglevel)

    except Exception as exc:
        _configure(default_level)
        __logger.error(str(exc))
        __logger.warning('Unable to set log level by given log level name %s. Falling back to %s.',
                         name.upper(),
                         LOGGING.getLevelName(default_level))

    finally:
        # Give us debugging feedback which level is in use actually
        __logger.debug(
            'Log level set to %s',
            LOGGING.getLevelName(__logger.getEffectiveLevel()))


def _configure(level: int):
    """ Runs the main logging configuration.

    :param level: The root log level to be applied
    """
    global _is_configured

    # This inherited log filter sorts out messages which log levels are equal or
    # less than INFO. Applying it to a stdout handler prevents messages from being
    # logged twice when a separate handler for stderr is configured.
    class StdoutFilter(LOGGING.Filter):
        def filter(self, record):
            return record.levelno <= LOGGING.INFO

    # We want to apply all setting to the root logger
    root_logger = LOGGING.root
    root_logger.setLevel(level)

    # After(!) setting level, prevent adding same handlers on
    # multiple calls of this function
    if _is_configured: return

    # Always suppress logging for the 'requests' and 'urllib3' library lower than WARNING.
    # This is important for security reasons as the log may be persisted within the pipeline run.
    # LOGGING.getLogger('requests').setLevel(LOGGING.WARNING)
    # LOGGING.getLogger("urllib3").setLevel(LOGGING.WARNING)

    # Create a console stdout handler and set its minimum level
    console_stdout_handler = LOGGING.StreamHandler(sys.stdout)
    console_stdout_handler.setLevel(LOGGING.DEBUG)
    console_stdout_handler.addFilter(StdoutFilter())

    # Create a console stderr handler and set its minimum level
    console_stderr_handler = LOGGING.StreamHandler(sys.stderr)
    console_stderr_handler.setLevel(LOGGING.WARNING)

    # Add appropriate formatters to handlers defined above
    console_stdout_handler.setFormatter(_get_formatter(level))
    console_stderr_handler.setFormatter(_get_formatter(level))

    # Finally, add the handlers to the root logger
    root_logger.addHandler(console_stdout_handler)
    root_logger.addHandler(console_stderr_handler)

    _is_configured = True


def _get_formatter(level: int) -> LOGGING.Formatter:
    """ Chooses appropriate logging formatter for the given log level.

    :param level: The root log level for which to get the appropriate Formatter
    :return: The evaluated logging formatter
    """
    if IS_RUNNING_AZURE_PIPELINE:
        high_resolution_formatter = AzureLogFormatter(
            fmt='[%(asctime)s] %(levelname)-8s %(filename)s:%(lineno)s %(funcName)s :: %(message)s',
            datefmt=None)

        low_resolution_formatter = AzureLogFormatter(
            fmt='[%(asctime)s] %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

    else:
        high_resolution_formatter = LOGGING.Formatter(
            fmt='[%(asctime)s] %(levelname)-8s %(filename)s:%(lineno)s %(funcName)s :: %(message)s',
            datefmt=None)

        low_resolution_formatter = LOGGING.Formatter(
            fmt='[%(asctime)s] %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

    if level <= LOGGING.DEBUG or level >= LOGGING.WARNING:
        return high_resolution_formatter
    else:
        return low_resolution_formatter
