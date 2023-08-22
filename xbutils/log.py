import sys
import logging

logging.basicConfig(format='%(levelname)s:%(message)s')


def fatal(__text: str, *args, error_code=1, **kwargs):
    logging.fatal(__text, *args, **kwargs)
    sys.exit(error_code)


critical = logging.critical
debug = logging.debug
warning = logging.warning
error = logging.error
info = logging.info
exception = logging.exception


def set_log_level(level: str = None):
    numeric_level = getattr(logging, level.upper(), None)
    if isinstance(numeric_level, int):
        logging.getLogger().setLevel(numeric_level)
