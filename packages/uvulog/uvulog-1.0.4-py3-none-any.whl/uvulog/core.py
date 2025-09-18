# -*- coding: utf-8 -*-
"""
Author: Lupnis J H <lupnisj@gmail.com>
Last modified: 2025-09-17
"""

import datetime
from enum import Enum
from filelock import FileLock
import gc
import os
from pathlib import Path
import re
import sys
import threading
import traceback
from typing import Any, Dict, List, Union, Optional


# -------------------------
# Terminal styling helpers
# -------------------------


class Styles(object):
    """Constants and small helpers to build ANSI escape sequences for terminal styling.

    Each constant is an integer that represents an ANSI SGR parameter. The
    helper methods produce strings that can be embedded into terminal output.
    """

    CLEAR = 0
    BOLD = 1
    BOLD_RESET = 22
    FAINT = 2
    FAINT_RESET = 22
    ITALIC = 3
    ITALIC_RESET = 23
    UNDERLINE = 4
    UNDERLINE_RESET = 24
    BLINK = 5
    BLINK_RESET = 25
    REVERSE = 7
    REVERSE_RESET = 27
    INVISIBLE = 8
    INVISIBLE_RESET = 28
    STRIKE = 9
    STRIKE_RESET = 29
    DEFAULT = 39
    DEFAULT_BG = 49
    BLACK = 30
    BLACK_BG = 40
    RED = 31
    RED_BG = 41
    GREEN = 32
    GREEN_BG = 42
    YELLOW = 33
    YELLOW_BG = 43
    BLUE = 34
    BLUE_BG = 44
    MAGENTA = 35
    MAGENTA_BG = 45
    CYAN = 36
    CYAN_BG = 46
    WHITE = 37
    WHITE_BG = 47
    BRIGHT_BLACK = 90
    BRIGHT_BLACK_BG = 100
    BRIGHT_RED = 91
    BRIGHT_RED_BG = 101
    BRIGHT_GREEN = 92
    BRIGHT_GREEN_BG = 102
    BRIGHT_YELLOW = 93
    BRIGHT_YELLOW_BG = 103
    BRIGHT_BLUE = 94
    BRIGHT_BLUE_BG = 104
    BRIGHT_MAGENTA = 95
    BRIGHT_MAGENTA_BG = 105
    BRIGHT_CYAN = 96
    BRIGHT_CYAN_BG = 106
    BRIGHT_WHITE = 97
    BRIGHT_WHITE_BG = 107

    @staticmethod
    def ID_COLOR(id: int) -> str:
        """Return 256-color foreground SGR code for the given id."""
        return f"38;5;{id}"

    @staticmethod
    def ID_COLOR_BG(id: int) -> str:
        """Return 256-color background SGR code for the given id."""
        return f"48;5;{id}"

    @staticmethod
    def RGB_COLOR(r: int, g: int, b: int) -> str:
        """Return RGB foreground SGR code for the given r,g,b values."""
        return f"38;2;{r};{g};{b}"

    @staticmethod
    def RGB_COLOR_BG(r: int, g: int, b: int) -> str:
        """Return RGB background SGR code for the given r,g,b values."""
        return f"48;2;{r};{g};{b}"

    @staticmethod
    def make_color_prefix(code: Union[int, str]) -> str:
        """Wrap a single SGR code into an ANSI escape sequence.

        Parameters
        ----------
        code: int | str
            The SGR numeric code (or semicolon-delimited codes) to place inside
            the escape sequence.  For example 31 -> "\x1b[31m".

        Returns
        -------
        str
            The ANSI escape string.
        """
        return f"\x1b[{code}m"

    @staticmethod
    def make_colors_prefix(codes: List[Any] = []) -> str:
        """Combine multiple codes into a single prefix.

        Note: the default empty list here mirrors the original source but using
        a mutable default is generally discouraged. We keep it so behaviour is
        unchanged; callers can pass a list of codes (ints/strs).
        """
        return ''.join([Styles.make_color_prefix(code) for code in codes])


