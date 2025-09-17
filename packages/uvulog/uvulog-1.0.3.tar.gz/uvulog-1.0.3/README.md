# uvulog

A simple logger for console and file logging, with colored output and log rotation.

![human-coded](https://img.shields.io/badge/human-coded-green?style=for-the-badge)
<span> </span>
![llm-documents](https://img.shields.io/badge/llm-documents-indigo?style=for-the-badge&logo=openai)

## Features

- **Colored terminal output**: ANSI color support, log levels highlighted.
- **File log rotation**: Automatic log file splitting, with cache and size/line limits.
- **Extensible render blocks**: Pluggable blocks for time, process ID, counters, source file, line number, etc.
- **Process safety**: Safe writing in multi-process/multi-threaded environments, with file locking.
- **High performance**: Memory buffering, batch writes, optimized for low overhead.
- **User-friendly API**: Easy integration, shortcut methods (`info`, `debug`, `error`, etc.).

## Quick Start

```python
from uvulog import Logger, Styled, Styles

logger = Logger()
logger.info(Styled("Hello uvulog!", Styles.GREEN, Styles.BOLD))
logger.error(Styled("Something went wrong!", Styles.RED, Styles.UNDERLINE))
```

## Log Levels

- TRACE
- DEBUG
- INFO
- NOTICE
- WARNING
- ERROR
- CRITICAL

Each level supports custom styles and formatting.

## File Log Rotation

- Automatically splits log files by size or line count
- Supports line caching to reduce disk IO
- Safe file locking to prevent concurrent write conflicts

**There is no config to directly enable/disable rotation. To enable this feature, you should add `{rotate_count}`, `{date}` or other enabled keys in blocks to `file`.`save_config`.`file_name_fmt`**

## Render Block Examples

- Timestamp `[2025-09-17 12:00:00]`
- Log level `INFO`
- Main message content
- Process ID, counter, source file, line number, etc.

---

## Installation

```bash
pip install uvulog
```

---

## Configuration Guide

You can fully customize uvulog using a configuration dictionary when creating a `Logger` instance.  
Below is a detailed example and explanation of each option:

```python
from uvulog import Logger, Levels

custom_config = {
    "logger_name": "myapp",
    "console": {
        "enabled": True,                # Enable console output
        "colored": True,                # Use ANSI colors in terminal
        "level": Levels.DEBUG,          # Minimum log level for console
        "text_fmt": "{time}{level}{main}\n",  # Output format
        "blocks_config": {              # Customize render blocks
            "time": {
                "args": [
                    ["[", 90],          # Bright black
                    ["{}", 97],         # Bright white
                    ["]", 90]
                ],
                "kwargs": {
                    "time_format": "%H:%M:%S"
                }
            },
            "level": {
                "args": [["{}"]],
                "kwargs": {
                    "levels": {
                        Levels.INFO: [[" I ", 37]],      # White
                        Levels.ERROR: [[" E ", 41, 30]]  # Red background, black text
                    }
                }
            },
            "main": {
                "args": [["{}"]],
                "kwargs": {
                    "levels": {
                        Levels.INFO: [["{}", 37]],
                        Levels.ERROR: [["{}", 91]]       # Bright red
                    }
                }
            }
        }
    },
    "file": {
        "enabled": True,                # Enable file logging
        "colored": False,               # No ANSI colors in file
        "save_config": {
            "root_dir": "logs",         # Log directory
            "file_name_fmt": "myapp.log", # Log file name
            "cache_lines": 100,         # Buffer lines before writing
            "max_lines": 10000,         # Max lines per file
            "max_size": 10 * 1024 * 1024 # Max size per file (bytes)
        },
        "level": Levels.INFO,           # Minimum log level for file
        "text_fmt": "{time}{level}{main}\n",
        "blocks_config": None           # Use default if None
    }
}

logger = Logger(config=custom_config)
```

### Configuration Options

- **logger_name**: Name of the logger, used in output.
- **console.enabled**: Enable/disable console output.
- **console.colored**: Use colored output in terminal.
- **console.level**: Minimum log level for console output.
- **console.text_fmt**: Format string for each log line.
- **console.blocks_config**: Dict to customize each block (time, level, main, etc.).
- **file.enabled**: Enable/disable file logging.
- **file.colored**: Use colored output in log files.
- **file.save_config.root_dir**: Directory to save log files.
- **file.save_config.file_name_fmt**: Log file name format.
- **file.save_config.cache_lines**: Number of lines to buffer before writing.
- **file.save_config.max_lines**: Maximum lines per log file.
- **file.save_config.max_size**: Maximum size per log file (in bytes).
- **file.level**: Minimum log level for file output.
- **file.text_fmt**: Format string for file log lines.
- **file.blocks_config**: Dict to customize blocks for file output.

You can override any block (such as time, level, main) with your own style and format.

---

## Use Cases

- Suitable for AI, data science, web backend, CLI tools, and all Python projects
- Supports multi-process/multi-threaded environments
- Compatible with Linux, Mac, and Windows

---

## License

MIT
