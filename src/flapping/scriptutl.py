"""
Utilities to help support the generator-based game script
"""
import time

from typing import Any, Callable, Iterator, List
Script = Iterator[None]  # This is meant to be a generator function used for async "scripting". Making more self-documenting.

class Pool:
    """A pool that manages generators and updataes them once a frame"""
    def __init__(self) -> None:
        self._pool: List[Script] = []

    def add(self, gen: Script) -> None:
        """Add generator to pool"""
        try:
            # update generator before adding it to Pool to run code that exists before the first "yield".
            next(gen)
            self._pool.append(gen)
        except StopIteration as e:
            pass

    def update(self) -> None:
        """Update all generators in the Pool, removing any that are complete"""
        to_del: List[Script] = []
        for gen in self._pool:
            try:
                next(gen)
            except StopIteration as e:
                to_del.append(gen)
        for g in to_del:
            self._pool.remove(g)


def wait_until(predicate: Callable[[], bool]) -> Iterator[None]:
    """Utility generator that blocks until given predicate evaluates to true"""
    while True:
        if predicate():
            break
        yield

# need to do a generic so that the return type of "func()" is the Iterator[Optional[FUNC_TYPE]]
def wait_until_non_none(func: Callable[[], Any]) -> Iterator[None]:
    """Utility generator that blocks until given function returns a non-None, then returns that value."""
    # Edge case: if "None" is a value you want to return, this will fail
    while True:
        val = func()
        if val is None:
            yield
        else:
            return val


def sleep(delay: float) -> Iterator[None]:
    """Utility generator that blocks for the given amount of time"""
    start = time.time()
    end = start + delay
    while time.time() < end:
        yield