class Styled(object):
    """A small wrapper that tracks a plain and a styled representation of text.

    - `plain` contains the text without ANSI sequences (what you'd use for
      log files and tests)
    - `styled` contains ANSI sequences for colored terminal output

    The class supports concatenation and format-like substitution while
    attempting to preserve both representations.
    """

    def __init__(self, data: Any = "", *styles: Any):
        # store the plain representation
        self.plain_str: str = data.plain_str if isinstance(
            data, Styled) else str(data)

        # split on tokens like {foo} but keep the tokens in the result
        splited_str: List[str] = re.split(r'(\{\{*[\w\W]*?\}\*\})', str(
            data)) if False else re.split(r'(\{\{*[\w\W]*?\}*\})', str(data))

        # build the styled string by interleaving style prefix and tokens.
        # even indices are text to style, odd indices are placeholders/escaped tokens
        self.styled_str: str = Styles.make_color_prefix(Styles.CLEAR) + ''.join([
            (Styles.make_colors_prefix(styles) + s) if i % 2 == 0 else s
            for i, s in enumerate(splited_str)
        ]) + Styles.make_color_prefix(Styles.CLEAR)

    # concatenation helpers -------------------------------------------------
    def __add__(self, oval: Any) -> 'Styled':
        """Return a new Styled that is the concatenation of `self` and `oval`."""
        generated_style = Styled()
        if isinstance(oval, Styled):
            generated_style.plain_str = self.plain_str + oval.plain_str
            generated_style.styled_str = self.styled_str + oval.styled_str
        else:
            generated_style.plain_str = self.plain_str + str(oval)
            generated_style.styled_str = self.styled_str + str(oval)
        return generated_style

    def __radd__(self, oval: Any) -> 'Styled':
        """Return a new Styled where `oval` is prefixed to `self`."""
        generated_styled = Styled()
        if isinstance(oval, Styled):
            generated_styled.plain_str = oval.plain_str + self.plain_str
            generated_styled.styled_str = oval.styled_str + self.styled_str
        else:
            generated_styled.plain_str = str(oval) + self.plain_str
            generated_styled.styled_str = str(oval) + self.styled_str
        return generated_styled

    def __iadd__(self, oval: Any) -> 'Styled':
        """In-place concatenation (augmented assignment)."""
        if isinstance(oval, Styled):
            self.plain_str += oval.plain_str
            self.styled_str += oval.styled_str
        else:
            self.plain_str += str(oval)
            self.styled_str += str(oval)
        return self

    @property
    def plain(self) -> str:
        return self.plain_str

    @property
    def styled(self) -> str:
        return self.styled_str

    def __str__(self) -> str:
        return self.styled_str

    def format(self, *args: Any, **kwargs: Any) -> 'Styled':
        """Format both the plain and styled representations using the provided
        arguments. If an argument is a Styled object, its corresponding
        representation (plain/styled) is used.

        Returns
        -------
        Styled
            A new Styled instance with formatted content.
        """
        generated_styled = Styled()
        args_plain = [arg.plain if isinstance(
            arg, Styled) else str(arg) for arg in args]
        kwargs_plain = {k: v.plain if isinstance(
            v, Styled) else str(v) for k, v in kwargs.items()}
        args_styled = [arg.styled if isinstance(
            arg, Styled) else str(arg) for arg in args]
        kwargs_styled = {k: v.styled if isinstance(
            v, Styled) else str(v) for k, v in kwargs.items()}
        generated_styled.plain_str = self.plain_str.format(
            *args_plain, **kwargs_plain)
        generated_styled.styled_str = self.styled_str.format(
            *args_styled, **kwargs_styled)
        return generated_styled


# -------------------------
# Log level constants
# -------------------------


class Levels(Enum):
    """Simple numeric severity levels used throughout the logger."""
    TRACE = -1
    DEBUG = 0
    INFO = 1
    NOTICE = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


# -------------------------
# Aliases
# -------------------------


S_ = Style = BlockStyles = BlockStyle = Styles
B_ = Block = Box = StyledBlock = Styled
L_ = Level = LogLevel = LogLevels = Levels


# -------------------------
# Render block primitives
# -------------------------


