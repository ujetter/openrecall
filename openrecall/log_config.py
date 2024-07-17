import logging
from logging.handlers import RotatingFileHandler
import logging.config
import json
import os

import logging
import logging.config
import yaml

_log_already_initialized = False


def setup_logging_new():
    # Load the logging configuration from the .yaml file
    STATUS_LEVEL_NUM = 100
    logging.STATUS = STATUS_LEVEL_NUM
    logging.addLevelName(STATUS_LEVEL_NUM, "STATUS")

    # Add a method to the Logger class to log messages at the new level
    def status(self, message, *args, **kws):
        if self.isEnabledFor(STATUS_LEVEL_NUM):
            self.log(STATUS_LEVEL_NUM, message, *args, **kws)
    logging.Logger.status = status

    def status2(message, *args, **kws):
        logging.log(STATUS_LEVEL_NUM, message, *args, **kws)
    logging.status = status2
    logging.status("setup_logging")
    with open(os.path.dirname(__file__)+'/log_config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        logging.config.dictConfig(config)
    logging.log(200, "config read")

    # Create a logger for your application


if not _log_already_initialized:
    logging.critical(f"Info---{_log_already_initialized}")
    setup_logging_new()
    _log_already_initialized = True
logger = logging.getLogger(__name__)
logging.status(__name__)


def setup_logging(log_file='openrecall.log', max_bytes=10000, backup_count=0):
    # Configure the root logger
    # logger = logging.getLogger()
    STATUS_LEVEL_NUM = 100
    logging.STATUS = STATUS_LEVEL_NUM
    logging.addLevelName(STATUS_LEVEL_NUM, "STATUS")

    # Add a method to the Logger class to log messages at the new level
    def status(self, message, *args, **kws):
        if self.isEnabledFor(STATUS_LEVEL_NUM):
            self._log(STATUS_LEVEL_NUM, message, args, **kws)
    logging.Logger.status = status
    logging.status = status

    DEBUG2_LEVEL_NUM = 25
    logging.DEBUG2 = DEBUG2_LEVEL_NUM
    logging.addLevelName(DEBUG2_LEVEL_NUM, "DEBUG2")

    # Add a method to the Logger class to log messages at the new level
    def debug2(self, message, *args, **kws):
        if self.isEnabledFor(DEBUG2_LEVEL_NUM):
            self._log(DEBUG2_LEVEL_NUM, message, args, **kws)
    logging.Logger.status = debug2
    logging.status = debug2

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG2)

    # Create a file handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setLevel(logging.NOTSET)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.NOTSET)

    # Create a logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the root logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.WARNING)


# setup_logging()


def log_always(*args):
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    logger.setLevel(logging.INFO)
    logger.info(" ".join(map(str, args)))  # pylint: disable=bad-builtin
    logger.setLevel(old_level)


def set_logging_level(loglevel):
    mp = logging.getLevelNamesMapping()
    if loglevel in mp:
        root_logger = logging.getLogger()
        old_level = root_logger.getEffectiveLevel()
        root_logger.setLevel(mp[loglevel])
        log_always("set DEBUGLEVEL=", logging.getLevelName(logging.getLevelName(
            loglevel)), "from", logging.getLevelName(old_level))
    else:
        logging.error(f"Debug level not known: {loglevel}")
        # pylint: disable=logging-not-lazy
        logging.error("use one of: "+" ".join(mp.keys())
                      )


def show_registered_loggers():
    from io import StringIO
    result_stream = StringIO()
    root_logger = logging.getLogger()
    loggers = [root_logger] + \
        [logging.getLogger(name) for name in logging.Logger.manager.loggerDict]

    for logger in loggers:
        result_stream.write(f"Logger: {logger.name}\n")
        for handler in logger.handlers:
            result_stream.write(
                f"    Handler: {handler.__class__.__name__}\n")
            if isinstance(handler, logging.FileHandler) or isinstance(handler, logging.handlers.RotatingFileHandler):
                result_stream.write(
                    f"        Filename: {handler.baseFilename}\n")
            result_stream.write(
                f"        Level: {logging.getLevelName(handler.level)}\n")
        if not logger.handlers:
            result_stream.write("    No handlers registered.\n")
        result_stream.write("\n")
    result = result_stream.getvalue()
    result_stream.close()
    return result

# show_registered_loggers()
