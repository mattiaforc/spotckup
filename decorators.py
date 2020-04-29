import functools
import logging
import time


def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        log = logging.getLogger('')
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        log.info(f'Finished in {run_time:.16f} secs')
        return value

    return wrapper_timer