class BaseRenderBlock(object):
    """A render block encapsulates a small piece of the log line.

    It carries a `render_block` (a Styled object) and exposes `render` which
    returns a Styled instance. Subclasses override `render` to add dynamic
    behaviour (time, process id, source file, etc.).
    """

    def __init__(self, *blocks: Any, begin: Any = '', sep: Any = '', end: Any = ' '):
        # allow passing tuples/lists which represent a (value, style...) pair
        if isinstance(begin, tuple) or isinstance(begin, list):
            begin = Styled(*begin)
        if isinstance(sep, tuple) or isinstance(sep, list):
            sep = Styled(*sep)
        if isinstance(end, tuple) or isinstance(end, list):
            end = Styled(*end)

        self.render_block: Styled = begin
        for block in blocks:
            if isinstance(block, tuple) or isinstance(block, list):
                block = Styled(*block)
            self.render_block += block + sep
        self.render_block += end
        # ensure render_block is a Styled instance
        self.render_block = Styled(self.render_block)

    def reset(self, *args: Any, **kwargs: Any) -> None:
        """Placeholder hook for blocks which keep state and may want to reset
        themselves. Subclasses override when necessary."""
        ...

    def render(self, level: Levels = Levels.INFO, fmt: Styled = Styled(), *args: Any, **kwargs: Any) -> Styled:
        """Return the pre-built `render_block` formatted with args/kwargs.

        Subclasses will typically call this implementation after computing the
        dynamic replacement tokens they want to inject.
        """
        return self.render_block.format(*args, **kwargs)

    @property
    def plain(self) -> str:
        return self.render_block.plain

    @property
    def styled(self) -> str:
        return self.render_block.styled

    @property
    def block(self) -> Styled:
        return self.render_block

    def __str__(self) -> str:
        return str(self.render_block)


class TimeRenderBlock(BaseRenderBlock):
    """Render the current local time using a configured format (strftime).

    The default format used by DEFAULT_BLOCKS_CONF_DICT is "%Y-%m-%d %H:%M:%S".
    """

    def __init__(self, *blocks: Any, begin: Any = '', sep: Any = '', end: Any = ' ', time_format: str = '%Y-%m-%d %H:%M:%S'):
        super(TimeRenderBlock, self).__init__(
            *blocks, begin=begin, sep=sep, end=end)
        self.time_format: str = time_format

    def render(self, level: Levels = Levels.INFO, fmt: Styled = Styled(), *args: Any, **kwargs: Any) -> Styled:
        return super(TimeRenderBlock, self).render(level, fmt, datetime.datetime.now().strftime(self.time_format))


class LevelRenderBlock(BaseRenderBlock):
    """Render different representations depending on the severity `level`."""

    def __init__(self, *blocks: Any, begin: Any = '', sep: Any = '', end: Any = ' ', levels: Dict[int, Any] = {}) -> None:
        super(LevelRenderBlock, self).__init__(
            *blocks, begin=begin, sep=sep, end=end)
        # store a mapping level -> BaseRenderBlock for quick lookup
        self.levels: Dict[int, BaseRenderBlock] = {level: BaseRenderBlock(
            *blocks, begin='', sep='', end='') for level, blocks in levels.items()}

    def render(self, level: Levels = Levels.INFO, fmt: Styled = Styled(), *args: Any, **kwargs: Any) -> Styled:
        # pick the block for the given level (fallback to the first available)
        chosen = self.levels.get(level, list(self.levels.values())[0])
        return super(LevelRenderBlock, self).render(level, fmt, chosen.block, *args, **kwargs)


class ProcessRenderBlock(BaseRenderBlock):
    """Render the current process id."""

    def render(self, level: Levels = Levels.INFO, fmt: Styled = Styled(), *args: Any, **kwargs: Any) -> Styled:
        return super(ProcessRenderBlock, self).render(level, fmt, os.getpid())


class CounterRenderBlock(BaseRenderBlock):
    """A simple incrementing counter block. Useful to show line numbers or
    event counts inside a single process.
    """

    def __init__(self, *blocks: Any, begin: Any = '', sep: Any = '', end: Any = ' ', init: int = 0, mod: Optional[int] = None) -> None:
        super(CounterRenderBlock, self).__init__(
            *blocks, begin=begin, sep=sep, end=end)
        self.init: int = init
        self.mod: Optional[int] = mod
        self.curr: int = init

    def reset(self, *args: Any, **kwargs: Any) -> None:
        self.curr = self.init

    def render(self, level: Levels = Levels.INFO, fmt: Styled = Styled(), *args: Any, **kwargs: Any) -> Styled:
        ret_val: Styled = super(CounterRenderBlock, self).render(
            level, fmt, self.curr)
        self.curr = self.curr + 1
        if self.mod is not None and self.curr >= self.mod and self.mod > 0:
            self.reset()
        return ret_val


