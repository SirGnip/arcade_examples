from typing import List, Tuple, Callable


class Timers:
    """Manages timers that are set and calls the callbacks when the timer is up.

    Usage:
        timers = Timers()
        timers.add(7, GlobalFunction)   # can use global functions as callbacks
        timers.add(2.5, self.GotTimer)  # can use class member functions as callbacks

        Don't forget to call Timers.step(time_delta) each frame...
    """

    def __init__(self):
        self._elapsed_seconds = 0.0
        self._timers: List[Tuple[float, Callable[..., None]]] = []

    # def add(self, timer_delay: float, callback: Callable[..., None]) -> None:
    def add(self, timer_delay: float, callback: Callable) -> None:
        trigger_time = self._elapsed_seconds + timer_delay
        self._timers.append((trigger_time, callback))

    def update(self, time_delta: float) -> None:
        """OPTIMIZE: If their are a large number of timers, I could keep the timer list sorted
        in order of when they will be triggered.  This way, I can search the list for the expired
        timers, and the first non-expired timer I find I can stop looking thru the whole list."""
        self._elapsed_seconds += time_delta
        timers_to_del = []
        for timer in self._timers:
            if timer[0] < self._elapsed_seconds:
                timer[1]()  # call callback
                timers_to_del.append(timer)
        # delete expired timers
        for t in timers_to_del:
            self._timers.remove(t)

    def dbg_print(self) -> None:
        for idx, timer in enumerate(self._timers):
            print(f'{idx} - {timer[0]} -> {repr(timer[1])}')

