import logging
import os

LOGGER_NAME = "ark"
LOGLEVEL_KEY = "LOG_LEVEL"


def get_info_dict(config):
    info_dict = {
        "apiVersion": config["API_VERSION"],
        "modelName": config["MODEL_NAME"],
        "modelVersion": config["MODEL"].__version__,
    }
    return info_dict


def _get_formatter(loglevel="INFO"):
    warn_fmt = "[%(asctime)s] %(levelname)s - %(message)s"
    debug_fmt = "[%(asctime)s] [%(filename)s:%(lineno)d] %(levelname)s - %(message)s"
    fmt = debug_fmt if loglevel.upper() in {"DEBUG"} else warn_fmt
    return logging.Formatter(
        fmt=fmt,
        datefmt="%Y-%b-%d %H:%M:%S %Z",
    )


def remove_all_handlers(logger):
    while logger.hasHandlers():
        try:
            logger.removeHandler(logger.handlers[0])
        except IndexError:
            break


def configure_logger(loglevel=None, logger_name=LOGGER_NAME, logfile=None):
    """Do basic logger configuration and set our main logger"""

    # Set as environment variable so other processes can retrieve it
    if loglevel is None:
        loglevel = os.environ.get(LOGLEVEL_KEY, "WARNING")
    else:
        os.environ[LOGLEVEL_KEY] = loglevel

    logger = logging.getLogger(logger_name)
    logger.setLevel(loglevel)
    remove_all_handlers(logger)
    logger.propagate = False

    formatter = _get_formatter(loglevel)

    def _prep_handler(handler):
        for ex_handler in logger.handlers:
            if type(ex_handler) is type(handler):
                # Remove old handler, don't want to double-handle
                logger.removeHandler(ex_handler)
        handler.setLevel(loglevel)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    sh = logging.StreamHandler()
    _prep_handler(sh)

    if logfile is not None:
        fh = logging.FileHandler(logfile, mode="a")
        _prep_handler(fh)

    return logger


def get_logger(base_name=LOGGER_NAME, multiprocessing_safe=False):
    """
    Return a logger.
    If multiprocessing_safe is True, append the process ID to the logger name
    """
    logger_name = base_name
    if multiprocessing_safe:
        pid = os.getpid()
        logger_name = f"{base_name}-process-{pid}"
    logger = logging.getLogger(logger_name)
    if not logger.hasHandlers():
        configure_logger(logger_name=logger_name)
    return logger