class SourceFileRenderBlock(BaseRenderBlock):
    """Render the calling source file path (relative). Uses traceback to find
    the stack frame. The exact stack depth (-5) mirrors the original source's
    heuristic and may be adjusted if integration context changes."""

    def render(self, level: Levels = Levels.INFO, fmt: Styled = Styled(), *args: Any, **kwargs: Any) -> Styled:
        file_name, _, _, _ = traceback.extract_stack()[-6:][0]
        return super(SourceFileRenderBlock, self).render(level, fmt, file_name)


class SourceLineRenderBlock(BaseRenderBlock):
    """Render the source line number of the call site."""

    def render(self, level: Levels = Levels.INFO, fmt: Styled = Styled(), *args: Any, **kwargs: Any) -> Styled:
        _, line_number, _, _ = traceback.extract_stack()[-6:][0]
        return super(SourceLineRenderBlock, self).render(level, fmt, line_number)


class MainRenderBlock(BaseRenderBlock):
    """Main message block. Allows per-level formatting of the main message."""

    def __init__(self, *blocks: Any, begin: Any = '', sep: Any = '', end: Any = '', levels: Dict[int, Any] = {}) -> None:
        super(MainRenderBlock, self).__init__(
            *blocks, begin=begin, sep=sep, end=end)
        self.levels: Dict[int, BaseRenderBlock] = {level: BaseRenderBlock(
            *blocks, begin=begin, sep=sep, end=end) for level, blocks in levels.items()}

    def render(self, level: Levels = Levels.INFO, fmt: Styled = Styled(), *args: Any, **kwargs: Any) -> Styled:
        chosen = self.levels.get(level, list(self.levels.values())[0])
        # chosen.block.format(fmt.format(*args, **kwargs)) -> Styled
        return super(MainRenderBlock, self).render(level, fmt, chosen.block.format(fmt.format(*args, **kwargs)))


# -------------------------
# Default configuration
# -------------------------

BLOCKS_MODULE_REF_DICT: Dict[str, Any] = {
    "date": TimeRenderBlock,
    "time": TimeRenderBlock,
    "name": BaseRenderBlock,
    "level": LevelRenderBlock,
    "process": ProcessRenderBlock,
    "counter": CounterRenderBlock,
    "source_file": SourceFileRenderBlock,
    "source_line": SourceLineRenderBlock,
    "main": MainRenderBlock
}

