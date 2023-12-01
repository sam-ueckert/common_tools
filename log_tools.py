"""
# Shared logging module

# Step 1: imports:
import setup_logger, log_exceptions

# Step 2: setup your logger (file is optional):
log = setup_logger(filename='foo.txt')

# Step 3 (optional) you can also change the default log level (default is 'INFO') via:
log.setLevel('DEBUG')
log.setLevel('INFO')
log.setLevel('WARNING')
log.setLevel('CRITICAL')

# Step 4: use log per these examples:
log.debug("debug message")
log.info("info message")
log.warning("warning message")
log.critical("critical message")
log.exception("exception")
# or use '@log_exception' decorator for an entire function (see examples below)

# '@log_exception' decorator examples:
    # This re-raises exceptions by default (stops program):
        @log_exceptions
        def foo():
            raise Exception("Something went wrong")

    # This does not re-raise exception (continues):
        @log_exceptions(re_raise=False)
        def foo():
            raise Exception("Something went wrong")
"""
import logging, logging.config
import functools
import path
import yaml
from typing import Callable, ParamSpec, TypeVar, Optional
from .file_tools import get_shared_settings

shared_settings = get_shared_settings()

Param = ParamSpec("Param")
RetType = TypeVar("RetType")
OriginalFunc = Callable[Param, RetType]
DecoratedFunc = Callable[Param, RetType]

def log_exceptions(func:OriginalFunc=None, re_raise: Optional[bool]=True) -> DecoratedFunc:
    if func is None:
        return functools.partial(log_exceptions, re_raise=re_raise)

    @functools.wraps(func)
    def decorated(*args, **kwargs) -> RetType:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(func.__name__)
            logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
            if re_raise:
                raise e

    return decorated

@log_exceptions
def setup_logger(filename='') -> logging.Logger:
    DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s',
            'datefmt': shared_settings['timestamp_format']
            # 'datefmt': "%Y-%m-%d %H:%M:%S %Z%z"
        },
    },
    'handlers': { 
        'default': { 
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'warning': { 
            'level': 'WARNING',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',  # Default is stderr
        },
        'logfile': { 
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': filename,
        },
    },
    'loggers': {
         '': {
              'level': 'INFO',
              'handlers' : ['default', 'warning', 'logfile']
              },
              }
    }
    if filename:
         logging.config.dictConfig(DEFAULT_LOGGING)
    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger()
    return logger


if __name__ == '__main__':
    print("Example logging (you are running this as a script instead of importing)")
    log = setup_logger()

    def test_log_levels():
        log.setLevel('DEBUG')
        print(log)
        log.setLevel('INFO')
        print(log)
        log.setLevel('WARNING')
        print(log)
        log.setLevel('CRITICAL')
        print(log)
        
        log.setLevel('DEBUG')
        log.debug('an debug error')
        log.info('an info error')
        log.warning('an warning error')
        log.critical('an critical error')
        log.exception('an exception error')

    @log_exceptions(re_raise=False)
    def test_without_re_raise():
        raise Exception("Something went wrong")

    @log_exceptions
    def test_with_re_raise():
        raise Exception("Something went wrong")
    
    test_log_levels()
    test_without_re_raise()
    print("continued without re-raise")
    print("------------------------------")
    test_with_re_raise()
    print("should raise exception and not see this")
