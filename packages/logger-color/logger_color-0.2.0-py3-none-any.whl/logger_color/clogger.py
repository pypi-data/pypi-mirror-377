"""Color Logger"""

import logging
import os
import sys
from logging import DEBUG, INFO
from logging import Formatter

from logger_color.cformatter import CFormatter, UFormatter

FORMAT_INFO = "%(asctime)s %(levelname)-8s %(message)s"
FORMAT_DEBUG = "%(asctime)s.%(msecs)03d %(levelname)-8s %(module)s.%(funcName)s: %(message)s"


class CLogger:
    """Color Logger"""

    def __init__(self, **kwargs):
        """Color Logger
        :param filename: Writes messages to this file. By default, logging only to the terminal
        :type filename: str

        :param format_info: INFO logging format for terminal. Default: time, level, message.
        :type format_info: str

        :param format_debug: DEBUG logging format for terminal.
            Default: time, level, module, function, message.
        :type format_debug: str

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
        self.filename: str = str(kwargs.get("filename") or "")
        self.format_info: str = str(kwargs.get("format_info") or FORMAT_INFO)
        self.format_debug: str = str(kwargs.get("format_debug") or FORMAT_DEBUG)
        self.level: int = self._init_level(**kwargs)
        self.level_file: int = self._init_level_file(**kwargs)
        self.mode: str = self._init_mode(**kwargs)
        self.color: bool = self._init_color(**kwargs)

    # ============================= init =============================

    @staticmethod
    def _init_color(**kwargs) -> bool:
        """Init logging color"""
        color = kwargs.get("color")
        if color is None:
            color = True
        return bool(color)

    def _init_formatter(
            self,
            level: int,
            color: bool = False,
            format_info: str = FORMAT_INFO,
            format_debug: str = FORMAT_DEBUG,
    ) -> UFormatter:
        """Init logging formatter"""
        if level <= DEBUG:
            format_ = format_debug
        else:
            format_ = format_info
        if color and self.color:
            formatter: UFormatter = CFormatter(fmt=format_)
        else:
            formatter = Formatter(fmt=format_, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter

    @staticmethod
    def _init_level(**kwargs) -> int:
        """Init logging level, by default INFO"""
        debug = kwargs.get("debug")
        if debug is None:
            debug = kwargs.get("DEBUG")
        if bool(debug):
            return DEBUG
        level = kwargs.get("level")
        if level is None:
            return INFO
        if isinstance(level, int):
            return level
        if isinstance(level, str):
            level = level.upper()
        # noinspection PyUnresolvedReferences,PyProtectedMember
        level_ = logging._nameToLevel.get(level)
        if isinstance(level_, int):
            return level_
        return INFO

    def _init_level_file(self, **kwargs) -> int:
        """Init logging level for file, by default the same as level for the terminal"""
        level = kwargs.get("level_file")
        if level is None:
            return self.level
        if isinstance(level, int):
            return level
        if isinstance(level, str):
            level = level.upper()
        # noinspection PyUnresolvedReferences,PyProtectedMember
        level_ = logging._nameToLevel.get(level)
        if isinstance(level_, int):
            return level_
        return self.level

    @staticmethod
    def _init_mode(**kwargs) -> str:
        """Init logging mode"""
        mode = kwargs.get("mode")
        if mode is None:
            mode = "w"
        expected = ["a", "w"]
        if mode not in expected:
            raise ValueError(f"{mode=}, {expected=}")
        return mode

    # =========================== methods ============================

    def start(self) -> None:
        """Starts logging"""
        logger = logging.getLogger()
        min_level = min(self.level, self.level_file)
        logger.setLevel(level=min_level)
        self._remove_handlers()
        self._add_stream_handler()
        self._add_file_handler()

    # =========================== helpers ============================

    @staticmethod
    def _remove_handlers() -> None:
        """Removes all logging handlers"""
        logger = logging.getLogger()
        while logger.handlers:
            handler = logger.handlers[0]
            logger.removeHandler(handler)

    @staticmethod
    def _check_dir_write(path: str) -> None:
        """Check directory write permission"""
        if not os.path.exists(path):
            raise OSError(f"Directory does not exist: {path}")
        if not os.access(path, os.W_OK):
            raise OSError(f"No write permission for directory: {path}")

    def _add_stream_handler(self) -> None:
        """Adds StreamHandler to Logger"""
        logger = logging.getLogger()
        formatter = self._init_formatter(
            level=self.level,
            color=self.color,
            format_info=self.format_info,
            format_debug=self.format_debug,
        )
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(self.level)
        handler.setFormatter(fmt=formatter)
        logger.addHandler(handler)

    def _add_file_handler(self) -> None:
        """Add FileHandler to Logger, logging WARNING if it does not have write-permissions"""
        if not self.filename:
            return
        logger = logging.getLogger()
        try:
            handler = logging.FileHandler(filename=self.filename, mode=self.mode)
            formatter = self._init_formatter(level=self.level_file)
            handler.setFormatter(fmt=formatter)
            handler.setLevel(self.level_file)
            logger.addHandler(handler)
        except OSError as ex:
            logging.warning(str(ex))