DEFAULT_BLOCKS_CONF_DICT: Dict[str, Any] = {
    "time": {  # [YYYY-mm-dd HH:MM:SS]
        "args": [
            ["[", Styles.BRIGHT_BLACK],
            ["{}", Styles.BRIGHT_WHITE],
            ["]", Styles.BRIGHT_BLACK]
        ],
        "kwargs": {
            "time_format": "%Y-%m-%d %H:%M:%S"
        }
    },
    "date": {  # YYYY_mm_dd
        "args": [
            ["{}"],
        ],
        "kwargs": {
            "time_format": "%Y_%m_%d",
            "end": "",
            "sep": "",
            "begin": ""
        }
    },
    "name": {  # ::
        "args": [
            ["{logger_name}", Styles.GREEN]
        ],
    },
    "level": {  # T/D/I/N/W/E/C
        "args": [
            ["{}"]
        ],
        "kwargs": {
            "levels": {
                Levels.TRACE: [
                    [" T ", Styles.BRIGHT_BLACK_BG, Styles.WHITE]
                ],
                Levels.DEBUG: [
                    [" D ", Styles.BRIGHT_BLACK_BG, Styles.BRIGHT_WHITE]
                ],
                Levels.INFO: [
                    [" I ", Styles.WHITE]
                ],
                Levels.NOTICE: [
                    [" N ", Styles.BOLD, Styles.BRIGHT_BLACK_BG]
                ],
                Levels.WARNING: [
                    [" W ", Styles.BRIGHT_YELLOW_BG, Styles.BLACK]
                ],
                Levels.ERROR: [
                    [" E ", Styles.RED_BG, Styles.BLACK]
                ],
                Levels.CRITICAL: [
                    [" C ", Styles.MAGENTA_BG, Styles.BOLD,
                        Styles.BLINK, Styles.BLACK]
                ]
            }
        }
    },
    "process": {  # pid
        "args": [
            [" #{} ", Styles.BRIGHT_BLACK_BG, Styles.WHITE]
        ]
    },
    "counter": {  # line_of_log
        "args": [
            ["[{}]", Styles.BRIGHT_CYAN]
        ]
    },
    "source_file": {  # F@[path/to/FOO.py]
        "args": [
            ["F@["],
            ["{}", Styles.CYAN],
            ["]"]
        ]
    },
    "source_line": {  # L@[line_number]
        "args": [
            ["L@["],
            ["{}", Styles.CYAN],
            ["]"]
        ]
    },
    "main": {
        "args": [
            ["{}"]
        ],
        "kwargs": {
            "levels": {
                Levels.TRACE: [
                    ["{}", Styles.BRIGHT_BLACK]
                ],
                Levels.DEBUG: [
                    ["{}", Styles.BRIGHT_BLACK]
                ],
                Levels.INFO: [
                    ["{}", Styles.WHITE]
                ],
                Levels.NOTICE: [
                    ["{}", Styles.BOLD, Styles.BRIGHT_WHITE]
                ],
                Levels.WARNING: [
                    ["{}", Styles.BRIGHT_YELLOW]
                ],
                Levels.ERROR: [
                    ["{}", Styles.BRIGHT_RED]
                ],
                Levels.CRITICAL: [
                    ["{}", Styles.MAGENTA, Styles.BOLD]
                ]
            }
        }
    }
}

DEFAULT_TEXT_FMT: str = "{time}{level}{main}\n"

DEFAULT_LOG_SAVE_CONFIG: Dict[str, Any] = {
    "root_dir": "logs",
    "dir_name_fmt": "",
    "file_name_fmt": "logs.txt",
    "cache_lines": 0,
    "max_lines": 0,
    "max_size": 0
}

DEFAULT_LOGGER_CONFIG: Dict[str, Any] = {
    "logger_name": "uvu",
    "console": {
        "enabled": True,
        "colored": True,
        "level": Levels.INFO,
        "text_fmt": DEFAULT_TEXT_FMT,
        "blocks_config": DEFAULT_BLOCKS_CONF_DICT
    },
    "file": {
        "enabled": True,
        "colored": False,
        "save_config": DEFAULT_LOG_SAVE_CONFIG,
        "level": Levels.INFO,
        "text_fmt": DEFAULT_TEXT_FMT,
        "blocks_config": DEFAULT_BLOCKS_CONF_DICT
    }
}


# -------------------------
# Console (stdout/stderr) writer
# -------------------------


