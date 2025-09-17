"""
Logging
------------

Logging tools with cpymad perks.
"""
from __future__ import annotations

import logging
import subprocess
import sys
from collections import defaultdict
from contextlib import suppress
from pathlib import Path

# Log Levels should be higher than info to be able to filter debug
# messages in the output and not get line duplicates
LOG_OUT_LVL = logging.WARNING - 2
LOG_CMD_LVL = logging.WARNING - 1

MADXCMD = 'madxcmd'
MADXOUT = 'madxout'

# ASCII Colors, change to your liking (the last three three-digits are RGB)
# Default colors should be readable on dark and light backgrounds
COLORS = dict(  # noqa: C408
    reset='\33[0m',
    name='\33[0m\33[38;2;127;127;127m',
    msg='',
    cmd_name='\33[0m\33[38;2;132;168;91m',
    cmd_msg='',
    out_name='\33[0m\33[38;2;114;147;203m',
    out_msg='\33[0m\33[38;2;127;127;127m',
    warn_name='',
    warn_msg='\33[0m\33[38;2;193;134;22m',
)


class StreamToLogger:
    """ File-like stream object that redirects writes to a logger instance. """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        last_line_empty = False
        for line in buf.rstrip().splitlines():
            with suppress(AttributeError):
                line = line.decode('utf-8')  # convert madx output from binary
            line = line.rstrip()

            if last_line_empty or len(line):
                self.logger.log(self.log_level, line)
                last_line_empty = False
            else:
                last_line_empty = True  # skips multiple empty lines

    def __call__(self, *args, **kwargs):
        self.write(*args, **kwargs)

    def flush(self):
        for handler in self.logger.handlers:
            handler.flush()


class MaxFilter(logging.Filter):
    """ To get messages only up to a certain level """
    def __init__(self, level):
        super(MaxFilter, self).__init__()
        self.__level = level

    def filter(self, log_record):
        return log_record.levelno <= self.__level


def _lvl_fmt(name_color='', msg_color=''):
    """ Defines the level/message formatter with colors """
    name_reset, msg_reset = '', ''
    if name_color:
        name_reset = COLORS['reset']
    if msg_color:
        msg_reset = COLORS['reset']

    return logging.Formatter(
        f'{name_color}%(levelname)7s{name_reset}'
        f' | '
        f'{msg_color}%(message)s{msg_reset}'
    )


def cpymad_logging_setup(
        command_log: Path = Path('madx_commands.log'),
        full_log: Path = Path('full_output.log'),
        output_log: Path = None,
        colors: bool = True,
        level=logging.INFO,
        clear_handlers: bool = True,
):
    """ Create all necessary logging.
    Adds stream handlers to root logger including cpymad loggers for output and commands.
    Takes also care of file handlers if specified.

    Args
        output_log: Path to write madx-output to (None to deactivate)
        command_log: Path to write madx-commands to (None to deactivate)
        full_log: Path to write full logging output to (None to deactivate)
        colors: Bool whether ascii-colors should be used
        level: Minimum stdout logging level. Madx commands and output are always logged
        clear_loggers: Clears all handlers of the loggers first.

    Returns
        dict with StreamToLoggers 'stdout' and 'command_log'.
        Can be used as `Madx(**cpymad_logging_setup())`
    """
    cdict = defaultdict(str)
    if colors:
        cdict.update(COLORS)

    msg_fmt = logging.Formatter('%(message)s')

    logging.addLevelName(LOG_OUT_LVL, 'madx')
    logging.addLevelName(LOG_CMD_LVL, 'cmd')

    # Setup Root Logger
    root_logger = logging.getLogger("")
    if clear_handlers:
        root_logger.handlers = []  # remove handlers in case someone already created them
    root_logger.setLevel(logging.NOTSET)

    if full_log is not None:
        # Add full logging to file
        fullfile_handler = logging.FileHandler(full_log, mode='w', )
        fullfile_handler.setFormatter(_lvl_fmt())
        root_logger.addHandler(fullfile_handler)

    # Add full logging to stdout
    fullstream_handler = logging.StreamHandler(sys.stdout)
    fullstream_handler.setLevel(level)
    fullstream_handler.addFilter(MaxFilter(min(LOG_CMD_LVL, LOG_OUT_LVL, logging.WARNING)-1))
    fullstream_handler.setFormatter(_lvl_fmt(cdict['name'], cdict['msg']))
    root_logger.addHandler(fullstream_handler)

    if level <= logging.WARNING:
        warnstream_handler = logging.StreamHandler(sys.stdout)
        warnstream_handler.setLevel(logging.WARNING)
        warnstream_handler.addFilter(MaxFilter(logging.WARNING))
        warnstream_handler.setFormatter(_lvl_fmt(cdict['warn_name'], cdict['warn_msg']))
        root_logger.addHandler(warnstream_handler)

    cmdstream_handler = logging.StreamHandler(sys.stdout)
    cmdstream_handler.setLevel(LOG_CMD_LVL)
    cmdstream_handler.addFilter(MaxFilter(LOG_CMD_LVL))
    cmdstream_handler.setFormatter(_lvl_fmt(cdict['cmd_name'], cdict['cmd_msg']))
    root_logger.addHandler(cmdstream_handler)

    outstream_handler = logging.StreamHandler(sys.stdout)
    outstream_handler.setLevel(LOG_OUT_LVL)
    outstream_handler.addFilter(MaxFilter(LOG_OUT_LVL))
    outstream_handler.setFormatter(_lvl_fmt(cdict['out_name'], cdict['out_msg']))
    root_logger.addHandler(outstream_handler)

    # create file-like loggers for madx-instance
    # create logger for madx output
    madx_out_logger = logging.getLogger(MADXOUT)
    if clear_handlers:
        madx_out_logger.handlers = []

    if output_log is not None:
        # log everything also to file
        madx_out_handler = logging.FileHandler(output_log, mode='w', )
        madx_out_handler.setFormatter(msg_fmt)
        madx_out_logger.addHandler(madx_out_handler)
    out_stream = StreamToLogger(madx_out_logger, log_level=LOG_OUT_LVL)

    # create logger for madx commands
    madx_cmd_logger = logging.getLogger(MADXCMD)
    if clear_handlers:
        madx_cmd_logger.handlers = []

    if command_log is not None:
        # log everything also to file
        madx_cmd_handler = logging.FileHandler(command_log, mode='w', )
        madx_cmd_handler.setFormatter(msg_fmt)
        madx_cmd_logger.addHandler(madx_cmd_handler)
    cmd_stream = StreamToLogger(madx_cmd_logger, log_level=LOG_CMD_LVL)

    return dict(stdout=out_stream, command_log=cmd_stream, stderr=subprocess.STDOUT)  # noqa: C408
