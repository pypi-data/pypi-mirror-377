"""Colored logging formatter"""

import re
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, NOTSET
from logging import Formatter, LogRecord
from typing import Dict, Union

DiStr = Dict[int, str]
DiFormatter = Dict[int, Formatter]

NO_COLOR = "\33[0m"
GRAY = "\33[90m"
BLUE = "\33[34m"
PURPLE = "\33[35m"
GREEN = "\33[1;32m"
RED = "\33[31m"
RED_BOLD = "\33[31;1m"
YELLOW = "\33[33m"

DIAG_INFO = 21
DIAG_WARNING = 31

COLORS = {
    DEBUG: GRAY,
    INFO: GREEN,
    WARNING: YELLOW,
    ERROR: RED,
    CRITICAL: RED_BOLD,

    NOTSET: NO_COLOR,
    DIAG_INFO: BLUE,
    DIAG_WARNING: PURPLE,
}
COLORS_ = {
    "DEBUG": GRAY,
    "INFO": GREEN,
    "WARNING": YELLOW,
    "ERROR": RED,
    "CRITICAL": RED_BOLD,

    "NOTSET": NO_COLOR,
    "DIAG_INFO": BLUE,
    "DIAG_WARNING": PURPLE,
}


class CFormatter(Formatter):
    """Colored logging formatter"""

    def __init__(self, fmt: str):
        super().__init__()
        self._colors: DiStr = COLORS.copy()
        self.formatters: DiFormatter = self._init_formatters(fmt=fmt)

    # ============================= init =============================

    def _init_formatters(self, fmt: str) -> DiFormatter:
        """Init colored logging formatters by logging levels"""
        date_fmt = "%Y-%m-%d %H:%M:%S"
        formatters: DiFormatter = {}  # return
        for level, color in self._colors.items():
            # no logging level
            if level == NOTSET:
                formatters[NOTSET] = Formatter(fmt=fmt, datefmt=date_fmt)
                continue
            # logging level in [DEBUG, ..., CRITICAL]. Change color
            fmt_ = fmt
            for fld in ["levelname", "levelno"]:
                if fld in fmt_:
                    regex = f"(%\\({fld}\\).*?s)"
                    fmt_ = re.sub(regex, f"{color}\\1{NO_COLOR}", fmt_)
            formatter = Formatter(fmt=fmt_, datefmt=date_fmt)
            formatters[level] = formatter
        return formatters

    # =========================== methods ============================

    def format(self, record: LogRecord) -> str:
        """Change color of logging record"""
        orig_msg: str = record.msg
        orig_args = record.args
        self._update_record(record)
        formatter: Formatter = self._get_formatter(level=record.levelno)
        msg: str = formatter.format(record)
        record.msg = orig_msg
        record.args = orig_args
        return msg

    # =========================== helpers ============================

    def _get_formatter(self, level: int) -> Formatter:
        """Returns colored formatter by logging level"""
        formatter = self.formatters.get(level) or self.formatters[NOTSET]
        return formatter

    @staticmethod
    def _update_record(record: LogRecord) -> None:
        """Updates data in LogRecord. Change message color.

        if record.levelno == 21, then record.levelname = DIAG_I
        if record.levelno == 31, then record.levelname = DIAG_W
        """
        if record.levelno not in [DIAG_INFO, DIAG_WARNING]:
            return
        # record.msg = f"{BLUE}{record.msg}{NO_COLOR}"

        if record.levelno == DIAG_INFO:
            record.levelname = "DIAG_I"
        elif record.levelno == DIAG_WARNING:
            record.levelname = "DIAG_W"


UFormatter = Union[CFormatter, Formatter]
