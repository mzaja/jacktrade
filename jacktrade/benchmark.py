import copy
import time
from functools import wraps
from math import log10
from typing import Callable

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------
NS_PER_DAY = 86400_000_000_000
NS_PER_HOUR = 3600_000_000_000
NS_PER_MINUTE = 60_000_000_000
NS_PER_SECOND = 1_000_000_000
NS_PER_MILLISECOND = 1_000_000
NS_PER_MICROSECOND = 1_000


# ---------------------------------------------------------------------------
# CLASSES
# ---------------------------------------------------------------------------
class CodeTimer:
    """
    Times a section of code inside a "with" statement.

    Example usage:
        ```py
        with CodeTimer() as t:
            # Code to time
        print(f"Execution took {t.s} seconds / {t.ms} milliseconds / {t.us} microseconds / {t.ns} nanoseconds.")
        ```

    Parameters:
        - no_print: If True, no message will be printed on exiting the timing block.
        - min_digits: Minimal number of digits to display when printing the result.
        - results:  A list where, if provided, CodeTimer instances holding timing results
                    are stored after every call. Useful when using the class as a decorator
                    to store the results of multiple wrapped function calls.

    Attributes:
        - ns: Code execution time in nanoseconds.
        - us: Code execution time in microseconds.
        - ms: Code execution time in milliseconds.
        - s: Code execution time in seconds.
        - m: Code execution time in minutes.
        - h: Code execution time in hours.
        - d: Code execution time in days.
    """

    _UNITS_SECONDS = ("ns", "us", "ms", "s")

    def __init__(
        self, no_print: bool = False, min_digits: int = 3, results: list = None
    ):
        self._no_print = no_print
        self._min_digits = min_digits
        self._results = results
        self.ns = -1
        self.us = -1
        self.ms = -1
        self.s = -1
        self.m = -1
        self.h = -1
        self.d = -1

    def __enter__(self):
        self._start_time_ns = time.perf_counter_ns()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.ns = time_ns = time.perf_counter_ns() - self._start_time_ns
        self.us = time_ns / NS_PER_MICROSECOND
        self.ms = time_ns / NS_PER_MILLISECOND
        self.s = time_ns / NS_PER_SECOND
        self.m = time_ns / NS_PER_MINUTE
        self.h = time_ns / NS_PER_HOUR
        self.d = time_ns / NS_PER_DAY

        if not self._no_print:
            print(
                f"Code execution took {self._format_time(time_ns, self._min_digits)}."
            )
        if self._results is not None:
            self._results.append(copy.copy(self))

    def __call__(self, function: Callable):
        """For using the class as a decorator."""

        @wraps(function)
        def wrapper(*args, **kwargs):
            with self:
                retval = function(*args, **kwargs)
            return retval

        return wrapper

    @classmethod
    def _format_time(cls, time_ns: int, min_digits: int) -> str:
        """Formats the time string based on the duration in nanoseconds."""
        # Sub 60 seconds, format in seconds, else use calendar time format
        if (time_ns / NS_PER_MINUTE) < 1:
            return cls._format_time_seconds(time_ns, min_digits)
        else:
            return cls._format_time_d_hh_mm_ss(time_ns, min_digits)

    @staticmethod
    def _count_digits(number: int) -> int:
        """Returns the number of digits in the provided integer."""
        # len(str(number)) is much slower than this solution
        return int(log10(number)) + 1 if number else 0

    @classmethod
    def _format_time_seconds(cls, time_ns: int, min_digits: int) -> str:
        """
        Automatically selects the suitable second-based time unit and returns
        a formatted string representation of time.
        """
        n_digits = cls._count_digits(time_ns)
        n_divisions = min(
            (n_digits - 1) // 3, len(cls._UNITS_SECONDS) - 1
        )  # How many times to divide by 1000
        digits_after_division = n_digits - 3 * n_divisions
        time_after_division = time_ns / (1000**n_divisions)
        decimal_places = max(0, min_digits - digits_after_division)
        fmt = (
            ",." + str(decimal_places) + "f"
        )  # How many digits spill over behind the decimal place
        return f"{time_after_division:{fmt}} {cls._UNITS_SECONDS[n_divisions]}"

    @classmethod
    def _format_time_d_hh_mm_ss(cls, time_ns: int, min_digits: int) -> str:
        """Formats the time in "[[d days, ]hh:]mm:ss[.ms]" format."""
        days, remainder_ns = divmod(time_ns, NS_PER_DAY)
        hours, remainder_ns = divmod(remainder_ns, NS_PER_HOUR)
        minutes, remainder_ns = divmod(remainder_ns, NS_PER_MINUTE)
        seconds, remainder_ns = divmod(remainder_ns, NS_PER_SECOND)
        # Determine the number of decimal places to display
        decimal_places = min_digits
        timestr = ""
        more_above = False  # Greater units of time are above zero
        if days > 0:
            decimal_places -= cls._count_digits(days)
            timestr += f"{days:,} day{'s' if days > 1 else ''}, "
            more_above = True
        if (time_ns / NS_PER_HOUR) >= 1:
            timestr += f"{hours:02d}:"
            decimal_places -= 2 if more_above else cls._count_digits(hours)
            more_above = True
        if (time_ns / NS_PER_MINUTE) >= 1:
            decimal_places -= 2 if more_above else cls._count_digits(minutes)
            more_above = True
        if (time_ns / NS_PER_SECOND) >= 1:
            decimal_places -= 2 if more_above else cls._count_digits(seconds)

        decimal_places = max(decimal_places, 0)
        return (
            timestr
            + f"{minutes:02d}:{seconds:02d}"
            + (
                f"{remainder_ns / NS_PER_SECOND:.{decimal_places}f}"[1:]
                if decimal_places
                else ""
            )
        )
