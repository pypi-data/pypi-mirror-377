"""Logging functions"""

import logging

from logger_color.cformatter import DIAG_INFO, DIAG_WARNING
from logger_color.clogger import CLogger


# noinspection PyIncorrectDocstring
def start_logging(**kwargs):
    """Start logging with the specified parameters
    :param filename: Writes messages to this file. By default, logging only to the terminal
    :type filename: str

    :param mode: "w" - Writes to file (default)
                 "a" - Appends to file
    :type mode: str

    :param level: Logging level for the terminal: "DEBUG", "INFO" (default), "WARNING", "ERROR",
        "CRITICAL", "DIAG_INFO", "DIAG_WARNING"
    :type level: str

    :param level_file: Logging level for the file. By default, the same as `level` parameter
    :type level_file: str

    :param color: True  - Prints a colored message to the terminal (default)
                  False - Prints a monochrome message to the terminal

    :param debug: True  - Sets logging level to DEBUG (rewrites `level` parameter),
                          works the same as level="DEBUG"
                  False - Gets logging level from `level` parameter (default)
    :type debug: bool
    """
    CLogger(**kwargs).start()


def debug(*args, **kwargs) -> None:
    """Log a message with severity "DEBUG" """
    logging.debug(*args, **kwargs)


def diag_info(msg, *args, **kwargs) -> None:
    """Log diagnostic message with severity "INFO"
    :param msg: Logging message
    """
    # noinspection PyProtectedMember
    logging.root._log(DIAG_INFO, msg, args, **kwargs)


def diag_warning(msg, *args, **kwargs) -> None:
    """Log diagnostic message with severity "WARNING"
    :param msg: Logging message
    """
    # noinspection PyProtectedMember
    logging.root._log(DIAG_WARNING, msg, args, **kwargs)


def info(*args, **kwargs) -> None:
    """Log a message with severity "INFO" """
    logging.info(*args, **kwargs)


def warning(*args, **kwargs) -> None:
    """Log a message with severity "WARNING" """
    logging.warning(*args, **kwargs)


def error(*args, **kwargs) -> None:
    """Log a message with severity "ERROR" """
    logging.error(*args, **kwargs)


def critical(*args, **kwargs) -> None:
    """Log a message with severity "CRITICAL" """
    logging.critical(*args, **kwargs)
