import logging
import os
import sys
import time
from logging import Formatter

_loggers = {}

COLORED_LOG_MAPPING = {
    'DEBUG': 37,  # white
    'INFO': 36,  # cyan
    'WARNING': 33,  # yellow
    'ERROR': 31,  # red
    'CRITICAL': 41,  # white on red bg
}

COLOR_PREFIX = '\033['
COLOR_SUFFIX = '\033[0m'


class ColoredFormatter(Formatter):

    def __init__(self, fmt):
        Formatter.__init__(self, fmt)

    def format(self, record):
        colored_record = record  # copy(record)
        levelName = colored_record.levelname
        seq = COLORED_LOG_MAPPING.get(levelName, 37)  # default white
        colored_levelname = '{0}{1}m{2}{3}'.format(COLOR_PREFIX, seq, levelName[:4], COLOR_SUFFIX)
        colored_record.levelname = colored_levelname
        return Formatter.format(self, colored_record)


def setup_custom_logger(name, log_level=logging.INFO):
    if name in _loggers:
        return _loggers[name]

    formatter = ColoredFormatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger_ = logging.getLogger(name)
    logger_.setLevel(log_level)

    if logger_.hasHandlers():
        logger_.handlers.clear()

    logger_.addHandler(handler)
    logger_.propagate = False

    _loggers[name] = logger_

    return logger_


# noinspection PyProtectedMember
def exit_process(is_error=True):
    from threading import Thread
    import _thread
    status = 1 if is_error else 0
    Thread(target=lambda: (time.sleep(3), _thread.interrupt_main()), daemon=True).start()
    Thread(target=lambda: (time.sleep(6), os._exit(status)), daemon=True).start()
    sys.exit(status)
