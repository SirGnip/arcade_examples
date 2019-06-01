import time

"""
Utilities to help support the generator-based game script 
"""


def wait_until(predicate):
    """Utility generator that blocks until given predicate evaluates to true"""
    while True:
        if predicate():
            break
        yield


def wait_until_non_none(func):
    """Utility generator that blocks until given function returns a non-None, then returns that value."""
    # Edge case: if "None" is a value you want to return, this will fail
    while True:
        val = func()
        if val is None:
            yield
        else:
            return val


def sleep(delay):
    """Utility generator that blocks for the given amount of time"""
    start = time.time()
    end = start + delay
    while time.time() < end:
        yield
