"""
Utilities to help support the generator-based game script
"""
import time

from typing import Callable, List, Optional, TypeVar, Generator

# A generator function used for async "scripting" of game events. A "Generator Script".
GenScript = Generator[None, None, None]


class Scheduler:
    """A Scheduler that manages a pool of generators and updataes them once a frame"""
    def __init__(self) -> None:
        self._pool: List[GenScript] = []

    def add(self, gen: GenScript) -> None:
        """Add generator to pool"""
        try:
            # update generator before adding it to Pool to run code that exists before the first "yield".
            next(gen)
            self._pool.append(gen)
        except StopIteration as e:
            pass

    def update(self) -> None:
        """Update all generators, removing any that are complete"""
        to_del: List[GenScript] = []
        for gen in self._pool:
            try:
                next(gen)
            except StopIteration as e:
                to_del.append(gen)
        for g in to_del:
            self._pool.remove(g)


def wait_until(predicate: Callable[[], bool]) -> GenScript:
    """Utility generator that blocks until given predicate evaluates to true"""
    while True:
        if predicate():
            break
        yield


T = TypeVar("T")


def wait_until_non_none(func: Callable[[], Optional[T]]) -> Generator[None, None, T]:
    """Utility generator that blocks until given function returns a non-None, then returns that value."""
    # Note that the callable "func" is expected to return None ("Optional[T]"). But, wait_until_non_none guarantees the
    # return value is non-none ("T").
    # Edge case: if "None" is a value you want to return, this function won't be useful.
    while True:
        val = func()
        if val is None:
            yield
        else:
            return val


def sleep(delay: float) -> GenScript:
    """Utility generator that blocks for the given amount of time"""
    start = time.time()
    end = start + delay
    while time.time() < end:
        yield
