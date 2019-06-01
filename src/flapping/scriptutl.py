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


def sleep(delay):
    """Utility generator that blocks for the given amount of time"""
    start = time.time()
    end = start + delay
    while time.time() < end:
        yield
