import logging
from logging.handlers import RotatingFileHandler
import logging.config
import os
import multiprocessing

import logging
import logging.config
import yaml
if not logging.root.hasHandlers():
    logging.config.dictConfig(
        yaml.safe_load(open(os.path.dirname(__file__)+'/log_config.yaml', 'r')))
    if (multiprocessing.current_process().name == "MainProcess"):
        logging.info(f"------------------------------------------------------")
        logging.info(f"------------------ NEW APPLICATION START -------------")
        logging.info(f"------------------------------------------------------")
    else:
        logging.info(
            f"launching new process{multiprocessing.current_process().name}")


def add_custom_log_level(level_name, level_num):
    """
    Adds a custom log level to the logging module.

    :param level_name: The name of the custom log level.
    :param level_num: The integer value of the custom log level.
    """
    # Add the custom log level to the logging module
    setattr(logging, level_name, level_num)
    logging.addLevelName(level_num, level_name)

    # Add a method to the Logger class to log messages at the new level
    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self.log(level_num, message, *args, **kwargs)
    setattr(logging.Logger, level_name.lower(), log_for_level)

    # Add a convenience function to the logging module for the custom level
    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)
    setattr(logging, level_name.lower(), log_to_root)


def setup_logging_new():
    # Load the logging configuration from the .yaml file
    logging.info("prepare logging.TRACE")
    add_custom_log_level("TRACE", 5)
    logging.debug("Trace is defined")
    add_custom_log_level("STATUS", 100)
    logging.debug("Status is defined")
    add_custom_log_level("TIMER", 15)
    logging.debug("TIMER is defined")
    logging.debug("Logging setup successfull.")
    l2 = logging.getLogger(__name__)
    if l2.getEffectiveLevel() <= logging.DEBUG and False:
        oldlevel = l2.getEffectiveLevel()
        l2.setLevel(logging.NOTSET)
        l2.debug("Testing new logging levels")
        logging.trace("Trace Test")
        logging.status("Status Test")
        logging.timer("Timer Test")
        l2.trace("Trace Test")
        l2.status("Status Test")
        l2.timer("Timer Test")
        l2.setLevel(oldlevel)

    # Create a logger for your application


setup_logging_new()
logger = logging.getLogger(__name__)
logger.debug(f"initializing: {__name__}")


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
        logger.status("set DEBUGLEVEL=" + logging.getLevelName(logging.getLevelName(
            loglevel)) + " from " + logging.getLevelName(old_level))
    else:
        logger.warning(f"--debug parameter level not known: {loglevel}")
        # pylint: disable=logging-not-lazy
        logger.warning("use one of: "+" ".join(mp.keys()))
        oldlevel = logging.getLevelName(
            logging.getLogger().getEffectiveLevel())
        logger.warning(f"contine with logging level={oldlevel}")


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