class ConsoleLogWritter(object):
    """A writer that outputs formatted logs to the console (stdout/stderr).
    """

    def __init__(self, logger_name: Optional[str] = "uvu", config: Optional[Dict[str, Any]] = DEFAULT_LOGGER_CONFIG["console"]) -> None:
        self.logger_name = logger_name
        self.enabled: bool = config.get("enabled", True)
        self.colored: bool = config.get("colored", False)
        self.level: Levels = config.get("level", Levels.TRACE)
        self.text_fmt: str = config.get("text_fmt", DEFAULT_TEXT_FMT)
        self.blocks_config: Dict[str, Any] = config.get(
            "blocks_config", DEFAULT_BLOCKS_CONF_DICT)
        # instantiate render blocks once for efficiency
        self.render_blocks: Dict[str, BaseRenderBlock] = {k: v(*self.blocks_config[k].get("args", []), **self.blocks_config[k].get(
            "kwargs", {})) for k, v in BLOCKS_MODULE_REF_DICT.items() if k in self.blocks_config}

    def log(self, level: Levels, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        """Emit a formatted message to the console.

        Parameters
        ----------
        level: Levels
            Severity level (use Levels constants)
        fmt: Styled
            The main message format block (usually a Styled or string)
        """
        if self.enabled == False or level.value < self.level.value:
            return
        text: Styled = Styled(self.text_fmt).format(
            **{k: v.render(level, fmt, *args, **kwargs, logger_name=self.logger_name) for k, v in self.render_blocks.items()})
        # pick colored vs plain representation
        out_text: str = text.styled if self.colored else text.plain
        if level in [Levels.ERROR, Levels.CRITICAL]:
            sys.stderr.write(out_text)
            sys.stderr.flush()
        else:
            sys.stdout.write(out_text)
            sys.stdout.flush()

    # convenience shortcuts -------------------------------------------------
    def trace(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.TRACE, fmt, *args, **kwargs)

    def debug(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.DEBUG, fmt, *args, **kwargs)

    def info(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.INFO, fmt, *args, **kwargs)

    def notice(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.NOTICE, fmt, *args, **kwargs)

    def warn(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.WARNING, fmt, *args, **kwargs)

    def error(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.ERROR, fmt, *args, **kwargs)

    def critical(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.CRITICAL, fmt, *args, **kwargs)


# -------------------------
# File writer
# -------------------------


class FileLogWriter(object):
    """Logger that writes formatted log entries to rotating files.
    """

    def __init__(self, logger_name: Optional[str] = "uvu", config: Optional[Dict[str, Any]] = DEFAULT_LOGGER_CONFIG["file"]) -> None:
        self.logger_name = logger_name
        self.enabled: bool = config.get("enabled", True)
        self.colored: bool = config.get("colored", False)
        save_config: Dict[str, Any] = config.get(
            "save_config", DEFAULT_LOG_SAVE_CONFIG)
        self.root_dir: str = save_config.get(
            "root_dir", DEFAULT_LOG_SAVE_CONFIG["root_dir"])
        self.dir_name_fmt: str = save_config.get(
            "dir_name_fmt", DEFAULT_LOG_SAVE_CONFIG["dir_name_fmt"])
        self.file_name_fmt: str = save_config.get(
            "file_name_fmt", DEFAULT_LOG_SAVE_CONFIG["file_name_fmt"])
        self.cache_lines: int = save_config.get(
            "cache_lines", DEFAULT_LOG_SAVE_CONFIG["cache_lines"])
        self.max_lines: int = save_config.get(
            "max_lines", DEFAULT_LOG_SAVE_CONFIG["max_lines"])
        self.max_size: int = self._xb_xib_to_bytes(save_config.get(
            "max_size", DEFAULT_LOG_SAVE_CONFIG["max_size"]))

        self.level: Levels = config.get("level", Levels.TRACE)
        self.text_fmt: str = config.get("text_fmt", DEFAULT_TEXT_FMT)
        self.blocks_config: Dict[str, Any] = config.get(
            "blocks_config", DEFAULT_BLOCKS_CONF_DICT)
        self.render_blocks: Dict[str, BaseRenderBlock] = {k: v(*self.blocks_config[k].get("args", []), **self.blocks_config[k].get(
            "kwargs", {})) for k, v in BLOCKS_MODULE_REF_DICT.items() if k in self.blocks_config}

        # buffering and rotation state
        self.buffer: List[str] = []
        self.buffered_bytes: int = 0
        self.accum_bytes: int = 0
        self.accum_lines: int = 0
        self.rotate_count: int = 0
        self.curr_root_dir_path: str = None
        self.curr_log_full_path: str = None
        self.file_handle: Optional[int] = None
        self.file_lock: Optional[FileLock] = None
        self.data_lock: threading.Lock = threading.Lock()

    def flush(self) -> None:
        """Force flush any pending buffered lines to disk immediately."""
        self._check_and_flush(None)
        try:
            # ensure directory and file created
            self._fmt_and_create(0)
            # write buffer (if any)
            self._flush_data(''.join(self.buffer).encode('utf-8'))
            # reset accumulators
            self.accum_bytes = 0
            self.accum_lines = 0
            self.buffer.clear()
            self.buffered_bytes = 0
            # hint to the GC to release resources
            gc.collect()
        except Exception:
            # original code intentionally ignores flush errors; preserve that
            ...

    def _xb_xib_to_bytes(self, size_t_str: Optional[Union[int, str]]) -> int:
        """Convert human friendly sizes like "10MiB" or 1024 into bytes.

        Returns 0 for None or an unrecognized unit.
        """
        if size_t_str is None:
            return 0
        if isinstance(size_t_str, int):
            return size_t_str
        size_t_str = size_t_str.strip()
        num, unit = re.match(r'([\d.]+)\s*([a-zA-Z]*)', size_t_str).groups()
        unit = unit.upper()
        # intentionally cast to int to preserve original logic; note this will
        # drop fractional part if provided
        num = int(num)
        size_map: Dict[str, int] = {
            '': 1, 'B': 1, 'KB': 10**3, 'MB': 10**6, 'GB': 10**9, 'TB': 10**12, 'PB': 10**15, 'EB': 10**18, 'ZB': 10**21, 'YB': 10**24,
            'KIB': 2**10, 'MIB': 2**20, 'GIB': 2**30, 'TIB': 2**40, 'PIB': 2**50, 'EIB': 2**60, 'ZIB': 2**70, 'YIB': 2**80
        }
        return num * size_map.get(unit, 0)

    def _close_file_handle(self) -> None:
        """Close the low-level file descriptor (if open) and release the lock."""
        if self.file_handle is not None:
            try:
                os.close(self.file_handle)
            except Exception:
                ...
            finally:
                self.file_handle = None
        if self.file_lock is not None:
            try:
                self.file_lock.release()
            except Exception:
                ...
            finally:
                self.file_lock = None

    def _open_file_handle(self, path: str) -> bool:
        """Open or create the log file and prepare a FileLock.

        Returns
        -------
        bool
            True if the file was newly created, False if it already existed.
        """
        if self.file_handle is not None or self.file_lock is not None:
            self._close_file_handle()
        flags = os.O_CREAT | os.O_APPEND | os.O_WRONLY
        try:
            new_file_created: bool = os.path.exists(path) == False
            self.file_handle = os.open(path, flags, 0o644)
            # create a file lock object for coordination (acquire/release later)
            self.file_lock = FileLock(f"{path}.lock")
            # test acquire/release to ensure lock file can be created
            self.file_lock.acquire()
            self.file_lock.release()
            return new_file_created
        except Exception as e:
            self.file_handle = None
            raise e

    def _fmt_and_create(self, rotate_count_append: int = 0) -> bool:
        """Ensure the current directory exists, compute rotation and return
        whether a new file was created (so callers can reset accumulators).
        """
        os.makedirs(self.root_dir, exist_ok=True)
        curr_dir_path = self.dir_name_fmt.format(
            **{k: "x"+v.render(logger_name=self.logger_name).plain for k, v in self.render_blocks.items()})
        curr_dir_path = str(Path(self.root_dir) / Path(curr_dir_path))
        if curr_dir_path != self.curr_root_dir_path:
            # changed directory -> close previous file handle and create new
            self._close_file_handle()
            self.curr_root_dir_path = curr_dir_path
            os.makedirs(curr_dir_path, exist_ok=True)
        # heuristic used by original code: number of files / 2 then used as rotate
        self.rotate_count = max(len(os.listdir(
            curr_dir_path)) // 2 + rotate_count_append, 0)
        curr_log_file = self.file_name_fmt.format(
            **{k: v.render(logger_name=self.logger_name).plain for k, v in self.render_blocks.items()}, rotate_count=self.rotate_count, logger_name=self.logger_name
        )
        curr_full_path = str(
            (Path(curr_dir_path) / Path(curr_log_file)).absolute())
        if curr_full_path != self.curr_log_full_path:
            self._close_file_handle()
            new_file_created: bool = self._open_file_handle(curr_full_path)
            self.curr_log_full_path = curr_full_path
            return new_file_created
        return False

    def _flush_data(self, data_bytes: bytes) -> None:
        """Write bytes to the file using either the low-level descriptor and
        the file lock or falling back to a standard open/write.
        """
        # FileLock provides a context manager; however the original code calls
        # acquire() directly and re-uses it. Using `with` is safer and clearer.
        if self.file_lock is not None:
            with self.file_lock.acquire():
                if self.file_handle is not None:
                    try:
                        os.write(self.file_handle, data_bytes)
                        return
                    except Exception as e:
                        # if write failed try the fallback
                        self._close_file_handle()
                        raise e
        try:
            # fallback: open the file and append
            with open(self.curr_log_full_path, 'ab') as f:
                f.write(data_bytes)
        except Exception as e:
            raise e

    def _check_and_flush(self, append_data: Optional[str] = None) -> None:
        """Append data to the in-memory buffer and flush to disk when
        thresholds are reached.
        """
        with self.data_lock:
            if append_data is not None and append_data != '':
                self.buffer.append(append_data)
                self.buffered_bytes += len(append_data.encode('utf-8'))
            if len(self.buffer) < self.cache_lines:
                return

            try:
                # if either max_lines or max_size would be exceeded perform a
                # rotate-and-write
                if (self.max_lines > 0 and self.accum_lines + len(self.buffer) >= self.max_lines) or (self.max_size > 0 and self.accum_bytes + self.buffered_bytes >= self.max_size):
                    self._fmt_and_create(0)
                    self._flush_data(''.join(self.buffer).encode('utf-8'))
                    self.accum_bytes = 0
                    self.accum_lines = 0
                else:
                    # otherwise, write and update rotate_count heuristically
                    new_file_created: bool = self._fmt_and_create(-1)
                    self._flush_data(''.join(self.buffer).encode('utf-8'))
                    if new_file_created == True:
                        self.accum_bytes = 0
                        self.accum_lines = 0
                self.buffer.clear()
                self.buffered_bytes = 0
                gc.collect()
            except:
                ...

    def log(self, level: Levels, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        """Prepare a formatted string and append it to the internal buffer.

        The actual writing is handled by `_check_and_flush` which will flush
        when thresholds are reached.
        """
        if self.enabled == False or level.value < self.level.value:
            return
        text: Styled = Styled(self.text_fmt).format(
            **{k: v.render(level, fmt, *args, **kwargs, logger_name=self.logger_name) for k, v in self.render_blocks.items()})
        out_text: str = text.styled if self.colored else text.plain
        return self._check_and_flush(out_text)

    # convenience shortcuts -------------------------------------------------
    def trace(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.TRACE, fmt, *args, **kwargs)

    def debug(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.DEBUG, fmt, *args, **kwargs)

    def info(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.INFO, fmt, *args, **kwargs)

    def notice(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.NOTICE, fmt, *args, **kwargs)

    def warn(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.WARNING, fmt, *args, **kwargs)

    def error(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.ERROR, fmt, *args, **kwargs)

    def critical(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.CRITICAL, fmt, *args, **kwargs)


# -------------------------
# Public Logger wrapper
# -------------------------


class Logger(object):
    """Facade that coordinates optional console and file writers."""

    def __init__(self, config: Optional[Dict[str, Any]] = DEFAULT_LOGGER_CONFIG, **update_configs: Any) -> None:
        config = {**config, **update_configs}
        self.console_logger: Optional[ConsoleLogWritter] = None
        self.file_logger: Optional[FileLogWriter] = None
        if "logger_name" in config:
            self.logger_name = config["logger_name"]
        else:
            self.logger_name = "uvu"
        if "console" in config and config["console"].get("enabled", False) == True:
            self.console_logger = ConsoleLogWritter(
                self.logger_name, config["console"])
        if "file" in config and config["file"].get("enabled", False) == True:
            self.file_logger = FileLogWriter(self.logger_name, config["file"])

    def flush(self) -> None:
        if self.file_logger is not None:
            self.file_logger.flush()

    def log(self, level: Levels, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        if self.console_logger is not None:
            self.console_logger.log(level, fmt, *args, **kwargs)
        if self.file_logger is not None:
            self.file_logger.log(level, fmt, *args, **kwargs)

    # convenience shortcuts -------------------------------------------------
    def trace(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.TRACE, fmt, *args, **kwargs)

    def debug(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.DEBUG, fmt, *args, **kwargs)

    def info(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.INFO, fmt, *args, **kwargs)

    def notice(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.NOTICE, fmt, *args, **kwargs)

    def warn(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.WARNING, fmt, *args, **kwargs)

    def error(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.ERROR, fmt, *args, **kwargs)

    def critical(self, fmt: Styled, *args: Any, **kwargs: Any) -> None:
        return self.log(Levels.CRITICAL, fmt, *args, **kwargs)
